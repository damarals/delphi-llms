import json
import sqlite3
from pathlib import Path

from delphi_llms.eval.export_sqlite import export_latest_run_to_sqlite


def test_export_latest_run_to_sqlite(tmp_path: Path) -> None:
    base = tmp_path / "runs"
    run = base / "run-20260101T000000Z"
    run.mkdir(parents=True)

    (run / "events.jsonl").write_text(
        json.dumps(
            {
                "type": "expert_response",
                "item_id": "1",
                "round": 1,
                "expert_id": "e1",
                "rating": 8,
                "category": "include",
                "rationale": "ok",
                "confidence": 0.8,
                "clarification_question": None,
                "facilitator_answer": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (run / "summary.json").write_text(
        json.dumps(
            [
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
        ),
        encoding="utf-8",
    )

    sqlite_path = tmp_path / "results.sqlite"
    out = export_latest_run_to_sqlite(base_run_dir=base, sqlite_path=sqlite_path)
    assert out == sqlite_path
    assert sqlite_path.exists()

    conn = sqlite3.connect(sqlite_path)
    try:
        tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
        assert "run_events" in tables
        assert "run_summary" in tables
    finally:
        conn.close()
