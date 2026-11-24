# reglens-agent

A LangGraph agent that reviews a product feature for compliance with Indian NBFC regulation. You describe a feature;
the agent researches it through [RegLens](https://github.com/Akus0ni/reglens) over MCP and writes findings whose
citations are **checked in code** against passages it actually retrieved. Then it waits for a human to approve, edit
or reject the memo before anything is filed. The wait is durable: the process can exit and the review resumes from
Postgres without repeating any research.

Python 3.14 · LangGraph · `langchain-mcp-adapters` · Claude (`claude-sonnet-5-5` plans and assesses,
`claude-haiku-5-5` researches, `claude-haiku-4-5` judges evals) · Postgres checkpointer · OpenTelemetry · GitHub
Actions

## Architecture

```mermaid
flowchart LR
    H[Compliance reviewer<br/>CLI: review / resume]
    subgraph Agent["reglens-agent (Python, LangGraph)"]
        P[plan<br/>Sonnet 5.5]
        R[research ⇄ tools<br/>Haiku 5.5, bounded]
        A[assess<br/>Sonnet 5.5]
        V[verify<br/>code]
        RV[review<br/>interrupt]
        F[file<br/>idempotent]
    end
    PG[(Postgres<br/>LangGraph checkpoints)]
    RL[RegLens API<br/>MCP /mcp, read-only]
    AN[Anthropic API]
    GH[GitHub<br/>report issue]
    AS[Aspire dashboard<br/>one trace end to end]

    H --> P
    P --> R --> A --> V --> RV --> F
    R -- search_regulations / get_passage --> RL
    P --> AN
    R --> AN
    A --> AN
    RV <-. state .-> PG
    H -- approve / edit / reject --> RV
    F --> GH
    Agent -.-> AS
    RL -.-> AS
```

How a review runs:

1. **Plan** (one Sonnet call, structured output): turn the feature into 1–6 compliance questions with search hints.
2. **Research:** for each question, Haiku calls RegLens's `search_regulations` and `get_passage` tools. The loop is
   bounded: 4 turns per question, 20 tool calls per review, and an identical call is refused. Every passage
   returned is recorded as evidence, by chunk id, from the tool's structured result, never from model text.
3. **Assess** (one Sonnet call): write findings with an obligation, severity, the passages relied on and a
   recommendation. The feature text and passages go in as delimited data, not instructions.
4. **Verify** (code): a finding survives only if every passage it cites was retrieved in this review and its
   paragraph reference matches. Failing findings are listed separately and never filed.
5. **Review:** `interrupt()` with the memo; the state is checkpointed in Postgres.
6. **File** (after approve or edit): write `reports/<thread_id>.md` and open one GitHub issue. Both are idempotent
   by thread id, so resuming twice files once.

One review costs about $0.045 and takes about 42 s (p50, n = 30).

## Evals

15 golden scenarios in `evals/scenarios.json` (13 that must cite specific paragraphs, 2 out of scope), two live runs
(spec 0002, `evals/results.md`):

| Check | Run 1 | Run 2 |
|-------|-------|-------|
| Completed, limits respected, searched, every citation retrieved | 15/15 | 15/15 |
| Required paragraphs cited | 13/13 | 13/13 |
| Severity at least the expected level | 13/13 | 13/13 |
| Out-of-scope features stay quiet | 2/2\* | 2/2 |

\* After one out-of-scope scenario was clarified (`docs/specs/0002-trajectory-evals.md` §9).

- **Memo quality:** `claude-haiku-4-5` judge, n = 30: grounded 4.60, actionable 4.63 out of 5. A hand check of 10
  memos by a second model agreed within one point on 20 of 20 judgements.
- **The CI gate** (`.github/workflows/evals.yml`) replays recorded runs, with no secrets and no live calls. Recordings
  are keyed by a hash of each exact model request and tool call. A pull request that changes a prompt fails until
  it is re-recorded live and is no worse than `evals/baseline.json`.
- **The gate in action:** a deliberately broken prompt was blocked ([PR #7](https://github.com/Akus0ni/reglens-agent/pull/7)).
- **Branch protection:** `main` requires the check.

## Quickstart (Windows, PowerShell)

Needs RegLens running (`docker compose up -d` and `dotnet run --project src/RegLens.Api` in the reglens repo), uv,
Docker, `gh` logged in, and `ANTHROPIC_API_KEY`.

```powershell
uv sync
uv run pytest                                     # offline; Docker for the Postgres crash test
uv run reglens-agent eval check                   # the CI gate, offline

$env:REGLENS_API_KEY = '<RegLens Auth:ApiKey>'
$env:AGENT_DATABASE_URL = 'postgresql://reglens:reglens-dev@127.0.0.1:5432/reglens_agent'
uv run reglens-agent setup                        # checkpoint database and tables, issue label

uv run reglens-agent review --feature-file samples/contact-access.md --confirm-spend [--no-issue]   # ~$0.05
uv run reglens-agent resume <thread_id> approve   # or reject, or edit --memo-file memo.md
uv run reglens-agent show <thread_id>
```

Traces go to the Aspire dashboard RegLens uses (http://localhost:18888): one trace spans the agent's nodes, the
Claude calls and RegLens's MCP handling.

## Known limitations

- **Code checks citations, not claims.** It proves every cited passage was retrieved, not that the passage supports
  what the finding says. The judge measures that (grounded 4.60/5); its lowest score went to a finding that went
  beyond its passages.
- **Research limits fire often.** In the eval runs, 21 of 29 reviews hit the per-question turn limit or the 20-call
  budget at least once, and the memo says so. With 13/13 required paragraphs cited, the limits haven't cost a required finding on this set.
- **Small eval set.** 15 scenarios. One scenario is about 7 points of any rate, so the gate compares counts against
  a baseline instead of chasing percentages.
- **The hand check is a second-model check.** Another Claude model labelled the judge's memos (by your decision),
  not a person.
- **Local only.** One RegLens API key, a CLI for approval, run and tested on Windows (CI on Linux). Traces include
  prompts by default.
- **A changed prompt costs a re-record.** About $0.70 to re-record all 15 scenarios live.

## Design and history

- RegLens's design records:
  - [hybrid search](https://github.com/Akus0ni/reglens/blob/main/docs/adr/0001-hybrid-search.md)
  - [MCP as the boundary](https://github.com/Akus0ni/reglens/blob/main/docs/adr/0002-mcp-boundary.md)
  - [citation verification](https://github.com/Akus0ni/reglens/blob/main/docs/adr/0003-citation-verification.md)
  - the [scale-up design](https://github.com/Akus0ni/reglens/blob/main/docs/scale-up.md), including agent orchestration
    at scale
- Specs: [0001 review agent](docs/specs/0001-review-agent.md), [0002 trajectory evals](docs/specs/0002-trajectory-evals.md).
  Decisions in `docs/plan.md`, history in `docs/project-log.md`.
