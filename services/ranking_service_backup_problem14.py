from typing import Any

import pandas as pd

from models.ranking_output import RankingOutput
from scoring.academic_score import calculate_academic_score
from scoring.mission_score import calculate_mission_fit
from scoring.preference_score import calculate_preference_fit
from scoring.residency_score import evaluate_residency_context
from repositories.school_repository import normalize_state_code
from validation.school_data_validator import (
    raise_for_school_data_errors,
    validate_school_data,
)


ELIGIBILITY_SORT_ORDER = {
    "Eligible": 3,
    "Verify Eligibility": 2,
    "Insufficient Data": 1,
    "Not Eligible": 0,
}


def _prepare_view(
    dataframe: pd.DataFrame,
    sort_columns: list[str],
    ascending: list[bool],
    top_n: int,
) -> pd.DataFrame:
    """
    Sort and label one independent school view.

    Each view gets its own view_rank so it is not mistaken for a universal
    ranking across every criterion.
    """
    if dataframe.empty:
        return dataframe.copy()

    view = dataframe.sort_values(
        by=sort_columns,
        ascending=ascending,
        na_position="last",
    ).head(top_n).reset_index(drop=True)

    view.insert(0, "view_rank", range(1, len(view) + 1))

    helper_columns = [
        column
        for column in ("_eligibility_sort", "_academic_sort")
        if column in view.columns
    ]
    if helper_columns:
        view = view.drop(columns=helper_columns)

    return view


def _build_school_views(
    ranked_all: pd.DataFrame,
    student: dict[str, Any],
    top_n: int,
) -> dict[str, pd.DataFrame]:
    """
    Build independent planning views from the full evaluated school set.

    Confirmed Not Eligible schools are excluded from recommendation-style
    views. They remain available in the main planning table and in the
    underlying exported data.
    """
    usable = ranked_all[
        ranked_all["eligibility_status"] != "Not Eligible"
    ].copy()

    academic = usable[
        usable["academic_score"].notna()
    ].copy()

    preference = usable[
        usable["basic_preference_score"].notna()
    ].copy()

    student_state_code = normalize_state_code(
        student.get("basic_information", {}).get("state_residency")
    )
    if student_state_code:
        home_state = usable[
            usable["school_state_code"] == student_state_code
        ].copy()
    else:
        home_state = usable.head(0).copy()

    high_fit_reaches = usable[
        usable["academic_category"].isin({"Reach", "High Reach"})
        & (
            usable["basic_preference_category"]
            == "Strong Basic Preference Match"
        )
    ].copy()

    public_out_of_state = usable[
        usable["residency_context"]
        .fillna("")
        .astype(str)
        .str.startswith("Out-of-state public")
    ].copy()

    incomplete_data = ranked_all[
        ranked_all["eligibility_status"] == "Insufficient Data"
    ].copy()

    return {
        "academic_comparison": _prepare_view(
            academic,
            sort_columns=[
                "_academic_sort",
                "basic_preference_score",
                "residency_priority",
                "data_completeness_score",
            ],
            ascending=[False, False, False, False],
            top_n=top_n,
        ),
        "preference_fit": _prepare_view(
            preference,
            sort_columns=[
                "basic_preference_score",
                "_academic_sort",
                "residency_priority",
                "data_completeness_score",
            ],
            ascending=[False, False, False, False],
            top_n=top_n,
        ),
        "home_state": _prepare_view(
            home_state,
            sort_columns=[
                "_eligibility_sort",
                "basic_preference_score",
                "_academic_sort",
                "data_completeness_score",
            ],
            ascending=[False, False, False, False],
            top_n=top_n,
        ),
        "high_fit_reaches": _prepare_view(
            high_fit_reaches,
            sort_columns=[
                "basic_preference_score",
                "_academic_sort",
                "residency_priority",
                "data_completeness_score",
            ],
            ascending=[False, False, False, False],
            top_n=top_n,
        ),
        "public_out_of_state": _prepare_view(
            public_out_of_state,
            sort_columns=[
                "residency_priority",
                "basic_preference_score",
                "_academic_sort",
                "data_completeness_score",
            ],
            ascending=[False, False, False, False],
            top_n=top_n,
        ),
        "incomplete_data": _prepare_view(
            incomplete_data,
            sort_columns=[
                "data_completeness_score",
                "basic_preference_score",
                "_academic_sort",
            ],
            ascending=[True, False, False],
            top_n=top_n,
        ),
    }


def resolve_eligibility_status(
    program_status: str,
    academic_status: str,
    residency_status: str,
) -> str:
    """
    Resolve the final four-status eligibility label.

    Conservative precedence:
    1. Explicit failure -> Not Eligible
    2. Missing eligibility-critical data -> Insufficient Data
    3. Known requirement needing official confirmation -> Verify Eligibility
    4. Otherwise -> Eligible
    """
    statuses = {
        program_status,
        academic_status,
        residency_status,
    }

    if "Not Eligible" in statuses:
        return "Not Eligible"
    if "Insufficient Data" in statuses:
        return "Insufficient Data"
    if "Verify Eligibility" in statuses:
        return "Verify Eligibility"
    return "Eligible"


