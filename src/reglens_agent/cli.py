"""Command line (spec 0001, R1.13, R1.14).

  uv run reglens-agent setup
  uv run reglens-agent review --feature-file samples/contact-access.md --confirm-spend [--no-issue] [--thread-id T]
  uv run reglens-agent resume <thread_id> approve|reject|edit [--memo-file M] [--note N]
  uv run reglens-agent show <thread_id>
"""

import argparse
import asyncio
import sys
import uuid
from collections.abc import Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from reglens_agent.filing import LABEL, Filer
from reglens_agent.graph import Models, build_graph, thread_config
from reglens_agent.pricing import cost_usd
from reglens_agent.settings import ASSESSOR_MODEL, PLANNER_MODEL, RESEARCH_MODEL, Settings, SettingsError
from reglens_agent.telemetry import telemetry

REPORTS_DIR = Path("reports")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    settings = Settings.from_env()
    # psycopg's async connections cannot use Windows' default ProactorEventLoop.
    loop_factory = asyncio.SelectorEventLoop if sys.platform == "win32" else None
    try:
        return asyncio.run(args.handler(args, settings), loop_factory=loop_factory)
    except SettingsError as error:
        print(error, file=sys.stderr)
        return 2


async def _setup(_: argparse.Namespace, settings: Settings) -> int:
    settings.require("AGENT_DATABASE_URL")
    await _create_database(settings.database_url)
    async with AsyncPostgresSaver.from_conn_string(settings.database_url) as saver:
        await saver.setup()
    Filer(REPORTS_DIR, settings.issue_repo).ensure_label()
    print(f"Checkpoint tables ready; label '{LABEL}' exists in {settings.issue_repo}.")
    return 0


async def _review(args: argparse.Namespace, settings: Settings) -> int:
    if not args.confirm_spend:
        print("review calls Claude (about $0.06 per review). Re-run with --confirm-spend.", file=sys.stderr)
        return 2
    settings.require("ANTHROPIC_API_KEY", "REGLENS_API_KEY", "AGENT_DATABASE_URL")
    feature = Path(args.feature_file).read_text(encoding="utf-8")
    thread_id = args.thread_id or str(uuid.uuid4())

    with telemetry(settings.otlp_endpoint) as tracer, tracer.start_as_current_span("review") as span:
        span.set_attribute("reglens_agent.thread_id", thread_id)
        models, tools = _live_models(), await _reglens_tools(settings)
        async with _graph(settings, models, tools) as graph:
            result = await graph.ainvoke({"thread_id": thread_id, "feature": feature, "create_issue": not args.no_issue},
                                         thread_config(thread_id))
    _print_pending(thread_id, result)
    return 0


async def _resume(args: argparse.Namespace, settings: Settings) -> int:
    settings.require("AGENT_DATABASE_URL")
    decision: dict[str, Any] = {"action": args.action, "note": args.note}
    if args.action == "edit":
        if not args.memo_file:
            print("edit needs --memo-file with the edited memo.", file=sys.stderr)
            return 2
        decision["memo"] = Path(args.memo_file).read_text(encoding="utf-8")

    with telemetry(settings.otlp_endpoint) as tracer, tracer.start_as_current_span("resume") as span:
        span.set_attribute("reglens_agent.thread_id", args.thread_id)
        # No model or tool is reachable on resume: research and assessment are already checkpointed (R1.15).
        async with _graph(settings, _no_models(), []) as graph:
            state = await graph.aget_state(thread_config(args.thread_id))
            if "review" not in state.next:
                print(f"Thread {args.thread_id} is not waiting for review (next: {list(state.next) or 'done'}).",
                      file=sys.stderr)
                return 1
            result = await graph.ainvoke(Command(resume=decision), thread_config(args.thread_id))
    filed = result.get("filed")
    print(f"{args.action}: " + (f"report {filed['report']}" + (f", issue {filed['issue_url']}" if filed["issue_url"]
                                                                  else ", no issue") if filed else "nothing filed"))
    return 0


