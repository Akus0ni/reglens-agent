"""The review graph (spec 0001, R1.4–R1.12, P1–P4).

plan → research ⇄ tools → assess → verify → review (interrupt) → file

Models, tools and the filer are passed in, so tests run the real graph with fakes and no network.
"""

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Annotated, Any, Protocol, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from reglens_agent import prompts
from reglens_agent.evidence import evidence_from_artifact, merge_evidence, render_memo, verify
from reglens_agent.filing import Filer
from reglens_agent.models import MAX_QUESTIONS, Decision, Findings, QuestionPlan
from reglens_agent.pricing import Usage, merge_usage, usage_of

TOOL_NAMES = ("search_regulations", "get_passage")
MAX_TURNS_PER_QUESTION = 4
MAX_TOOL_CALLS = 20
RECURSION_LIMIT = 60


class StructuredModel(Protocol):
    """A chat model that can return a Pydantic object (``with_structured_output``)."""

    def with_structured_output(self, schema: Any, **kwargs: Any) -> Any: ...


class ToolCallingModel(Protocol):
    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> Any: ...


class Models:
    """The three model roles (D10) and the names their usage is priced under."""

    def __init__(self, planner: StructuredModel, researcher: ToolCallingModel, assessor: StructuredModel,
                 planner_name: str, researcher_name: str, assessor_name: str) -> None:
        self.planner, self.researcher, self.assessor = planner, researcher, assessor
        self.planner_name, self.researcher_name, self.assessor_name = planner_name, researcher_name, assessor_name


def _replace(_: Any, right: Any) -> Any:
    return right


class ReviewState(TypedDict, total=False):
    thread_id: str
    feature: str
    create_issue: bool
    questions: list[dict]
    question_index: int
    question_turns: int
    messages: Annotated[list[BaseMessage], _replace]
    evidence: Annotated[dict[str, dict], merge_evidence]
    tool_call_hashes: Annotated[list[str], lambda left, right: (left or []) + (right or [])]
    guard_notes: Annotated[list[str], lambda left, right: (left or []) + (right or [])]
    findings: list[dict]
    rejected: list[dict]
    memo: str
    decision: dict
    filed: dict
    usage: Annotated[Usage, merge_usage]


def call_hash(name: str, args: Mapping[str, Any]) -> str:
    """Identity of a tool call: name plus canonical JSON arguments (R1.7c)."""
    return hashlib.sha256(f"{name}\0{json.dumps(args, sort_keys=True, separators=(',', ':'))}".encode()).hexdigest()


