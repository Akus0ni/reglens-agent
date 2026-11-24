"""Test doubles for the model roles, the RegLens tools and the GitHub CLI. No network, no API keys."""

import json
from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.tools import StructuredTool

from reglens_agent.graph import Models

USAGE = {"input_tokens": 1000, "output_tokens": 100, "total_tokens": 1100}


class FakeStructured:
    """``with_structured_output`` that returns the scripted objects in order and counts calls."""

    def __init__(self, *outputs: Any) -> None:
        self._outputs = list(outputs)
        self.calls: list[list] = []

    def with_structured_output(self, schema: Any, **kwargs: Any) -> "FakeStructured":
        assert kwargs.get("include_raw") is True
        return self

    async def ainvoke(self, messages: list) -> dict:
        self.calls.append(messages)
        return {"raw": AIMessage(content="", usage_metadata=USAGE), "parsed": self._outputs.pop(0),
                "parsing_error": None}


class FakeResearcher:
    """A tool-calling model: each ``ainvoke`` returns the next scripted reply (default: stop calling tools)."""

    def __init__(self, replies: Sequence[AIMessage] = (), repeat: AIMessage | None = None) -> None:
        self._replies = list(replies)
        self._repeat = repeat
        self.calls: list[list] = []

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "FakeResearcher":
        return self

    async def ainvoke(self, messages: list) -> AIMessage:
        self.calls.append(list(messages))
        if self._replies:
            return self._replies.pop(0)
        if self._repeat is not None:
            return self._repeat
        return AIMessage(content="Found what I need.", usage_metadata=USAGE)


def tool_call(name: str, args: dict, call_id: str) -> dict:
    return {"name": name, "args": args, "id": call_id, "type": "tool_call"}


def calls(*tool_calls: dict) -> AIMessage:
    return AIMessage(content="", tool_calls=list(tool_calls), usage_metadata=USAGE)


def passage(chunk_id: int, para_ref: str, text: str = "The regulated entity shall obtain consent.") -> dict:
    return {"chunkId": chunk_id, "documentId": "dpdp-rules-2025",
            "documentTitle": "Digital Personal Data Protection Rules, 2025", "paraRef": para_ref, "heading": "",
            "pageStart": 26, "pageEnd": 26, "content": text}


class FakeReglens:
    """``search_regulations`` and ``get_passage`` with RegLens's result shapes (structured content as artifact)."""

    def __init__(self, passages: Sequence[dict]) -> None:
        self._passages = {p["chunkId"]: p for p in passages}
        self.calls: list[tuple[str, dict]] = []

    def tools(self) -> list[StructuredTool]:
        async def search_regulations(query: str, topK: int = 8) -> tuple[str, dict]:  # noqa: N803 (MCP schema name)
            self.calls.append(("search_regulations", {"query": query, "topK": topK}))
            hits = [{k: v for k, v in p.items() if k != "content"} | {"excerpt": p["content"][:300]}
                    for p in list(self._passages.values())[:topK]]
            result = {"query": query, "hits": hits}
            return json.dumps(result), {"structured_content": result}

        async def get_passage(chunkId: int) -> tuple[str, dict]:  # noqa: N803
            self.calls.append(("get_passage", {"chunkId": chunkId}))
            if chunkId not in self._passages:
                raise ValueError(f"No passage with id {chunkId}.")
            return json.dumps(self._passages[chunkId]), {"structured_content": self._passages[chunkId]}

        return [
            StructuredTool.from_function(coroutine=search_regulations, name="search_regulations",
                                         description="search", response_format="content_and_artifact"),
            StructuredTool.from_function(coroutine=get_passage, name="get_passage", description="passage",
                                         response_format="content_and_artifact"),
        ]


class FakeGh:
    """Records ``gh`` invocations; ``issue list`` answers from ``existing``, ``issue create`` returns a new URL."""

    def __init__(self, existing: Sequence[str] = ()) -> None:
        self.existing = list(existing)
        self.invocations: list[tuple[list[str], str | None]] = []

    def __call__(self, args: Sequence[str], stdin: str | None) -> str:
        self.invocations.append((list(args), stdin))
        if args[:2] == ["issue", "list"]:
            return json.dumps([{"url": url} for url in self.existing])
        if args[:2] == ["issue", "create"]:
            url = f"https://github.com/Akus0ni/reglens-agent/issues/{len(self.existing) + 1}"
            self.existing.append(url)
            return url + "\n"
        return ""

    @property
    def created(self) -> int:
        return sum(1 for args, _ in self.invocations if args[:2] == ["issue", "create"])


def models(planner: FakeStructured, researcher: FakeResearcher, assessor: FakeStructured) -> Models:
    return Models(planner, researcher, assessor, "claude-sonnet-5-5", "claude-haiku-5-5", "claude-sonnet-5-5")
