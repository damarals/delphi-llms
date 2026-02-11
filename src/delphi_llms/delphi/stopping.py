from dataclasses import dataclass


@dataclass(frozen=True)
class StopDecision:
    stop: bool
    reason: str


def has_full_convergence(categories: list[str]) -> bool:
    if not categories:
        return False
    return len(set(categories)) == 1


def should_stop(categories: list[str], current_round: int, n_max: int) -> StopDecision:
    if has_full_convergence(categories):
        return StopDecision(stop=True, reason="converged")
    if current_round >= n_max:
        return StopDecision(stop=True, reason="max_rounds_reached")
    return StopDecision(stop=False, reason="continue")
