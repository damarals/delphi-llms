from pathlib import Path

from typer.testing import CliRunner

from delphi_llms.cli import app


def test_dataset_validate_succeeds_with_required_paths(tmp_path: Path, monkeypatch) -> None:
    round1 = tmp_path / "round1.xlsx"
    round2 = tmp_path / "round2.xlsx"
    round1.write_text("x", encoding="utf-8")
    round2.write_text("x", encoding="utf-8")

    config = tmp_path / "experiment.yaml"
    config.write_text(
        "\n".join(
            [
                "dataset_paths:",
                f"  round1_results: {round1}",
                f"  round2_results: {round2}",
            ]
        ),
        encoding="utf-8",
    )

    def fake_parse(path: Path, round_number: int):  # type: ignore[no-untyped-def]
        import pandas as pd

        ratings = pd.DataFrame({"expert_seq": [1, 2, 1, 2], "rating": [7, 8, 6, 9]})
        summary = pd.DataFrame({"item_text": ["q1", "q2"]})
        return ratings, summary

    monkeypatch.setattr("delphi_llms.cli.parse_round_results_xlsx", fake_parse)

    result = CliRunner().invoke(app, ["dataset", "validate", "--config", str(config)])
    assert result.exit_code == 0
    assert "round 1: experts=2 items=2 ratings=4" in result.stdout
    assert "round 2: experts=2 items=2 ratings=4" in result.stdout


def test_dataset_validate_fails_when_required_key_is_missing(tmp_path: Path) -> None:
    config = tmp_path / "experiment.yaml"
    config.write_text("dataset_paths:\n  round1_results: data/raw/r1.xlsx\n", encoding="utf-8")

    result = CliRunner().invoke(app, ["dataset", "validate", "--config", str(config)])
    assert result.exit_code == 1
    assert "Missing required config key" in result.stdout
