"""Evidence from RegLens tool results, citation verification and the memo (spec 0001, R1.6, R1.9, R1.10).

Chunk ids come only from the tools' structured content (the ``MCPToolArtifact``), never from model text, so a model
cannot cite a passage into existence (P3).
"""

import re
from collections.abc import Iterable, Mapping
from typing import Any

Evidence = dict[str, Any]


def evidence_from_artifact(artifact: Any) -> list[Evidence]:
    """Passages in a ``search_regulations`` or ``get_passage`` result. Anything else yields nothing."""
    content = artifact.get("structured_content") if isinstance(artifact, Mapping) else None
    if not isinstance(content, Mapping):
        return []
    if isinstance(content.get("hits"), list):
        return [_item(hit, hit.get("excerpt", ""), full=False) for hit in content["hits"] if _has_id(hit)]
    if _has_id(content) and "content" in content:
        return [_item(content, content["content"], full=True)]
    return []


def merge_evidence(left: Mapping[str, Evidence] | None, right: Mapping[str, Evidence] | None) -> dict[str, Evidence]:
    """LangGraph reducer: adds passages by chunk id; a full text replaces an excerpt, never the reverse."""
    merged = dict(left or {})
    for key, item in (right or {}).items():
        if key not in merged or (item["full"] and not merged[key]["full"]):
            merged[key] = item
    return merged


def paragraph(ref: str) -> str:
    """The paragraph part of a reference: "Para 5, part 2 of 3" and "para 5" both give "para 5"."""
    head = ref.split(",")[0]
    return re.sub(r"\s+", " ", head).strip().lower()


def verify(findings: Iterable[Mapping[str, Any]], evidence: Mapping[str, Evidence]) -> tuple[list[dict], list[dict]]:
    """Accepts a finding only if every cited id was returned by a tool in this run and its reference matches one of
    them (R1.9). Returns (accepted, rejected); each rejected finding carries its reason."""
    accepted, rejected = [], []
    for finding in findings:
        ids = [str(i) for i in finding.get("evidence_chunk_ids", [])]
        unseen = [i for i in ids if i not in evidence]
        if not ids:
            reason = "no evidence cited"
        elif unseen:
            reason = f"cites passages not retrieved in this review: {', '.join(unseen)}"
        elif paragraph(str(finding.get("para_ref", ""))) not in {paragraph(evidence[i]["para_ref"]) for i in ids}:
            refs = ", ".join(sorted({evidence[i]["para_ref"] for i in ids}))
            reason = f"para_ref '{finding.get('para_ref')}' is not the reference of its evidence ({refs})"
        else:
            accepted.append(dict(finding))
            continue
        rejected.append({**finding, "reason": reason})
    return accepted, rejected


_SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def render_memo(feature: str, questions: Iterable[Mapping[str, Any]], accepted: Iterable[Mapping[str, Any]],
                rejected: Iterable[Mapping[str, Any]], evidence: Mapping[str, Evidence], notes: Iterable[str]) -> str:
    """The memo, written by code from verified findings only (R1.10)."""
    questions = list(questions)
    accepted = sorted(accepted, key=lambda f: (_SEVERITY_ORDER.get(str(f["severity"]), 9), str(f["question_id"])))
    lines = ["# Compliance review", "", "## Feature", "", feature.strip(), "", "## Questions researched", ""]
    lines += [f"- **{q['id']}** {q['text']}" for q in questions]
    lines += ["", f"## Findings ({len(accepted)})", ""]
    if not accepted:
        lines.append("No verified findings: the retrieved regulation states no obligation this feature touches.")
    for number, finding in enumerate(accepted, start=1):
        lines += [f"### {number}. [{finding['severity']}] {finding['obligation']}", "",
                  f"- Question: {finding['question_id']}",
                  f"- Recommendation: {finding['recommendation']}",
                  "- Citations:"]
        lines += [f"  - {_citation(evidence[str(i)])}" for i in finding["evidence_chunk_ids"]]
        lines.append("")
    rejected = list(rejected)
    if rejected:
        lines += ["## Rejected by verification", "",
                  "Findings the model proposed whose citations failed the code check. They are not findings.", ""]
        lines += [f"- {r['obligation']} ({r.get('para_ref', '?')}): {r['reason']}" for r in rejected]
        lines.append("")
    notes = list(notes)
    if notes:
        lines += ["## Research limits reached", ""] + [f"- {note}" for note in notes] + [""]
    return "\n".join(lines).rstrip() + "\n"


def _citation(item: Mapping[str, Any]) -> str:
    pages = f"p. {item['page_start']}" if item["page_start"] == item["page_end"] else \
        f"pp. {item['page_start']}-{item['page_end']}"
    return f"{item['document_title']}, {item['para_ref']}, {pages} (passage {item['chunk_id']})"


def _has_id(value: Any) -> bool:
    return isinstance(value, Mapping) and isinstance(value.get("chunkId"), int)


def _item(source: Mapping[str, Any], text: str, full: bool) -> Evidence:
    return {
        "chunk_id": source["chunkId"],
        "document_id": source.get("documentId", ""),
        "document_title": source.get("documentTitle", ""),
        "para_ref": source.get("paraRef", ""),
        "heading": source.get("heading", ""),
        "page_start": source.get("pageStart", 0),
        "page_end": source.get("pageEnd", 0),
        "text": text,
        "full": full,
    }