async def _show(args: argparse.Namespace, settings: Settings) -> int:
    settings.require("AGENT_DATABASE_URL")
    async with _graph(settings, _no_models(), []) as graph:
        state = await graph.aget_state(thread_config(args.thread_id))
    if not state.values:
        print(f"No review with thread id {args.thread_id}.", file=sys.stderr)
        return 1
    values = state.values
    print(values.get("memo", "(no memo yet)"))
    print(f"next: {list(state.next) or 'done'}; decision: {values.get('decision')}; filed: {values.get('filed')}")
    _print_cost(values.get("usage", {}))
    return 0


@asynccontextmanager
async def _graph(settings: Settings, models: Models, tools: list):
    async with AsyncPostgresSaver.from_conn_string(settings.database_url) as saver:
        yield build_graph(models, tools, Filer(REPORTS_DIR, settings.issue_repo)).compile(checkpointer=saver)


def _live_models() -> Models:
    from langchain_anthropic import ChatAnthropic

    planner = ChatAnthropic(model=PLANNER_MODEL, max_tokens=2048, reasoning_effort="medium", max_retries=2)
    researcher = ChatAnthropic(model=RESEARCH_MODEL, max_tokens=1024, reasoning_effort="low", max_retries=2)
    assessor = ChatAnthropic(model=ASSESSOR_MODEL, max_tokens=8192, reasoning_effort="medium", max_retries=2)
    return Models(planner, researcher, assessor, PLANNER_MODEL, RESEARCH_MODEL, ASSESSOR_MODEL)


class _Unreachable:
    """Stands in for every model on resume and show: any call is a bug (R1.15)."""

    def __getattr__(self, name: str) -> Any:
        raise RuntimeError(f"No model may be called here (attempted '{name}').")


def _no_models() -> Models:
    return Models(_Unreachable(), _Unreachable(), _Unreachable(), PLANNER_MODEL, RESEARCH_MODEL, ASSESSOR_MODEL)


async def _reglens_tools(settings: Settings) -> list:
    from langchain_mcp_adapters.client import MultiServerMCPClient

    client = MultiServerMCPClient({"reglens": {
        "transport": "http",
        "url": settings.reglens_mcp_url,
        "headers": {"X-API-Key": settings.reglens_api_key},
    }})
    return await client.get_tools()


async def _create_database(url: str) -> None:
    import psycopg
    from psycopg import sql
    from psycopg.conninfo import conninfo_to_dict, make_conninfo

    target = conninfo_to_dict(url)
    name = target.get("dbname")
    if not name:
        raise SettingsError("AGENT_DATABASE_URL must name a database, e.g. .../reglens_agent.")
    async with await psycopg.AsyncConnection.connect(make_conninfo(url, dbname="postgres"), autocommit=True) as conn:
        exists = await (await conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))).fetchone()
        if not exists:
            await conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))


def _print_pending(thread_id: str, result: dict) -> None:
    print(result.get("memo", ""))
    _print_cost(result.get("usage", {}))
    print(f"\nWaiting for review. Thread: {thread_id}")
    print(f"  uv run reglens-agent resume {thread_id} approve | reject | edit --memo-file <file>")


def _print_cost(usage: dict) -> None:
    if usage:
        parts = ", ".join(f"{m}: {u['calls']} calls, {u['input']} in / {u['output']} out" for m, u in usage.items())
        print(f"Cost: ${cost_usd(usage):.4f} ({parts})")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reglens-agent", description="Compliance review over RegLens (MCP).")
    commands = parser.add_subparsers(required=True)

    setup = commands.add_parser("setup", help="Create the checkpoint database and tables and the issue label.")
    setup.set_defaults(handler=_setup)

    review = commands.add_parser("review", help="Review a feature; stops at the human approval step.")
    review.add_argument("--feature-file", required=True)
    review.add_argument("--thread-id")
    review.add_argument("--no-issue", action="store_true", help="File the report only, no GitHub issue.")
    review.add_argument("--confirm-spend", action="store_true", help="Required: the review calls Claude.")
    review.set_defaults(handler=_review)

    resume = commands.add_parser("resume", help="Approve, edit or reject a waiting review.")
    resume.add_argument("thread_id")
    resume.add_argument("action", choices=["approve", "edit", "reject"])
    resume.add_argument("--memo-file")
    resume.add_argument("--note")
    resume.set_defaults(handler=_resume)

    show = commands.add_parser("show", help="Print a review's memo, state and cost.")
    show.add_argument("thread_id")
    show.set_defaults(handler=_show)
    return parser
