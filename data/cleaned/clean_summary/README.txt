MedAppAgent AAMC FACTS 2025 — Batch 5

CONTENTS
- 4 cleaned source CSVs.
- 4 combined app-ready CSVs.
- Validation report, source metadata, data dictionary, and manifest.

RECOMMENDED APP FILES
1. combined_medical_education_history_1980_2026_wide.csv
   Best for one-row-per-year feature lookup and historical comparisons.

2. combined_medical_education_history_1980_2026_long.csv
   Best for SQL, retrieval, flexible charts, and model context.

3. combined_gender_applicant_matriculant_trends_1980_2026_long.csv
   Best for gender trend queries across applicant and matriculant stages.

4. combined_medical_education_pipeline_2016_2026.csv
   Best for recent applicants, matriculants, enrollment, and graduates.

IMPORTANT INTERPRETATION NOTES
- Applicant-to-matriculant ratios are national aggregate ratios, not individual-school acceptance rates.
- Another Gender Identity or Not Reported is calculated as All minus Men minus Women.
- Chart 3 explicitly states that Another Gender Identity and unreported gender are included only in All Matriculants.
- The 2025-2026 graduates value is unavailable in Table 1 and is stored as blank.
- Official sources contain two one-person discrepancies, preserved rather than overwritten:
  * 2019-2020 applicants: Charts 1 and 2 show 53,369; Table 1 shows 53,368.
  * 2025-2026 matriculants: Chart 3 shows 23,441; Table 1 shows 23,440.
- Use source_table columns when exact source fidelity matters.

VALIDATION
- Total checks performed: 204
- Internal arithmetic errors: 0
- Official-source mismatch warnings: 2
- Historical academic years: 46
