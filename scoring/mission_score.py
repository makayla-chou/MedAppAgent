from typing import Any

import pandas as pd


def calculate_mission_fit(
    student: dict[str, Any],
    school: pd.Series,
) -> dict[str, Any]:
    """
    Score only curated mission tags, not raw prose.

    The current school CSV does not contain curated mission tags, so this
    component intentionally returns no score instead of inventing fit.
    """
    school_tags = school.get("mission_tags")
    if school_tags is None or pd.isna(school_tags) or not str(school_tags).strip():
        return {
            "mission_fit_score": None,
            "mission_matches": [],
            "mission_warnings": [
                "Mission fit was not scored because curated school mission tags are unavailable."
            ],
        }

    applicant_tags = {
        str(item).strip().lower()
        for item in student.get("goals", {}).get("career_interests", [])
        if str(item).strip()
    }
    normalized_school_tags = {
        item.strip().lower()
        for item in str(school_tags).split("|")
        if item.strip()
    }

    if not applicant_tags:
        return {
            "mission_fit_score": None,
            "mission_matches": [],
            "mission_warnings": ["Applicant career-interest tags are missing."],
        }

    matches = sorted(applicant_tags & normalized_school_tags)
    score = round(100 * len(matches) / len(applicant_tags), 1)

    return {
        "mission_fit_score": score,
        "mission_matches": matches,
        "mission_warnings": [],
    }
