"""Scenarios and deterministic trajectory checks (spec 0002, R2.1, R2.5, R2.6, P3)."""

import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from reglens_agent.evidence import paragraph
from reglens_agent.graph import MAX_TOOL_CALLS, MAX_TURNS_PER_QUESTION

SCENARIOS = Path("evals/scenarios.json")
HARD_CHECKS = ("completed", "guards", "searched", "verified", "quiet")
SCORED_CHECKS = ("required", "severity")
SEVERITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


@dataclass(frozen=True)
class Scenario:
    id: str
    feature: str
    in_scope: bool
    required: list[list[dict]]
    min_severity: str | None


def load_scenarios(path: Path = SCENARIOS) -> list[Scenario]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Scenario(s["id"], s["feature"], s["in_scope"], s["required"], s["min_severity"]) for s in data["scenarios"]]


def check(scenario: Scenario, state: Mapping[str, Any]) -> dict[str, dict]:
    """Every check for one finished-to-review run: ``{name: {"passed": bool | None, "detail": str}}``.
    ``None`` means the check does not apply (required/severity out of scope, quiet in scope)."""
    evidence = state.get("evidence", {})
    findings = state.get("findings", [])
    results: dict[str, dict] = {}

    results["completed"] = _result(bool(state.get("memo")) and bool(state.get("questions")), "reached review with a memo")

    tool_calls = len(state.get("tool_call_hashes", []))
    turns = Counter(state.get("turns_log", []))
    worst = max(turns.values(), default=0)
    results["guards"] = _result(tool_calls <= MAX_TOOL_CALLS and worst <= MAX_TURNS_PER_QUESTION,
                                f"{tool_calls} tool calls (max {MAX_TOOL_CALLS}), at most {worst} turns per question "
                                f"(max {MAX_TURNS_PER_QUESTION})")

    searches = state.get("tools_log", []).count("search_regulations")
    results["searched"] = _result(searches > 0 or not scenario.in_scope, f"{searches} search_regulations calls")

    unseen = sorted({str(i) for f in findings for i in f["evidence_chunk_ids"] if str(i) not in evidence})
    results["verified"] = _result(not unseen, "all cited passages retrieved" if not unseen else f"unseen: {unseen}")

    if scenario.in_scope:
        met, missing, strongest = _required(scenario, findings, evidence)
        results["required"] = _result(not missing, f"met {met}" + (f"; missing {missing}" if missing else ""))
        floor = SEVERITY_RANK[scenario.min_severity or "LOW"]
        results["severity"] = _result(strongest >= floor,
                                      f"strongest matching {_name(strongest)}, needs {scenario.min_severity}")
        results["quiet"] = {"passed": None, "detail": "in scope"}
    else:
        results["required"] = {"passed": None, "detail": "out of scope"}
        results["severity"] = {"passed": None, "detail": "out of scope"}
        loud = [f["severity"] for f in findings if SEVERITY_RANK[f["severity"]] >= SEVERITY_RANK["MEDIUM"]]
        results["quiet"] = _result(not loud, f"{len(findings)} findings, {len(loud)} MEDIUM or HIGH")
    return results


def gate(checks_by_scenario: Mapping[str, Mapping[str, dict]], baseline: Mapping[str, int]) -> list[str]:
    """Failures, worded for a CI log: hard checks on every scenario; scored checks no worse than the baseline."""
    failures = [f"{scenario}: {name} failed ({result['detail']})"
                for scenario, results in checks_by_scenario.items()
                for name in HARD_CHECKS if (result := results[name])["passed"] is False]
    for name in SCORED_CHECKS:
        passed = count(checks_by_scenario, name)
        if passed < baseline[name]:
            failing = [s for s, r in checks_by_scenario.items() if r[name]["passed"] is False]
            failures.append(f"{name}: {passed} scenarios pass, baseline {baseline[name]}; failing: "
                            + "; ".join(f"{s} ({checks_by_scenario[s][name]['detail']})" for s in failing))
    return failures


def count(checks_by_scenario: Mapping[str, Mapping[str, dict]], name: str) -> int:
    return sum(1 for results in checks_by_scenario.values() if results[name]["passed"] is True)


def _required(scenario: Scenario, findings: list[dict], evidence: Mapping[str, dict]) -> tuple[list, list, int]:
    met, missing, strongest = [], [], 0
    for group in scenario.required:
        options = {(o["document"], paragraph(o["para"])) for o in group}
        matching = [f for f in findings if any((evidence[str(i)]["document_id"], paragraph(evidence[str(i)]["para_ref"]))
                                               in options for i in f["evidence_chunk_ids"] if str(i) in evidence)]
        label = " or ".join(o["para"] for o in group)
        if matching:
            met.append(label)
            strongest = max(strongest, *(SEVERITY_RANK[f["severity"]] for f in matching))
        else:
            missing.append(label)
    return met, missing, strongest


def _result(passed: bool, detail: str) -> dict:
    return {"passed": passed, "detail": detail}


def _name(rank: int) -> str:
    return next((name for name, value in SEVERITY_RANK.items() if value == rank), "none")
