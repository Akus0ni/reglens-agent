"""Filing is idempotent by thread id (spec 0001, R1.12, P4)."""

from reglens_agent.filing import Filer, marker
from tests.fakes import FakeGh


def test_files_the_report_and_creates_one_issue_with_the_marker(tmp_path):
    gh = FakeGh()

    filed = Filer(tmp_path, "Akus0ni/reglens-agent", gh).file("t-1", "Compliance review: X", "# Memo\n", True)

    assert (tmp_path / "t-1.md").read_text(encoding="utf-8") == "# Memo\n"
    assert filed.issue_url == "https://github.com/Akus0ni/reglens-agent/issues/1"
    assert (tmp_path / "t-1.issue").read_text(encoding="utf-8") == filed.issue_url
    assert gh.created == 1
    assert marker("t-1") in gh.invocations[-1][1]


def test_filing_again_reuses_the_local_record(tmp_path):
    gh = FakeGh()
    filer = Filer(tmp_path, "Akus0ni/reglens-agent", gh)

    first = filer.file("t-1", "T", "# Memo\n", True)
    second = filer.file("t-1", "T", "# Memo\n", True)

    assert second == first
    assert gh.created == 1


def test_an_issue_created_before_a_crash_is_found_by_its_marker(tmp_path):
    gh = FakeGh(existing=["https://github.com/Akus0ni/reglens-agent/issues/7"])  # created, record never written

    filed = Filer(tmp_path, "Akus0ni/reglens-agent", gh).file("t-1", "T", "# Memo\n", True)

    assert filed.issue_url.endswith("/issues/7")
    assert gh.created == 0
    search = next(args for args, _ in gh.invocations if args[:2] == ["issue", "list"])
    assert f'"{marker("t-1")}" in:body' in search


def test_no_issue_writes_the_report_only(tmp_path):
    gh = FakeGh()

    filed = Filer(tmp_path, "Akus0ni/reglens-agent", gh).file("t-1", "T", "# Memo\n", False)

    assert filed.issue_url is None
    assert gh.invocations == []
    assert (tmp_path / "t-1.md").exists()
