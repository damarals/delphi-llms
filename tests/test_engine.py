from delphi_llms.delphi.engine import run_recursive_delphi, run_standard_delphi


def test_run_standard_delphi_stops_on_first_round_convergence() -> None:
    items = [{"item_id": "i1", "item_text": "Item 1"}]
    expert_ids = ["e1", "e2", "e3", "e4", "e5"]

    def fake_call(*, item_id: str, item_text: str, round_number: int, expert_id: str, seed: int):  # type: ignore[no-untyped-def]
        return {"rating": 8, "category": "include", "rationale": "ok", "confidence": 0.8}

    result = run_standard_delphi(
        items=items,
        expert_seeds=[11, 22, 33, 44, 55],
        n_max=10,
        call_expert=fake_call,
        expert_ids=expert_ids,
    )

    assert len(result["item_results"]) == 1
    item = result["item_results"][0]
    assert item["final_category"] == "include"
    assert item["stop_reason"] == "converged"
    assert item["rounds_run"] == 1


def test_run_standard_delphi_uses_fallback_when_no_convergence() -> None:
    items = [{"item_id": "i1", "item_text": "Item 1"}]
    expert_ids = ["e1", "e2", "e3", "e4", "e5"]

    def fake_call(*, item_id: str, item_text: str, round_number: int, expert_id: str, seed: int):  # type: ignore[no-untyped-def]
        if expert_id in {"e1", "e2", "e3"}:
            return {"rating": 8, "category": "include", "rationale": "ok", "confidence": 0.7}
        return {"rating": 2, "category": "exclude", "rationale": "ok", "confidence": 0.7}

    result = run_standard_delphi(
        items=items,
        expert_seeds=[11, 22, 33, 44, 55],
        n_max=1,
        call_expert=fake_call,
        expert_ids=expert_ids,
    )

    item = result["item_results"][0]
    assert item["stop_reason"] == "max_rounds_reached"
    assert item["final_category"] == "include"


def test_run_recursive_delphi_includes_clarification_fields() -> None:
    items = [{"item_id": "i1", "item_text": "Item 1"}]
    expert_ids = ["e1", "e2", "e3", "e4", "e5"]

    def ask(*, item_id: str, item_text: str, round_number: int, expert_id: str, seed: int) -> str:  # type: ignore[no-untyped-def]
        return f"q-{expert_id}"

    def fac(  # type: ignore[no-untyped-def]
        *, item_id: str, item_text: str, round_number: int, expert_id: str, clarification_question: str
    ) -> str:
        return f"a-{clarification_question}"

    def final(  # type: ignore[no-untyped-def]
        *,
        item_id: str,
        item_text: str,
        round_number: int,
        expert_id: str,
        seed: int,
        clarification_question: str,
        facilitator_answer: str,
    ):
        return {"rating": 8, "category": "include", "rationale": "ok", "confidence": 0.8}

    result = run_recursive_delphi(
        items=items,
        expert_seeds=[11, 22, 33, 44, 55],
        n_max=10,
        ask_expert_clarification=ask,
        call_facilitator=fac,
        call_expert_with_clarification=final,
        expert_ids=expert_ids,
    )

    responses = [e for e in result["event_log"] if e.get("type") == "expert_response"]
    assert responses
    assert all(r.get("clarification_question") for r in responses)
    assert all(r.get("facilitator_answer") for r in responses)
