"""`reglens-agent eval …` (spec 0002, R2.3, R2.6–R2.10).

  eval record --runs 2 --confirm-spend   live runs; run 1 becomes the gate's recordings (~$0.05 per review)
  eval check [--write-baseline]          replay the recordings and apply the gate (free, offline; CI runs this)
  eval judge --confirm-spend [--run F]   score the memos with claude-haiku-4-5; writes evals/hand-check.md
  eval report [RUN ...]                  write evals/results.md
"""

import argparse
import sys
from pathlib import Path
from urllib.parse import urlsplit

from reglens_agent.evals.checks import load_scenarios
from reglens_agent.evals.runner import RUNS, check_gate, record, replay_all
from reglens_agent.pricing import cost_usd
from reglens_agent.settings import Settings


def add_parser(commands: argparse._SubParsersAction) -> None:
    evals = commands.add_parser("eval", help="Trajectory evals and the CI gate (spec 0002).")
    sub = evals.add_subparsers(required=True)

    rec = sub.add_parser("record", help="Run every scenario live and record it.")
    rec.add_argument("--runs", type=int, default=2, help="How many runs, numbered from --first-run.")
    rec.add_argument("--first-run", type=int, default=1, help="Number of the first run (run 1 writes recordings).")
    rec.add_argument("--scenario", action="append", help="Only these scenario ids (repeatable).")
    rec.add_argument("--confirm-spend", action="store_true")
    rec.set_defaults(handler=_record)

    chk = sub.add_parser("check", help="Replay the recordings and apply the gate.")
    chk.add_argument("--write-baseline", action="store_true", help="Store this replay as the baseline (R2.7).")
    chk.set_defaults(handler=_check)

    jdg = sub.add_parser("judge", help="Score memos with the judge and write the hand-check sheet.")
    jdg.add_argument("--run", action="append", help="Run file(s); default: the latest runs.")
    jdg.add_argument("--confirm-spend", action="store_true")
    jdg.set_defaults(handler=_judge)

    rep = sub.add_parser("report", help="Write evals/results.md.")
    rep.add_argument("runs", nargs="*")
    rep.set_defaults(handler=_report)


async def _record(args: argparse.Namespace, settings: Settings) -> int:
    if not args.confirm_spend:
        print(f"eval record runs {len(load_scenarios())} reviews per run (~$0.05 each). Re-run with --confirm-spend.",
              file=sys.stderr)
        return 2
    settings.require("ANTHROPIC_API_KEY", "REGLENS_API_KEY")
    if not _reglens_ready(settings.reglens_mcp_url):
        print("RegLens is not ready (GET /health/ready). Start it first.", file=sys.stderr)
        return 1
    from reglens_agent.cli import _live_models, _reglens_tools
    from reglens_agent.telemetry import telemetry

    with telemetry(settings.otlp_endpoint):
        runs = list(range(args.first_run, args.first_run + args.runs))
        paths = await record(runs, _live_models(), await _reglens_tools(settings), only=args.scenario)
    print("Wrote " + ", ".join(str(p) for p in paths))
    return 0


async def _check(args: argparse.Namespace, _: Settings) -> int:
    checks = await replay_all()
    failures = check_gate(checks, write_baseline=args.write_baseline)
    for scenario, results in checks.items():
        print(f"{scenario}: " + ", ".join(f"{n} {'ok' if r['passed'] else ('-' if r['passed'] is None else 'FAIL')}"
                                          for n, r in results.items()))
    if failures:
        print("\nGate FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("\nGate passed." + (" Baseline written." if args.write_baseline else ""))
    return 0


async def _judge(args: argparse.Namespace, settings: Settings) -> int:
    if not args.confirm_spend:
        print("eval judge calls claude-haiku-4-5 once per memo. Re-run with --confirm-spend.", file=sys.stderr)
        return 2
    settings.require("ANTHROPIC_API_KEY")
    from langchain_anthropic import ChatAnthropic

    from reglens_agent.evals.judge import JUDGE_MODEL, judge_run, write_hand_check

    runs = [Path(p) for p in args.run] if args.run else _latest_runs()
    features = {s.id: s.feature for s in load_scenarios()}
    model = ChatAnthropic(model=JUDGE_MODEL, temperature=0, max_tokens=1024, max_retries=2)
    for path in runs:
        usage = await judge_run(path, features, model)
        print(f"Judged {path.name}: ${cost_usd(usage):.4f}")
    from reglens_agent.evals.runner import merged_runs

    write_hand_check(merged_runs(runs)[0], features)
    print("Wrote evals/hand-check.md (labels to fill in before `eval report`).")
    return 0


async def _report(args: argparse.Namespace, _: Settings) -> int:
    from reglens_agent.evals.report import write_report

    runs = [Path(p) for p in args.runs] if args.runs else _latest_runs()
    print(f"Wrote {write_report(runs)}")
    return 0


def _latest_runs() -> list[Path]:
    """Every run file, oldest first; the report merges them by run number."""
    files = sorted(RUNS.glob("*-r*.json"))
    if not files:
        raise SystemExit("No run files in evals/runs. Run `eval record` first.")
    return files


def _reglens_ready(mcp_url: str) -> bool:
    import httpx

    parts = urlsplit(mcp_url)
    try:
        return httpx.get(f"{parts.scheme}://{parts.netloc}/health/ready", timeout=5).status_code == 200
    except httpx.HTTPError:
        return False
