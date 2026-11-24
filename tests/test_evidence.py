"""Citation verification, evidence and the memo (spec 0001, R1.6, R1.9, R1.10)."""

import pytest

from reglens_agent.evidence import evidence_from_artifact, merge_evidence, paragraph, render_memo, verify
from tests.fakes import passage


def _evidence(*items: dict) -> dict:
    found = {}
    for item in items:
        for e in evidence_from_artifact({"structured_content": item}):
            found = merge_evidence(found, {str(e["chunk_id"]): e})
    return found


EVIDENCE = _evidence(passage(1966, "Rule 7"), passage(2158, "Para 100, part 2 of 3"))


def finding(ids: list[int], ref: str) -> dict:
    return {"question_id": "q1", "obligation": "Report breaches", "document": "DPDP Rules", "para_ref": ref,
            "severity": "HIGH", "evidence_chunk_ids": ids, "recommendation": "Add a breach process."}


def test_accepts_a_finding_whose_ids_were_retrieved_and_ref_matches():
    accepted, rejected = verify([finding([1966], "Rule 7"), finding([2158], "Para 100")], EVIDENCE)

    assert len(accepted) == 2
    assert rejected == []


@pytest.mark.parametrize(("ids", "ref", "reason"), [
    ([9999], "Rule 7", "cites passages not retrieved in this review: 9999"),
    ([1966, 9999], "Rule 7", "cites passages not retrieved in this review: 9999"),
    ([1966], "Rule 8", "para_ref 'Rule 8' is not the reference of its evidence (Rule 7)"),
    ([], "Rule 7", "no evidence cited"),
])
def test_rejects_unseen_ids_mismatched_refs_and_missing_evidence(ids, ref, reason):
    accepted, rejected = verify([finding(ids, ref)], EVIDENCE)

    assert accepted == []
    assert rejected[0]["reason"] == reason


def test_paragraph_ignores_the_part_suffix_case_and_spacing():
    assert paragraph("Para 100, part 2 of 3") == paragraph("para  100") == "para 100"


def test_reads_hits_and_passages_from_structured_content_only():
    search = {"query": "x", "hits": [{k: v for k, v in passage(1, "Rule 1").items() if k != "content"} | {"excerpt": "e"}]}

    assert [e["chunk_id"] for e in evidence_from_artifact({"structured_content": search})] == [1]
    assert evidence_from_artifact({"structured_content": passage(2, "Rule 2")})[0]["full"] is True
    assert evidence_from_artifact(None) == []
    assert evidence_from_artifact({"structured_content": {"chunkId": "not-an-int", "content": "x"}}) == []


def test_a_full_passage_replaces_an_excerpt_but_not_the_reverse():
    excerpt = {"7": {"chunk_id": 7, "full": False, "text": "short"}}
    full = {"7": {"chunk_id": 7, "full": True, "text": "long"}}

    assert merge_evidence(excerpt, full)["7"]["text"] == "long"
    assert merge_evidence(full, excerpt)["7"]["text"] == "long"


def test_memo_lists_verified_findings_with_citations_then_rejected_ones_and_limits():
    accepted, rejected = verify([finding([1966], "Rule 7"), finding([42], "Rule 9")], EVIDENCE)

    memo = render_memo("Feature X", [{"id": "q1", "text": "Breach?"}], accepted, rejected, EVIDENCE,
                       ["q2: stopped after 4 research turns."])

    assert "## Findings (1)" in memo
    assert "Digital Personal Data Protection Rules, 2025, Rule 7, p. 26 (passage 1966)" in memo
    assert "## Rejected by verification" in memo and "cites passages not retrieved in this review: 42" in memo
    assert "## Research limits reached" in memo
