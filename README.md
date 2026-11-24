# reglens-agent

A LangGraph agent that reviews a product feature for compliance with Indian NBFC regulation. It researches through
[RegLens](https://github.com/Akus0ni/reglens) over MCP, writes findings whose citations are **checked in code**
against passages it retrieved, and waits for a human to approve, edit or reject the memo before anything is filed.
The wait is durable: the process can exit and the review resumes from Postgres without repeating any research.

```text
plan (Sonnet) → research ⇄ tools (Haiku + RegLens MCP) → assess (Sonnet) → verify (code) → review (interrupt) → file
```

Status: spec 0001 (the agent) and spec 0002 (trajectory evals, CI gate) built. See `docs/` and `evals/results.md`.

## Quickstart (Windows, PowerShell)

Needs RegLens running (`docker compose up -d` and `dotnet run --project src/RegLens.Api` in the reglens repo), uv,
Docker, `gh` logged in, and `ANTHROPIC_API_KEY`.

```powershell
uv sync
uv run pytest                                     # offline; Docker for the Postgres crash test

$env:REGLENS_API_KEY = '<RegLens Auth:ApiKey>'
$env:AGENT_DATABASE_URL = 'postgresql://reglens:reglens-dev@127.0.0.1:5432/reglens_agent'
uv run reglens-agent setup                        # checkpoint database and tables, issue label

uv run reglens-agent review --feature-file samples/contact-access.md --confirm-spend [--no-issue]   # ~$0.05
uv run reglens-agent resume <thread_id> approve   # or reject, or edit --memo-file memo.md
uv run reglens-agent show <thread_id>
```

Traces go to the Aspire dashboard RegLens uses (http://localhost:18888): one trace spans the agent's nodes, the
Claude calls and RegLens's MCP handling.

## Results so far (n = 3 sample features, one run each)

| Sample | Verified findings | Cost | Time |
|--------|-------------------|------|------|
| Phone contacts read for loan recovery | 4 | $0.049 | 48 s |
| Aadhaar images kept indefinitely for re-KYC | 6 | $0.063 | 49 s |
| APR shown only after the borrower accepts | 4 | $0.042 | 36 s |

## Evals (spec 0002)

15 golden scenarios (13 that must cite specific paragraphs, 2 out of scope), two live runs, n = 15 each:

| Check | Run 1 | Run 2 |
|-------|-------|-------|
| Completed, limits respected, searched, every citation retrieved | 15/15 | 15/15 |
| Required paragraphs cited | 13/13 | 13/13 |
| Severity at least the expected level | 13/13 | 13/13 |
| Out-of-scope features stay quiet | 2/2* | 2/2 |

\* After one out-of-scope scenario was clarified (see `docs/specs/0002-trajectory-evals.md` §9).

Memo quality, `claude-haiku-4-5` judge (n = 30): grounded 4.60, actionable 4.63 out of 5. A hand check of 10 memos
by a second model agreed within one point on 20 of 20 judgements. CI (`.github/workflows/evals.yml`) replays the
recorded runs, so a pull request that changes a prompt fails until it is re-recorded and is no worse than
`evals/baseline.json`.
