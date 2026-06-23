from typing import Any

from models.validation import ValidationIssue


MCAT_SECTION_FIELDS = {
    "chem_physics": "Chem/Physics",
    "cars": "CARS",
    "bio_biochem": "Bio/Biochem",
    "psych_social": "Psych/Soc",
}


def _parse_integer(value: Any) -> int:
    """
    Convert a value to an integer without silently truncating decimals.
    """
    if isinstance(value, bool):
        raise ValueError

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError
        return int(value)

    text = str(value).strip()
    if not text:
        raise ValueError

    return int(text)


def validate_student_profile(
    profile: dict[str, Any],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not isinstance(profile, dict):
        return [
            ValidationIssue(
                "profile",
                "error",
                "Profile must be a JSON object.",
            )
        ]

    basic = profile.get("basic_information", {})
    academics = profile.get("academics", {})
    preferences = profile.get("school_preferences", {})
    achievements = profile.get("achievements", {})
    descriptions = profile.get("experience_descriptions", {})

    if not basic.get("name"):
        issues.append(ValidationIssue(
            "basic_information.name",
            "warning",
            "Applicant name is missing; a filename fallback will be used.",
        ))

    if not basic.get("state_residency"):
        issues.append(ValidationIssue(
            "basic_information.state_residency",
            "warning",
            "State residency is missing, so in-state strategy cannot be assessed.",
        ))

    overall_gpa = academics.get("overall_gpa")
    if overall_gpa is None:
        issues.append(ValidationIssue(
            "academics.overall_gpa",
            "error",
            "Overall GPA is required.",
        ))
    else:
        try:
            gpa = float(overall_gpa)
            if not 0.0 <= gpa <= 4.0:
                raise ValueError
        except (TypeError, ValueError):
            issues.append(ValidationIssue(
                "academics.overall_gpa",
                "error",
                "Overall GPA must be a number between 0.0 and 4.0.",
            ))

    mcat_taken = bool(academics.get("mcat_taken", False))
    mcat_total = academics.get("mcat_total")
    valid_mcat_total: int | None = None

    if mcat_taken and mcat_total is None:
        issues.append(ValidationIssue(
            "academics.mcat_total",
            "error",
            "MCAT is marked as taken, but no total score was provided.",
        ))

    if mcat_total is not None:
        try:
            valid_mcat_total = _parse_integer(mcat_total)
            if not 472 <= valid_mcat_total <= 528:
                raise ValueError
        except (TypeError, ValueError):
            issues.append(ValidationIssue(
                "academics.mcat_total",
                "error",
                "MCAT total must be an integer between 472 and 528.",
            ))
            valid_mcat_total = None

    sections = academics.get("mcat_sections", {})
    valid_section_scores: dict[str, int] = {}

    if not isinstance(sections, dict):
        if mcat_taken or mcat_total is not None:
            issues.append(ValidationIssue(
                "academics.mcat_sections",
                "error",
                "MCAT section scores must be provided as an object.",
            ))
        sections = {}

    for field_name, display_name in MCAT_SECTION_FIELDS.items():
        value = sections.get(field_name)

        if value is None:
            if mcat_taken:
                issues.append(ValidationIssue(
                    f"academics.mcat_sections.{field_name}",
                    "error",
                    f"{display_name} score is required when the MCAT is marked as taken.",
                ))
            continue

        try:
            section_score = _parse_integer(value)
            if not 118 <= section_score <= 132:
                raise ValueError
            valid_section_scores[field_name] = section_score
        except (TypeError, ValueError):
            issues.append(ValidationIssue(
                f"academics.mcat_sections.{field_name}",
                "error",
                f"{display_name} score must be an integer between 118 and 132.",
            ))

    if (
        valid_mcat_total is not None
        and len(valid_section_scores) == len(MCAT_SECTION_FIELDS)
    ):
        section_sum = sum(valid_section_scores.values())

        if section_sum != valid_mcat_total:
            issues.append(ValidationIssue(
                "academics.mcat_sections",
                "error",
                (
                    f"MCAT section scores add up to {section_sum}, "
                    f"but the reported total is {valid_mcat_total}."
                ),
            ))

    school_types = preferences.get("school_types", [])
    if not school_types:
        issues.append(ValidationIssue(
            "school_preferences.school_types",
            "warning",
            "No program type was selected.",
        ))

    research_outputs = {
        str(item).strip().lower()
        for item in achievements.get("research_outputs", [])
    }
    research_description = str(descriptions.get("research", "")).lower()
    if (
        "publication submitted" in research_outputs
        and any(
            phrase in research_description
            for phrase in (
                "being prepared for submission",
                "preparing for submission",
                "manuscript in preparation",
            )
        )
    ):
        issues.append(ValidationIssue(
            "achievements.research_outputs",
            "warning",
            (
                "The research description says the manuscript is being prepared, "
                "but the achievements list says it was submitted."
            ),
        ))

    return issues


def raise_for_profile_errors(issues: list[ValidationIssue]) -> None:
    errors = [
        issue
        for issue in issues
        if issue.severity == "error"
    ]

    if errors:
        message = "; ".join(
            f"{issue.field}: {issue.message}"
            for issue in errors
        )
        raise ValueError(f"Invalid student profile: {message}")
