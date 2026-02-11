from pathlib import Path

import typer

from delphi_llms.config import load_yaml
from delphi_llms.data.loader import parse_round_results_xlsx


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
    _ensure_config_exists(config)
    typer.echo(f"experiment run stub: {config}")


@evaluate_app.command("run")
def evaluate_run(config: Path = typer.Option(..., exists=False)) -> None:
    _ensure_config_exists(config)
    typer.echo(f"evaluation run stub: {config}")


@export_app.command("sqlite")
def export_sqlite(config: Path = typer.Option(..., exists=False)) -> None:
    _ensure_config_exists(config)
    typer.echo(f"sqlite export stub: {config}")
