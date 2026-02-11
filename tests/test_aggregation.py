from delphi_llms.delphi.aggregation import finalize_category
from delphi_llms.models import ExpertResponse


def _response(expert_id: str, category: str, rating: int) -> ExpertResponse:
    return ExpertResponse(
        item_id="item-1",
        round=10,
        expert_id=expert_id,
        clarification_question=None,
        facilitator_answer=None,
        rating=rating,
        category=category,
        rationale="test",
        confidence=0.7,
    )


def test_finalize_category_uses_majority_vote() -> None:
    responses = [
        _response("e1", "include", 8),
        _response("e2", "include", 7),
        _response("e3", "exclude", 2),
        _response("e4", "include", 9),
        _response("e5", "exclude", 3),
    ]
    assert finalize_category(responses) == "include"


def test_finalize_category_uses_median_tiebreak() -> None:
    responses = [
        _response("e1", "include", 8),
        _response("e2", "include", 8),
        _response("e3", "exclude", 8),
        _response("e4", "exclude", 8),
    ]
    assert finalize_category(responses) == "include"
