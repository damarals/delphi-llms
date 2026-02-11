from dataclasses import dataclass
from statistics import median

from pydantic import BaseModel, Field


class ExpertResponse(BaseModel):
    item_id: str
    round: int = Field(ge=1)
    expert_id: str
    clarification_question: str | None = None
    facilitator_answer: str | None = None
    rating: int = Field(ge=1, le=9)
    category: str
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)


@dataclass(frozen=True)
class FinalizationStats:
    winning_category: str
    median_rating: float
    votes: dict[str, int]


def compute_median_rating(responses: list[ExpertResponse]) -> float:
    ratings = [response.rating for response in responses]
    if not ratings:
        raise ValueError("responses must not be empty")
    return float(median(ratings))
