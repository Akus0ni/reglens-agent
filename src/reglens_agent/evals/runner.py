"""Running the scenarios live (recording) or from recordings (the CI gate) (spec 0002, R2.3, R2.4, R2.6, R2.7)."""

import json
import statistics
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver

from reglens_agent.evals.checks import Scenario, check, count, gate, load_scenarios
from reglens_agent.evals.recording import StaleRecording, Store, Throttle, recorded_models, recorded_tools
from reglens_agent.filing import Filer
from reglens_agent.graph import Models, build_graph, thread_config
from reglens_agent.pricing import cost_usd
from reglens_agent.settings import ASSESSOR_MODEL, PLANNER_MODEL, RESEARCH_MODEL

RECORDINGS = Path("evals/recordings")
RUNS = Path("evals/runs")
BASELINE = Path("evals/baseline.json")
MODEL_NAMES = (PLANNER_MODEL, RESEARCH_MODEL, ASSESSOR_MODEL)
READS_PER_MINUTE = 25  # under RegLens's 30 reads a minute per caller


async def run_scenario(scenario: Scenario, models: Models | None, tools: list, store: Store,
                       throttle: Throttle | None = None) -> dict[str, Any]:
    """One review to the approval interrupt; nothing is filed (no resume)."""
    graph = build_graph(recorded_models(models, store, MODEL_NAMES), recorded_tools(tools, store, throttle),
                        Filer(Path(tempfile.gettempdir()) / "reglens-agent-evals", "unused/unused"))
    started = time.perf_counter()
    state = await graph.compile(checkpointer=InMemorySaver()).ainvoke(
        {"thread_id": scenario.id, "feature": scenario.feature, "create_issue": False}, thread_config(scenario.id))
    seconds = time.perf_counter() - started
    state = {k: v for k, v in state.items() if k not in ("messages", "__interrupt__")}
    return {"state": state, "checks": check(scenario, state), "usage": state.get("usage", {}),
            "cost_usd": cost_usd(state.get("usage", {})), "seconds": round(seconds, 1)}


def _log(line: str) -> None:
    print(line, flush=True)


async def record(runs: list[int], models: Models, tools: list, only: list[str] | None = None,
                 log: Any = _log) -> list[Path]:
    """Live runs, numbered ``runs``. Run 1's recordings become the gate's (R2.3). ``only`` limits the scenarios, so
    one scenario or one lost run can be recorded again without repeating the rest; the report merges run files by
    run number."""
    scenarios = [s for s in load_scenarios() if not only or s.id in only]
    if only and len(scenarios) != len(only):
        raise SystemExit(f"Unknown scenario id in {only}.")
    throttle = Throttle(READS_PER_MINUTE)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    written: list[Path] = []
    RUNS.mkdir(parents=True, exist_ok=True)
    RECORDINGS.mkdir(parents=True, exist_ok=True)
    for run in runs:
        results: dict[str, Any] = {}
        for scenario in scenarios:
            store = Store(scenario.id)
            result = await run_scenario(scenario, models, tools, store, throttle)
            results[scenario.id] = result
            failed = [n for n, r in result["checks"].items() if r["passed"] is False]
            log(f"run {run} {scenario.id}: ${result['cost_usd']:.4f}, {result['seconds']} s, "
                + ("all checks pass" if not failed else f"failed: {', '.join(failed)}"))
            if run == 1:
                _write_json(RECORDINGS / f"{scenario.id}.json", store.data)
        path = RUNS / f"{stamp}-r{run}.json"
        _write_json(path, {"run": run, "started_utc": stamp, "commit": _commit(), "models": list(MODEL_NAMES),
                           "scenarios": results, "summary": summarize(results)})
        written.append(path)
        log(f"run {run}: {summarize(results)}")
    return written


async def replay_all() -> dict[str, dict]:
    """Every scenario from its recording. A missing or stale recording fails that scenario's checks with the reason;
    the other scenarios are still checked, so one run of the gate shows every problem."""
    checks: dict[str, dict] = {}
    for scenario in load_scenarios():
        path = RECORDINGS / f"{scenario.id}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        checks[scenario.id] = await replay_scenario(scenario, data)
    return checks


