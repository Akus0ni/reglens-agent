# Project log

Newest first. What was done, why, and the problems hit.

## 2026-11-24 — Repository set up

- Public repo `Akus0ni/reglens-agent` with a uv package skeleton (Python 3.14), CODEOWNERS, delete-branch-on-merge and
  the "Protect main" ruleset (copied from RegLens's `scripts/protect-main.ps1`).
- The RegLens workflow, copied and adapted: the `agent-spec` skill and spec template, the guard hook, the PR template,
  the branch clean-up script. Decisions D1–D11 recorded from the owner's answers.
