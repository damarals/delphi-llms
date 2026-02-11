# Repository Guidelines

## Project Structure & Module Organization

This repository is currently documentation-first. All agreed design decisions live in `docs/`.

- `docs/README.md`: documentation index
- `docs/01-06-*.md`: context, experimental design, architecture, data/evaluation, devcontainer, implementation plan

Implementation is planned under:

- `src/delphi_llms/`: Python package (data loading, agents, Delphi engine, evaluation, visualization)
- `tests/`: unit/integration tests
- `.devcontainer/`: reproducible development environment (`uv` + Ollama)

Use this structure when adding code; do not place runtime logic inside `docs/`.

## Build, Test, and Development Commands

The code scaffold is not yet committed. Use these standard commands once `pyproject.toml` and the package are added:

- `uv sync --locked`: install dependencies from lockfile
- `uv run pytest`: run test suite
- `uv run ruff check .`: lint code
- `uv run ruff format .`: format code
- `uv run python -m delphi_llms.cli --help`: inspect CLI entrypoints

If using devcontainer:

- `Dev Containers: Reopen in Container` (VS Code)
- Verify Ollama with `ollama list`

## Coding Style & Naming Conventions

- Language: Python 3.12+
- Indentation: 4 spaces; UTF-8; keep files ASCII unless required
- Names: `snake_case` for functions/modules, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- Keep prompts, schemas, and stopping rules explicit and versioned
- Prefer small, testable modules over large workflow files

## Testing Guidelines

- Framework: `pytest`
- Test files: `tests/test_<module>.py`
- Cover core experimental logic first:
  - aggregation
  - convergence/stopping
  - majority fallback and tie-break
  - schema validation for expert outputs

Add one end-to-end smoke test for a tiny item subset.

## Commit & Pull Request Guidelines

No stable commit history is available yet; adopt Conventional Commits:

- `feat: add delphi stopping criteria`
- `fix: handle category tie-break by median`
- `docs: update experimental design`

PRs should include:

1. Scope summary and rationale
2. Linked issue (if any)
3. Test evidence (`pytest`/lint output)
4. Notes on config changes (models, seeds, `OLLAMA_HOST`)

## Security & Configuration Tips

- Never commit secrets or local tokens.
- Keep model/runtime settings in environment variables and checked-in example configs.
- Avoid leaking human ground-truth labels into facilitator context during recursive runs.

