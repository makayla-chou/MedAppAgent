from pathlib import Path
import re
from typing import Any

import pandas as pd


STATE_NAME_TO_CODE = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "Puerto Rico": "PR",
}

REGION_ALIASES = {
    "West Coast": "West",
    "No geographic preference": "No geographic preference",
}

DEFAULT_AAMC_RESIDENCY_FILE = Path(
    "data/cleaned/aamc_a1_school_residency.csv"
)

AAMC_RESIDENCY_COLUMN_MAP = {
    "school_state_code": "aamc_residency_state_code",
    "aamc_a1_medical_school": "aamc_a1_medical_school",
    "match_status": "aamc_residency_match_status",
    "applications_total": "aamc_applications_total",
    "applications_in_state_pct": "aamc_applications_in_state_pct",
    "applications_out_of_state_pct": "aamc_applications_out_of_state_pct",
    "matriculants_total": "aamc_matriculants_total",
    "matriculants_in_state_pct": "aamc_matriculants_in_state_pct",
    "matriculants_out_of_state_pct": "aamc_matriculants_out_of_state_pct",
    "academic_year": "aamc_residency_academic_year",
}


def _extract_numbers(value: Any) -> list[float]:
    if value is None or pd.isna(value):
        return []

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "n/a", "nr", "not available"}:
        return []

    return [
        float(number)
        for number in re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))
    ]


def parse_number(value: Any) -> float | None:
    numbers = _extract_numbers(value)
    return numbers[0] if numbers else None


def parse_average_number(value: Any) -> float | None:
    """Parse a reported average; use the midpoint only for a true numeric range."""
    numbers = _extract_numbers(value)
    if not numbers:
        return None

    text = str(value)
    numeric_range = re.search(
        r"(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)",
        text,
    )
    if numeric_range:
        lower = float(numeric_range.group(1))
        upper = float(numeric_range.group(2))
        return (lower + upper) / 2

    return numbers[0]


def parse_minimum_number(value: Any) -> float | None:
    """Parse the lower bound of a listed minimum or minimum range."""
    return parse_number(value)


def parse_boolean(value: Any) -> bool | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip().lower()
    if text in {"true", "yes", "1", "public"}:
        return True
    if text in {"false", "no", "0", "private"}:
        return False
    return None


