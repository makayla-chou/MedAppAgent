MedAppAgent AAMC FACTS 2025 — Batch 4

CONTENTS
- 4 cleaned source-table CSVs.
- 3 combined app-ready CSVs.
- Validation report, source metadata, data dictionary, and manifest.

RECOMMENDED APP FILES
1. combined_socioeconomic_access_indicators_2018_2026_long.csv
   Best for SQL, filtering, charts, retrieval, and model context.

2. combined_socioeconomic_access_indicators_2018_2026_wide.csv
   Best for direct feature lookup across academic years.

3. combined_socioeconomic_access_stage_summary_2025_2026.csv
   Best for current-year comparisons across applicants, acceptees, and matriculants.

IMPORTANT INTERPRETATION NOTES
- The three A-24 SES categories form a mutually exclusive distribution and sum to the total population.
- DACA, first-generation, and fee-assistance values are separate binary indicators.
- Do not add the DACA, first-generation, and fee-assistance counts together; the same person may appear in more than one indicator.
- Derived acceptance and matriculation ratios are national aggregate ratios, not acceptance rates for individual medical schools.
- Percent fields are stored as percentage points: 13.8 means 13.8%.
- SES is not calculated for non-U.S. citizens and non-permanent residents; the source's Not Applicable/Unknown category retains these cases as described by AAMC.
- The exact AAMC notes and descriptions are preserved in source_metadata.csv.

VALIDATION
- Checks performed: 204
- Failed checks: 0
- Clean A-24 rows: 24
- Clean A-25 rows: 24
- Clean A-26 rows: 18
- Clean A-27 rows: 12
- Combined normalized rows: 126
