import pytest
from pydantic import ValidationError

from delphi_llms.models import ExpertResponse


def test_expert_response_accepts_valid_payload() -> None:
    payload = {
        "item_id": "item-1",
        "round": 1,
        "expert_id": "expert-1",
        "clarification_question": None,
        "facilitator_answer": None,
        "rating": 7,
        "category": "include",
        "rationale": "Clear relevance to scope.",
        "confidence": 0.8,
    }
    response = ExpertResponse.model_validate(payload)
    assert response.rating == 7


def test_expert_response_rejects_invalid_rating() -> None:
    payload = {
        "item_id": "item-1",
        "round": 1,
        "expert_id": "expert-1",
        "clarification_question": None,
        "facilitator_answer": None,
        "rating": 10,
        "category": "include",
        "rationale": "Invalid rating for this scale.",
        "confidence": 0.8,
    }
    with pytest.raises(ValidationError):
        ExpertResponse.model_validate(payload)
