// PreToolUse hook: keeps Claude Code off `main`.
// Blocks `git commit` / `git push` while main is checked out, pushes that target main from any branch,
// and `gh pr merge` (only the owner merges). Exit code 2 blocks the tool call; stderr is shown to Claude.
import { execFileSync } from "node:child_process";

let raw = "";
for await (const chunk of process.stdin) raw += chunk;

let input;
try { input = JSON.parse(raw); } catch { process.exit(0); }

const cmd = String(input?.tool_input?.command ?? "");
if (!cmd) process.exit(0);

const block = (msg) => { process.stderr.write(msg + "\n"); process.exit(2); };

const branch = (() => {
  try {
    return execFileSync("git", ["-C", input.cwd || process.cwd(), "branch", "--show-current"],
      { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  } catch { return ""; }
})();

// Split on shell separators so `git switch -c x && git commit` is judged per command.
const parts = cmd.split(/&&|\|\||;|\n|\|/).map((s) => s.trim());

for (const p of parts) {
  if (/^gh\s+pr\s+merge\b/.test(p)) {
    block("Blocked: only the repo owner merges pull requests in reglens-agent. Raise or update the PR and stop.");
  }
  const git = p.match(/^git(?:\s+-C\s+\S+)?\s+(commit|push)\b(.*)$/);
  if (!git) continue;
  const [, verb, rest] = git;
  if (branch === "main") {
    block(`Blocked: \`git ${verb}\` on main. Create a branch first (spec/NNNN-name or feat/NNNN-name), commit there, and open a PR. See the agent-spec skill.`);
  }
  if (verb === "push" && /(^|\s|:)(refs\/heads\/)?main(\s|$)/.test(rest)) {
    block("Blocked: pushing to main. Push your branch and open a PR instead.");
  }
}
process.exit(0);
