# reglens-agent

A LangGraph agent that reviews a product feature for compliance with Indian NBFC regulation. It researches through
[RegLens](https://github.com/Akus0ni/reglens) over MCP, writes findings whose citations are **checked in code**
against passages it retrieved, and waits for a human to approve, edit or reject the memo before anything is filed.
The wait is durable: the process can exit and the review resumes from Postgres without repeating any research.

```text
plan (Sonnet) → research ⇄ tools (Haiku + RegLens MCP) → assess (Sonnet) → verify (code) → review (interrupt) → file
```

Status: spec 0001 (the agent) built. Spec 0002 (trajectory evals, CI gate) next. See `docs/`.

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

These show the agent works, not how good it is. Quality is measured in spec 0002.