def normalize_state_code(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    if len(text) == 2:
        return text.upper()

    return STATE_NAME_TO_CODE.get(text.title())


def normalize_region(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    return REGION_ALIASES.get(text, text)


def _slugify_identifier(value: Any) -> str:
    """Convert a value into a stable lowercase identifier component."""
    if value is None or pd.isna(value):
        return "unknown"

    text = str(value).strip().lower()
    if not text:
        return "unknown"

    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def _add_canonical_school_ids(
    schools: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add one stable identifier per campus.

    School names alone are not unique. For example, Mayo Clinic Alix School
    of Medicine has separate Scottsdale and Rochester campus rows. The ID
    combines school name, state, and city so those rows remain distinct.
    """
    if "school_name" not in schools.columns:
        raise ValueError(
            "School data must contain a school_name column."
        )

    school_ids = []
    for _, school in schools.iterrows():
        school_ids.append(
            "__".join(
                [
                    _slugify_identifier(school.get("school_name")),
                    _slugify_identifier(school.get("school_state_code")),
                    _slugify_identifier(school.get("school_city")),
                ]
            )
        )

    schools = schools.copy()
    schools["school_id"] = school_ids

    duplicate_ids = schools.loc[
        schools["school_id"].duplicated(keep=False),
        [
            "school_id",
            "school_name",
            "school_state_code",
            "school_city",
        ],
    ]
    if not duplicate_ids.empty:
        duplicate_text = duplicate_ids.to_dict(orient="records")
        raise ValueError(
            "Canonical school IDs are not unique. Check for duplicate "
            f"campus rows: {duplicate_text}"
        )

    return schools


def _add_empty_aamc_residency_columns(
    schools: pd.DataFrame,
) -> pd.DataFrame:
    for output_column in AAMC_RESIDENCY_COLUMN_MAP.values():
        if output_column not in schools.columns:
            schools[output_column] = pd.NA

    return schools


def _merge_aamc_residency_data(
    schools: pd.DataFrame,
    residency_filename: str | Path | None,
) -> pd.DataFrame:
    """
    Add school-level AAMC A-1 residency composition data.

    The curated crosswalk uses school names from the main dataset. Repeated
    identical AAMC rows are collapsed before merging so the number of campus
    rows cannot increase. When multiple campus rows share one AAMC school
    record, the merged data is explicitly labeled as institution-level data
    shared across those campuses.
    """
    if residency_filename is None:
        schools = _add_empty_aamc_residency_columns(schools)
        schools["aamc_residency_scope"] = "Unavailable"
        schools["aamc_residency_shared_across_campuses"] = False
        schools["aamc_residency_state_mismatch"] = False
        return schools

    residency_path = Path(residency_filename)
    if not residency_path.exists():
        schools = _add_empty_aamc_residency_columns(schools)
        schools["aamc_residency_scope"] = "Unavailable"
        schools["aamc_residency_shared_across_campuses"] = False
        schools["aamc_residency_state_mismatch"] = False
        return schools

    residency = pd.read_csv(residency_path)

    required_columns = {
        "school_name",
        *AAMC_RESIDENCY_COLUMN_MAP.keys(),
    }
    missing_columns = required_columns.difference(residency.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(
            "AAMC residency data is missing required columns: "
            f"{missing_text}"
        )

    selected_columns = [
        "school_name",
        *AAMC_RESIDENCY_COLUMN_MAP.keys(),
    ]
    residency = residency[selected_columns].copy()

    duplicate_groups = residency.groupby(
        "school_name",
        dropna=False,
    )

    conflicting_duplicates: list[str] = []
    comparison_columns = list(AAMC_RESIDENCY_COLUMN_MAP.keys())

    for school_name, group in duplicate_groups:
        if len(group) <= 1:
            continue

        unique_rows = group[comparison_columns].drop_duplicates()
        if len(unique_rows) > 1:
            conflicting_duplicates.append(str(school_name))

    if conflicting_duplicates:
        raise ValueError(
            "AAMC residency data contains conflicting duplicate rows for: "
            + ", ".join(sorted(conflicting_duplicates))
        )

    residency = residency.drop_duplicates(
        subset=["school_name"],
        keep="first",
    )

    residency = residency.rename(
        columns=AAMC_RESIDENCY_COLUMN_MAP
    )

    numeric_columns = [
        "aamc_applications_total",
        "aamc_applications_in_state_pct",
        "aamc_applications_out_of_state_pct",
        "aamc_matriculants_total",
        "aamc_matriculants_in_state_pct",
        "aamc_matriculants_out_of_state_pct",
    ]
    for column in numeric_columns:
        residency[column] = pd.to_numeric(
            residency[column],
            errors="coerce",
        )

    original_row_count = len(schools)
    campus_counts = schools.groupby(
        "school_name",
        dropna=False,
    )["school_id"].transform("nunique")

    schools_for_merge = schools.copy()
    schools_for_merge["_campus_count_for_school_name"] = campus_counts

    merged = schools_for_merge.merge(
        residency,
        on="school_name",
        how="left",
        validate="many_to_one",
    )

    if len(merged) != original_row_count:
        raise RuntimeError(
            "AAMC residency merge changed the number of school rows."
        )

    matched = merged["aamc_residency_match_status"].eq("Matched")
    shared = matched & merged["_campus_count_for_school_name"].gt(1)

    merged["aamc_residency_shared_across_campuses"] = shared
    merged["aamc_residency_scope"] = "Unavailable"
    merged.loc[matched, "aamc_residency_scope"] = (
        "School-level AAMC data"
    )
    merged.loc[shared, "aamc_residency_scope"] = (
        "Institution-level AAMC data shared across campus rows"
    )

    campus_state = merged["school_state_code"].fillna("")
    aamc_state = merged["aamc_residency_state_code"].fillna("")
    merged["aamc_residency_state_mismatch"] = (
        matched
        & campus_state.ne("")
        & aamc_state.ne("")
        & campus_state.ne(aamc_state)
    )

    return merged.drop(
        columns=["_campus_count_for_school_name"]
    )


def load_schools(
    filename: str | Path,
    residency_filename: str | Path | None = DEFAULT_AAMC_RESIDENCY_FILE,
) -> pd.DataFrame:
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"School data file not found: {path}")

    schools = pd.read_csv(path)
    schools.columns = (
        schools.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    schools["school_state"] = schools.get("state_aamc")

    state_code_source = schools.get("state_shemmassian")
    if state_code_source is None:
        state_code_source = schools.get("state_aamc")

    schools["school_state_code"] = state_code_source.apply(normalize_state_code)

    if "state_aamc" in schools.columns:
        missing_code = schools["school_state_code"].isna()
        schools.loc[missing_code, "school_state_code"] = schools.loc[
            missing_code, "state_aamc"
        ].apply(normalize_state_code)

    schools["school_degree_type"] = (
        schools.get("degree_type", pd.Series(index=schools.index, dtype="object"))
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .replace("", pd.NA)
    )
    schools["school_gpa"] = schools.get(
        "average_gpa", pd.Series(index=schools.index, dtype="object")
    ).apply(parse_average_number)
    schools["school_mcat"] = schools.get(
        "average_mcat", pd.Series(index=schools.index, dtype="object")
    ).apply(parse_average_number)
    schools["minimum_mcat_numeric"] = schools.get(
        "minimum_mcat", pd.Series(index=schools.index, dtype="object")
    ).apply(parse_minimum_number)
    schools["is_public_bool"] = schools.get(
        "is_public", pd.Series(index=schools.index, dtype="object")
    ).apply(parse_boolean)
    schools["school_city"] = schools.get("campus_city")
    schools["school_region"] = schools.get(
        "region", pd.Series(index=schools.index, dtype="object")
    ).apply(normalize_region)
    schools["school_setting"] = schools.get("setting")

    schools = _add_canonical_school_ids(schools)

    schools = _merge_aamc_residency_data(
        schools=schools,
        residency_filename=residency_filename,
    )

    return schools


def search_schools_by_name(
    schools: pd.DataFrame,
    query: str,
    limit: int = 10,
) -> pd.DataFrame:
    if not query.strip():
        return schools.head(0).copy()

    return schools[
        schools["school_name"].str.contains(query, case=False, na=False)
    ].head(limit).copy()