def calculate_data_completeness(school: pd.Series) -> float:
    fields = [
        "school_state_code",
        "school_degree_type",
        "school_gpa",
        "school_mcat",
        "is_public_bool",
        "school_region",
        "school_setting",
        "application_deadline",
    ]
    present = 0
    for field in fields:
        value = school.get(field)
        if value is not None and not pd.isna(value) and str(value).strip():
            present += 1
    return round(100 * present / len(fields), 1)


def rank_schools(
    student: dict[str, Any],
    schools: pd.DataFrame,
    top_n: int = 25,
) -> RankingOutput:
    requested_types = student.get("school_preferences", {}).get("school_types", [])
    data_issues = validate_school_data(schools, requested_types)
    raise_for_school_data_errors(data_issues)
    data_warnings = [
        issue.message for issue in data_issues if issue.severity == "warning"
    ]

    rows: list[dict[str, Any]] = []

    for _, school in schools.iterrows():
        academic = calculate_academic_score(student, school)
        residency = evaluate_residency_context(student, school)
        preference = calculate_preference_fit(student, school)
        mission = calculate_mission_fit(student, school)

        program_status = preference[
            "program_eligibility_status"
        ]
        academic_status = academic[
            "academic_eligibility_status"
        ]
        residency_status = residency[
            "residency_eligibility_status"
        ]

        eligibility_status = resolve_eligibility_status(
            program_status=program_status,
            academic_status=academic_status,
            residency_status=residency_status,
        )

        eligibility_reasons: list[str] = []
        eligibility_verification: list[str] = []

        if program_status == "Not Eligible":
            eligibility_reasons.append(
                "The school's degree type is outside the applicant's selected program types."
            )
        elif program_status == "Insufficient Data":
            eligibility_verification.extend(
                preference["preference_verification"]
            )

        if academic_status == "Not Eligible":
            eligibility_reasons.append(
                "The applicant is below the school's listed minimum MCAT."
            )
        elif academic_status == "Insufficient Data":
            eligibility_verification.append(
                "A listed minimum MCAT cannot be evaluated because the applicant has no MCAT score."
            )

        if residency_status in {
            "Verify Eligibility",
            "Insufficient Data",
        }:
            eligibility_verification.extend(
                residency["residency_warnings"]
            )

        verification_needed = (
            preference["preference_verification"]
            + residency["residency_warnings"]
            + mission["mission_warnings"]
        )

        row = school.to_dict()
        row.update(academic)
        row.update(residency)
        row.update(preference)
        row.update(mission)
        row["eligibility_status"] = eligibility_status
        row["eligibility_reasons"] = eligibility_reasons
        row["eligibility_verification"] = eligibility_verification
        row["data_completeness_score"] = calculate_data_completeness(school)
        row["verification_needed"] = verification_needed
        rows.append(row)

    ranked = pd.DataFrame(rows)
    ranked["_eligibility_sort"] = ranked[
        "eligibility_status"
    ].map(
        ELIGIBILITY_SORT_ORDER
    ).fillna(0)

    student_has_mcat = student.get("academics", {}).get("mcat_total") is not None
    if student_has_mcat:
        ranked["_academic_sort"] = ranked["academic_score"].fillna(-1)
        ranking_basis = (
            "Schools are grouped by the four eligibility statuses, then ordered as a planning list by basic preference score, "
            "then residency context, academic comparison index, and data completeness. "
            "The basic preference score uses only degree type, state-border proximity, "
            "preferred region, setting, and explicit dealbreaker penalties. "
            "It is not a complete school-fit or admission-probability measure."
        )
        sort_columns = [
            "_eligibility_sort",
            "basic_preference_score",
            "residency_priority",
            "_academic_sort",
            "data_completeness_score",
        ]
    else:
        ranked["_academic_sort"] = ranked["gpa_position_score"].fillna(-1)
        ranking_basis = (
            "Because the applicant has no MCAT, schools are not assigned an academic competitiveness category. "
            "Schools are grouped by the four eligibility statuses, then ordered provisionally by residency context and basic preference score, "
            "GPA position, and data completeness. The basic preference score uses only "
            "degree type, state-border proximity, preferred region, setting, and explicit "
            "dealbreaker penalties."
        )
        sort_columns = [
            "_eligibility_sort",
            "residency_priority",
            "basic_preference_score",
            "_academic_sort",
            "data_completeness_score",
        ]

    ranked_all = ranked.sort_values(
        by=sort_columns,
        ascending=[False] * len(sort_columns),
        na_position="last",
    ).reset_index(drop=True)

    school_views = _build_school_views(
        ranked_all=ranked_all,
        student=student,
        top_n=top_n,
    )

    ranked_planning = ranked_all.head(top_n).copy()
    ranked_planning.insert(
        0,
        "rank",
        range(1, len(ranked_planning) + 1),
    )
    ranked_planning["ranking_basis"] = ranking_basis
    ranked_planning = ranked_planning.drop(
        columns=["_eligibility_sort", "_academic_sort"]
    )

    return RankingOutput(
        ranked_schools=ranked_planning,
        data_warnings=data_warnings,
        ranking_basis=ranking_basis,
        school_views=school_views,
    )
