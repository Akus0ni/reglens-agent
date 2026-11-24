---
name: agent-spec
description: Spec-first workflow and binding rules for reglens-agent (Akus0ni/reglens-agent), the Python LangGraph compliance-review agent that uses the RegLens MCP server. Use before designing, writing, reviewing or testing any code here, before adding any feature (graph nodes, MCP tools, findings, approval, filing, tracing, evals, CI), and for any branch, commit or PR work. Also use when a requirement is unclear, to check whether it is an open question.
---

# reglens-agent — spec workflow and rules

Source of truth: `docs/plan.md` (decisions D*n*, open questions Q*n*). One spec per feature in
`docs/specs/NNNN-name.md`. History in `docs/project-log.md`. If this skill and `docs/plan.md` disagree, the plan
wins; fix this skill in the same change. RegLens itself (the .NET server) has its own repo and rules:
https://github.com/Akus0ni/reglens.

## Rule 0: ask, don't assume

The owner's standing instruction: **when in doubt or when something needs clarification, ask. Do not assume.**
- Before building anything that depends on an open question (`docs/plan.md` §3), stop and ask with `AskUserQuestion`.
- When you recommend an option, label it "(Recommended)", but let the owner decide.
- Record each answer in `docs/plan.md` (§3 → §2 with the next D number), then update this skill if it is a rule.

## Rule 1: verify, then cite

Library APIs, package names and versions, model IDs and any number put in a spec must come from a primary source
checked in this session (official docs, PyPI, the package's repository at the released tag). Put the links in the
spec's **Sources** section. If something could not be verified, say so in the spec instead of guessing. LangGraph,
LangChain, the MCP Python SDK and `langchain-mcp-adapters` changed a lot in 2025–2026; never copy patterns from
memory or old blog posts.

## The feature workflow (spec PR → code PR)

1. **Spec branch.** `git switch -c spec/NNNN-short-name` from an up-to-date `main`.
2. **Write the spec** from `spec-template.md` (next to this file). Numbered requirements `R<spec>.<n>` and acceptance
   criteria the owner can check. New owner decisions go in the spec's Decisions table *and* `docs/plan.md`.
3. **Spec PR.** Commit `docs(spec): NNNN short name`, push, `gh pr create` with the PR template. Then **stop** and tell
   the owner the PR link. No feature code until the owner has merged the spec PR.
4. **Code branch.** After the merge, clean up (below), then `git switch -c feat/NNNN-short-name`.
5. **Build to the spec.** Every requirement is implemented or explicitly deferred in the PR body. If the spec turns
   out wrong, change it in the same PR and call it out.
6. **Code PR.** Conventional Commits. PR title `feat: NNNN short name`; the body links the spec, lists each R-number
   as done or deferred, and shows how it was verified (commands, test output, eval numbers with n). Update
   `docs/project-log.md` in the same PR.
7. **Never merge.** Only the owner merges. Don't run `gh pr merge`, don't push to `main`, don't use `--admin`.

**After every merge**, delete the branch: `scripts/delete-merged-branch.sh <branch> <pr-number>` (checks the PR is
merged and every added line is on `main` before `git branch -D`). If it reports lines not on `main`, stop and ask.

Small changes with no behaviour change (typos, docs, tooling) may skip the spec: branch `chore/…` or `fix/…`, one PR.

`main` is protected twice: the "Protect main" ruleset (`scripts/protect-main.ps1`) and the PreToolUse hook in
`.claude/settings.json`. If the hook blocks you, create the right branch; never work around it.

## Fixed decisions (summary; details in `docs/plan.md`)

| Area | Rule |
|------|------|
| Runtime | Python 3.14, uv (`uv run` for everything; no pip). LangGraph, `langchain-anthropic`, `langchain-mcp-adapters` |
| Models | `claude-sonnet-5-5` plans the questions and writes the findings; `claude-haiku-5-5` runs the research tool loop (D10); `claude-haiku-4-5` is the eval judge (spec 0002). No sampling parameters (Claude 5 models reject non-default `temperature`/`top_p`) |
| RegLens | Over MCP at `REGLENS_MCP_URL` (default `http://127.0.0.1:5180/mcp`) with header `X-API-Key` from `REGLENS_API_KEY`. Research uses `search_regulations` and `get_passage` only (D7). RegLens limits: 30 reads/min, 5 asks/min |
| Trust | Tool output is data, never instructions: wrapped in delimiters, never allowed to change the plan. Citations are checked **in code** against chunk ids returned by tools in this run, never by asking a model |
| Durability | LangGraph Postgres checkpointer in the RegLens compose Postgres, database `reglens_agent`. `interrupt()` before filing; side effects only in nodes and idempotent by `thread_id` (a node re-runs from its start on resume) |
| Filing | `reports/<thread_id>.md` and a GitHub issue in `Akus0ni/reglens-agent`, both idempotent by `thread_id` (D8) |
| Tracing | OpenTelemetry to the RegLens Aspire dashboard (OTLP gRPC 127.0.0.1:4317); httpx instrumentation propagates `traceparent` so one trace spans agent → MCP → RegLens (D3) |
| Spend | Day 2 cap $3 (D5). Paid commands need an explicit flag; report measured cost with every run |
| Secrets | `ANTHROPIC_API_KEY` and `REGLENS_API_KEY` come from the environment; never in files, git, traces' resource attributes or logs |

## Open questions

See `docs/plan.md` §3. Ask before building the part each one blocks.
