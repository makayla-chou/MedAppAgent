import json
import unittest
from pathlib import Path

from config import DEFAULT_SCHOOLS_FILE, PROFILE_DIR
from repositories.school_repository import (
    load_schools,
    normalize_state_code,
    parse_average_number,
)
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


if __name__ == "__main__":
    unittest.main()
