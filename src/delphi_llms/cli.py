from pathlib import Path
import json
import os
from datetime import UTC, datetime

import typer

from delphi_llms.agents.ollama import call_ollama_expert, ensure_model_available
from delphi_llms.config import load_yaml
from delphi_llms.data.loader import parse_round_results_xlsx
from delphi_llms.delphi.engine import run_standard_delphi


app = typer.Typer(help="Delphi LLM experiments CLI.")
dataset_app = typer.Typer(help="Dataset operations.")
experiment_app = typer.Typer(help="Experiment operations.")
evaluate_app = typer.Typer(help="Evaluation operations.")
export_app = typer.Typer(help="Export operations.")

app.add_typer(dataset_app, name="dataset")
app.add_typer(experiment_app, name="experiment")
app.add_typer(evaluate_app, name="evaluate")
app.add_typer(export_app, name="export")


def _ensure_config_exists(config: Path) -> None:
    if not config.exists():
        raise typer.BadParameter(f"Config file not found: {config}")


def _required_path(config_data: dict, dotted_key: str) -> Path:
    cursor = config_data
    for key in dotted_key.split("."):
        if not isinstance(cursor, dict) or key not in cursor:
            raise typer.BadParameter(f"Missing required config key: {dotted_key}")
        cursor = cursor[key]
    if not isinstance(cursor, str) or not cursor.strip():
        raise typer.BadParameter(f"Invalid path value for key: {dotted_key}")
    return Path(cursor)


@dataset_app.command("validate")
def dataset_validate(config: Path = typer.Option(..., exists=False)) -> None:
    try:
        _ensure_config_exists(config)
        config_data = load_yaml(config)
        round1_path = _required_path(config_data, "dataset_paths.round1_results")
        round2_path = _required_path(config_data, "dataset_paths.round2_results")

        if not round1_path.exists():
            raise typer.BadParameter(f"Round 1 results file not found: {round1_path}")
        if not round2_path.exists():
            raise typer.BadParameter(f"Round 2 results file not found: {round2_path}")

        r1_ratings, r1_summary = parse_round_results_xlsx(round1_path, round_number=1)
        r2_ratings, r2_summary = parse_round_results_xlsx(round2_path, round_number=2)

        typer.echo(f"dataset config ok: {config}")
        typer.echo(
            f"round 1: experts={r1_ratings['expert_seq'].nunique()} "
            f"items={len(r1_summary)} ratings={len(r1_ratings)}"
        )
        typer.echo(
            f"round 2: experts={r2_ratings['expert_seq'].nunique()} "
            f"items={len(r2_summary)} ratings={len(r2_ratings)}"
        )
    except typer.BadParameter as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc


@experiment_app.command("run")
def experiment_run(config: Path = typer.Option(..., exists=False)) -> None:
    try:
        _ensure_config_exists(config)
        config_data = load_yaml(config)
        mode = str(config_data.get("mode", "standard")).strip().lower()
        if mode != "standard":
            raise typer.BadParameter("Only mode=standard is implemented in this increment.")

        model = str(config_data.get("model", "")).strip()
        if not model:
            raise typer.BadParameter("Missing required config key: model")

        n_max = int(config_data.get("n_max", 10))
        expert_seeds = list(config_data.get("experts", {}).get("seeds", []))
        if not expert_seeds:
            raise typer.BadParameter("Missing required config key: experts.seeds")

        smoke_limit = int(config_data.get("smoke", {}).get("limit", 5))
        round1_path = _required_path(config_data, "dataset_paths.round1_results")
        if not round1_path.exists():
            raise typer.BadParameter(f"Round 1 results file not found: {round1_path}")

        _, round1_summary = parse_round_results_xlsx(round1_path, round_number=1)
        items = (
            round1_summary[["item_col", "item_text"]]
            .rename(columns={"item_col": "item_id"})
            .head(smoke_limit)
            .to_dict(orient="records")
        )
        if not items:
            raise typer.BadParameter("No items loaded from round 1 summary.")

        ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        try:
            ensure_model_available(ollama_host=ollama_host, model=model)
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc

        run_data = run_standard_delphi(
            items=items,
            expert_seeds=expert_seeds,
            n_max=n_max,
            call_expert=lambda **kwargs: call_ollama_expert(  # noqa: E731
                model=model,
                ollama_host=ollama_host,
                **kwargs,
            ),
        )

        run_dir = Path(config_data.get("outputs", {}).get("run_dir", "runs/latest"))
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        output_dir = run_dir / f"run-{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        events_path = output_dir / "events.jsonl"
        with events_path.open("w", encoding="utf-8") as handle:
            for event in run_data["event_log"]:
                handle.write(json.dumps(event, ensure_ascii=True) + "\n")

        summary_path = output_dir / "summary.json"
        with summary_path.open("w", encoding="utf-8") as handle:
            json.dump(run_data["item_results"], handle, ensure_ascii=True, indent=2)

        typer.echo(f"experiment run complete: {output_dir}")
        typer.echo(f"events: {events_path}")
        typer.echo(f"summary: {summary_path}")
    except typer.BadParameter as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc


@evaluate_app.command("run")
def evaluate_run(config: Path = typer.Option(..., exists=False)) -> None:
    _ensure_config_exists(config)
    typer.echo(f"evaluation run stub: {config}")


@export_app.command("sqlite")
def export_sqlite(config: Path = typer.Option(..., exists=False)) -> None:
    _ensure_config_exists(config)
    typer.echo(f"sqlite export stub: {config}")