def build_graph(models: Models, tools: Sequence[BaseTool], filer: Filer) -> StateGraph:
    by_name = {tool.name: tool for tool in tools if tool.name in TOOL_NAMES}
    research_model = models.researcher.bind_tools(list(by_name.values())) if by_name else None

    async def plan(state: ReviewState) -> dict:
        runnable = models.planner.with_structured_output(QuestionPlan, method="json_schema", include_raw=True)
        result = await runnable.ainvoke([SystemMessage(prompts.PLAN_SYSTEM),
                                         HumanMessage(prompts.plan_message(state["feature"]))])
        parsed = _parsed(result, "plan")
        questions = [q.model_dump() for q in parsed.questions[:MAX_QUESTIONS]]
        return {"questions": questions, "question_index": 0, "question_turns": 0, "messages": [],
                "usage": usage_of(models.planner_name, result["raw"])}

    async def research(state: ReviewState) -> dict:
        index, questions = state["question_index"], state["questions"]
        question = questions[index]
        if len(state.get("tool_call_hashes", [])) >= MAX_TOOL_CALLS:
            skipped = ", ".join(q["id"] for q in questions[index:])
            return {"question_index": len(questions), "messages": [],
                    "guard_notes": [f"Tool-call budget ({MAX_TOOL_CALLS}) reached; research stopped before {skipped}."]}
        if state.get("question_turns", 0) >= MAX_TURNS_PER_QUESTION:
            return {**_advance(state),
                    "guard_notes": [f"{question['id']}: stopped after {MAX_TURNS_PER_QUESTION} research turns."]}
        if research_model is None:
            raise RuntimeError("No RegLens tools are available to research with.")

        messages = state.get("messages") or [SystemMessage(prompts.RESEARCH_SYSTEM),
                                             HumanMessage(prompts.research_message(question))]
        reply: AIMessage = await research_model.ainvoke(messages)
        update: dict = {"messages": [*messages, reply], "question_turns": state.get("question_turns", 0) + 1,
                        "usage": usage_of(models.researcher_name, reply)}
        if not reply.tool_calls:
            update |= _advance(state)
        return update

    async def run_tools(state: ReviewState) -> dict:
        reply = state["messages"][-1]
        seen = set(state.get("tool_call_hashes", []))
        used = len(seen)
        results: list[ToolMessage] = []
        new_hashes: list[str] = []
        evidence: dict[str, dict] = {}
        for call in reply.tool_calls:
            key = call_hash(call["name"], call["args"])
            if call["name"] not in by_name:
                results.append(_refusal(call, f"Unknown tool '{call['name']}'. Use {' or '.join(TOOL_NAMES)}."))
            elif key in seen:
                results.append(_refusal(call, "Refused: this exact call was already made in this review. "
                                              "Use the earlier result or change the arguments."))
            elif used + len(new_hashes) >= MAX_TOOL_CALLS:
                results.append(_refusal(call, f"Refused: the review's budget of {MAX_TOOL_CALLS} tool calls is used up."))
            else:
                message = await by_name[call["name"]].ainvoke(call)
                new_hashes.append(key)
                seen.add(key)
                for item in evidence_from_artifact(getattr(message, "artifact", None)):
                    evidence = merge_evidence(evidence, {str(item["chunk_id"]): item})
                results.append(ToolMessage(content=prompts.tool_result_block(call["name"], _text(message.content)),
                                           tool_call_id=call["id"], name=call["name"],
                                           status=getattr(message, "status", "success")))
        return {"messages": [*state["messages"], *results], "tool_call_hashes": new_hashes, "evidence": evidence}

    async def assess(state: ReviewState) -> dict:
        evidence = state.get("evidence", {})
        if not evidence:
            return {"findings": [], "guard_notes": ["No passages were retrieved, so nothing could be assessed."]}
        runnable = models.assessor.with_structured_output(Findings, method="json_schema", include_raw=True)
        result = await runnable.ainvoke([
            SystemMessage(prompts.ASSESS_SYSTEM),
            HumanMessage(prompts.assess_message(state["feature"], state["questions"], evidence))])
        parsed = _parsed(result, "assess")
        return {"findings": [f.model_dump(mode="json") for f in parsed.findings],
                "usage": usage_of(models.assessor_name, result["raw"])}

    def check(state: ReviewState) -> dict:
        evidence = state.get("evidence", {})
        accepted, rejected = verify(state.get("findings", []), evidence)
        memo = render_memo(state["feature"], state["questions"], accepted, rejected, evidence,
                           state.get("guard_notes", []))
        return {"findings": accepted, "rejected": rejected, "memo": memo}

    def review(state: ReviewState) -> dict:
        # Nothing before interrupt() has side effects: this node re-runs from its start on resume (R1.11).
        answer = interrupt({"thread_id": state["thread_id"], "memo": state["memo"], "findings": state["findings"]},
                           response_schema=Decision)
        decision = answer if isinstance(answer, Decision) else Decision.model_validate(answer)
        return {"decision": decision.model_dump()}

    def file(state: ReviewState) -> dict:
        decision = state["decision"]
        edited = decision["action"] == "edit" and decision.get("memo")
        memo = decision["memo"] if edited else state["memo"]
        filed = filer.file(state["thread_id"], _title(state["feature"]), memo, state.get("create_issue", True))
        return {"filed": {"report": filed.report, "issue_url": filed.issue_url}}

    graph = StateGraph(ReviewState)
    graph.add_node("plan", plan)
    graph.add_node("research", research)
    graph.add_node("tools", run_tools)
    graph.add_node("assess", assess)
    graph.add_node("verify", check)
    graph.add_node("review", review)
    graph.add_node("file", file)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "research")
    graph.add_conditional_edges("research", _after_research, ["tools", "research", "assess"])
    graph.add_edge("tools", "research")
    graph.add_edge("assess", "verify")
    graph.add_edge("verify", "review")
    graph.add_conditional_edges("review", lambda s: "file" if s["decision"]["action"] != "reject" else END,
                                ["file", END])
    graph.add_edge("file", END)
    return graph


def _after_research(state: ReviewState) -> str:
    messages = state.get("messages") or []
    if messages and isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        return "tools"
    return "research" if state["question_index"] < len(state["questions"]) else "assess"


def _advance(state: ReviewState) -> dict:
    return {"question_index": state["question_index"] + 1, "question_turns": 0, "messages": []}


def _parsed(result: Mapping[str, Any], step: str) -> Any:
    if result.get("parsed") is None:
        raise RuntimeError(f"The {step} model returned no valid structured output: {result.get('parsing_error')}")
    return result["parsed"]


def _refusal(call: Mapping[str, Any], text: str) -> ToolMessage:
    return ToolMessage(content=text, tool_call_id=call["id"], name=call["name"], status="error")


def _text(content: Any) -> str:
    if isinstance(content, str):
        return content
    parts = [part.get("text", "") if isinstance(part, Mapping) else str(part) for part in content or []]
    return "\n".join(parts)


def _title(feature: str) -> str:
    first = next((line.strip("# ").strip() for line in feature.splitlines() if line.strip()), "feature")
    return f"Compliance review: {first[:80]}"


def thread_config(thread_id: str) -> RunnableConfig:
    return {"configurable": {"thread_id": thread_id}, "recursion_limit": RECURSION_LIMIT}

