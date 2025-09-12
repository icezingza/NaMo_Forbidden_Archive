# Contributing Guide

Thanks for improving NaMo Forbidden Archive!

## Dev setup
1. Fork + clone
2. `make setup`
3. Create a feature branch

## Commit & PR
- Use conventional commits where possible (feat, fix, docs, chore)
- Include tests for new behavior
- Run `make precommit` before pushing
- Open a PR with a clear description and checklist

## Code style
- Python 3.11
- `ruff` + `black` enforced in CI
- Small, focused functions; avoid side-effects in core logic

## Tests
- Place under `tests/`
- Keep them fast and deterministic
- Use pytest fixtures where useful

## Security
- Never commit secrets
- Prefer environment variables and `.env`
- Report vulnerabilities via `SECURITY.md`
