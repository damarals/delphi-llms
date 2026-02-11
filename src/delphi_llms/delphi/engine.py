from concurrent.futures import ThreadPoolExecutor
from statistics import median
from typing import Callable

from delphi_llms.delphi.aggregation import finalize_category
from delphi_llms.delphi.stopping import should_stop
from delphi_llms.models import ExpertResponse


def _build_response(
    *,
    item_id: str,
    round_number: int,
    expert_id: str,
    payload: dict,
) -> ExpertResponse:
    return ExpertResponse(
        item_id=item_id,
        round=round_number,
        expert_id=expert_id,
        clarification_question=None,
        facilitator_answer=None,
        rating=int(payload["rating"]),
        category=str(payload["category"]),
        rationale=str(payload.get("rationale", "")),
        confidence=float(payload.get("confidence", 0.5)),
    )


def _round_metrics(responses: list[ExpertResponse]) -> dict:
    ratings = [r.rating for r in responses]
    n = len(ratings)
    agreement_inclusion = sum(1 for r in ratings if r >= 7) / n if n else 0.0
    agreement_exclusion = sum(1 for r in ratings if r <= 3) / n if n else 0.0
    return {
        "median": float(median(ratings)) if ratings else 0.0,
        "agreement_inclusion": float(agreement_inclusion),
        "agreement_exclusion": float(agreement_exclusion),
    }


def run_standard_delphi(
    *,
    items: list[dict],
    expert_seeds: list[int],
    n_max: int,
    call_expert: Callable[..., dict],
    expert_ids: list[str] | None = None,
) -> dict:
    if not items:
        raise ValueError("items must not be empty")
    if not expert_seeds:
        raise ValueError("expert_seeds must not be empty")

    if expert_ids is None:
        expert_ids = [f"expert_{idx+1}" for idx in range(len(expert_seeds))]
    if len(expert_ids) != len(expert_seeds):
        raise ValueError("expert_ids and expert_seeds must have the same length")

    item_results: list[dict] = []
    event_log: list[dict] = []

    for item in items:
        item_id = str(item["item_id"])
        item_text = str(item["item_text"])
        stop_reason = "max_rounds_reached"
        final_category = None
        rounds_run = 0
        final_metrics = {"median": None, "agreement_inclusion": None, "agreement_exclusion": None}

        for round_number in range(1, n_max + 1):
            rounds_run = round_number

            with ThreadPoolExecutor(max_workers=len(expert_ids)) as pool:
                futures = [
                    pool.submit(
                        call_expert,
                        item_id=item_id,
                        item_text=item_text,
                        round_number=round_number,
                        expert_id=expert_id,
                        seed=seed,
                    )
                    for expert_id, seed in zip(expert_ids, expert_seeds, strict=True)
                ]
                payloads = [future.result() for future in futures]

            responses = [
                _build_response(
                    item_id=item_id,
                    round_number=round_number,
                    expert_id=expert_id,
                    payload=payload,
                )
                for expert_id, payload in zip(expert_ids, payloads, strict=True)
            ]
            categories = [response.category for response in responses]
            decision = should_stop(categories=categories, current_round=round_number, n_max=n_max)
            metrics = _round_metrics(responses)

            for response in responses:
                event_log.append({"type": "expert_response", **response.model_dump()})
            event_log.append(
                {
                    "type": "round_summary",
                    "item_id": item_id,
                    "round": round_number,
                    "categories": categories,
                    "stop": decision.stop,
                    "reason": decision.reason,
                    **metrics,
                }
            )

            if decision.stop:
                stop_reason = decision.reason
                final_category = (
                    categories[0] if decision.reason == "converged" else finalize_category(responses)
                )
                final_metrics = metrics
                break

        if final_category is None:
            raise RuntimeError("failed to finalize category")

        item_results.append(
            {
                "item_id": item_id,
                "item_text": item_text,
                "final_category": final_category,
                "stop_reason": stop_reason,
                "rounds_run": rounds_run,
                "final_median": final_metrics["median"],
                "final_agreement_inclusion": final_metrics["agreement_inclusion"],
                "final_agreement_exclusion": final_metrics["agreement_exclusion"],
            }
        )

    return {"item_results": item_results, "event_log": event_log}


