# NaMo Forbidden Archive — Overview

> Starter README scaffold to clarify purpose, usage, and architecture at a glance.

## What is this?
Short descriptor of the project (1–2 sentences). State the mission and audience.

## Features
- Bullet one-liners of what the tool does
- CLI / API / Batch modes (if applicable)
- Supported inputs/outputs

## Quickstart
```bash
# 1) Create virtualenv (example)
python -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt
pip install -r requirements-dev.txt  # dev-only

# 3) Run (pick one)
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables
Copy `.env.example` to `.env` and fill values:
- `APP_ENV` = `dev` | `prod`
- `APP_PORT` = port number (e.g., 8000)
- `OPENAI_API_KEY` = if your pipelines call OpenAI
- Add other keys used by your code paths.

## Project Layout (suggested)
```text
app.py / src/
├─ core/                 # core logic (stateless)
├─ adapters/             # IO, APIs, file adapters
├─ pipelines/            # orchestrations
├─ assets/               # model/data assets (avoid large files in git)
└─ tests/                # unit/integration tests
```

## Make Targets
See `Makefile` for common ops:
- `make setup` — install dev tools
- `make lint` — ruff + black check
- `make test` — run pytest
- `make audit` — pip-audit for vulns
- `make format` — auto-format code
- `make run` — start app (env vars required)

## Architecture Sketch
See `docs/ARCHITECTURE.md` for a high-level diagram and dataflow.

## API / CLI
- Document endpoints/commands in `docs/API_SPEC.md` (add examples).

## Release & Versioning
- Use SemVer: `MAJOR.MINOR.PATCH`
- Tag releases in GitHub and attach changelog entries.

## Contributing
See `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.

## Security
Vulnerability reports: see `SECURITY.md`.

## License
Specify your project license (e.g., MIT). Link to `LICENSE`.
