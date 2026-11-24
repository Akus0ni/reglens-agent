# Spec 0001 — Review agent

> Status: **Approved (PR #2, 2026-11-24) · Implemented in `feat/0001-review-agent`** · Created: 2026-11-24 · Owner: @Akus0ni
> Depends on: RegLens specs 0001–0006 (the MCP server) · Blocked by open questions: none
> Sprint phase: D2·0–D2·4

## 1. Context

A product team describes a feature ("our lending app reads the borrower's phone contacts for recovery") and wants to
know which NBFC rules it touches. This spec builds an agent that does the following:

1. Turns the description into a few compliance questions.
2. Researches each question through RegLens over MCP.
3. Drafts findings in which every citation is checked **in code** against passages the agent actually retrieved.
4. Pauses for a human to approve, edit or reject the memo before anything is filed.

The pause is durable: the process can die while it waits and the review resumes without repeating any research.

RegLens (the .NET server, spec 0006) already provides the tools:
- `search_regulations(query, topK)` returns ranked passages with `chunkId`, `paraRef`, heading and a 300-character
  excerpt.
- `get_passage(chunkId)` returns one passage's full text (at most about 2,000 characters).

Both are read-only. RegLens returns each result as structured content and also as JSON text, and it requires an
`X-API-Key` header. It also allows 30 reads a minute per caller.

Checked while writing this spec (2026-11-24, §9):

- `langchain-mcp-adapters` 0.3.2 requires `mcp>=1.24,<2`, so the agent uses the 1.x MCP client (1.30.0). That client
  uses the `initialize` handshake (`2025-11-25`). RegLens's stateless server serves it; RegLens has a test for exactly
  that client type.
- **Tool results.** The adapter gives the model the tool's text content and keeps `structuredContent` as the
  message's artifact. RegLens's C# SDK puts the JSON in the text too (`AIFunctionMcpServerTool`, `v2.4.0`), so the
  model sees chunk ids and the code reads them from the artifact.
- **Tool errors.** A tool error (`isError`) comes back to the model as a `ToolMessage` with `status="error"`, so the
  run doesn't crash.
- **Interrupts.** On resume, LangGraph re-runs the interrupted node from its start. Code before `interrupt()` must be
  safe to repeat, and side effects belong after it or in a later node.

## 2. Decisions

Builds on:
- D1 (feature in, cited memo out, approval before filing)
- D3 (OpenTelemetry to Aspire)
- D5 ($3 cap)
- D6 (Python 3.14)
- D7 (search and get_passage only)
- D8 (report and GitHub issue)
- D10 (Sonnet plans and assesses, Haiku 5.5 researches)
- D11 (Postgres checkpointer)

New design choices are marked P*n* in §5. No new owner decisions.

## 3. Scope

**In scope:**
- A LangGraph graph: `plan → research ⇄ tools → assess → verify → review (interrupt) → file`.
- RegLens tools over MCP.
- A Pydantic `Finding` model.
- Code verification of citations.
- Loop guards.
- A Postgres checkpointer.
- A CLI to review, resume and show.
- Markdown report and GitHub issue, both idempotent.
- OpenTelemetry traces.
- Three sample features.
- Unit and integration tests with fakes (no paid calls in `pytest`).

**Out of scope:**
- Golden scenarios, the LLM judge, recorded fixtures and the CI gate (spec 0002).
- A web UI.
- Parallel research across questions.
- `ask_regulations` (D7).
- Streaming output.
- Multi-user approval or roles.

## 4. Requirements

| ID | Requirement |
|----|-------------|
| R1.1 | A uv project on Python 3.14 with pinned dependencies (`uv.lock`): `langgraph`, `langchain-anthropic`, `langchain-mcp-adapters`, `langgraph-checkpoint-postgres`, `psycopg[binary]`, `pydantic`, OpenTelemetry SDK and OTLP gRPC exporter, `opentelemetry-instrumentation-httpx`, `opentelemetry-instrumentation-langchain`; dev: `pytest`, `pytest-asyncio`, `testcontainers[postgres]`. `uv run pytest` runs everything offline |
| R1.2 | Settings come from environment variables only, validated at start: `ANTHROPIC_API_KEY`, `REGLENS_API_KEY`, `REGLENS_MCP_URL` (default `http://127.0.0.1:5180/mcp`), `AGENT_DATABASE_URL`, `AGENT_ISSUE_REPO` (default `Akus0ni/reglens-agent`), `OTEL_EXPORTER_OTLP_ENDPOINT` (default `http://127.0.0.1:4317`; empty turns export off). A command fails at start, naming the variable, when one it needs is missing (`review` needs both keys; `resume`, `show` and `setup` need no Anthropic key). No key is logged or written to a span attribute |
| R1.3 | The RegLens tools load through `MultiServerMCPClient` (`transport: "http"`, the `X-API-Key` header). Only `search_regulations` and `get_passage` are bound to the model (D7); any other tool the server lists is ignored |
| R1.4 | **plan**: one `claude-sonnet-5-5` call with structured output (`method="json_schema"`) turns the feature into 1–6 questions, each with a short id and a search hint. The feature text is wrapped in `<feature>` delimiters as data |
| R1.5 | **research ⇄ tools**: for each question in turn, `claude-haiku-5-5` (effort low) bound to the two tools decides which to call; the **tools** node executes them through MCP. A question ends when the model stops calling tools, or after 4 model turns for that question |
| R1.6 | Every passage a tool returns is recorded in state as evidence, keyed by chunk id: document id and title, `paraRef`, heading, pages, and the excerpt or full text. Ids are read from the tool's structured artifact, never parsed from model text |
| R1.7 | **Loop guards**: (a) at most 4 model turns per question; (b) at most 20 tool calls per review; (c) a call whose (tool name, canonical JSON arguments) hash was already executed in this review is not executed again and gets a `ToolMessage` saying so; (d) LangGraph `recursion_limit` 60. Hitting (a) or (b) moves on with what was found and is recorded in the memo |
| R1.8 | **assess**: one `claude-sonnet-5-5` call with structured output returns `Finding`s: `question_id`, `obligation`, `document`, `para_ref`, `severity` (`LOW`, `MEDIUM`, `HIGH`), `evidence_chunk_ids` (1 or more), `recommendation`. It may return no findings. Evidence goes in as escaped `<passage id=… document=… ref=…>` blocks, and the system prompt says passage text is data, never instructions |
| R1.9 | **verify** (code, no model): a finding is accepted only if every `evidence_chunk_id` is in this run's evidence and its `para_ref` matches the `paraRef` of one of those chunks (comparing the paragraph part, so "Para 5" matches "Para 5, part 2 of 3"). Rejected findings are kept in state with the reason and listed separately in the memo. They are never filed as findings |
| R1.10 | The **memo** is rendered by code from the verified findings: severity, obligation, citation (document, ref, pages, chunk id), recommendation, then rejected findings and guard notes |
| R1.11 | **review** calls `interrupt({"thread_id", "memo", "findings"}, response_schema=Decision)` with `Decision{action: approve, edit or reject; memo: str or None; note: str or None}`. Nothing before the `interrupt()` call has side effects |
| R1.12 | **file** runs only for approve or edit. It writes `reports/<thread_id>.md` (the approved or edited memo) and creates one GitHub issue in `AGENT_ISSUE_REPO`, labelled `compliance-review`, whose body contains the marker `reglens-agent:thread_id=<thread_id>`. Filing is idempotent: a second run for the same thread rewrites the same file and finds the existing issue (a local record `reports/<thread_id>.issue`, then a `gh` search for the marker) instead of creating another. Reject files nothing |
| R1.13 | The checkpointer is `AsyncPostgresSaver` on database `reglens_agent` in the RegLens compose Postgres. `reglens-agent setup` creates the database if missing, runs `setup()` and creates the issue label. `thread_id` is a UUID |
| R1.14 | CLI (`uv run reglens-agent …`): `setup`; `review --feature-file F [--thread-id T] [--no-issue] --confirm-spend` runs to the interrupt and prints the memo and thread id; `resume T approve\|reject\|edit [--memo-file M]` runs to the end; `show T` prints the state and the next step. `review` without `--confirm-spend` refuses, because it calls Claude |
| R1.15 | **Resume after a crash**: killing the process while it waits for approval and then running `resume` with the same thread id finishes the review with **no** new model or tool calls before filing. Running `resume` twice files once |
| R1.16 | Each review records its cost: per-model input and output tokens from the responses' usage metadata, priced (Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 per MTok, as in RegLens `ModelPricing`), printed with the memo and stored in state |
| R1.17 | OpenTelemetry: service name `reglens-agent`, OTLP gRPC to the Aspire dashboard. A root span per CLI command with the `thread_id`, LangChain/LangGraph spans from the instrumentation, and httpx instrumentation so MCP requests carry `traceparent` and RegLens's spans join the same trace |
| R1.18 | Three sample features in `samples/`: phone-contact access for recovery; keeping Aadhaar images indefinitely for re-KYC; showing the APR only after the borrower accepts the loan |
| R1.19 | Tests (no network, no paid calls): verify accepts and rejects (unseen id, mismatched ref, empty evidence); guards (per-question turn limit, total tool-call limit, repeated call refused); memo rendering; filing idempotency and reject; interrupt and resume with a fake model and fake tools on `InMemorySaver`; and resume with no new calls on a real `AsyncPostgresSaver` (Testcontainers) |

## 5. Design

```text
feature ─► plan (Sonnet, ≤6 questions)
              │
              ▼
          research (Haiku + tools) ◄──┐  per question, ≤4 turns; ≤20 tool calls per review
              │ tool calls            │  repeated (tool, args) refused
              ▼                       │
          tools (MCP: search_regulations / get_passage) ─┘   evidence[chunkId] ← artifacts
              │ all questions done
              ▼
          assess (Sonnet, structured Findings over <passage> data)
              ▼
          verify (code: ids seen? ref matches?)  → memo (code)
              ▼
          review: interrupt(memo) ── checkpoint in Postgres; process may exit ──
              ▼  Command(resume=Decision)
          file (approve/edit: reports/<thread>.md + issue, idempotent) │ reject: end
```

**P1, state.**
- `ReviewState`: `feature`, `questions`, `question_index`, `messages` (per question, cleared on advance),
  `evidence: dict[int, Evidence]`, `tool_calls: list[str]` (hashes), `turns`, `guard_notes`, `findings`, `rejected`,
  `memo`, `decision`, `filed`, `usage`.
- Reducers keep evidence additive.
- Messages are scoped to one question, so the research context stays small. This is the main cost control besides D10.

**P2, research as graph steps, not an inner loop.**
- `research` (a model turn) and `tools` (execution) are separate nodes joined by a conditional edge, so every turn is
  checkpointed.
- A crash during research resumes at the last turn instead of paying for the whole node again.
- `tools` is our own node, not the prebuilt `ToolNode`, because it must record evidence from artifacts and apply the
  repeat guard before executing.

**P3, trust boundaries.**
- The feature text and every tool result are data, inside delimiters.
- The plan comes only from the plan node; later nodes can't add questions.
- Citations are checked by `verify` against `evidence`, which only the tools node writes. Asking a model whether its
  citations are real is never the check.

**P4, side effects.**
- Only `file` has side effects, and it runs after the interrupt.
- The report is overwritten with identical content.
- The issue check uses a local record first, then searches for the marker, then creates. A crash between creating the
  issue and writing the record is caught by the marker search (GitHub's search can lag by seconds; the PR notes
  this).

**P5, model calls and cost** (estimates, to be measured by R1.16):

| Step | Model | Calls per review | Tokens per call (in / out) | Cost per review |
|------|-------|------------------|----------------------------|-----------------|
| plan | Sonnet 5.5 | 1 | ~1.5k / ~0.5k | ~$0.008 |
| research | Haiku 5.5 | ~6 questions × ~3 turns | ~4k / ~0.2k | ~$0.008 |
| assess | Sonnet 5.5 | 1 | ~12k / ~2k | ~$0.044 |
| **Total** | | | | **≈ $0.06** |

- Spec 0001's paid runs are the three samples plus the crash test and a few development runs: about 10 reviews, so
  **≈ $0.6**. That leaves about $2.4 of the $3 cap (D5) for spec 0002.
- RegLens tool calls cost nothing: no LLM, local Ollama embeddings.

**P6, telemetry.** `opentelemetry-instrumentation-langchain` (Traceloop) creates workflow, task and GenAI spans
from LangChain callbacks. By default it records prompts and completions; set `TRACELOOP_TRACE_CONTENT=false` to turn
that off. That matches RegLens's D62 choice for local use. `HTTPXClientInstrumentor` injects `traceparent` into the MCP client's httpx requests;
RegLens's ASP.NET Core instrumentation continues the trace.

### System design concepts exercised

| Concept | Where | What could go wrong without it |
|---------|-------|--------------------------------|
| Service-to-service contract over a standard protocol | R1.3 | Coupling the agent to RegLens's internals |
| Bounded loops | R1.7 | A model that never stops calling tools burns the budget |
| Trust boundaries, validation in code | R1.8–R1.9, P3 | A fabricated or mismatched citation filed as a finding |
| Durable execution and checkpointing | R1.13, R1.15, P2 | A crash during the approval wait repeats the research (cost, different results) |
| Idempotency keys | R1.12, P4 | A resumed run files the report or opens the issue twice |
| Human-in-the-loop gate | R1.11 | Filing findings nobody reviewed |
| Distributed tracing across services | R1.17 | Can't tell whether a slow review is Sonnet, Haiku or RegLens |
| Cost attribution | R1.16, P5 | No idea what a review costs before running evals at scale |

## 6. Acceptance criteria

| # | Check | How |
|---|-------|-----|
| A1 | `uv run pytest` passes offline (R1.19), with no network and no API key | test output |
| A2 | All three samples produce a memo with verified findings; RegLens's log or trace shows the MCP calls arriving with the key | `review --confirm-spend` ×3, output in the PR |
| A3 | A finding with an unseen chunk id is rejected (test), and a forced loop stops at the guard (test) | `pytest` |
| A4 | Crash test: start a review, kill the process at the approval wait, `resume <id> approve` from a new process. No new model or tool calls (from the trace and the usage record), the report is written and one issue is created. A second `resume` creates no second issue | commands and output in the PR |
| A5 | `resume <id> reject` files nothing | output in the PR |
| A6 | One review appears in the Aspire dashboard as one trace: CLI root → graph nodes → Anthropic calls → MCP HTTP → RegLens `POST /mcp` spans | span list or screenshot in the PR |
| A7 | Measured cost per review (R1.16) for the three samples, and the total spend ≤ $1 for this spec | output in the PR |

## 7. Measurements

- Cost and latency per review for the three samples: n = 3. These are not eval numbers; spec 0002 measures quality.
- Tool calls per review, and how often each guard fires.

## 8. Open questions

| # | Question | Blocks |
|---|----------|--------|
| — | None | — |

## 9. Changes made while building

| Where | Change | Why |
|-------|--------|-----|
| R1.3 | The first live run failed on its first `search_regulations` call: the Python MCP client validates `structuredContent` against `outputSchema`, and RegLens omitted null properties its schema marks required. Fixed in RegLens (reglens PR #21, `fix/mcp-null-fields`), not worked around here | The bug was the server's; RegLens's own C# client doesn't validate, so its tests passed |
| R1.17 | `telemetry.py` gives Traceloop's `TraceloopCallbackHandler` no-op `on_interrupt` and `on_resume` | LangGraph 1.2 sends graph lifecycle events to every callback handler (its docs say only `GraphCallbackHandler` subclasses); Traceloop 0.63.1 has neither method, and each interrupt logged an `AttributeError` |
| R1.14 | The CLI and the Postgres test run asyncio on a `SelectorEventLoop` on Windows | psycopg's async connections cannot use Windows' default `ProactorEventLoop` |
| R1.5 | `ChatAnthropic(reasoning_effort=…)`: the installed 1.7.12 has the `reasoning_effort` field; `effort` is an alias the docs mention but not a model field | Checked against the installed package |
| R1.15 | `resume` and `show` build the graph with models that raise on any attribute access and with no tools, and need neither API key | Makes "no new model or tool calls on resume" structural, not just observed |
| P6 | Unverified item 1 is answered: the Traceloop instrumentation names each LangGraph node (`execute_task plan`, …) and the LLM calls (`ChatAnthropic.chat`) as spans under `invoke_agent LangGraph` | Seen in the dashboard (A6) |

## 10. Results (2026-11-24)

- **A1:** `uv run pytest`: **23 passed**, offline. The suite includes the Postgres crash test on Testcontainers
  (`postgres:17-alpine`): review to the interrupt in one graph, approve twice from a new graph built with
  unreachable models and no tools; no new model or tool calls, one issue.
- **A2, A7** (RegLens at `fix/mcp-null-fields`, n = 3, one run each):

  | Sample | Findings (verified / rejected) | Main citations | Guards fired | Cost | Wall time |
  |--------|--------------------------------|----------------|--------------|------|-----------|
  | Phone contacts for recovery | 4 / 0 | Credit Facilities Para 13; RBC Para 100; DPDP Rule 3 | q5 turn limit | $0.0492 | 47.8 s |
  | Aadhaar images kept for re-KYC | 6 / 0 | KYC Paras 23, 42, 47; DPDP Rules 6, 8; Credit Facilities Paras 13, 14 | tool budget (20) | $0.0628 | 49.3 s |
  | APR shown after acceptance | 4 / 0 | RBC Para 29 (KFS); Credit Facilities Paras 9, 11 | q2–q4 turn limit | $0.0416 | 36.4 s |

  Per review: 2 Sonnet calls (9–16k tokens in) and 15–18 Haiku calls (about 60k in). Haiku is about a third of the
  cost. Every review hit a research limit at least once.
- **A3:** covered by tests (`test_rejects_unseen_ids…`, `test_a_repeated_call_is_refused…`, `test_the_review_stops…`).
  No live finding was rejected.
- **A4:** the Aadhaar review's process had exited at the interrupt. `resume <id> approve` ran from a new process with
  `ANTHROPIC_API_KEY` and `REGLENS_API_KEY` both empty. It wrote `reports/<id>.md` and created issue
  Akus0ni/reglens-agent#3 (label `compliance-review`, thread-id marker in the body). A second `resume` was refused:
  "not waiting for review (next: done)".
- **A5:** `resume <id> reject` on the APR review: "nothing filed".
- **A6:** one review is one trace in the Aspire dashboard: 47.5 s, 420 spans across `reglens-agent` and
  `reglens-api`. Under `review`: the MCP `initialize`/`tools/list`/`tools/call` requests with RegLens's `POST /mcp/`
  spans nested inside, and `invoke_agent LangGraph` → `execute_task <node>` → `ChatAnthropic.chat` → Anthropic
  HTTP.
- **Spend:** $0.1536 for the three samples, plus the first run that failed at its first tool call (one Sonnet and
  one Haiku call, about $0.01): **about $0.16** of the $3 cap.
- **Observed, for spec 0002:** code verifies citations, not what a finding says about them. In the three memos the
  one claim I checked against the source held: the Aadhaar memo's finding 5 cites DPDP Rule 8 for a one-year minimum
  retention followed by erasure, and Rule 8(3) says exactly that. Checking content systematically is what spec
  0002's judge and hand check are for. Each tool call also opens a new MCP session (`initialize` +
  `notifications/initialized` + the call), the adapter's default; it costs a few ms against RegLens.

## 11. Sources (checked 2026-11-24)

- PyPI, versions and release dates:
  - `langgraph` 1.2.24 (2026-11-20)
  - `langgraph-checkpoint-postgres` 3.2.1 (2026-11-14)
  - `langchain-anthropic` 1.7.12 (2026-11-19)
  - `langchain-core` 1.8.4
  - `langchain-mcp-adapters` 0.3.2 (2026-08-06)
  - `mcp` 1.30.0, the latest 1.x (2.3.0 exists but the adapter requires `<2`)
  - `opentelemetry-sdk` and `-exporter-otlp-proto-grpc` 1.45.2
  - `opentelemetry-instrumentation-httpx` 0.66b2 (instruments `httpx` and `httpx2`)
  - `opentelemetry-instrumentation-langchain` 0.63.1
  - `pydantic` 2.14.4, `psycopg` 3.3.9, `pytest` 9.2.0, `pytest-asyncio` 1.5.0, `testcontainers` 4.15.0
  - Windows cp314 wheels confirmed for `grpcio`, `psycopg-binary`, `pydantic-core`, `orjson`
- `langchain-mcp-adapters` README and `tools.py`: `MultiServerMCPClient`, the `http` transport with `headers`,
  `handle_tool_errors`, and structured content as the `MCPToolArtifact`.
  https://github.com/langchain-ai/langchain-mcp-adapters
- MCP C# SDK `v2.4.0` `AIFunctionMcpServerTool.cs`: object results are serialized to a text block as well as
  `StructuredContent`. https://github.com/modelcontextprotocol/csharp-sdk/tree/v2.4.0
- LangGraph interrupts (`interrupt()`, `Command(resume=…)`, `response_schema`, a node re-runs from its start on
  resume): https://docs.langchain.com/oss/python/langgraph/interrupts. Durable execution (`thread_id` length,
  Postgres checkpointer): https://docs.langchain.com/oss/python/langgraph/durable-execution
- `langgraph-checkpoint-postgres` README (`AsyncPostgresSaver.from_conn_string`, `setup()` on first use,
  `autocommit=True` and `dict_row` for hand-made connections):
  https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint-postgres
- LangChain Anthropic integration: Claude 5 models reject non-default `temperature`/`top_p`/`top_k`; `effort`
  (alias of `reasoning_effort`); `with_structured_output(method="json_schema")` uses native structured outputs.
  https://docs.langchain.com/oss/python/integrations/chat/anthropic
- `opentelemetry-instrumentation-langchain` README: `LangchainInstrumentor().instrument()`, and content capture on
  by default (`TRACELOOP_TRACE_CONTENT`). https://github.com/traceloop/openllmetry
- Prices: RegLens `src/RegLens.Application/ModelPricing.cs` (Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 per MTok).
- Not verified yet, and checked in the code PR:
  - that the Traceloop instrumentation names LangGraph nodes as separate spans with `langgraph` 1.2
  - the exact usage-metadata field names `langchain-anthropic` 1.7 returns for cache and reasoning tokens
