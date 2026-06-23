# MedAppAgent

MedAppAgent is a Streamlit medical-school advising prototype. It combines structured applicant intake, cleaned AAMC/school datasets, deterministic scoring, Supabase persistence, and OpenAI agents for profile analysis, school-fit interpretation, critic review, and report follow-up questions.

## Features

- Authenticated Streamlit intake form with Supabase profile saving.
- Deterministic school ranking from `data/cleaned/final_med_school_data.csv`.
- AAMC aggregate context from `data/cleaned/`.
- Saved report history, report reloads, downloads, and follow-up Q&A.
- CLI report generation for local testing and batch runs.

## Project Structure

- `app.py`: Streamlit app, auth flow, profile form, saved reports, follow-up UI.
- `main.py`: CLI and shared report-generation pipeline.
- `agents/`: OpenAI profile, school-fit, critic, and follow-up agents.
- `services/`: ranking, AAMC context, profile, report, agent, and follow-up orchestration.
- `repositories/`: local CSV/JSON and Supabase persistence.
- `scoring/`: academic, preference, residency, and mission scoring.
- `validation/`: applicant and school-data checks.
- `reports/`: final report and table formatting.
- `data/cleaned/`: runtime school catalog and cleaned AAMC context tables.
- `tests/`: unittest coverage for ranking, validation, and data-context behavior.

## Scoring Notes

MedAppAgent does not produce an admissions probability.

- Academic comparison uses GPA/MCAT distance from reported school averages.
- Missing MCAT prevents academic competitiveness classification.
- Preference fit, residency context, and eligibility are separate concepts.
- AAMC values are historical aggregate context, not personal odds.
- Public-school residency access and school-specific policies still require official verification.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with Supabase and OpenAI credentials.

## Run Locally

Streamlit app:

```bash
streamlit run app.py
```

CLI with agents:

```bash
python main.py data/student_profiles/student1_profile.json
```

CLI without API calls:

```bash
python main.py data/student_profiles/student1_profile.json --skip-agents
```

Optional CLI arguments:

```bash
python main.py data/student_profiles/student1_profile.json \
  --schools data/cleaned/final_med_school_data.csv \
  --top 25 \
  --output outputs
```

## Tests and Data Audit

```bash
python -m unittest tests.test_refactor
python scripts/audit_cleaned_data.py
```

The audit script shows which cleaned CSVs are ranking inputs, report/agent context, registered-only tables, or currently unwired.

## Deployment

The repo is prepared for Streamlit Community Cloud with `requirements.txt`, `runtime.txt`, `.env.example`, and `.streamlit/config.toml`. `runtime.txt` pins Python 3.12 so hosted builds use dependency wheels instead of trying to compile packages from source.

Set these secrets in Streamlit Cloud:

```toml
SUPABASE_URL = "..."
SUPABASE_PUBLISHABLE_KEY = "..."
OPENAI_API_KEY = "..."
PROFILE_AGENT_MODEL = "gpt-4.1-mini"
SCHOOL_FIT_AGENT_MODEL = "gpt-4.1-mini"
CRITIC_AGENT_MODEL = "gpt-4.1-mini"
FOLLOWUP_AGENT_MODEL = "gpt-4.1-mini"
```

Use `app.py` as the Streamlit entry point.

## Current Dataset Limitation

`data/cleaned/final_med_school_data.csv` currently contains MD school rows. If an applicant requests DO or MD/PhD programs that are absent from the dataset, the app surfaces a warning and those programs cannot appear in rankings.

## Security

Never commit `.env`, API keys, Supabase secrets, generated reports, or applicant-identifying output. Use Supabase Row Level Security so users can only access their own profiles and reports.
