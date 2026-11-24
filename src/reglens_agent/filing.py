"""Filing an approved memo: a Markdown report and a GitHub issue, both idempotent by thread id (spec 0001, R1.12, P4).

The issue check goes: local record → search GitHub for the marker → create. The record catches a resumed run; the
marker search catches a crash between creating the issue and writing the record (GitHub search can lag by seconds).
"""

import json
import os
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

LABEL = "compliance-review"

Runner = Callable[[Sequence[str], str | None], str]


def run_gh(args: Sequence[str], stdin: str | None = None) -> str:
    """Runs the GitHub CLI with the owner's login and returns stdout; a failure raises with gh's message."""
    result = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True, encoding="utf-8", check=False)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:2])} failed: {result.stderr.strip()}")
    return result.stdout


def marker(thread_id: str) -> str:
    return f"reglens-agent:thread_id={thread_id}"


@dataclass(frozen=True)
class Filed:
    report: str
    issue_url: str | None


class Filer:
    def __init__(self, reports_dir: Path, issue_repo: str, runner: Runner = run_gh) -> None:
        self._reports = reports_dir
        self._repo = issue_repo
        self._gh = runner

    def file(self, thread_id: str, title: str, memo: str, create_issue: bool) -> Filed:
        self._reports.mkdir(parents=True, exist_ok=True)
        report = self._reports / f"{thread_id}.md"
        _write_atomically(report, memo)
        issue = self._issue(thread_id, title, memo) if create_issue else None
        return Filed(str(report), issue)

    def _issue(self, thread_id: str, title: str, memo: str) -> str:
        record = self._reports / f"{thread_id}.issue"
        if record.exists():
            return record.read_text(encoding="utf-8").strip()

        found = json.loads(self._gh(["issue", "list", "--repo", self._repo, "--state", "all", "--search",
                                     f"\"{marker(thread_id)}\" in:body", "--json", "url", "--limit", "1"], None) or "[]")
        if found:
            url = found[0]["url"]
        else:
            body = f"{memo}\n\n<!-- {marker(thread_id)} -->\n"
            url = self._gh(["issue", "create", "--repo", self._repo, "--title", title, "--label", LABEL,
                            "--body-file", "-"], body).strip()
        _write_atomically(record, url)
        return url

    def ensure_label(self) -> None:
        """Creates the issue label if it is missing (`setup`)."""
        self._gh(["label", "create", LABEL, "--repo", self._repo, "--force", "--color", "B60205",
                  "--description", "Filed by reglens-agent after human approval"], None)


def _write_atomically(path: Path, text: str) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)
