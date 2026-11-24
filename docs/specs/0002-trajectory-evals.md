# Spec 0002 — Trajectory evals and a CI gate

> Status: **Approved (PR #5, 2026-11-24) · Implemented in `feat/0002-trajectory-evals`** · Created: 2026-11-24 · Owner: @Akus0ni
> Depends on: spec 0001; RegLens with PR #21 (MCP results match their schemas) · Blocked by open questions: none
> Sprint phase: D2·5

## 1. Context

Spec 0001's agent works on three sample features, but nothing measures it or stops a change from making it worse.
This spec adds:
- **15 golden scenarios** with the paragraphs a good review must cite.
- **Deterministic checks** on each run's trajectory and memo.
- An **LLM judge** for memo quality, with a hand check of the judge.
- A **GitHub Actions gate** that fails a pull request whose agent no longer passes.

The gate must not call Claude: one live review costs about $0.05, and Day 2 has $3 in total (D5). So a live run is
recorded once, locally, and CI replays it.
- The recording holds every model reply and every RegLens tool result, keyed by a hash of exactly what was sent.
- A prompt or code change that alters any request no longer matches its recording, and CI fails with "stale
  recording: re-record".
- The re-recorded run must then pass the checks against the stored baseline.

So a changed prompt can't merge until a live run shows it is no worse (D12).

## 2. Decisions

Builds on: D3 (tracing), D5 ($3 cap), D9 (two specs), D10 (`claude-haiku-4-5` judge), D4 (workflow).

New decisions made by the owner for this spec (2026-11-24):

| # | Decision |
|---|----------|
| D12 | CI replays recorded runs; nothing in CI calls Claude or RegLens. Model replies and tool results are recorded together, keyed by a SHA-256 of the role, model and canonical request. A request with no recording fails the gate |
| D13 | The 15 scenarios are drafted by Claude, with every expected paragraph checked against RegLens's stored text, and reviewed by the owner in this spec PR |
| D14 | The judge's hand check (10 memos) is labelled by Claude in the working session, without calling the Claude API, and reported as a second-model check, not a human one |
| D15 | Live eval runs: 15 scenarios × 2 runs |

## 3. Scope

**In scope:**
- `evals/scenarios.json` (in this PR).
- A recorder and replayer for the three model roles and the two RegLens tools.
- CLI `eval record | check | judge | report`.
- Deterministic checks and a baseline.
- The judge and the hand-check sheet.
- `evals/results.md`.
- `.github/workflows/evals.yml`.
- The ruleset's required status check.
- The broken-prompt demonstration.

**Out of scope:**
- Changing the agent's prompts or limits to raise scores (P1).
- Live model calls in CI.
- Evaluating RegLens itself (its own evals cover that).
- Scenario authoring tools.

## 4. Requirements

| ID | Requirement |
|----|-------------|
| R2.1 | `evals/scenarios.json` holds 15 scenarios (13 in scope, 2 out of scope): `id`, `feature`, `in_scope`, `required` (groups of document id + paragraph options), `min_severity` |
| R2.2 | A recorder wraps the three model roles and the two tools. Model key: SHA-256 of role, model id and the request (messages via `messages_to_dict`, plus the schema name or bound tool names), as canonical JSON. Tool key: SHA-256 of tool name and canonical arguments. It stores the reply (`messages_to_dict`, plus the parsed object for structured calls) or the tool result (text, artifact, status) |
| R2.3 | `eval record --runs N --confirm-spend` runs every scenario live through the spec 0001 graph (RegLens and Anthropic, in-memory checkpointer, stops at the review interrupt, files nothing). It writes `evals/runs/<UTC timestamp>-r<n>.json`: per-scenario state, checks, usage, cost, wall time, git commit and model ids. Run 1's recordings go to `evals/recordings/<scenario>.json`. It refuses to start if the RegLens API isn't ready |
| R2.4 | A replayer serves recorded replies and tool results by key. An unknown key raises `StaleRecording`, naming the scenario, the role or tool, and the re-record command |
| R2.5 | Deterministic checks per scenario: **completed** (reached the review step with a memo); **guards** (tool calls ≤ 20, turns per question ≤ 4); **searched** (in-scope scenarios called `search_regulations` at least once); **verified** (every accepted finding's evidence ids are in the run's evidence); **required** (each required group met by an accepted finding citing one of its options); **severity** (the strongest finding meeting a required group is at least `min_severity`); **quiet** (out-of-scope scenarios have no MEDIUM or HIGH finding). Groups and options are sets: order doesn't matter, and alternative paragraphs are allowed |
| R2.6 | `eval check` replays every recording and computes the checks. It passes when **completed, guards, searched, verified and quiet** hold for every scenario, and **required** and **severity** pass in no fewer scenarios than in `evals/baseline.json`. A failure prints the scenario and the failing check, and the exit code is non-zero |
| R2.7 | `evals/baseline.json` is written only by `eval check --write-baseline`, after a full live run, in a PR that says so. It is never written silently |
| R2.8 | `eval judge --confirm-spend` scores each memo of the latest run with `claude-haiku-4-5` (structured output, temperature 0) on a 1–5 rubric for **grounded** (each finding is supported by the passages it cites, which the judge is shown) and **actionable** (the recommendations are specific and fit the feature), with a one-line reason each. Results go into the run file. The judge never runs in CI |
| R2.9 | `eval judge` also writes `evals/hand-check.md`: 10 memos (the first 10 scenarios of run 1), the rubric, the cited passages and a blank label column. Claude fills it in the session without calling the API (D14). `eval report` computes agreement (within 1 point, exact) from the filled sheet |
| R2.10 | `eval report` writes `evals/results.md`: per-scenario checks for both runs, the pass count per check with n, the spread between runs (scenarios whose checks differ), judge means with n, hand-check agreement, cost and p50 wall time per review, date, commit and model ids |
| R2.11 | `.github/workflows/evals.yml` runs on every pull request and on pushes to `main`: checkout, `astral-sh/setup-uv`, `uv sync --locked`, `uv run pytest`, `uv run reglens-agent eval check`. No secrets. Job name `evals` |
| R2.12 | `scripts/protect-main.ps1` adds a `required_status_checks` rule for `evals` to the "Protect main" ruleset, and the script is re-run |
| R2.13 | **Broken-prompt demo** on branch `demo/broken-prompt`, never merged. (a) Change the assess prompt to cite passages "from memory" and push without re-recording: the gate fails as stale. (b) Re-record live: the gate fails on named checks. The PR records both runs and is then closed |
| R2.14 | Tests (offline): recorder and replayer round-trip; a changed prompt raises `StaleRecording`; each check on hand-made states (including alternative paragraphs and order); the baseline comparison |
| R2.15 | Spend is measured and reported; this spec's total stays within the remaining Day 2 cap: $3 minus the $0.16 already spent |

## 5. Design

```text
local, paid:  eval record ─► graph (live models + RegLens) ─► Recorder ─► evals/recordings/*.json + evals/runs/*.json
              eval judge  ─► claude-haiku-4-5 ─► scores in the run file; evals/hand-check.md
              eval report ─► evals/results.md
CI, free:     eval check  ─► graph (Replayer: recorded models + tools) ─► checks ─► vs evals/baseline.json ─► pass/fail
```

**P1, no tuning on the scenarios.**
- The agent's prompts, models and limits are spec 0001's.
- This spec measures them; it doesn't change them.
- If the results argue for a change, that is a new spec, re-recorded and compared with this baseline.

**P2, why record whole requests.**
- Keying on the full request (system prompt, messages, tool results already seen, schema) makes the recording a
  contract: the same code and prompts replay exactly, and any change in what is sent shows up as stale.
- Keying on only the scenario id would replay old answers for a new prompt and pass a regression.
- A recording can't drift silently, either: replay is deterministic, so CI's result equals the recorded run's result.

**P3, gate rule.**
- The hard checks (completed, guards, searched, verified, quiet) are invariants of a correct agent and must hold
  for all 15 scenarios.
- **required** and **severity** depend on the model's research, so their bar is the stored baseline: "no worse
  than the run the owner accepted" instead of a threshold set before any data.
- With n = 13 in-scope scenarios, one scenario is 7.7 points. The report gives counts, not percentages.

**P4, run variance.**
- Two runs show how much the same code varies.
- A scenario that passes in one run and fails in the other is reported as unstable.
- The gate uses run 1, the run whose recordings are committed.

**P5, the judge.**
- One `claude-haiku-4-5` call per memo, with the memo and the full text of every cited passage, at temperature 0
  (Haiku 4.5 accepts sampling settings).
- The judge only sees verified findings; the code check already guarantees the citations exist.
- The judge asks the other question: does the passage support what the finding says?

**P6, cost** (from spec 0001's measured $0.04–0.06 per review):

| Item | Estimate |
|------|----------|
| 15 scenarios × 2 runs | ≈ $1.6 |
| Judge, 30 memos × ~6k tokens in, ~0.3k out on Haiku 4.5 ($1/$5 per MTok) | ≈ $0.23 |
| Demo re-record, 15 scenarios | ≈ $0.8 |
| **Total** | **≈ $2.6** |

The remaining cap is about $2.84. If spend before the demo exceeds $2.0, the demo re-records only the first 5
scenarios, and the PR says so.

**P7, the hand check without the API (D14).**
- Claude reads `evals/hand-check.md` in the working session and fills in the labels against the same rubric and
  passages, before seeing the judge's scores (the sheet hides them).
- `eval report` then reads the labels.

### System design concepts exercised

| Concept | Where | What could go wrong without it |
|---------|-------|--------------------------------|
| Regression gate in CI | R2.6, R2.11–R2.12 | A prompt change that loses citations merges unnoticed |
| Test doubles at a service boundary (record and replay) | R2.2–R2.4, P2 | CI needs secrets, money and a running .NET server, or replays answers to questions no longer asked |
| Contract-keyed fixtures | P2 | Stale fixtures pass a changed prompt |
| Measuring variance before trusting a number | P4, R2.10 | One lucky run taken as the agent's quality |
| Validating the judge | R2.9, P5 | A lenient judge reports quality that isn't there |

## 6. Acceptance criteria

| # | Check | How |
|---|-------|-----|
| A1 | `uv run pytest` passes offline, including the new recorder, replayer, check and baseline tests | test output |
| A2 | `eval record --runs 2 --confirm-spend` completes for all 15 scenarios; `evals/runs/` has two run files and `evals/recordings/` has 15 | command output |
| A3 | `eval check` passes on the committed recordings and baseline, both locally and in GitHub Actions on this PR | Actions run link |
| A4 | `evals/results.md` shows the per-scenario checks for both runs, the pass counts with n, the spread, judge means with n, hand-check agreement, and cost and latency | file in the PR |
| A5 | Broken-prompt demo: a PR whose gate fails as stale, then fails on named checks after re-recording; closed unmerged | PR link |
| A6 | `main`'s ruleset requires the `evals` check | `gh api …/rulesets` output |
| A7 | Measured spend within the remaining cap | run files |

## 7. Measurements

- Per check: scenarios passing out of 15 (hard checks) or 13 (required, severity), for both runs.
- Spread: scenarios whose result differs between runs.
- Judge: mean grounded and actionable scores (n = 30 memos) and the score distribution.
- Hand check: agreement within 1 point and exact (n = 10).
- Cost and wall time per review: mean and p50, n = 30.

## 8. Open questions

| # | Question | Blocks |
|---|----------|--------|
| — | None | — |

## 9. Changes made while building

| Where | Change | Why |
|-------|--------|-----|
| R2.1 (owner decision, after run 1) | `oos-office-seating` now says bookings are anonymous (no employee name, ID or other personal data stored or shown); `scenarios.json` version 2 | Version 1 said what the tool *shows*, not what it *stores*. Run 1 asked whether bookings identify employees and raised two conditional MEDIUM DPDP findings (Rules 3 and 6), a defensible reading. This test was fixed after seeing a result; the run 1 record keeps the original outcome |
| R2.3 | `eval record --first-run N --scenario ID` records one run or one scenario again; the report merges run files by run number (a later file's scenario replaces an earlier one) | The machine ran out of memory during run 2, and Claude Code stopped the recording and the RegLens API. Run 1 had finished; run 2 was lost (about 9 reviews, ≈ $0.45 paid with nothing saved) |
| R2.3 | Progress lines are flushed | Run 2's progress was buffered and lost with the process |
| R2.5 | The graph state logs each research turn's question id and each executed tool (`turns_log`, `tools_log`) | The checks need them. They change no request sent to a model |
| R2.4 | The stale-recording message names the scenario and the command that re-records just it | Seen in practice: rewording one scenario made exactly that scenario stale |

## 10. Results (2026-11-24; full tables in `evals/results.md`)

- **A1:** `uv run pytest`: **30 passed**, offline. Covers record/replay round trip, a changed prompt raising
  `StaleRecording`, a recorded tool error replaying as an error, each check on hand-made states, and the gate.
- **A2:** two live runs of 15 reviews. Run 1 is `20261124T140912Z-r1.json`, plus `20261124T152938Z-r1.json`, which
  re-records `oos-office-seating` after the scenario was clarified. Run 2 is `20261124T153003Z-r2.json`.
  `evals/recordings/` holds 15 recordings.

  | Check | Run 1 (as first recorded) | Run 1 (merged) | Run 2 |
  |-------|---------------------------|----------------|-------|
  | completed, guards, searched, verified | 15/15 each | 15/15 each | 15/15 each |
  | quiet | 1/2 (office seating, v1 wording) | 2/2 | 2/2 |
  | required | 13/13 | 13/13 | 13/13 |
  | severity | 13/13 | 13/13 | 13/13 |

  **Spread:** no scenario's check results differed between run 1 (merged) and run 2. Each review cost about $0.045
  (run 1 $0.70, run 2 $0.68), with p50 wall times of 41.8 s and 43.4 s.
- **A3:** `eval check` passes on the committed recordings. The baseline (`evals/baseline.json`) is required 13,
  severity 13. The GitHub Actions run is linked in the PR.
- **A4, judge** (`claude-haiku-4-5`, n = 30 memos):
  - Grounded mean 4.60 and actionable mean 4.63.
  - The lowest scores: grounded 2 for `rbc-kfs-after-acceptance` (run 1), where it called a claim that "a single
    tap is not valid acceptance" an inference beyond the passages; and actionable 3 for that memo and for the v1
    `oos-office-seating` memo.
  - **Hand check** (D14: Claude, in the session, no API call, labelled before seeing any judge score; a
    second-model check, not a human one): 10 memos × 2 criteria. Within 1 point: **20/20**. Exact: 14/20.
  - Judge cost $0.144.
- **A5:** broken-prompt demo: see the PR.
- **A6:** ruleset: see the PR.
- **A7, spend:** run 1 $0.70, run 2 lost to the memory reap (≈ $0.45, estimated from timing), the office-seating
  re-record $0.01, run 2 $0.68, judge $0.14. That's about $2.0 for this spec so far, and about **$2.14** for Day 2
  with spec 0001's $0.16.

## 11. Sources (checked 2026-11-24)

- `astral-sh/setup-uv` latest release v10.4.0 (2026-11-20) and `actions/checkout` v7.0.1 (2026-07-20), from the
  GitHub releases API.
- GitHub rulesets, "Require status checks to pass before merging":
  https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  The exact REST payload is checked when the code PR applies it; GitHub rejects an invalid ruleset.
- `langchain_core.messages.messages_to_dict` and `messages_from_dict` round-trip an `AIMessage` with `tool_calls` and
  `usage_metadata` (tested against the installed `langchain-core` 1.8.4).
- `claude-haiku-4-5` accepts `temperature`; Claude 5 models reject non-default sampling settings:
  https://docs.langchain.com/oss/python/integrations/chat/anthropic. Price $1/$5 per MTok, as in RegLens
  `ModelPricing.cs`.
- Expected paragraphs, checked against RegLens's `chunks` table on 2026-11-24. Each clause the scenario relies on
  was found in the stored text:

  | Paragraph | Clause relied on |
  |-----------|------------------|
  | Credit Facilities Para 10(1) | disbursal into the borrower's bank account |
  | Credit Facilities Para 11 | cooling-off exit without penalty |
  | Credit Facilities Para 13 | data collection need-based, with consent |
  | Credit Facilities Para 14(4) | servers located within India |
  | RBC Para 29 | KFS before the contract |
  | RBC Para 30 | penal charges, not penal interest; no capitalisation |
  | RBC Paras 33 and 34 | no pre-payment charges on floating-rate non-business loans to individuals |
  | RBC Paras 35 and 39 | 30 days to release documents; compensation for delay |
  | RBC Para 100 | no calls before 8 a.m. or after 7 p.m.; privacy of family and friends |
  | KYC Para 23 | Aadhaar handling |
  | KYC Para 42(1) | high-risk customers updated at least once every two years |
  | DPDP Rule 6 | security safeguards |
  | DPDP Rule 7 | breach intimation to the Board |
  | DPDP Rule 8(3) | one-year minimum retention, then erasure |
  | DPDP Rule 10 | verifiable consent of a parent |
