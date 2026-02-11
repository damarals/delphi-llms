from delphi_llms.delphi.stopping import has_full_convergence, should_stop


def test_has_full_convergence_when_all_categories_match() -> None:
    categories = ["include", "include", "include", "include", "include"]
    assert has_full_convergence(categories) is True


def test_should_stop_when_max_round_reached_without_convergence() -> None:
    categories = ["include", "exclude", "maybe", "include", "exclude"]
    decision = should_stop(categories=categories, current_round=10, n_max=10)
    assert decision.stop is True
    assert decision.reason == "max_rounds_reached"
