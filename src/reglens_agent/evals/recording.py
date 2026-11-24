"""Record and replay of model replies and RegLens tool results (spec 0002, R2.2, R2.4, P2; D12).

Every reply is keyed by a SHA-256 of what was sent: the role, the model, the request's messages (reduced to the
fields a model reads) and the schema or tool names. A replayed run therefore reproduces the recorded run exactly, and
any change to a prompt, a message or the tools makes its key unknown: ``StaleRecording``.
"""

import asyncio
import hashlib
import json
import time
from collections import deque
from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, messages_from_dict, messages_to_dict
from langchain_core.tools import BaseTool, StructuredTool, ToolException

from reglens_agent.graph import Models

RERECORD = "uv run reglens-agent eval record --runs 1 --scenario <id> --confirm-spend"


class StaleRecording(Exception):
    """A request the recording has never seen: the code or a prompt changed since it was recorded."""

    def __init__(self, scenario: str, what: str) -> None:
        super().__init__(f"stale recording: scenario '{scenario}' made a {what} request that was never recorded. "
                         f"A prompt or the code changed; re-record with `{RERECORD.replace('<id>', scenario)}`.")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _message_shape(message: BaseMessage) -> dict:
    """The parts of a message a model reads; ids, timings and usage are left out of the key."""
    shape: dict[str, Any] = {"type": message.type, "content": message.content}
    if isinstance(message, AIMessage) and message.tool_calls:
        shape["tool_calls"] = [{"name": c["name"], "args": c["args"], "id": c["id"]} for c in message.tool_calls]
    for field in ("tool_call_id", "name", "status"):
        if getattr(message, field, None) is not None:
            shape[field] = getattr(message, field)
    return shape


def model_key(role: str, model: str, extra: Any, messages: Sequence[BaseMessage]) -> str:
    body = _canonical({"role": role, "model": model, "extra": extra, "messages": [_message_shape(m) for m in messages]})
    return hashlib.sha256(body.encode()).hexdigest()


def tool_key(name: str, args: dict) -> str:
    return hashlib.sha256(_canonical({"tool": name, "args": args}).encode()).hexdigest()


class Store:
    """One scenario's recording: ``{"models": {key: …}, "tools": {key: …}}``. ``replay`` raises on unknown keys."""

    def __init__(self, scenario: str, data: dict | None = None, replay: bool = False) -> None:
        self.scenario = scenario
        self.replay = replay
        self.data = data or {"scenario": scenario, "models": {}, "tools": {}}

    def get(self, section: str, key: str, what: str) -> dict:
        if key not in self.data[section]:
            raise StaleRecording(self.scenario, what)
        return self.data[section][key]

    def put(self, section: str, key: str, value: dict) -> None:
        self.data[section][key] = value


class _StructuredCall:
    def __init__(self, inner: Any, store: Store, role: str, model: str, schema: Any) -> None:
        self._inner, self._store, self._role, self._model, self._schema = inner, store, role, model, schema

    async def ainvoke(self, messages: Sequence[BaseMessage]) -> dict:
        key = model_key(self._role, self._model, self._schema.__name__, messages)
        if self._store.replay:
            saved = self._store.get("models", key, f"{self._role} model")
            raw = messages_from_dict([saved["reply"]])[0]
            return {"raw": raw, "parsed": self._schema.model_validate(saved["parsed"]), "parsing_error": None}
        result = await self._inner.ainvoke(messages)
        parsed = result.get("parsed")
        self._store.put("models", key, {"role": self._role, "model": self._model,
                                        "reply": messages_to_dict([result["raw"]])[0],
                                        "parsed": parsed.model_dump(mode="json") if parsed is not None else None})
        return result


