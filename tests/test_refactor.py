import json
import tempfile
import unittest
from pathlib import Path

from config import DEFAULT_SCHOOLS_FILE, PROFILE_DIR
from main import generate_report_for_profile
from repositories.school_repository import (
    load_schools,
    normalize_state_code,
    parse_average_number,
)
from services.aamc_data_service import get_available_tables, get_context_for_profile
from services.aamc_data_service import get_undergraduate_institution_context
from services.ranking_service import rank_schools
from validation.profile_validator import validate_student_profile


class RefactorTests(unittest.TestCase):
    def test_state_normalization(self):
        self.assertEqual(normalize_state_code("North Carolina"), "NC")
        self.assertEqual(normalize_state_code("NC"), "NC")


    def test_average_parser_ignores_percentile_text(self):
        self.assertEqual(parse_average_number("509 (74th %-ile)"), 509.0)
        self.assertEqual(parse_average_number("508-528"), 518.0)

    def test_missing_mcat_is_not_classified(self):
        profile_path = PROFILE_DIR / "student1_profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        schools = load_schools(DEFAULT_SCHOOLS_FILE)
        result = rank_schools(profile, schools, top_n=25)

        self.assertTrue(
            (result.ranked_schools["academic_category"] == "Insufficient Data").all()
        )
        self.assertTrue(result.ranked_schools["academic_score"].isna().all())

    def test_north_carolina_residency_is_detected(self):
        profile_path = PROFILE_DIR / "student1_profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        schools = load_schools(DEFAULT_SCHOOLS_FILE)
        result = rank_schools(profile, schools, top_n=25)

        nc_rows = result.ranked_schools[
            result.ranked_schools["school_state_code"] == "NC"
        ]
        self.assertFalse(nc_rows.empty)
        self.assertTrue(
            nc_rows["residency_context"].str.contains("In-state").all()
        )

    def test_missing_do_dataset_is_reported(self):
        profile_path = PROFILE_DIR / "student1_profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        schools = load_schools(DEFAULT_SCHOOLS_FILE)
        result = rank_schools(profile, schools, top_n=10)

        self.assertTrue(any("DO" in warning for warning in result.data_warnings))

    def test_profile_contradiction_is_flagged(self):
        profile = {
            "basic_information": {"name": "Test", "state_residency": "Virginia"},
            "academics": {"overall_gpa": 3.7, "mcat_taken": False, "mcat_total": None},
            "school_preferences": {"school_types": ["MD"]},
            "achievements": {"research_outputs": ["Publication submitted"]},
            "experience_descriptions": {
                "research": "A manuscript is being prepared for submission."
            },
        }
        issues = validate_student_profile(profile)
        self.assertTrue(
            any(issue.field == "achievements.research_outputs" for issue in issues)
        )

    def test_cleaned_context_tables_are_available(self):
        tables = get_available_tables()

        for table_name in (
            "yearly",
            "major",
            "applicant_state",
            "matriculant_state",
            "acceptance_grid",
        ):
            self.assertIn(table_name, tables)
            self.assertIn("data/cleaned", tables[table_name])

    def test_profile_context_uses_cleaned_academic_tables(self):
        profile_path = PROFILE_DIR / "student1_profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        context = get_context_for_profile(profile)

        self.assertIn("National academic benchmark context", context)
        self.assertIn("Undergraduate-major aggregate context", context)
        self.assertIn("Home-state academic context", context)
        self.assertIn("Do not use demographic or access data to change school rankings", context)

    def test_ohio_state_does_not_match_iowa_state(self):
        context = get_undergraduate_institution_context("Ohio State University")

        self.assertIsNotNone(context)
        self.assertIn("The Ohio State University Main Campus", context)
        self.assertNotIn("Iowa State University", context)

    def test_report_can_be_limited_to_selected_schools(self):
        profile_path = PROFILE_DIR / "student1_profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        schools = load_schools(DEFAULT_SCHOOLS_FILE)
        selected_names = schools["school_name"].dropna().head(3).tolist()

        with tempfile.TemporaryDirectory() as output_root:
            result = generate_report_for_profile(
                profile,
                output_root=output_root,
                top_n=25,
                use_agents=False,
                selected_school_names=selected_names,
            )

        self.assertEqual(set(result.ranked_schools["school_name"]), set(selected_names))
        self.assertEqual(len(result.ranked_schools), len(selected_names))


if __name__ == "__main__":
    unittest.main()
