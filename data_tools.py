import pandas as pd
from datetime import datetime


DATA_PATH = "data/medical_school_master.csv"


def load_school_data():
    """
    Loads the cleaned medical school master CSV.
    """
    df = pd.read_csv(DATA_PATH)

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


def search_schools_by_name(query: str, limit: int = 10):
    """
    Searches schools by name.
    """
    df = load_school_data()

    matches = df[
        df["school_name"].str.contains(query, case=False, na=False)
    ]

    return matches.head(limit).to_dict(orient="records")


def filter_schools_by_stats(mcat: int, gpa: float, state: str | None = None):
    """
    Filters schools where applicant stats are within a reasonable range.
    This is not perfect admissions logic, but it gives the agent grounded data.
    """
    df = load_school_data()

    # Basic safety checks
    if "median_mcat" not in df.columns or "median_gpa" not in df.columns:
        raise ValueError("CSV must contain median_mcat and median_gpa columns.")

    # Keep schools where the applicant is not wildly below the median
    filtered = df[
        (df["median_mcat"].isna() | (df["median_mcat"] <= mcat + 4)) &
        (df["median_gpa"].isna() | (df["median_gpa"] <= gpa + 0.15))
    ]

    if state and "state" in df.columns:
        in_state = filtered[filtered["state"].str.upper() == state.upper()]
        out_state = filtered[filtered["state"].str.upper() != state.upper()]
        filtered = pd.concat([in_state, out_state])

    return filtered.to_dict(orient="records")


def get_upcoming_deadlines(days_ahead: int = 30):
    """
    Finds schools with upcoming AMCAS deadlines.
    """
    df = load_school_data()

    if "application_deadline" not in df.columns:
        raise ValueError("CSV must contain application_deadline column.")

    df["application_deadline"] = pd.to_datetime(
        df["application_deadline"],
        errors="coerce"
    )

    today = pd.Timestamp.today().normalize()
    cutoff = today + pd.Timedelta(days=days_ahead)

    upcoming = df[
        (df["application_deadline"] >= today) &
        (df["application_deadline"] <= cutoff)
    ]

    return upcoming.sort_values("application_deadline").to_dict(orient="records")


def rank_schools_for_applicant(mcat: int, gpa: float, state: str, interests: str):
    """
    Creates a rough numerical fit score.
    This gives the agent a ranked list instead of making it guess.
    """
    df = load_school_data()

    df["fit_score"] = 0

    if "median_mcat" in df.columns:
        df["fit_score"] += (10 - abs(df["median_mcat"] - mcat)).clip(lower=0)

    if "median_gpa" in df.columns:
        df["fit_score"] += (1 - abs(df["median_gpa"] - gpa)).clip(lower=0) * 10

    if "state" in df.columns:
        df.loc[df["state"].str.upper() == state.upper(), "fit_score"] += 5

    if "mission" in df.columns:
        interest_terms = interests.lower().split()
        for term in interest_terms:
            df.loc[
                df["mission"].str.lower().str.contains(term, na=False),
                "fit_score"
            ] += 1

    return (
        df.sort_values("fit_score", ascending=False)
        .head(25)
        .to_dict(orient="records")
    )