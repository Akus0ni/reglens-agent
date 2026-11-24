# reglens-agent plan

Owner: @Akus0ni · Started: 2026-11-24 (Day 2 of the RegLens sprint)

## 1. Goal

A Python LangGraph agent that reviews a product feature for compliance with Indian NBFC regulation. A feature
description goes in; the agent turns it into compliance questions, researches them through
[RegLens](https://github.com/Akus0ni/reglens) over MCP, and drafts findings whose every citation is checked in code
against passages it actually retrieved. A human approves, edits or rejects the memo before anything is filed, and the
wait survives a crash. Trajectory evals gate changes in CI.

## 2. Decisions

"Owner" = decided by the owner in conversation. "Plan" = from the sprint tracker the owner adopted
(`reglens-sprint.html`, outside this repo); confirm before changing. RegLens decisions are cited as "RegLens D*n*".

| # | Decision | Source | Date |
|---|----------|--------|------|
| D1 | The agent is the sprint's Day 2 project: feature description in, cited findings memo out, human approval before filing (RegLens D1, D5) | Owner | 2026-11-23 |
| D2 | Public repo `Akus0ni/reglens-agent` (RegLens D65) | Owner | 2026-11-24 |
| D3 | Traces go over OpenTelemetry to the Aspire dashboard RegLens already uses, not Langfuse, so one trace can span agent → MCP → RegLens (RegLens D66) | Owner | 2026-11-24 |
| D4 | Same workflow as RegLens: spec PR → code PR, protected `main`, the guard hook, a project log (RegLens D67) | Owner | 2026-11-24 |
| D5 | Spend cap for Day 2's paid runs, development and live evals together: $3 (RegLens D68) | Owner | 2026-11-24 |
| D6 | Python 3.14 with uv. Checked: `grpcio`, `psycopg-binary`, `pydantic-core` and `orjson` ship Windows wheels for 3.14 | Owner | 2026-11-24 |
| D7 | The research step uses RegLens's `search_regulations` and `get_passage` only, not `ask_regulations`: one LLM layer, and every cited chunk id is one the agent saw | Owner | 2026-11-24 |
| D8 | After approval, the agent writes `reports/<thread_id>.md` and opens a GitHub issue in `Akus0ni/reglens-agent`, both idempotent by `thread_id` | Owner | 2026-11-24 |
| D9 | Two specs: 0001 the review agent (graph, tools, findings and verification, loop guards, durable approval, filing, tracing); 0002 trajectory evals, recorded MCP fixtures and the GitHub Actions gate | Owner | 2026-11-24 |
| D10 | `claude-sonnet-5-5` plans the questions and writes the findings; `claude-haiku-5-5` runs the research tool loop (amends RegLens D3 for this step, to fit D5); `claude-haiku-4-5` is the eval judge | Owner | 2026-11-24 |
| D11 | LangGraph with the Postgres checkpointer in the RegLens compose Postgres, separate database; `langchain-mcp-adapters` for the MCP tools | Plan | 2026-11-24 |

## 3. Open questions

| # | Question | Blocks |
|---|----------|--------|
| — | None | — |

## 4. Specs (proposed order)

| Spec | Feature |
|------|---------|
| 0001 | Review agent: plan → research (MCP) → assess → verify → human review (interrupt) → file; loop guards; Postgres checkpointer; OpenTelemetry |
| 0002 | Trajectory evals: 15 golden scenarios, deterministic checks, Haiku 4.5 judge with a hand check, recorded MCP fixtures, GitHub Actions gate |

The portfolio pass (README, ADRs, demo) is a chore PR after 0002.
