import json
from pathlib import Path

import pandas as pd

from delphi_llms.data.loader import parse_round_results_xlsx


def classify_human_category(agreement_inclusion: float, agreement_exclusion: float) -> str:
    if agreement_inclusion >= 0.75 and agreement_exclusion < 0.75:
        return "include"
    if agreement_exclusion >= 0.75 and agreement_inclusion < 0.75:
        return "exclude"
    return "maybe"


def load_latest_run_dir(base_run_dir: Path) -> Path:
    if not base_run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {base_run_dir}")
    candidates = [p for p in base_run_dir.iterdir() if p.is_dir() and p.name.startswith("run-")]
    if not candidates:
        raise FileNotFoundError(f"No run-* directories found under: {base_run_dir}")
    return sorted(candidates)[-1]


def evaluate_run_against_human(
    *,
    run_dir: Path,
    round2_results_path: Path,
) -> dict:
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Run summary not found: {summary_path}")
    item_results = json.loads(summary_path.read_text(encoding="utf-8"))
    llm_df = pd.DataFrame(item_results)

    _, human_summary = parse_round_results_xlsx(round2_results_path, round_number=2)
    human_df = human_summary.copy()
    human_df["human_category"] = human_df.apply(
        lambda r: classify_human_category(
            float(r["agreement_inclusion"]),
            float(r["agreement_exclusion"]),
        ),
        axis=1,
    )

    merged = llm_df.merge(
        human_df[
            [
                "item_text",
                "human_category",
                "median",
                "agreement_inclusion",
                "agreement_exclusion",
            ]
        ],
        on="item_text",
        how="left",
        suffixes=("_llm", "_human"),
    )
    merged["decision_match"] = merged["final_category"] == merged["human_category"]
    merged["abs_median_error"] = (merged["final_median"] - merged["median"]).abs()
    merged["abs_agreement_inclusion_error"] = (
        merged["final_agreement_inclusion"] - merged["agreement_inclusion"]
    ).abs()
    merged["abs_agreement_exclusion_error"] = (
        merged["final_agreement_exclusion"] - merged["agreement_exclusion"]
    ).abs()

    total = int(len(merged))
    matched = int(merged["decision_match"].sum())
    summary = {
        "run_dir": str(run_dir),
        "items_evaluated": total,
        "decision_matches": matched,
        "decision_match_ratio": (matched / total) if total else 0.0,
        "mean_abs_median_error": float(merged["abs_median_error"].mean()) if total else 0.0,
        "mean_abs_agreement_inclusion_error": (
            float(merged["abs_agreement_inclusion_error"].mean()) if total else 0.0
        ),
        "mean_abs_agreement_exclusion_error": (
            float(merged["abs_agreement_exclusion_error"].mean()) if total else 0.0
        ),
    }
    return {"summary": summary, "items": merged}
