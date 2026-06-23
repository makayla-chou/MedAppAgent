MedAppAgent AAMC FACTS 2025 — Batch 3

CONTENTS
- 6 cleaned source-table CSVs.
- 6 normalized or combined app-ready CSVs.
- Validation report, source metadata, data dictionary, and manifest.

RECOMMENDED APP FILES
1. combined_state_race_outcomes_2025_2026_long.csv
   Use for SQL, filtering by state and race/ethnicity, retrieval, and charts.

2. combined_state_race_outcomes_2025_2026_wide.csv
   Use for direct state-level app lookups and feature generation.

3. combined_race_gender_stage_counts_2025_2026_long.csv
   Use for gender, race/ethnicity, subcategory, and application-stage queries.

4. combined_race_gender_outcomes_2025_2026_wide.csv
   Use when the app needs applicants, acceptees, matriculants, and derived ratios in one row.

5. combined_race_ethnicity_trends_2021_2026_long.csv
   Use for five-year trend analysis and model context retrieval.

6. combined_race_ethnicity_stage_summary_2025_2026.csv
   Use for current-year comparisons across applicants, acceptees, and matriculants.

IMPORTANT INTERPRETATION NOTES
- Applicant-to-matriculant ratios are descriptive population ratios, not acceptance rates for a specific medical school.
- A-10 and A-11 use race/ethnicity selected alone, with Multiple Race or Ethnicity as a separate category.
- A-14 distinguishes Alone, In Combination, and Alone or In Combination.
- In-combination categories overlap. Do not add them together to estimate an unduplicated total.
- AAMC changed the race/ethnicity collection methodology for 2025-2026 and added Middle Eastern or North African.
- Values shown as dashes in the source tables are stored as blank CSV values.
- Another Gender Identity and declined-to-report gender responses appear only in the A-12 All section.
- Percentage values are stored as percentage points: 30.8 means 30.8%.

VALIDATION
- Cross-table checks performed: 52
- Failed checks: 0
- State/legal-residence entities retained: 60
- State-by-race long rows: 780
- A-12 cleaned rows: 213
- A-12 normalized long rows: 852
- A-14 combined trend rows: 405
