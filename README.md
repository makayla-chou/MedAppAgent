# MedAppAgent

MedAppAgent is a medical-school application advising prototype. It combines structured applicant data, a local medical-school dataset, deterministic comparison logic, and three LLM agents.

## Current architecture

- `repositories/`: loading and saving profile and school data
- `validation/`: applicant and school-data quality checks
- `scoring/`: separate academic, preference, residency, and mission components
- `services/`: ranking, AAMC context, agent orchestration, and report saving
- `agents/`: profile, school-fit, and critic agents
- `reports/`: final report construction and table formatting
- `scripts/data_builders/`: scraping and dataset-building utilities

## Important scoring behavior

The system does not use one mixed match score.

- Academic comparison uses GPA and MCAT distance from reported school averages.
- Missing MCAT produces `Insufficient Data`, not a Target or Reach label.
- Personal preference fit is scored separately from competitiveness.
- Residency is reported as categorical context.
- Data completeness is reported separately.
- All classifications are planning aids, not acceptance probabilities.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in the keys in `.env`.

## Run from the terminal

```bash
python main.py data/student_profiles/student1_profile.json
```

Optional arguments:

```bash
python main.py data/student_profiles/student1_profile.json \
  --schools data/cleaned/final_med_school_data.csv \
  --top 25 \
  --output outputs
```

## Run the Streamlit interface

```bash
streamlit run app.py
```

## Current dataset limitation

`data/cleaned/final_med_school_data.csv` currently contains MD schools only. The validator will warn when an applicant requests DO or MD/PhD programs that are absent from the dataset.

## Test without spending API credits

```bash
python main.py data/student_profiles/student1_profile.json --skip-agents
```

This runs validation, normalization, scoring, ranking, and report saving without calling the LLM agents.

## Security

Never commit or upload `.env`. The project includes only `.env.example`; copy it locally and add real credentials there.
