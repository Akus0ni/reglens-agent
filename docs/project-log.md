# Project log

Newest first. What was done, why, and the problems hit.

## 2026-11-24 — Spec 0002: trajectory evals and the CI gate

- 15 golden scenarios, deterministic checks, record and replay keyed by the exact request, and a GitHub Actions gate
  that replays the recordings with no secrets. Plus a `claude-haiku-4-5` judge and a hand check.
- Two live runs: every check passed in every scenario in run 2 and in run 1 after one scenario was clarified;
  required 13/13 and severity 13/13 both times; no spread between runs. Judge 4.60 / 4.63 (n = 30); hand check within
  1 point 20/20, exact 14/20 (labelled by Claude without the API, D14).
- Problems hit: the machine ran out of memory during run 2, and Claude Code stopped the recording and the RegLens
  API (run 2 lost, about $0.45; `--first-run` and `--scenario` added, output unbuffered). The office-seating
  scenario said what the tool shows, not what it stores, and run 1 reasonably flagged DPDP: reworded by owner
  decision, re-recorded. PowerShell's `*>` writes a byte-order mark that hid one progress line.
- Spend: about $2.14 of the $3 Day 2 cap. Tests: 30.

## 2026-11-24 — Spec 0001: review agent built

- LangGraph graph plan → research ⇄ tools → assess → verify → review → file, with RegLens over MCP, Haiku 5.5 for the
  research loop and Sonnet 5.5 for planning and findings. Citations are checked in code; loop guards; Postgres
  checkpointer; report and GitHub issue filed idempotently; OpenTelemetry to the Aspire dashboard.
- Three sample reviews: 4, 6 and 4 verified findings, $0.04–0.06 and 36–49 s each. One crash-and-resume approval filed
  issue #3; a reject filed nothing.
- Problems hit: RegLens's MCP results left out null properties its schema requires, and the Python MCP client rejected
  them (fixed in reglens PR #21); LangGraph sends `on_interrupt` to every callback handler and Traceloop's has none;
  psycopg async needs a selector event loop on Windows.
- Spend: about $0.16 of $3. Tests: 23.

## 2026-11-24 — Repository set up

- Public repo `Akus0ni/reglens-agent` with a uv package skeleton (Python 3.14), CODEOWNERS, delete-branch-on-merge and
  the "Protect main" ruleset (copied from RegLens's `scripts/protect-main.ps1`).
- The RegLens workflow, copied and adapted: the `agent-spec` skill and spec template, the guard hook, the PR template,
  the branch clean-up script. Decisions D1–D11 recorded from the owner's answers.
