import json
import sqlite3
from pathlib import Path

from delphi_llms.eval.compare import load_latest_run_dir


def export_latest_run_to_sqlite(*, base_run_dir: Path, sqlite_path: Path) -> Path:
    run_dir = load_latest_run_dir(base_run_dir)
    events_path = run_dir / "events.jsonl"
    summary_path = run_dir / "summary.json"
    evaluation_summary_path = run_dir / "evaluation_summary.json"
    evaluation_items_path = run_dir / "evaluation_items.csv"

    if not events_path.exists():
        raise FileNotFoundError(f"events file not found: {events_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"summary file not found: {summary_path}")

    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(sqlite_path)
    try:
        conn.execute("drop table if exists run_events")
        conn.execute("drop table if exists run_summary")
        conn.execute("drop table if exists eval_summary")
        conn.execute("drop table if exists eval_items")

        conn.execute(
            """
            create table run_events (
              type text,
              item_id text,
              round integer,
              expert_id text,
              rating real,
              category text,
              rationale text,
              confidence real,
              clarification_question text,
              facilitator_answer text,
              stop integer,
              reason text,
              categories_json text,
              median real,
              agreement_inclusion real,
              agreement_exclusion real
            )
            """
        )
        conn.execute(
            """
            create table run_summary (
              item_id text,
              item_text text,
              final_category text,
              stop_reason text,
              rounds_run integer,
              final_median real,
              final_agreement_inclusion real,
              final_agreement_exclusion real
            )
            """
        )

        with events_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                conn.execute(
                    """
                    insert into run_events (
                      type, item_id, round, expert_id, rating, category, rationale, confidence,
                      clarification_question, facilitator_answer, stop, reason, categories_json,
                      median, agreement_inclusion, agreement_exclusion
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row.get("type"),
                        row.get("item_id"),
                        row.get("round"),
                        row.get("expert_id"),
                        row.get("rating"),
                        row.get("category"),
                        row.get("rationale"),
                        row.get("confidence"),
                        row.get("clarification_question"),
                        row.get("facilitator_answer"),
                        1 if row.get("stop") else 0 if "stop" in row else None,
                        row.get("reason"),
                        json.dumps(row.get("categories")) if row.get("categories") is not None else None,
                        row.get("median"),
                        row.get("agreement_inclusion"),
                        row.get("agreement_exclusion"),
                    ),
                )

        summary_rows = json.loads(summary_path.read_text(encoding="utf-8"))
        for row in summary_rows:
            conn.execute(
                """
                insert into run_summary (
                  item_id, item_text, final_category, stop_reason, rounds_run,
                  final_median, final_agreement_inclusion, final_agreement_exclusion
                ) values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("item_id"),
                    row.get("item_text"),
                    row.get("final_category"),
                    row.get("stop_reason"),
                    row.get("rounds_run"),
                    row.get("final_median"),
                    row.get("final_agreement_inclusion"),
                    row.get("final_agreement_exclusion"),
                ),
            )

        if evaluation_summary_path.exists():
            conn.execute(
                """
                create table eval_summary (
                  run_dir text,
                  items_evaluated integer,
                  decision_matches integer,
                  decision_match_ratio real,
                  mean_abs_median_error real,
                  mean_abs_agreement_inclusion_error real,
                  mean_abs_agreement_exclusion_error real
                )
                """
            )
            row = json.loads(evaluation_summary_path.read_text(encoding="utf-8"))
            conn.execute(
                """
                insert into eval_summary values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("run_dir"),
                    row.get("items_evaluated"),
                    row.get("decision_matches"),
                    row.get("decision_match_ratio"),
                    row.get("mean_abs_median_error"),
                    row.get("mean_abs_agreement_inclusion_error"),
                    row.get("mean_abs_agreement_exclusion_error"),
                ),
            )

        if evaluation_items_path.exists():
            import pandas as pd

            df = pd.read_csv(evaluation_items_path)
            df.to_sql("eval_items", conn, if_exists="replace", index=False)

        conn.commit()
    finally:
        conn.close()

    return sqlite_path