async def replay_scenario(scenario: Scenario, recording: dict | None) -> dict[str, dict]:
    if recording is None:
        return unreplayable(scenario, f"no recording ({RECORDINGS / (scenario.id + '.json')})")
    store = Store(scenario.id, recording, replay=True)
    try:
        return (await run_scenario(scenario, None, _replay_tool_stubs(store), store))["checks"]
    except StaleRecording as stale:
        return unreplayable(scenario, str(stale))


def unreplayable(scenario: Scenario, reason: str) -> dict[str, dict]:
    """Every applicable check fails with the reason, so the gate counts the scenario as failing."""
    failed = {"passed": False, "detail": reason}
    skipped = {"passed": None, "detail": "not replayed"}
    return {"completed": failed, "guards": skipped, "searched": skipped, "verified": skipped,
            "required": failed if scenario.in_scope else skipped, "severity": failed if scenario.in_scope else skipped,
            "quiet": skipped if scenario.in_scope else failed}


def check_gate(checks: dict[str, dict], write_baseline: bool = False) -> list[str]:
    if write_baseline and any(r["completed"]["passed"] is False for r in checks.values()):
        return ["Refusing to write a baseline: some scenarios did not replay (see above)."]
    if write_baseline:
        _write_json(BASELINE, {"required": count(checks, "required"), "severity": count(checks, "severity"),
                               "written_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "commit": _commit()})
    if not BASELINE.exists():
        return [f"No baseline ({BASELINE}). Write it once from an accepted run with `eval check --write-baseline`."]
    return gate(checks, json.loads(BASELINE.read_text(encoding="utf-8")))


def merged_runs(paths: list[Path]) -> list[dict[str, Any]]:
    """Run files merged by run number, oldest first: a later file's scenario replaces an earlier one (a re-record)."""
    runs: dict[int, dict[str, Any]] = {}
    for path in sorted(paths):
        data = json.loads(path.read_text(encoding="utf-8"))
        run = runs.setdefault(data["run"], {"run": data["run"], "files": [], "commits": [], "models": data["models"],
                                            "scenarios": {}, "judge_usage": {}})
        run["files"].append(path.name)
        run["commits"].append(data["commit"])
        run["scenarios"].update(data["scenarios"])
        for model, counts in data.get("judge", {}).get("usage", {}).items():
            total = run["judge_usage"].setdefault(model, {"input": 0, "output": 0, "calls": 0})
            for key, value in counts.items():
                total[key] += value
    for run in runs.values():
        run["summary"] = summarize(run["scenarios"])
    return [runs[n] for n in sorted(runs)]


def summarize(results: dict[str, Any]) -> dict[str, Any]:
    checks = {s: r["checks"] for s, r in results.items()}
    names = ("completed", "guards", "searched", "verified", "quiet", "required", "severity")
    applicable = {n: sum(1 for c in checks.values() if c[n]["passed"] is not None) for n in names}
    costs = [r["cost_usd"] for r in results.values()]
    seconds = [r["seconds"] for r in results.values()]
    return {"passed": {n: f"{count(checks, n)}/{applicable[n]}" for n in names},
            "cost_usd": round(sum(costs), 4), "cost_per_review_usd": round(statistics.mean(costs), 4),
            "p50_seconds": statistics.median(seconds)}


def _replay_tool_stubs(store: Store) -> list:
    """Stand-ins with the recorded tools' names and schemas; their calls are answered by the store."""
    from langchain_core.tools import StructuredTool

    async def unreachable(**_: Any) -> None:
        raise RuntimeError("A live RegLens call during replay.")

    names = sorted({saved["name"] for saved in store.data["tools"].values()} | {"search_regulations", "get_passage"})
    schemas = {"search_regulations": {"type": "object", "properties": {"query": {"type": "string"},
                                                                       "topK": {"type": ["integer", "null"]}},
                                      "required": ["query"]},
               "get_passage": {"type": "object", "properties": {"chunkId": {"type": "integer"}}, "required": ["chunkId"]}}
    return [StructuredTool.from_function(coroutine=unreachable, name=name, description=name,
                                         args_schema=schemas.get(name, {"type": "object"})) for name in names]


def _commit() -> str:
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout
        dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True).stdout
        return sha.strip() + ("-dirty" if dirty.strip() else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