def run_recursive_delphi(
    *,
    items: list[dict],
    expert_seeds: list[int],
    n_max: int,
    ask_expert_clarification: Callable[..., str],
    call_facilitator: Callable[..., str],
    call_expert_with_clarification: Callable[..., dict],
    expert_ids: list[str] | None = None,
) -> dict:
    if not items:
        raise ValueError("items must not be empty")
    if not expert_seeds:
        raise ValueError("expert_seeds must not be empty")

    if expert_ids is None:
        expert_ids = [f"expert_{idx+1}" for idx in range(len(expert_seeds))]
    if len(expert_ids) != len(expert_seeds):
        raise ValueError("expert_ids and expert_seeds must have the same length")

    item_results: list[dict] = []
    event_log: list[dict] = []

    for item in items:
        item_id = str(item["item_id"])
        item_text = str(item["item_text"])
        stop_reason = "max_rounds_reached"
        final_category = None
        rounds_run = 0
        final_metrics = {"median": None, "agreement_inclusion": None, "agreement_exclusion": None}

        for round_number in range(1, n_max + 1):
            rounds_run = round_number

            def _expert_one(expert_id: str, seed: int) -> ExpertResponse:
                question = ask_expert_clarification(
                    item_id=item_id,
                    item_text=item_text,
                    round_number=round_number,
                    expert_id=expert_id,
                    seed=seed,
                )
                answer = call_facilitator(
                    item_id=item_id,
                    item_text=item_text,
                    round_number=round_number,
                    expert_id=expert_id,
                    clarification_question=question,
                )
                payload = call_expert_with_clarification(
                    item_id=item_id,
                    item_text=item_text,
                    round_number=round_number,
                    expert_id=expert_id,
                    seed=seed,
                    clarification_question=question,
                    facilitator_answer=answer,
                )
                return ExpertResponse(
                    item_id=item_id,
                    round=round_number,
                    expert_id=expert_id,
                    clarification_question=question,
                    facilitator_answer=answer,
                    rating=int(payload["rating"]),
                    category=str(payload["category"]),
                    rationale=str(payload.get("rationale", "")),
                    confidence=float(payload.get("confidence", 0.5)),
                )

            with ThreadPoolExecutor(max_workers=len(expert_ids)) as pool:
                futures = [
                    pool.submit(_expert_one, expert_id, seed)
                    for expert_id, seed in zip(expert_ids, expert_seeds, strict=True)
                ]
                responses = [future.result() for future in futures]

            categories = [response.category for response in responses]
            decision = should_stop(categories=categories, current_round=round_number, n_max=n_max)
            metrics = _round_metrics(responses)

            for response in responses:
                event_log.append({"type": "expert_response", **response.model_dump()})
            event_log.append(
                {
                    "type": "round_summary",
                    "item_id": item_id,
                    "round": round_number,
                    "categories": categories,
                    "stop": decision.stop,
                    "reason": decision.reason,
                    **metrics,
                }
            )

            if decision.stop:
                stop_reason = decision.reason
                final_category = (
                    categories[0] if decision.reason == "converged" else finalize_category(responses)
                )
                final_metrics = metrics
                break

        if final_category is None:
            raise RuntimeError("failed to finalize category")

        item_results.append(
            {
                "item_id": item_id,
                "item_text": item_text,
                "final_category": final_category,
                "stop_reason": stop_reason,
                "rounds_run": rounds_run,
                "final_median": final_metrics["median"],
                "final_agreement_inclusion": final_metrics["agreement_inclusion"],
                "final_agreement_exclusion": final_metrics["agreement_exclusion"],
            }
        )

    return {"item_results": item_results, "event_log": event_log}
