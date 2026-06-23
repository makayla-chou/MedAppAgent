MedAppAgent AAMC FACTS 2025 — Batch 2

CONTENTS
- 5 cleaned source-table CSVs.
- 4 combined, app-ready CSVs.
- Source metadata, manifest, and data dictionary.

RECOMMENDED APP FILES
1. combined_state_outcomes_2025_2026_wide.csv
   Use for direct state-level lookups and context generation.

2. combined_state_applicant_matriculant_trends_2016_2026_long.csv
   Use for SQL, charts, trend analysis, and retrieval by year.

3. combined_gender_trends_2006_2026_long.csv
   Use for SQL, filtering, charts, and LLM context retrieval.

4. combined_gender_trends_2006_2026_wide.csv
   Use when your app needs one row containing a full historical series.

IMPORTANT INTERPRETATION NOTES
- State matriculation rate is matriculants divided by applicants from a state of legal residence.
  It is not the acceptance rate of any individual medical school.
- Percent fields are stored as percentage points. Example: 51.4 means 51.4%.
- A dash in the original gender tables is represented as a blank CSV value.
- Another Gender Identity was added to the AMCAS gender question in 2023-2024.
- The AAMC notes and methodology language are preserved in source_metadata.csv.
- Region totals, special categories, and overall totals are retained and identified by entity_type.
- The national totals from A-3, A-4, and A-5 are joined under the canonical name United States Total.

VALIDATION
- A-4 current-year matriculants were compared with A-5 in-state plus out-of-state matriculants.
- Number of failed equality checks: 0
- Number of rows without comparable values: 0
- Combined state entities: 60
- State trend rows: 600
- Gender history covers: 2006-2007 through 2025-2026
