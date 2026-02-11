from pathlib import Path

import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def parse_round_results_xlsx(path: Path, round_number: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    dataset_sheet = pd.read_excel(path, sheet_name="Dataset", header=None)
    return parse_dataset_sheet(dataset_sheet, round_number=round_number)


def parse_dataset_sheet(dataset_sheet: pd.DataFrame, round_number: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    labels = dataset_sheet[0].astype(str).str.strip()
    lower_labels = labels.str.lower()

    expert_rows = dataset_sheet.index[lower_labels == "anonymised expert"].tolist()
    if not expert_rows:
        raise ValueError("No expert rows found in Dataset sheet.")

    required_summary_rows = {
        "min": "Min",
        "max": "Max",
        "median": "Median",
        "agreement_inclusion": "AGREEMENT_INCLUSION",
        "agreement_exclusion": "AGREEMENT_EXCLUSION",
    }

    summary_row_index: dict[str, int] = {}
    for key, label in required_summary_rows.items():
        matches = dataset_sheet.index[labels == label].tolist()
        if not matches:
            raise ValueError(f"Missing required summary row: {label}")
        summary_row_index[key] = matches[0]

    comments_matches = dataset_sheet.index[labels == "Comments summary"].tolist()
    comments_row_index = comments_matches[0] if comments_matches else None

    domain_row = dataset_sheet.iloc[0, :]
    item_text_row = dataset_sheet.iloc[1, :]
    item_columns = [
        col
        for col in range(1, dataset_sheet.shape[1])
        if pd.notna(item_text_row.iloc[col]) and str(item_text_row.iloc[col]).strip()
    ]

    domains = domain_row.ffill()
    item_meta = pd.DataFrame(
        {
            "item_col": item_columns,
            "item_domain": [str(domains.iloc[col]).strip() for col in item_columns],
            "item_text": [str(item_text_row.iloc[col]).strip() for col in item_columns],
        }
    )

    ratings_records: list[dict] = []
    for expert_seq, row_idx in enumerate(expert_rows, start=1):
        for item_col in item_columns:
            rating = pd.to_numeric(dataset_sheet.iloc[row_idx, item_col], errors="coerce")
            if pd.isna(rating):
                continue
            meta = item_meta[item_meta["item_col"] == item_col].iloc[0]
            ratings_records.append(
                {
                    "round": round_number,
                    "expert_seq": expert_seq,
                    "expert_label": "Anonymised expert",
                    "row_idx": row_idx,
                    "item_col": item_col,
                    "item_domain": meta["item_domain"],
                    "item_text": meta["item_text"],
                    "rating": int(rating),
                }
            )

    ratings_long = pd.DataFrame(ratings_records)

    summary_records: list[dict] = []
    for item_col in item_columns:
        meta = item_meta[item_meta["item_col"] == item_col].iloc[0]
        summary_records.append(
            {
                "round": round_number,
                "item_col": item_col,
                "item_domain": meta["item_domain"],
                "item_text": meta["item_text"],
                "min": pd.to_numeric(dataset_sheet.iloc[summary_row_index["min"], item_col], errors="coerce"),
                "max": pd.to_numeric(dataset_sheet.iloc[summary_row_index["max"], item_col], errors="coerce"),
                "median": pd.to_numeric(
                    dataset_sheet.iloc[summary_row_index["median"], item_col], errors="coerce"
                ),
                "agreement_inclusion": pd.to_numeric(
                    dataset_sheet.iloc[summary_row_index["agreement_inclusion"], item_col], errors="coerce"
                ),
                "agreement_exclusion": pd.to_numeric(
                    dataset_sheet.iloc[summary_row_index["agreement_exclusion"], item_col], errors="coerce"
                ),
                "comments_summary": (
                    str(dataset_sheet.iloc[comments_row_index, item_col]).strip()
                    if comments_row_index is not None and pd.notna(dataset_sheet.iloc[comments_row_index, item_col])
                    else None
                ),
            }
        )

    item_summary = pd.DataFrame(summary_records)
    return ratings_long, item_summary
