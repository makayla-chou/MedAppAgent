from __future__ import annotations

import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from config import DATA_DIR


CLEANED_ROOT = DATA_DIR / "cleaned"

# Keep this spelling for now because it matches the folder currently in the project.
# The folder can be renamed later in a separate cleanup step.
INSTITUTION_DIR = CLEANED_ROOT / "clean_data_instituion"
LEGAL_RESIDENCE_GENDER_DIR = (
    CLEANED_ROOT / "clean_data_legal_residence_and_gender"
)
MCAT_GPA_DIR = CLEANED_ROOT / "clean_MCAT_and_GPA"
OTHER_DIR = CLEANED_ROOT / "clean_other"
RACE_ETHNICITY_DIR = CLEANED_ROOT / "clean_race_and_ethnicity"
SUMMARY_DIR = CLEANED_ROOT / "clean_summary"


TABLE_FILES: dict[str, tuple[Path, ...]] = {
    "yearly": (
        MCAT_GPA_DIR / "aamc_a16_clean.csv",
    ),
    "major": (
        MCAT_GPA_DIR / "aamc_a17_major_stats.csv",
    ),
    "race_ethnicity": (
        MCAT_GPA_DIR / "aamc_a18_race_ethnicity_stats.csv",
    ),
    "applicant_state": (
        MCAT_GPA_DIR / "aamc_a19_applicant_state_stats.csv",
    ),
    "matriculant_state": (
        MCAT_GPA_DIR / "aamc_a20_matriculant_state_stats.csv",
    ),
    "applicant_gender": (
        MCAT_GPA_DIR / "aamc_a21_applicant_gender_stats.csv",
    ),
    "matriculant_gender": (
        MCAT_GPA_DIR / "aamc_a22_matriculant_gender_stats.csv",
    ),
    "acceptance_grid": (
        MCAT_GPA_DIR / "aamc_a23_acceptance_grid.csv",
    ),

    # Institution-level context.
    "undergraduate_demographics": (
        INSTITUTION_DIR
        / "combined_undergraduate_applicant_demographics_wide.csv",
    ),
    "undergraduate_demographics_long": (
        INSTITUTION_DIR / "combined_undergraduate_demographics_long.csv",
    ),
    "undergraduate_applicant_totals": (
        INSTITUTION_DIR
        / "facts_a2_undergraduate_institutions_total_applicants.csv",
    ),
    "medical_school_application_totals": (
        INSTITUTION_DIR
        / "facts_a1_medical_school_applications_matriculants.csv",
    ),

    # Legal-residence and gender context.
    "state_outcomes": (
        LEGAL_RESIDENCE_GENDER_DIR
        / "combined_state_outcomes_2025_2026_wide.csv",
    ),
    "state_trends": (
        LEGAL_RESIDENCE_GENDER_DIR
        / "combined_state_applicant_matriculant_trends_2016_2026_long.csv",
    ),
    "gender_trends": (
        LEGAL_RESIDENCE_GENDER_DIR
        / "combined_gender_trends_2006_2026_long.csv",
    ),

    # Race/ethnicity context.
    "race_stage_summary": (
        RACE_ETHNICITY_DIR
        / "combined_race_ethnicity_stage_summary_2025_2026.csv",
    ),
    "race_trends": (
        RACE_ETHNICITY_DIR
        / "combined_race_ethnicity_trends_2021_2026_long.csv",
    ),
    "race_gender_stage_counts": (
        RACE_ETHNICITY_DIR
        / "combined_race_gender_stage_counts_2025_2026_long.csv",
    ),
    "state_race_outcomes": (
        RACE_ETHNICITY_DIR
        / "combined_state_race_outcomes_2025_2026_long.csv",
    ),

    # Socioeconomic and access context.
    "socioeconomic_access": (
        OTHER_DIR
        / "combined_socioeconomic_access_indicators_2018_2026_long.csv",
    ),
    "socioeconomic_access_summary": (
        OTHER_DIR
        / "combined_socioeconomic_access_stage_summary_2025_2026.csv",
    ),

    # National summary and historical context.
    "medical_pipeline": (
        SUMMARY_DIR / "combined_medical_education_pipeline_2016_2026.csv",
    ),
    "medical_history": (
        SUMMARY_DIR
        / "combined_medical_education_history_1980_2026_long.csv",
    ),
    "historical_gender": (
        SUMMARY_DIR
        / "combined_gender_applicant_matriculant_trends_1980_2026_long.csv",
    ),
}


