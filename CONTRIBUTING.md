# Contributing to NamoNexus ACC

Thank you for your interest in contributing to the **NamoNexus Advanced Conversational Core**.

**Brand:** NamoNexus  
**Author:** Kanin Raksaraj  
**Contact:** [contact@namonexus.com](mailto:contact@namonexus.com)

---

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Follow the [Installation Guide](Documentation/INSTALL_GUIDE.md) to set up your environment
4. Create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

---

## Branch Naming Convention

| Prefix | Purpose |
|---|---|
| `feature/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation updates |
| `refactor/` | Code refactoring |
| `chore/` | Maintenance tasks |

---

## Code Standards

- **Language:** Python 3.11+
- **Style:** `ruff` + `black` enforced in CI
- **Type hints:** Required for all public functions and methods
- **Docstrings:** Required for all classes and public methods
- **Tests:** Add or update tests for any changed functionality
- Small, focused functions; avoid side-effects in core logic

---

## Project Structure

```
core/               — Core cognitive engines
adapters/           — Decoupled I/O adapters (emotion, memory, TTS)
Core_Scripts/       — Telegram bot and arousal detection
docs/               — Technical documentation
Documentation/      — Installation, architecture, license
Pitch_Presentation/ — Business and investor materials
scripts/            — Evaluation and utility scripts
templates/          — Prompt and response templates
```

---

## Submitting Changes

1. Run `make precommit` before pushing
2. Ensure all tests pass: `pytest`
3. Commit with a clear message following [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add new emotion dimension`
   - `fix: resolve session TTL race condition`
   - `docs: update API reference`
4. Open a Merge Request with a clear description

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

---

## Security

- Never commit secrets or API keys
- Use environment variables and `.env`
- Report vulnerabilities via `SECURITY.md`

---

## Questions?

Contact us at [contact@namonexus.com](mailto:contact@namonexus.com)
