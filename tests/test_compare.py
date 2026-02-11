import json
from pathlib import Path

from delphi_llms.eval.compare import classify_human_category, evaluate_run_against_human


def test_classify_human_category() -> None:
    assert classify_human_category(0.8, 0.1) == "include"
    assert classify_human_category(0.2, 0.8) == "exclude"
    assert classify_human_category(0.5, 0.1) == "maybe"


def test_evaluate_run_against_human(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-20260101T000000Z"
    run_dir.mkdir(parents=True)
    summary = [
        {
            "item_id": "1",
            "item_text": "Q1",
            "final_category": "include",
            "stop_reason": "converged",
            "rounds_run": 1,
            "final_median": 8.0,
            "final_agreement_inclusion": 1.0,
            "final_agreement_exclusion": 0.0,
        }
    ]
    (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")

    # Create a small round2 file using expected structure.
    import pandas as pd

    df = pd.DataFrame(
        [
            ["Experts", "Domain"],
            [None, "Q1"],
            ["Anonymised expert", 8],
            ["Min", 8],
            ["Max", 8],
            ["Median", 8],
            ["AGREEMENT_INCLUSION", 1.0],
            ["AGREEMENT_EXCLUSION", 0.0],
        ]
    )
    round2 = tmp_path / "r2.xlsx"
    with pd.ExcelWriter(round2, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Dataset", index=False, header=False)

    result = evaluate_run_against_human(run_dir=run_dir, round2_results_path=round2)
    assert result["summary"]["items_evaluated"] == 1
    assert result["summary"]["decision_matches"] == 1