class RecordingStructured:
    """Wraps a model used with ``with_structured_output`` (plan, assess)."""

    def __init__(self, inner: Any, store: Store, role: str, model: str) -> None:
        self._inner, self._store, self._role, self._model = inner, store, role, model

    def with_structured_output(self, schema: Any, **kwargs: Any) -> _StructuredCall:
        inner = None if self._store.replay else self._inner.with_structured_output(schema, **kwargs)
        return _StructuredCall(inner, self._store, self._role, self._model, schema)


class _BoundCall:
    def __init__(self, inner: Any, store: Store, role: str, model: str, tool_names: list[str]) -> None:
        self._inner, self._store, self._role, self._model, self._tools = inner, store, role, model, tool_names

    async def ainvoke(self, messages: Sequence[BaseMessage]) -> AIMessage:
        key = model_key(self._role, self._model, self._tools, messages)
        if self._store.replay:
            return messages_from_dict([self._store.get("models", key, f"{self._role} model")["reply"]])[0]
        reply = await self._inner.ainvoke(messages)
        self._store.put("models", key, {"role": self._role, "model": self._model,
                                        "reply": messages_to_dict([reply])[0], "parsed": None})
        return reply


class RecordingToolCaller:
    """Wraps the research model (``bind_tools``)."""

    def __init__(self, inner: Any, store: Store, role: str, model: str) -> None:
        self._inner, self._store, self._role, self._model = inner, store, role, model

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> _BoundCall:
        names = sorted(t.name for t in tools)
        inner = None if self._store.replay else self._inner.bind_tools(tools, **kwargs)
        return _BoundCall(inner, self._store, self._role, self._model, names)


class Throttle:
    """At most ``per_minute`` calls in any 60 s window (RegLens allows 30 reads a minute per caller)."""

    def __init__(self, per_minute: int) -> None:
        self._limit = per_minute
        self._times: deque[float] = deque()

    async def wait(self) -> None:
        now = time.monotonic()
        while self._times and now - self._times[0] >= 60:
            self._times.popleft()
        if len(self._times) >= self._limit:
            await asyncio.sleep(60 - (now - self._times[0]) + 0.1)
            return await self.wait()
        self._times.append(time.monotonic())
        return None


def recorded_tools(tools: Sequence[BaseTool], store: Store, throttle: Throttle | None = None) -> list[BaseTool]:
    """The RegLens tools behind the store: recorded live, or served from the recording."""
    wrapped: list[BaseTool] = []
    for tool in tools:
        wrapped.append(_wrap(tool, store, throttle))
    return wrapped


def _wrap(tool: BaseTool, store: Store, throttle: Throttle | None) -> BaseTool:
    async def call(**args: Any) -> tuple[str, Any]:
        key = tool_key(tool.name, args)
        if store.replay:
            saved = store.get("tools", key, f"{tool.name} tool")
        else:
            if throttle is not None:
                await throttle.wait()
            message = await tool.ainvoke({"type": "tool_call", "id": "record", "name": tool.name, "args": args})
            saved = {"name": tool.name, "args": args, "content": message.content,
                     "artifact": getattr(message, "artifact", None), "status": getattr(message, "status", "success")}
            store.put("tools", key, saved)
        if saved["status"] == "error":
            raise ToolException(_text(saved["content"]))
        return saved["content"], saved["artifact"]

    return StructuredTool.from_function(coroutine=call, name=tool.name, description=tool.description,
                                        args_schema=tool.args_schema, response_format="content_and_artifact",
                                        handle_tool_error=True)


def _text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content or [])


def recorded_models(models: Models | None, store: Store, names: tuple[str, str, str]) -> Models:
    """The three roles behind the store. In replay mode ``models`` may be None: nothing live is reachable."""
    planner, researcher, assessor = (models.planner, models.researcher, models.assessor) if models else (None, None, None)
    return Models(RecordingStructured(planner, store, "plan", names[0]),
                  RecordingToolCaller(researcher, store, "research", names[1]),
                  RecordingStructured(assessor, store, "assess", names[2]),
                  *names)
