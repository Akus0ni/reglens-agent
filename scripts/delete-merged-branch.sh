#!/usr/bin/env bash
# Deletes a local branch once its PR is merged and every line it added is on main.
# Squash merges rewrite history, so `git branch -d` and tree/diff comparisons give false alarms;
# checking the branch's added lines against main does not.
# Usage: scripts/delete-merged-branch.sh <branch> <pr-number>
set -euo pipefail
# Git Bash rewrites arguments like `main:.claude/x` as Windows paths; keep them as written.
export MSYS_NO_PATHCONV=1
branch="${1:?branch name}"; pr="${2:?PR number}"

state=$(gh pr view "$pr" --json state --jq .state)
[ "$state" = "MERGED" ] || { echo "PR #$pr is $state, not MERGED. Keeping $branch." >&2; exit 1; }

git switch -q main
git pull -q --ff-only
git fetch -q --prune

base=$(git merge-base main "$branch")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
missing=0
# One pass per file: added lines that do not appear anywhere in main's copy of that file.
while IFS= read -r file; do
  git cat-file -e "main:$file" 2>/dev/null || { echo "Missing on main: $file" >&2; missing=1; continue; }
  # Identical content on both sides: nothing to check. A binary file has no lines to compare, so it must match exactly.
  [ "$(git rev-parse "main:$file")" = "$(git rev-parse "$branch:$file")" ] && continue
  if git diff --numstat "$base" "$branch" -- "$file" | grep -q $'^-	-	'; then
    echo "Binary file differs on main: $file" >&2; missing=1; continue
  fi
  git show "main:$file" > "$work/main"
  git diff "$base" "$branch" -- "$file" | grep '^+' | grep -v '^+++' | sed 's/^+//' | grep -v '^$' > "$work/added" || true
  if grep -vxFf "$work/main" "$work/added" > "$work/absent"; then
    sed "s|^|Not on main ($file): |" "$work/absent" | cut -c1-160 >&2
    missing=1
  fi
done < <(git diff --name-only --diff-filter=AM "$base" "$branch")

[ "$missing" -eq 0 ] || { echo "$branch has work that is not on main. Not deleting; ask the owner." >&2; exit 1; }
git branch -D "$branch"
