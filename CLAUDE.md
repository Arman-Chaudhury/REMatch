# REMatch (Property Watch)

Watches the Nassau County assessment roll for changes at addresses people care about and emails them.
Python package in `property_watch/`, Postgres schema in `schema.sql`, tests in `tests/` (pure functions, no database needed).

## Run checks
```
uv venv -p 3.12 .venv && uv pip install -p .venv/bin/python -r requirements.txt ruff
.venv/bin/python -m pytest tests -q
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```
Use the project-local `.venv` only. Never install globally. The old `venv/` folder is broken and ignored.
CI (.github/workflows/ci.yml) runs ruff check, ruff format --check and pytest on every push and PR. Live data (data.ny.gov, the Land Records Viewer, email sending) must never be hit from tests.

## Agent fleet
Before any work, read DIRECTION.md at the repo root and follow its rules. Proposals and logs go there, never in commits to main.
