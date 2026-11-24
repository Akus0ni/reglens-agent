"""Record and replay, the checks and the gate (spec 0002, R2.2–R2.7, R2.14)."""

import pytest

from reglens_agent import prompts
from reglens_agent.evals.checks import Scenario, check, gate
from reglens_agent.evals.recording import StaleRecording, Store
from reglens_agent.evals.runner import replay_scenario, run_scenario
from reglens_agent.models import Finding, Findings, Question, QuestionPlan, Severity
from tests.fakes import FakeReglens, FakeResearcher, FakeStructured, calls, models, passage, tool_call

SCENARIO = Scenario("dpdp-breach", "We tell nobody about breaches.", True,
                    [[{"document": "dpdp-rules-2025", "para": "Rule 7"}]], "HIGH")


def _live():
    reglens = FakeReglens([passage(1966, "Rule 7"), passage(1965, "Rule 6")])
    planner = FakeStructured(QuestionPlan(questions=[Question(id="q1", text="Breach?", search_hint="breach")]))
    researcher = FakeResearcher([calls(tool_call("search_regulations", {"query": "breach", "topK": 5}, "c1")),
                                 calls(tool_call("get_passage", {"chunkId": 1966}, "c2"))])
    assessor = FakeStructured(Findings(findings=[Finding(
        question_id="q1", obligation="Tell the Board.", document="DPDP Rules", para_ref="Rule 7",
        severity=Severity.HIGH, evidence_chunk_ids=[1966], recommendation="Add a process.")]))
    return models(planner, researcher, assessor), reglens


async def test_a_recorded_run_replays_identically_with_nothing_live():
    live_models, reglens = _live()
    store = Store(SCENARIO.id)
    recorded = await run_scenario(SCENARIO, live_models, reglens.tools(), store)

    replay = Store(SCENARIO.id, store.data, replay=True)
    replayed = await run_scenario(SCENARIO, None, reglens.tools(), replay)

    assert replayed["state"]["findings"] == recorded["state"]["findings"]
    assert replayed["checks"] == recorded["checks"]
    assert replayed["usage"] == recorded["usage"]
    assert len(reglens.calls) == 2  # only the live run reached the tools
    assert {v["role"] for v in store.data["models"].values()} == {"plan", "research", "assess"}


async def test_a_changed_prompt_makes_the_recording_stale(monkeypatch):
    live_models, reglens = _live()
    store = Store(SCENARIO.id)
    await run_scenario(SCENARIO, live_models, reglens.tools(), store)
    monkeypatch.setattr(prompts, "ASSESS_SYSTEM", prompts.ASSESS_SYSTEM + " Cite passages from memory.")

    with pytest.raises(StaleRecording, match="scenario 'dpdp-breach' made a assess model request"):
        await run_scenario(SCENARIO, None, reglens.tools(), Store(SCENARIO.id, store.data, replay=True))


async def test_a_recorded_tool_error_replays_as_an_error():
    live_models, reglens = _live()
    researcher = FakeResearcher([calls(tool_call("get_passage", {"chunkId": 404}, "c1"))])
    live_models.researcher = researcher
    store = Store(SCENARIO.id)
    await run_scenario(SCENARIO, live_models, reglens.tools(), store)

    saved = next(v for v in store.data["tools"].values() if v["args"] == {"chunkId": 404})
    assert saved["status"] == "error"
    replayed = await run_scenario(SCENARIO, None, reglens.tools(), Store(SCENARIO.id, store.data, replay=True))
    assert replayed["checks"]["completed"]["passed"] is True


def _state(findings, evidence_refs, turns=("q1",), tools=("search_regulations",), calls_made=3):
    evidence = {str(cid): {"chunk_id": cid, "document_id": doc, "para_ref": ref} for cid, (doc, ref) in evidence_refs.items()}
    return {"memo": "m", "questions": [{"id": "q1"}], "evidence": evidence, "findings": findings,
            "turns_log": list(turns), "tools_log": list(tools), "tool_call_hashes": ["h"] * calls_made}


def _finding(ids, severity="HIGH"):
    return {"evidence_chunk_ids": ids, "severity": severity}


def test_required_accepts_any_option_in_a_group_and_part_suffixes():
    scenario = Scenario("s", "f", True, [[{"document": "rbc", "para": "Para 33"}, {"document": "rbc", "para": "Para 34"}]],
                        "HIGH")
    state = _state([_finding([2])], {2: ("rbc", "Para 34, part 2 of 2")})

    result = check(scenario, state)

    assert result["required"]["passed"] is True
    assert result["severity"]["passed"] is True


def test_required_and_severity_fail_with_details():
    scenario = Scenario("s", "f", True, [[{"document": "cf", "para": "Para 13"}], [{"document": "rbc", "para": "Para 100"}]],
                        "HIGH")
    state = _state([_finding([1], "MEDIUM")], {1: ("cf", "Para 13")})

    result = check(scenario, state)

    assert result["required"] == {"passed": False, "detail": "met ['Para 13']; missing ['Para 100']"}
    assert result["severity"] == {"passed": False, "detail": "strongest matching MEDIUM, needs HIGH"}


def test_guards_searched_verified_and_quiet():
    out_of_scope = Scenario("oos", "f", False, [], None)

    loud = check(out_of_scope, _state([_finding([1], "MEDIUM")], {1: ("cf", "Para 13")}))
    unseen = check(SCENARIO, _state([_finding([9])], {}))
    looping = check(SCENARIO, _state([], {}, turns=("q1",) * 5, tools=(), calls_made=21))

    assert loud["quiet"]["passed"] is False and loud["required"]["passed"] is None
    assert unseen["verified"] == {"passed": False, "detail": "unseen: ['9']"}
    assert looping["guards"]["passed"] is False
    assert looping["searched"]["passed"] is False


def test_gate_requires_hard_checks_everywhere_and_scored_checks_no_worse_than_baseline():
    ok = {"passed": True, "detail": "ok"}
    def results(**overrides):
        base = {n: ok for n in ("completed", "guards", "searched", "verified", "required", "severity")}
        return base | {"quiet": {"passed": None, "detail": "in scope"}} | overrides

    checks = {"a": results(), "b": results(required={"passed": False, "detail": "missing ['Para 7']"})}

    assert gate(checks, {"required": 1, "severity": 2}) == []
    assert gate(checks, {"required": 2, "severity": 2}) == [
        "required: 1 scenarios pass, baseline 2; failing: b (missing ['Para 7'])"]
    assert gate({"a": results(verified={"passed": False, "detail": "unseen: ['9']"})}, {"required": 0, "severity": 0}) == [
        "a: verified failed (unseen: ['9'])"]


async def test_a_stale_scenario_fails_its_checks_without_stopping_the_others(monkeypatch):
    live_models, reglens = _live()
    store = Store(SCENARIO.id)
    await run_scenario(SCENARIO, live_models, reglens.tools(), store)
    monkeypatch.setattr(prompts, "PLAN_SYSTEM", prompts.PLAN_SYSTEM + " Changed.")

    stale = await replay_scenario(SCENARIO, store.data)
    missing = await replay_scenario(SCENARIO, None)

    assert stale["completed"]["passed"] is False and "stale recording" in stale["completed"]["detail"]
    assert stale["required"]["passed"] is False
    assert missing["completed"]["detail"].startswith("no recording")
    assert gate({SCENARIO.id: stale}, {"required": 1, "severity": 1})[0].startswith("dpdp-breach: completed failed (stale")
