"""Data shapes at the agent's boundaries (spec 0001, R1.4, R1.8, R1.11).

Graph state holds plain dicts (``model_dump()``) so checkpoints never depend on these classes; the Pydantic models
are used where data crosses a boundary: model output, the human's decision, the memo.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

MAX_QUESTIONS = 6


class Question(BaseModel):
    """One compliance question the research step looks up."""

    id: str = Field(description="Short id, q1 to q6.")
    text: str = Field(description="The compliance question, answerable from NBFC regulation or the DPDP Rules.")
    search_hint: str = Field(description="Words likely to appear in the relevant regulation, for the first search.")


class QuestionPlan(BaseModel):
    """The plan step's output (R1.4)."""

    questions: list[Question] = Field(min_length=1, max_length=MAX_QUESTIONS)


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Finding(BaseModel):
    """One compliance finding (R1.8). Its citations are checked in code before it reaches the memo (R1.9)."""

    question_id: str = Field(description="The id of the question this finding answers.")
    obligation: str = Field(description="What the regulation requires, in one or two plain sentences.")
    document: str = Field(description="The title of the regulation the obligation comes from.")
    para_ref: str = Field(description="The paragraph or rule reference, exactly as given in the passage, e.g. 'Rule 7'.")
    severity: Severity = Field(description="HIGH: the feature as described breaks the rule. MEDIUM: it likely does, or "
                               "needs a control it doesn't mention. LOW: worth checking.")
    evidence_chunk_ids: list[int] = Field(min_length=1, description="The passage ids this finding relies on.")
    recommendation: str = Field(description="What the team should change or check.")


class Findings(BaseModel):
    """The assess step's output. May be empty when nothing applies."""

    findings: list[Finding]


class Decision(BaseModel):
    """The human's answer at the review interrupt (R1.11)."""

    action: Literal["approve", "edit", "reject"]
    memo: str | None = Field(default=None, description="The edited memo, for action 'edit'.")
    note: str | None = None
