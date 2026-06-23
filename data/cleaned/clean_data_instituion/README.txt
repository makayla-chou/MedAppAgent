MedAppAgent AAMC FACTS 2025-2026 CSV Export

Recommended files:
1. combined_undergraduate_applicant_demographics_wide.csv
   Best for direct app lookups and joining one row per undergraduate institution.
2. combined_undergraduate_demographics_long.csv
   Best for filtering, charts, aggregations, and database storage.
3. facts_a1_medical_school_applications_matriculants.csv
   Separate medical-school-level table with application and matriculant characteristics.

Important caveats:
- Demographic tables count people who identified with a category alone or in combination, so categories overlap and should not be summed.
- Blank demographic values in the wide table mean the institution did not meet that source table's publication threshold. Blank does not mean zero.
- group_share_of_institution_pct is derived from group_applicants / total_applicants × 100.
- pct_of_all_group_applicants_nationally is the source's national-share percentage, not the demographic percentage within the institution.
- Table A-2.3 was uploaded twice. The duplicate was verified as identical and exported only once.
- The A-1 aggregate Total row and footnotes are preserved in source_metadata.csv rather than mixed into the school-level data.
