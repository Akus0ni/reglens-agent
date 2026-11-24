# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

reglens-agent is a Python LangGraph agent that reviews product features for compliance with Indian NBFC regulation,
using the [RegLens](https://github.com/Akus0ni/reglens) MCP server (a separate .NET repo) for research. **Built: spec
0001, the review agent** (`src/reglens_agent/`: `graph.py` nodes and guards, `evidence.py` citation checks and memo,
`filing.py` report and issue, `cli.py`). **Built: spec 0002**, trajectory evals and the CI gate (`src/reglens_agent/evals/`, `evals/`). Next: portfolio pass. Plan, decisions (D*n*) and open
questions (Q*n*): `docs/plan.md`. Specs: `docs/specs/`. History: `docs/project-log.md`.

## Workflow — read first

- **Load the `agent-spec` skill** (`.claude/skills/agent-spec/SKILL.md`) before designing, coding, reviewing or
  touching git. It holds the binding rules and the feature workflow.
- Every feature: **spec PR** (`spec/NNNN-name`) → owner merges → **code PR** (`feat/NNNN-name`). Stop after opening
  each PR; only the owner merges.
- `main` never takes direct commits. A PreToolUse hook (`.claude/settings.json` → `.claude/hooks/guard-main.mjs`, needs
  Node) blocks `git commit`/`git push` on `main`, pushes to `main`, and `gh pr merge`. GitHub enforces the same with the
  "Protect main" ruleset (`scripts/protect-main.ps1`).
- The owner's standing rules: **ask when in doubt, don't assume**, and **verify against primary sources and cite
  them**.

## Commands

```powershell
uv sync; uv run pytest                            # offline; Docker for the Postgres crash test
$env:AGENT_DATABASE_URL = 'postgresql://reglens:reglens-dev@127.0.0.1:5432/reglens_agent'
uv run reglens-agent setup
uv run reglens-agent review --feature-file samples/contact-access.md --confirm-spend [--no-issue]  # ~$0.05, needs both keys
uv run reglens-agent resume <thread_id> approve|reject|edit [--memo-file M]   # no API keys needed
uv run reglens-agent show <thread_id>
uv run reglens-agent eval check                    # the CI gate: replay recordings, compare with evals/baseline.json (free)
uv run reglens-agent eval record --runs 1 --scenario <id> --confirm-spend   # re-record (live, ~$0.05 a review)
uv run reglens-agent eval judge --confirm-spend; uv run reglens-agent eval report
```

A change to any prompt or request makes the recordings stale: re-record every scenario (`eval record --runs 2`),
then `eval check`. `--write-baseline` only in a PR that says so (spec 0002, R2.7).

## Environment

- Windows 11, PowerShell 5.1 and Git Bash. Python 3.14 with uv: use `uv run` for everything.
- RegLens must be running for live runs: `docker compose up -d` and `dotnet run --project src/RegLens.Api` in the
  reglens repo (http://127.0.0.1:5180, MCP at `/mcp`).
- `ANTHROPIC_API_KEY` is a Windows user environment variable; a terminal opened before it was set does not see it
  (load it with `[Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY','User')`). `REGLENS_API_KEY` is the RegLens
  API key (`dotnet user-secrets list --project src/RegLens.Api` in the reglens repo). Never put either in a file.
- Git Bash rewrites `branch:.dir/file` arguments as Windows paths; `scripts/delete-merged-branch.sh` sets
  `MSYS_NO_PATHCONV=1` for that.
