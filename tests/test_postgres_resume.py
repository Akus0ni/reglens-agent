"""Durable approval on a real Postgres checkpointer (spec 0001, R1.13, R1.15).

The review runs to the interrupt in one graph instance; a second instance, built with models that raise if called
and no tools (as `resume` builds it), approves from the checkpoint alone. Needs Docker (Testcontainers).
"""

import asyncio
import sys

import pytest
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from testcontainers.postgres import PostgresContainer

from reglens_agent.cli import _no_models
from reglens_agent.filing import Filer
from reglens_agent.graph import build_graph, thread_config
from reglens_agent.models import Finding, Findings, Question, QuestionPlan, Severity
from tests.fakes import FakeGh, FakeReglens, FakeResearcher, FakeStructured, calls, models, passage, tool_call


@pytest.fixture(scope="module")
def database_url():
    with PostgresContainer("postgres:17-alpine", driver=None) as postgres:
        yield postgres.get_connection_url()


def _run(coroutine):
    # psycopg's async connections cannot use Windows' default ProactorEventLoop.
    factory = asyncio.SelectorEventLoop if sys.platform == "win32" else None
    return asyncio.run(coroutine, loop_factory=factory)


def test_resume_after_a_restart_makes_no_new_calls_and_files_once(tmp_path, database_url):
    reglens = FakeReglens([passage(1966, "Rule 7")])
    planner = FakeStructured(QuestionPlan(questions=[Question(id="q1", text="Breach?", search_hint="breach")]))
    researcher = FakeResearcher([calls(tool_call("get_passage", {"chunkId": 1966}, "c1"))])
    assessor = FakeStructured(Findings(findings=[Finding(
        question_id="q1", obligation="Tell the Board.", document="DPDP Rules", para_ref="Rule 7",
        severity=Severity.HIGH, evidence_chunk_ids=[1966], recommendation="Add a process.")]))
    gh = FakeGh()
    filer = Filer(tmp_path, "Akus0ni/reglens-agent", gh)
    config = thread_config("crash-test")

    async def review_until_interrupt() -> None:
        async with AsyncPostgresSaver.from_conn_string(database_url) as saver:
            await saver.setup()
            graph = build_graph(models(planner, researcher, assessor), reglens.tools(), filer).compile(checkpointer=saver)
            result = await graph.ainvoke({"thread_id": "crash-test", "feature": "F", "create_issue": True}, config)
            assert "__interrupt__" in result
        # The process "dies" here: the saver and graph are gone; only Postgres keeps the state.

    async def resume(action: str) -> dict:
        async with AsyncPostgresSaver.from_conn_string(database_url) as saver:
            graph = build_graph(_no_models(), [], filer).compile(checkpointer=saver)
            return await graph.ainvoke(Command(resume={"action": action}), config)

    _run(review_until_interrupt())
    model_calls = (len(planner.calls), len(researcher.calls), len(assessor.calls))
    tool_calls = len(reglens.calls)

    first = _run(resume("approve"))
    second = _run(resume("approve"))  # a second resume after the run finished

    assert (len(planner.calls), len(researcher.calls), len(assessor.calls)) == model_calls
    assert len(reglens.calls) == tool_calls
    assert first["filed"]["issue_url"].endswith("/issues/1")
    assert second["filed"] == first["filed"]
    assert gh.created == 1
