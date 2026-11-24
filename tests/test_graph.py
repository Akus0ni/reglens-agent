"""The review graph end to end with fakes (spec 0001, R1.4–R1.12, R1.7 guards)."""

from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from reglens_agent.filing import Filer
from reglens_agent.graph import MAX_TOOL_CALLS, MAX_TURNS_PER_QUESTION, build_graph, thread_config
from reglens_agent.models import Finding, Findings, Question, QuestionPlan, Severity
from tests.fakes import FakeGh, FakeReglens, FakeResearcher, FakeStructured, calls, models, passage, tool_call

PLAN = QuestionPlan(questions=[
    Question(id="q1", text="Must a breach be reported?", search_hint="personal data breach intimation"),
    Question(id="q2", text="Is consent needed?", search_hint="consent notice"),
])
GOOD = Finding(question_id="q1", obligation="Tell the Board within 72 hours.", document="DPDP Rules",
               para_ref="Rule 7", severity=Severity.HIGH, evidence_chunk_ids=[1966], recommendation="Add a process.")
FAKE = Finding(question_id="q2", obligation="Invented.", document="DPDP Rules", para_ref="Rule 99",
               severity=Severity.LOW, evidence_chunk_ids=[424242], recommendation="None.")


def _run(tmp_path: Path, researcher: FakeResearcher, findings: Findings | None = None, gh: FakeGh | None = None):
    reglens = FakeReglens([passage(1966, "Rule 7"), passage(1965, "Rule 6")])
    planner, assessor = FakeStructured(PLAN), FakeStructured(findings or Findings(findings=[GOOD, FAKE]))
    gh = gh or FakeGh()
    graph = build_graph(models(planner, researcher, assessor), reglens.tools(),
                        Filer(tmp_path / "reports", "Akus0ni/reglens-agent", gh)).compile(checkpointer=InMemorySaver())
    return graph, reglens, planner, assessor, gh


async def _start(graph, thread: str = "t-1") -> dict:
    return await graph.ainvoke({"thread_id": thread, "feature": "Breach feature", "create_issue": True},
                               thread_config(thread))


async def test_researches_assesses_verifies_and_waits_for_review(tmp_path):
    researcher = FakeResearcher([
        calls(tool_call("search_regulations", {"query": "breach", "topK": 5}, "c1")),
        calls(tool_call("get_passage", {"chunkId": 1966}, "c2")),
    ])
    graph, reglens, planner, assessor, gh = _run(tmp_path, researcher)

    result = await _start(graph)

    assert result["__interrupt__"][0].value["thread_id"] == "t-1"
    assert [c[0] for c in reglens.calls] == ["search_regulations", "get_passage"]
    assert result["evidence"]["1966"]["full"] is True
    assert [f["para_ref"] for f in result["findings"]] == ["Rule 7"]
    assert result["rejected"][0]["reason"] == "cites passages not retrieved in this review: 424242"
    assert "## Findings (1)" in result["memo"]
    assert result["usage"]["claude-haiku-5-5"]["calls"] == 4  # q1: 3 turns, q2: 1 turn
    assert result["usage"]["claude-sonnet-5-5"]["calls"] == 2  # plan + assess
    assert gh.invocations == [] and not (tmp_path / "reports").exists()  # nothing filed before approval


async def test_tool_results_reach_the_model_as_delimited_data(tmp_path):
    researcher = FakeResearcher([calls(tool_call("search_regulations", {"query": "breach"}, "c1"))])
    graph, *_ = _run(tmp_path, researcher)

    await _start(graph)

    tool_message = researcher.calls[1][-1]
    assert tool_message.content.startswith('<tool_result tool="search_regulations">')


async def test_approve_files_the_report_and_one_issue(tmp_path):
    graph, *_, gh = _run(tmp_path, FakeResearcher([calls(tool_call("get_passage", {"chunkId": 1966}, "c1"))]))
    await _start(graph)

    result = await graph.ainvoke(Command(resume={"action": "approve"}), thread_config("t-1"))

    report = Path(result["filed"]["report"])
    assert report.read_text(encoding="utf-8") == result["memo"]
    assert result["filed"]["issue_url"].endswith("/issues/1")
    assert gh.created == 1
    create_args, body = next((a, b) for a, b in gh.invocations if a[:2] == ["issue", "create"])
    assert "reglens-agent:thread_id=t-1" in body and "--label" in create_args


async def test_edit_files_the_edited_memo(tmp_path):
    graph, *_ = _run(tmp_path, FakeResearcher())
    await _start(graph)

    result = await graph.ainvoke(Command(resume={"action": "edit", "memo": "# Edited\n"}), thread_config("t-1"))

    assert Path(result["filed"]["report"]).read_text(encoding="utf-8") == "# Edited\n"


async def test_reject_files_nothing(tmp_path):
    graph, *_, gh = _run(tmp_path, FakeResearcher())
    await _start(graph)

    result = await graph.ainvoke(Command(resume={"action": "reject", "note": "not now"}), thread_config("t-1"))

    assert "filed" not in result
    assert gh.invocations == [] and not (tmp_path / "reports").exists()


async def test_an_invalid_decision_is_refused(tmp_path):
    graph, *_ = _run(tmp_path, FakeResearcher())
    await _start(graph)

    with pytest.raises(Exception, match="action"):
        await graph.ainvoke(Command(resume={"action": "ship it"}), thread_config("t-1"))


async def test_a_repeated_call_is_refused_and_a_question_stops_after_four_turns(tmp_path):
    same = calls(tool_call("search_regulations", {"query": "breach", "topK": 5}, "c1"))
    researcher = FakeResearcher(repeat=same)
    graph, reglens, *_ = _run(tmp_path, researcher, Findings(findings=[]))

    result = await _start(graph)

    assert len(reglens.calls) == 1  # executed once; every repeat refused
    assert researcher.calls[2][-1].content.startswith("Refused: this exact call was already made")
    assert result["usage"]["claude-haiku-5-5"]["calls"] == 2 * MAX_TURNS_PER_QUESTION
    assert result["guard_notes"] == [f"q1: stopped after {MAX_TURNS_PER_QUESTION} research turns.",
                                     f"q2: stopped after {MAX_TURNS_PER_QUESTION} research turns."]


async def test_the_review_stops_calling_tools_at_the_budget(tmp_path):
    turns = [calls(*[tool_call("search_regulations", {"query": f"q{t}-{i}"}, f"c{t}-{i}") for i in range(6)])
             for t in range(10)]
    graph, reglens, *_ = _run(tmp_path, FakeResearcher(turns), Findings(findings=[]))

    result = await _start(graph)

    assert len(reglens.calls) == MAX_TOOL_CALLS
    assert any("Tool-call budget (20) reached" in note for note in result["guard_notes"])


async def test_unknown_tools_are_refused(tmp_path):
    graph, reglens, *_ = _run(tmp_path, FakeResearcher([calls(tool_call("ask_regulations", {"question": "x"}, "c1"))]),
                              Findings(findings=[]))

    await _start(graph)

    assert reglens.calls == []
