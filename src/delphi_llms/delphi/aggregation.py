from collections import Counter
from statistics import median

from delphi_llms.models import ExpertResponse


def finalize_category(responses: list[ExpertResponse]) -> str:
    if not responses:
        raise ValueError("responses must not be empty")

    votes = Counter(response.category for response in responses)
    top_count = max(votes.values())
    top_categories = sorted([category for category, count in votes.items() if count == top_count])

    if len(top_categories) == 1:
        return top_categories[0]

    # Tie-break rule: highest category-specific median wins.
    category_medians = {
        category: float(median([r.rating for r in responses if r.category == category]))
        for category in top_categories
    }
    best_median = max(category_medians.values())
    median_tied = sorted([c for c, value in category_medians.items() if value == best_median])
    if len(median_tied) == 1:
        return median_tied[0]

    # Deterministic fallback aligned with expected decision strictness.
    priority = {"include": 3, "maybe": 2, "exclude": 1}
    return sorted(median_tied, key=lambda c: (-priority.get(c, 0), c))[0]
