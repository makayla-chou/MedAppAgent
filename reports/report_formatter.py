import json

import pandas as pd

from models.validation import ValidationIssue


AGENT_COLUMNS = [
    "rank",
    "school_name",
    "school_state_code",
    "school_degree_type",
    "school_gpa",
    "school_mcat",
    "minimum_mcat_numeric",
    "is_public_bool",
    "school_city",
    "school_region",
    "school_setting",
    "application_deadline",
    "eligibility_status",
    "program_eligibility_status",
    "academic_eligibility_status",
    "residency_eligibility_status",
    "eligibility_reasons",
    "eligibility_verification",
    "academic_score",
    "academic_category",
    "gpa_difference",
    "mcat_difference",
    "basic_preference_score",
    "basic_preference_category",
    "preference_components",
    "preference_component_weights",
    "preference_penalty",
    "dealbreaker_conflicts",
    "geographic_proximity_hops",
    "preference_score_basis",
    "residency_context",
    "data_completeness_score",
    "academic_reasons",
    "academic_warnings",
    "preference_reasons",
    "preference_warnings",
    "verification_needed",
]

SUMMARY_COLUMNS = [
    "rank",
    "school_name",
    "school_state_code",
    "eligibility_status",
    "academic_score",
    "academic_category",
    "basic_preference_score",
    "basic_preference_category",
    "preference_penalty",
    "residency_context",
    "data_completeness_score",
]


def _serialize_cell(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def prepare_ranked_schools_for_agents(
    ranked_schools: pd.DataFrame,
) -> str:
    columns = [
        column
        for column in AGENT_COLUMNS
        if column in ranked_schools.columns
    ]
    table = ranked_schools[columns].copy()

    for column in table.columns:
        table[column] = table[column].apply(
            _serialize_cell
        )

    return table.to_string(index=False)


def dataframe_to_markdown(
    dataframe: pd.DataFrame,
) -> str:
    if dataframe.empty:
        return "No schools were ranked."

    columns = list(dataframe.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(
        "---"
        for _ in columns
    ) + " |"
    rows = []

    for _, row in dataframe.iterrows():
        values = []

        for column in columns:
            value = _serialize_cell(row[column])

            if (
                value is None
                or (
                    not isinstance(value, (list, dict))
                    and pd.isna(value)
                )
            ):
                text = ""
            else:
                text = (
                    str(value)
                    .replace("|", "\\|")
                    .replace("\n", " ")
                )

            values.append(text)

        rows.append(
            "| " + " | ".join(values) + " |"
        )

    return "\n".join(
        [header, separator, *rows]
    )


def ranking_summary_to_markdown(
    ranked_schools: pd.DataFrame,
) -> str:
    columns = [
        column
        for column in SUMMARY_COLUMNS
        if column in ranked_schools.columns
    ]

    return dataframe_to_markdown(
        ranked_schools[columns].copy()
    )


def format_validation_issues(
    issues: list[ValidationIssue],
) -> str:
    if not issues:
        return (
            "No applicant-profile validation issues "
            "were detected."
        )

    return "\n".join(
        (
            f"- **{issue.severity.upper()} — "
            f"{issue.field}:** {issue.message}"
        )
        for issue in issues
    )


def format_data_warnings(
    warnings: list[str],
) -> str:
    if not warnings:
        return (
            "No school-dataset warnings were detected."
        )

    return "\n".join(
        f"- {warning}"
        for warning in warnings
    )

SCHOOL_VIEW_CONFIG = {
    "academic_comparison": {
        "title": "Academic Comparison View",
        "description": (
            "Orders schools by the applicant's academic comparison index. "
            "This is not an admission-probability ranking."
        ),
        "columns": [
            "view_rank",
            "school_name",
            "school_state_code",
            "eligibility_status",
            "academic_score",
            "academic_category",
            "gpa_difference",
            "mcat_difference",
        ],
        "empty_message": (
            "No academic comparison view is available because the applicant "
            "does not have enough GPA/MCAT comparison data."
        ),
    },
    "preference_fit": {
        "title": "Preference-Fit View",
        "description": (
            "Orders schools by the basic preference score while preserving "
            "eligibility and dealbreaker outcomes."
        ),
        "columns": [
            "view_rank",
            "school_name",
            "school_state_code",
            "eligibility_status",
            "dealbreaker_status",
            "basic_preference_score",
            "basic_preference_category",
            "residency_context",
        ],
        "empty_message": "No schools have enough information for a preference-fit view.",
    },
    "home_state": {
        "title": "Home-State View",
        "description": (
            "Shows schools located in the applicant's state of legal residency."
        ),
        "columns": [
            "view_rank",
            "school_name",
            "school_state_code",
            "eligibility_status",
            "academic_category",
            "basic_preference_score",
            "residency_context",
        ],
        "empty_message": "No home-state schools were available in the evaluated dataset.",
    },
    "high_fit_reaches": {
        "title": "High-Fit Reach View",
        "description": (
            "Shows academically Reach or High Reach schools that still have a "
            "Strong Basic Preference Match. Confirmed Not Eligible schools are excluded."
        ),
        "columns": [
            "view_rank",
            "school_name",
            "school_state_code",
            "eligibility_status",
            "academic_category",
            "academic_score",
            "basic_preference_score",
            "basic_preference_category",
        ],
        "empty_message": (
            "No high-fit reaches were identified. This view also requires a "
            "usable academic comparison, including an MCAT score."
        ),
    },
    "public_out_of_state": {
        "title": "Public Out-of-State View",
        "description": (
            "Orders public out-of-state schools by observed residency access "
            "and fit. Official eligibility must still be verified."
        ),
        "columns": [
            "view_rank",
            "school_name",
            "school_state_code",
            "eligibility_status",
            "residency_access_category",
            "matriculants_out_of_state_pct",
            "basic_preference_score",
            "academic_category",
        ],
        "empty_message": "No public out-of-state schools were available.",
    },
    "incomplete_data": {
        "title": "Incomplete-Data Review",
        "description": (
            "Shows schools that cannot be fully evaluated because important "
            "eligibility or comparison data is missing."
        ),
        "columns": [
            "view_rank",
            "school_name",
            "school_state_code",
            "eligibility_status",
            "data_completeness_score",
            "eligibility_verification",
            "verification_needed",
        ],
        "empty_message": "No schools were classified as having insufficient data.",
    },
}


def school_views_to_markdown(
    school_views: dict[str, pd.DataFrame],
) -> str:
    """
    Format each independent school view as its own report subsection.

    The views intentionally use view_rank rather than the main planning-list
    rank because each view answers a different question.
    """
    sections: list[str] = []

    for view_name, config in SCHOOL_VIEW_CONFIG.items():
        dataframe = school_views.get(view_name)

        sections.append(f"### {config['title']}")
        sections.append(config["description"])

        if dataframe is None or dataframe.empty:
            sections.append(config["empty_message"])
            continue

        columns = [
            column
            for column in config["columns"]
            if column in dataframe.columns
        ]

        sections.append(
            dataframe_to_markdown(
                dataframe[columns].copy()
            )
        )

    return "\n\n".join(sections)