STATE_ABBREVIATIONS = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}


MAJOR_GROUP_ALIASES = {
    "biology": "Biological Sciences",
    "biological sciences": "Biological Sciences",
    "biomedical engineering": "Other",
    "biomedial engineering": "Other",
    "neuroscience": "Biological Sciences",
    "public health": "Specialized Health Sciences",
}


PROFILE_PATHS = {
    "gpa": (
        ("academics", "overall_gpa"),
        ("academics", "cumulative_gpa"),
        ("academics", "gpa"),
        ("overall_gpa",),
        ("gpa",),
    ),
    "mcat": (
        ("academics", "mcat_total"),
        ("academics", "mcat"),
        ("mcat_total",),
        ("mcat",),
    ),
    "state": (
        ("basic_information", "state_residency"),
        ("basic_information", "state_of_residence"),
        ("basic_information", "legal_residence"),
        ("demographics", "state_of_residence"),
        ("residency", "state"),
        ("state_of_residence",),
        ("state",),
    ),
    "undergraduate_institution": (
        ("basic_information", "undergraduate_school"),
        ("academics", "undergraduate_institution"),
        ("education", "undergraduate_institution"),
        ("basic_information", "undergraduate_institution"),
        ("undergraduate_institution",),
        ("college",),
    ),
    "major": (
        ("basic_information", "major_group"),
        ("basic_information", "major"),
        ("academics", "major"),
        ("education", "major"),
        ("major",),
    ),
    "first_generation": (
        ("background", "first_generation_college_student"),
        ("background", "first_generation"),
        ("demographics", "first_generation"),
        ("first_generation_college_student",),
        ("first_generation",),
    ),
    "daca": (
        ("background", "daca_status"),
        ("citizenship", "daca_status"),
        ("daca_status",),
    ),
    "fee_assistance": (
        ("background", "fee_assistance_program"),
        ("financial", "fee_assistance_program"),
        ("fee_assistance_program",),
        ("received_fee_assistance",),
    ),
}


def _resolve_table_path(table_name: str) -> Path:
    if table_name not in TABLE_FILES:
        available = ", ".join(sorted(TABLE_FILES))
        raise ValueError(
            f"Unknown table '{table_name}'. Available tables: {available}"
        )

    candidates = TABLE_FILES[table_name]
    for path in candidates:
        if path.exists():
            return path

    searched = "\n".join(f"- {path}" for path in candidates)
    raise FileNotFoundError(
        f"Missing cleaned AAMC table '{table_name}'. Searched:\n{searched}"
    )


@lru_cache(maxsize=None)
def load_table(table_name: str) -> pd.DataFrame:
    """Load one configured AAMC table and cache it for the process lifetime."""
    file_path = _resolve_table_path(table_name)
    return pd.read_csv(file_path, low_memory=False)


def get_available_tables() -> dict[str, str]:
    """Return tables currently available on disk for debugging and tests."""
    available: dict[str, str] = {}
    for table_name in TABLE_FILES:
        try:
            available[table_name] = str(_resolve_table_path(table_name))
        except FileNotFoundError:
            continue
    return available


def _get_nested_value(
    data: dict[str, Any],
    path: tuple[str, ...],
) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first_profile_value(
    profile: dict[str, Any],
    field_name: str,
) -> Any:
    for path in PROFILE_PATHS[field_name]:
        value = _get_nested_value(profile, path)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _to_float(value: Any) -> float | None:
    try:
        if value is None or isinstance(value, bool):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    number = _to_float(value)
    if number is None:
        return None
    return int(number)


