# Repository Guidelines

## Project Structure & Module Organization

MedAppAgent is a Python prototype for medical-school advising, ranking, and report generation. The CLI entry point is `main.py`; the Streamlit UI is `app.py`; shared settings live in `config.py`. Core code is organized by responsibility: `repositories/` loads profiles, schools, Supabase records, and reports; `validation/` checks profile and school data; `scoring/` contains academic, mission, residency, and preference scoring; `services/` orchestrates ranking, agents, AAMC context, profiles, and report persistence; `agents/` holds LLM-facing agent logic; `reports/` builds final report text; `models/` defines structured outputs. Tests are in `tests/`. Input data is under `data/`, with sample profiles in `data/student_profiles/` and cleaned datasets in `data/cleaned/`. Generated reports belong in `outputs/`.

## Build, Test, and Development Commands

- `python -m venv .venv && source .venv/bin/activate`: create and activate a local environment.
- `pip install -r requirements.txt`: install dependencies when the requirements manifest is present.
- `python main.py data/student_profiles/student1_profile.json --skip-agents`: run the full local pipeline without API calls.
- `python main.py data/student_profiles/student1_profile.json --top 25 --output outputs`: generate a ranked report bundle.
- `streamlit run app.py`: launch the web interface.
- `python -m unittest`: run the current test suite.

## Coding Style & Naming Conventions

Use standard Python 3 style with 4-space indentation, type hints where they clarify contracts, and small functions grouped by domain. Prefer `snake_case` for modules, functions, variables, and JSON keys; use `PascalCase` for dataclasses and model classes. Keep deterministic scoring logic in `scoring/` or `services/ranking_service.py`, not in agent prompts. Avoid committing `__pycache__/` files or ad hoc backups.

## Testing Guidelines

Tests use `unittest`; add new tests under `tests/` with names like `test_<behavior>.py` or methods named `test_<expected_behavior>`. Favor focused tests for validators, parsers, score classification, and report shape. Use `--skip-agents` for integration checks so tests do not spend API credits or depend on live LLM responses.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `updated readme` and `renaming and organization`. Keep future commits concise and scoped to one change. Pull requests should describe the user-facing behavior changed, list commands run, mention data or output artifacts touched, and link related issues. Include screenshots only for Streamlit UI changes.

## Security & Configuration Tips

Keep real credentials in `.env`; never commit API keys or Supabase secrets. When adding configuration, read from environment variables in `config.py` or the relevant service. Treat `outputs/` as generated data.
