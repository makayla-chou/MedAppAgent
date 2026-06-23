import json
from pathlib import Path
from typing import Any

from models.validation import ValidationIssue
from repositories.local_profile_repository import load_student_profile
from validation.profile_validator import raise_for_profile_errors, validate_student_profile


def load_and_validate_profile(
    profile_file: str | Path,
) -> tuple[dict[str, Any], list[ValidationIssue]]:
    profile = load_student_profile(profile_file)
    issues = validate_student_profile(profile)
    raise_for_profile_errors(issues)
    return profile, issues


def validate_profile_data(
    profile: dict[str, Any],
) -> list[ValidationIssue]:
    issues = validate_student_profile(profile)
    raise_for_profile_errors(issues)
    return issues


def profile_to_text(profile: dict[str, Any]) -> str:
    return json.dumps(profile, indent=2, ensure_ascii=False)


def get_student_name(
    profile: dict[str, Any],
    fallback_name: str = "student",
) -> str:
    basic = profile.get("basic_information", {})
    name = basic.get("name") or profile.get("name") or fallback_name
    return str(name).strip()