def _is_affirmative(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if value is None:
        return False

    normalized = str(value).strip().lower()
    return normalized in {
        "yes",
        "y",
        "true",
        "1",
        "first generation",
        "first-generation",
        "daca",
        "approved",
        "received",
        "recipient",
        "used",
        "applied",
    }


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _format_count(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return "Not reported"
    return f"{int(round(number)):,}"


def _format_percent(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return "Not reported"
    return f"{number:.1f}%"


def _latest_row(
    dataframe: pd.DataFrame,
    year_column: str = "academic_year",
) -> pd.Series | None:
    if dataframe.empty or year_column not in dataframe.columns:
        return None

    working = dataframe.copy()
    working["_year_sort"] = pd.to_numeric(
        working[year_column].astype(str).str.slice(0, 4),
        errors="coerce",
    )
    working = working.dropna(subset=["_year_sort"])
    if working.empty:
        return None
    return working.sort_values("_year_sort").iloc[-1]


def _latest_metric_value(
    dataframe: pd.DataFrame,
    metric: str,
    statistic: str,
    **filters: str,
) -> tuple[Any, Any] | None:
    if dataframe.empty:
        return None

    result = dataframe[
        (
            dataframe["metric"].astype(str).str.casefold()
            == metric.casefold()
        )
        & (
            dataframe["statistic"].astype(str).str.casefold()
            == statistic.casefold()
        )
    ].copy()

    for column, expected_value in filters.items():
        if column not in result.columns:
            return None
        result = result[
            result[column].astype(str).str.casefold()
            == str(expected_value).casefold()
        ]

    row = _latest_row(result)
    if row is None:
        return None
    return row.get("value"), row.get("academic_year")


def _format_mean(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return "Not reported"
    return f"{number:.1f}"


def _safe_context_section(builder: Any, *args: Any) -> str | None:
    """
    Optional context tables should never crash the report pipeline.

    The GPA/MCAT formatter separately explains a missing acceptance grid because
    that table is central to the academic context.
    """
    try:
        result = builder(*args)
    except (FileNotFoundError, KeyError, ValueError, TypeError):
        return None
    return result or None


# ---------------------------------------------------------------------------
# Existing public lookup functions
# ---------------------------------------------------------------------------

def get_acceptance_grid_row(
    gpa_range: str,
    mcat_range: str,
) -> dict[str, Any] | None:
    dataframe = load_table("acceptance_grid")
    result = dataframe[
        (dataframe["gpa_range"] == gpa_range)
        & (dataframe["mcat_range"] == mcat_range)
    ]
    if result.empty:
        return None
    return result.iloc[0].to_dict()


def get_state_stats(
    state: str,
    population: str,
) -> pd.DataFrame:
    table_name = (
        "applicant_state"
        if population.lower() == "applicants"
        else "matriculant_state"
    )
    dataframe = load_table(table_name)
    return dataframe[
        dataframe["state"].astype(str).str.lower() == state.lower()
    ].copy()


def get_major_stats(
    major: str,
    population: str | None = None,
) -> pd.DataFrame:
    dataframe = load_table("major")
    result = dataframe[
        dataframe["major"].astype(str).str.lower() == major.lower()
    ]
    if population:
        result = result[
            result["population"].astype(str).str.lower()
            == population.lower()
        ]
    return result.copy()


def get_yearly_metric(
    metric: str,
    statistic: str = "Mean",
    population: str | None = None,
) -> pd.DataFrame:
    dataframe = load_table("yearly")
    result = dataframe[
        (
            dataframe["metric"].astype(str).str.lower()
            == metric.lower()
        )
        & (
            dataframe["statistic"].astype(str).str.lower()
            == statistic.lower()
        )
    ]
    if population:
        result = result[
            result["population"].astype(str).str.lower()
            == population.lower()
        ]
    return result.copy()


def get_gpa_range(gpa: float) -> str:
    if gpa > 3.79:
        return "Greater than 3.79"
    if gpa >= 3.60:
        return "3.60-3.79"
    if gpa >= 3.40:
        return "3.40-3.59"
    if gpa >= 3.20:
        return "3.20-3.39"
    if gpa >= 3.00:
        return "3.00-3.19"
    if gpa >= 2.80:
        return "2.80-2.99"
    if gpa >= 2.60:
        return "2.60-2.79"
    if gpa >= 2.40:
        return "2.40-2.59"
    if gpa >= 2.20:
        return "2.20-2.39"
    if gpa >= 2.00:
        return "2.00-2.19"
    return "Less than 2.00"


def get_mcat_range(mcat: int) -> str:
    if mcat < 486:
        return "Less than 486"
    if mcat <= 489:
        return "486-489"
    if mcat <= 493:
        return "490-493"
    if mcat <= 497:
        return "494-497"
    if mcat <= 501:
        return "498-501"
    if mcat <= 505:
        return "502-505"
    if mcat <= 509:
        return "506-509"
    if mcat <= 513:
        return "510-513"
    if mcat <= 517:
        return "514-517"
    return "Greater than 517"


def get_acceptance_context(
    gpa: float,
    mcat: int,
) -> dict[str, Any] | None:
    result = get_acceptance_grid_row(
        gpa_range=get_gpa_range(gpa),
        mcat_range=get_mcat_range(mcat),
    )
    if result is None:
        return None
    return {
        "entered_gpa": gpa,
        "entered_mcat": mcat,
        **result,
    }


def format_acceptance_context(
    context: dict[str, Any] | None,
) -> str:
    if context is None:
        return "No matching AAMC GPA/MCAT acceptance-grid data was found."

    gpa_range = context.get("gpa_range", "Unknown")
    mcat_range = context.get("mcat_range", "Unknown")
    data_status = context.get("data_status", "available")

    if data_status == "suppressed":
        return (
            "GPA/MCAT aggregate context:\n"
            f"- GPA range: {gpa_range}\n"
            f"- MCAT range: {mcat_range}\n"
            "- AAMC suppressed the values because the group was too small.\n"
            "- No reliable aggregate percentage is available."
        )

    if data_status == "zero_applicants":
        return (
            "GPA/MCAT aggregate context:\n"
            f"- GPA range: {gpa_range}\n"
            f"- MCAT range: {mcat_range}\n"
            "- The table reports zero applicants in this category.\n"
            "- An aggregate percentage cannot be calculated."
        )

    return (
        "GPA/MCAT aggregate context:\n"
        f"- GPA range: {gpa_range}\n"
        f"- MCAT range: {mcat_range}\n"
        f"- Applicants: {_format_count(context.get('applicants'))}\n"
        f"- Acceptees: {_format_count(context.get('acceptees'))}\n"
        "- Aggregate acceptance ratio: "
        f"{_format_percent(context.get('acceptance_rate_percent'))}\n"
        "- This historical group-level statistic is not the applicant's "
        "personal probability."
    )


# ---------------------------------------------------------------------------
# New context builders
# ---------------------------------------------------------------------------

def get_national_academic_context() -> str | None:
    dataframe = load_table("yearly")
    applicant_gpa = _latest_metric_value(
        dataframe,
        "GPA Total",
        "Mean",
        population="Applicants",
    )
    matriculant_gpa = _latest_metric_value(
        dataframe,
        "GPA Total",
        "Mean",
        population="Matriculants",
    )
    applicant_mcat = _latest_metric_value(
        dataframe,
        "Total MCAT",
        "Mean",
        population="Applicants",
    )
    matriculant_mcat = _latest_metric_value(
        dataframe,
        "Total MCAT",
        "Mean",
        population="Matriculants",
    )

    if not any((applicant_gpa, matriculant_gpa, applicant_mcat, matriculant_mcat)):
        return None

    academic_year = next(
        (
            year
            for value in (
                applicant_gpa,
                matriculant_gpa,
                applicant_mcat,
                matriculant_mcat,
            )
            if value is not None
            for year in (value[1],)
            if year is not None
        ),
        "latest available",
    )

    return (
        "National academic benchmark context:\n"
        f"- Academic year: {academic_year}\n"
        "- Applicant mean GPA / MCAT: "
        f"{_format_mean(applicant_gpa[0] if applicant_gpa else None)} / "
        f"{_format_mean(applicant_mcat[0] if applicant_mcat else None)}\n"
        "- Matriculant mean GPA / MCAT: "
        f"{_format_mean(matriculant_gpa[0] if matriculant_gpa else None)} / "
        f"{_format_mean(matriculant_mcat[0] if matriculant_mcat else None)}\n"
        "- These are national descriptive benchmarks, not cutoffs."
    )


def get_major_academic_context(major: Any) -> str | None:
    if major is None or not str(major).strip():
        return None

    dataframe = load_table("major")
    requested_major = str(major).strip()
    mapped_major = MAJOR_GROUP_ALIASES.get(
        requested_major.casefold(),
        requested_major,
    )
    target = _normalize_text(mapped_major)
    matches = dataframe[
        dataframe["major"].map(_normalize_text) == target
    ]
    if matches.empty:
        return None

    major_name = matches.iloc[0].get("major", str(major))
    applicant_count = _latest_metric_value(
        matches,
        "Total Applicants",
        "Count",
        population="Applicants",
    )
    matriculant_count = _latest_metric_value(
        matches,
        "Total Matriculants",
        "Count",
        population="Matriculants",
    )
    applicant_gpa = _latest_metric_value(
        matches,
        "GPA Total",
        "Mean",
        population="Applicants",
    )
    applicant_mcat = _latest_metric_value(
        matches,
        "Total MCAT",
        "Mean",
        population="Applicants",
    )
    matriculant_gpa = _latest_metric_value(
        matches,
        "GPA Total",
        "Mean",
        population="Matriculants",
    )
    matriculant_mcat = _latest_metric_value(
        matches,
        "Total MCAT",
        "Mean",
        population="Matriculants",
    )

    academic_year = next(
        (
            year
            for value in (
                applicant_count,
                matriculant_count,
                applicant_gpa,
                applicant_mcat,
                matriculant_gpa,
                matriculant_mcat,
            )
            if value is not None
            for year in (value[1],)
            if year is not None
        ),
        "latest available",
    )

    return (
        "Undergraduate-major aggregate context:\n"
        f"- Applicant-reported major: {requested_major}\n"
        f"- AAMC major group used: {major_name}\n"
        f"- Academic year: {academic_year}\n"
        "- Applicants / matriculants: "
        f"{_format_count(applicant_count[0] if applicant_count else None)} / "
        f"{_format_count(matriculant_count[0] if matriculant_count else None)}\n"
        "- Applicant mean GPA / MCAT: "
        f"{_format_mean(applicant_gpa[0] if applicant_gpa else None)} / "
        f"{_format_mean(applicant_mcat[0] if applicant_mcat else None)}\n"
        "- Matriculant mean GPA / MCAT: "
        f"{_format_mean(matriculant_gpa[0] if matriculant_gpa else None)} / "
        f"{_format_mean(matriculant_mcat[0] if matriculant_mcat else None)}\n"
        "- This is major-group context only; it should not change school rankings."
    )


def get_state_academic_context(state: Any) -> str | None:
    state_name = _canonical_state_name(state)
    if state_name is None:
        return None

    applicant_data = load_table("applicant_state")
    matriculant_data = load_table("matriculant_state")

    applicant_matches = applicant_data[
        applicant_data["state"].map(_normalize_text)
        == _normalize_text(state_name)
    ]
    matriculant_matches = matriculant_data[
        matriculant_data["state"].map(_normalize_text)
        == _normalize_text(state_name)
    ]
    if applicant_matches.empty and matriculant_matches.empty:
        return None

    applicant_count = _latest_metric_value(
        applicant_matches,
        "Total Applicants",
        "Count",
    )
    applicant_gpa = _latest_metric_value(
        applicant_matches,
        "GPA Total",
        "Mean",
    )
    applicant_mcat = _latest_metric_value(
        applicant_matches,
        "Total MCAT",
        "Mean",
    )
    matriculant_gpa = _latest_metric_value(
        matriculant_matches,
        "GPA Total",
        "Mean",
    )
    matriculant_mcat = _latest_metric_value(
        matriculant_matches,
        "Total MCAT",
        "Mean",
    )

    academic_year = next(
        (
            year
            for value in (
                applicant_count,
                applicant_gpa,
                applicant_mcat,
                matriculant_gpa,
                matriculant_mcat,
            )
            if value is not None
            for year in (value[1],)
            if year is not None
        ),
        "latest available",
    )

    return (
        "Home-state academic context:\n"
        f"- State of legal residence: {state_name}\n"
        f"- Academic year: {academic_year}\n"
        f"- Applicants from this state: "
        f"{_format_count(applicant_count[0] if applicant_count else None)}\n"
        "- Applicant mean GPA / MCAT: "
        f"{_format_mean(applicant_gpa[0] if applicant_gpa else None)} / "
        f"{_format_mean(applicant_mcat[0] if applicant_mcat else None)}\n"
        "- Matriculant mean GPA / MCAT: "
        f"{_format_mean(matriculant_gpa[0] if matriculant_gpa else None)} / "
        f"{_format_mean(matriculant_mcat[0] if matriculant_mcat else None)}\n"
        "- These are legal-residence aggregates, not school-specific outcomes."
    )


def get_national_pipeline_context() -> str | None:
    dataframe = load_table("medical_pipeline")
    row = _latest_row(dataframe)
    if row is None:
        return None

    return (
        "National MD application context:\n"
        f"- Academic year: {row.get('academic_year', 'Unknown')}\n"
        f"- Applicants: {_format_count(row.get('applicants'))}\n"
        f"- Matriculants: {_format_count(row.get('matriculants'))}\n"
        "- National applicant-to-matriculant ratio: "
        f"{_format_percent(row.get('applicant_to_matriculant_ratio_percent'))}\n"
        f"- Total enrollment: {_format_count(row.get('enrollment'))}\n"
        "- This is a national aggregate, not an individual-school "
        "acceptance rate."
    )


def _canonical_state_name(state: Any) -> str | None:
    if state is None:
        return None

    text = str(state).strip()
    if not text:
        return None

    abbreviation = text.upper()
    if abbreviation in STATE_ABBREVIATIONS:
        return STATE_ABBREVIATIONS[abbreviation]
    return text


def get_state_context(state: Any) -> str | None:
    state_name = _canonical_state_name(state)
    if state_name is None:
        return None

    dataframe = load_table("state_outcomes")
    target = _normalize_text(state_name)
    matches = dataframe[
        dataframe["entity_name"].map(_normalize_text) == target
    ]
    if matches.empty:
        return None

    row = matches.iloc[0]
    return (
        "State-of-legal-residence context:\n"
        f"- State: {row.get('entity_name', state_name)}\n"
        f"- Applicants: {_format_count(row.get('applicants'))}\n"
        f"- Matriculants: {_format_count(row.get('matriculants'))}\n"
        "- Applicant-to-matriculant ratio: "
        f"{_format_percent(row.get('overall_matriculation_rate_percent'))}\n"
        "- Matriculated in state: "
        f"{_format_percent(row.get('matriculated_in_state_percent'))}\n"
        "- Matriculated out of state: "
        f"{_format_percent(row.get('matriculated_out_of_state_percent'))}\n"
        "- Did not matriculate: "
        f"{_format_percent(row.get('did_not_matriculate_percent'))}\n"
        "- These figures describe applicants from the state, not the "
        "acceptance rate of schools located there."
    )


def _best_institution_match(
    institution_name: str,
    dataframe: pd.DataFrame,
) -> pd.Series | None:
    if dataframe.empty or "institution_name" not in dataframe.columns:
        return None

    target = _normalize_text(institution_name)
    if not target:
        return None

    normalized = dataframe["institution_name"].map(_normalize_text)
    exact = dataframe[normalized == target]
    if not exact.empty:
        return exact.iloc[0]

    scores = normalized.map(
        lambda candidate: SequenceMatcher(
            None,
            target,
            candidate,
        ).ratio()
    )
    best_index = scores.idxmax()
    if float(scores.loc[best_index]) < 0.80:
        return None
    return dataframe.loc[best_index]


def get_undergraduate_institution_context(
    institution_name: Any,
) -> str | None:
    if institution_name is None or not str(institution_name).strip():
        return None

    dataframe = load_table("undergraduate_demographics")
    row = _best_institution_match(str(institution_name), dataframe)
    if row is None:
        return None

    location_parts = [
        str(row.get("city")).strip()
        if pd.notna(row.get("city"))
        else "",
        str(row.get("state_or_province")).strip()
        if pd.notna(row.get("state_or_province"))
        else "",
    ]
    location = ", ".join(part for part in location_parts if part)

    lines = [
        "Undergraduate-institution context:",
        f"- Matched institution: {row.get('institution_name')}",
    ]
    if location:
        lines.append(f"- Location: {location}")
    lines.extend([
        f"- Academic year: {row.get('academic_year', 'Unknown')}",
        "- Applicants to U.S. MD-granting medical schools: "
        f"{_format_count(row.get('total_applicants'))}",
        "- This reports applicant volume from the institution, not the "
        "institution's medical-school acceptance rate.",
    ])
    return "\n".join(lines)


ACCESS_INDICATORS = {
    "first_generation": "First Generation College Student",
    "daca": "DACA Status",
    "fee_assistance": "Applied Fee Assistance Program Benefits",
}


def get_access_context(profile: dict[str, Any]) -> str | None:
    requested_indicators = [
        indicator_name
        for profile_field, indicator_name in ACCESS_INDICATORS.items()
        if _is_affirmative(
            _first_profile_value(profile, profile_field)
        )
    ]
    if not requested_indicators:
        return None

    dataframe = load_table("socioeconomic_access_summary")
    lines = ["Applicant-relevant access context:"]

    for indicator_name in requested_indicators:
        matches = dataframe[
            dataframe["indicator_name"].astype(str) == indicator_name
        ]
        if matches.empty:
            continue

        row = matches.iloc[0]
        lines.extend([
            f"- {indicator_name}:",
            "  - Applicants: "
            f"{_format_count(row.get('applicant_count'))} "
            f"({_format_percent(row.get('applicant_percent_of_total'))})",
            "  - Acceptees: "
            f"{_format_count(row.get('acceptee_count'))} "
            f"({_format_percent(row.get('acceptee_percent_of_total'))})",
            "  - Matriculants: "
            f"{_format_count(row.get('matriculant_count'))} "
            f"({_format_percent(row.get('matriculant_percent_of_total'))})",
            "  - Aggregate acceptance ratio: "
            f"{_format_percent(row.get('acceptance_ratio_percent'))}",
        ])

    if len(lines) == 1:
        return None

    lines.append(
        "- These are national descriptive aggregates and must not be "
        "treated as personal admissions probabilities."
    )
    return "\n".join(lines)


def get_context_for_profile(profile: dict[str, Any]) -> str:
    """
    Build a compact, profile-relevant evidence block.

    The service intentionally does not dump every CSV into the prompt.
    It selects only context connected to the applicant plus one current
    national summary.
    """
    sections: list[str] = []

    gpa = _to_float(_first_profile_value(profile, "gpa"))
    mcat = _to_int(_first_profile_value(profile, "mcat"))

    if gpa is None:
        sections.append(
            "GPA/MCAT aggregate context unavailable because GPA is missing."
        )
    elif mcat is None:
        sections.append(
            "GPA/MCAT aggregate context:\n"
            f"- Applicant GPA: {gpa:.2f}\n"
            "- MCAT score: Not available\n"
            "- The GPA/MCAT grid cannot be used until an MCAT score is "
            "available."
        )
    else:
        try:
            sections.append(
                format_acceptance_context(
                    get_acceptance_context(gpa, mcat)
                )
            )
        except FileNotFoundError:
            sections.append(
                "GPA/MCAT aggregate context unavailable because "
                "aamc_a23_acceptance_grid.csv was not found in "
                "data/cleaned/clean_MCAT_and_GPA."
            )

    optional_sections = (
        _safe_context_section(get_national_academic_context),
        _safe_context_section(
            get_major_academic_context,
            _first_profile_value(profile, "major"),
        ),
        _safe_context_section(
            get_state_academic_context,
            _first_profile_value(profile, "state"),
        ),
        _safe_context_section(
            get_state_context,
            _first_profile_value(profile, "state"),
        ),
        _safe_context_section(
            get_undergraduate_institution_context,
            _first_profile_value(
                profile,
                "undergraduate_institution",
            ),
        ),
        _safe_context_section(get_access_context, profile),
        _safe_context_section(get_national_pipeline_context),
    )

    sections.extend(
        section
        for section in optional_sections
        if section
    )

    sections.append(
        "Use restrictions:\n"
        "- Treat all AAMC values as historical, aggregate context.\n"
        "- Do not present aggregate ratios as a student's personal chance.\n"
        "- Do not use demographic or access data to change school rankings."
    )

    return "\n\n".join(sections)
