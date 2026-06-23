import pandas as pd

from models.validation import ValidationIssue


REQUIRED_COLUMNS = {
    "school_name",
    "school_state_code",
    "school_degree_type",
    "school_gpa",
    "school_mcat",
    "is_public_bool",
    "school_region",
    "school_setting",
}


def validate_school_data(
    schools: pd.DataFrame,
    requested_degree_types: list[str] | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    missing_columns = sorted(REQUIRED_COLUMNS - set(schools.columns))
    if missing_columns:
        issues.append(ValidationIssue(
            "school_data.columns",
            "error",
            "Missing normalized school columns: " + ", ".join(missing_columns),
        ))
        return issues

    if schools.empty:
        issues.append(ValidationIssue(
            "school_data",
            "error",
            "The school dataset contains no rows.",
        ))
        return issues

    available_types = {
        str(value).upper()
        for value in schools["school_degree_type"].dropna().unique()
    }
    requested_types = {
        str(value).upper() for value in (requested_degree_types or [])
    }
    absent_types = sorted(requested_types - available_types)

    if absent_types:
        issues.append(ValidationIssue(
            "school_data.degree_type",
            "warning",
            "The dataset has no rows for requested program type(s): "
            + ", ".join(absent_types)
            + ". Those programs cannot appear in the rankings.",
        ))

    for column, label in (
        ("school_gpa", "reported GPA"),
        ("school_mcat", "reported MCAT"),
        ("school_state_code", "state"),
        ("school_degree_type", "degree type"),
    ):
        missing_rate = float(schools[column].isna().mean())
        if missing_rate > 0:
            issues.append(ValidationIssue(
                f"school_data.{column}",
                "warning",
                f"{missing_rate:.1%} of schools are missing {label} data.",
            ))

    return issues


def raise_for_school_data_errors(issues: list[ValidationIssue]) -> None:
    errors = [issue for issue in issues if issue.severity == "error"]
    if errors:
        message = "; ".join(issue.message for issue in errors)
        raise ValueError(f"Invalid school dataset: {message}")
