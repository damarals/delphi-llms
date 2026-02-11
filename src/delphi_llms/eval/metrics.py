def agreement_ratio(matches: int, total: int) -> float:
    if total <= 0:
        raise ValueError("total must be greater than zero")
    return matches / total
