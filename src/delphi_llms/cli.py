from pathlib import Path

import typer


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


@dataset_app.command("validate")
def dataset_validate(config: Path = typer.Option(..., exists=False)) -> None:
    _ensure_config_exists(config)
    typer.echo(f"dataset config ok: {config}")


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
