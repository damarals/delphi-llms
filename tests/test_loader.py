import math

import pandas as pd

from delphi_llms.data.loader import parse_dataset_sheet


def test_parse_dataset_sheet_builds_ratings_and_summary() -> None:
    df = pd.DataFrame(
        [
            ["Experts", "Safety", math.nan, "Recognition"],
            [math.nan, "Q1", "Q2", "Q3"],
            ["Anonymised expert", 9, 8, 7],
            ["Anonymised expert", 7, 6, 5],
            ["Min", 7, 6, 5],
            ["Max", 9, 8, 7],
            ["Median", 8, 7, 6],
            ["AGREEMENT_INCLUSION", 1.0, 0.5, 0.0],
            ["AGREEMENT_EXCLUSION", 0.0, 0.0, 0.5],
            [math.nan, math.nan, math.nan, math.nan],
            ["Comments summary", "c1", "c2", "c3"],
        ]
    )

    ratings_long, item_summary = parse_dataset_sheet(df, round_number=1)

    assert len(ratings_long) == 6
    assert ratings_long["expert_seq"].nunique() == 2
    assert ratings_long["item_domain"].tolist()[:3] == ["Safety", "Safety", "Recognition"]

    assert len(item_summary) == 3
    row_q2 = item_summary[item_summary["item_text"] == "Q2"].iloc[0]
    assert row_q2["min"] == 6
    assert row_q2["max"] == 8
    assert row_q2["median"] == 7
    assert row_q2["agreement_inclusion"] == 0.5
    assert row_q2["agreement_exclusion"] == 0.0
    assert row_q2["comments_summary"] == "c2"


def test_parse_dataset_sheet_requires_expected_stat_rows() -> None:
    df = pd.DataFrame(
        [
            ["Experts", "Safety"],
            [math.nan, "Q1"],
            ["Anonymised expert", 9],
            ["Min", 1],
            ["Max", 9],
            # Missing "Median" row
            ["AGREEMENT_INCLUSION", 1.0],
            ["AGREEMENT_EXCLUSION", 0.0],
        ]
    )

    try:
        parse_dataset_sheet(df, round_number=1)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Missing required summary row" in str(exc)
