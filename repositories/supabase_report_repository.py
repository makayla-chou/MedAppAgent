import json
from typing import Any

import pandas as pd


def _json_safe(value: Any) -> Any:
    """
    Convert ordinary Python data into strict JSON-compatible data.

    This rejects NaN and infinity instead of sending invalid JSON to Supabase.
    """
    serialized = json.dumps(
        value,
        default=str,
        allow_nan=False,
    )
    return json.loads(serialized)


def _dataframe_to_records(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError("ranked_schools must be a pandas DataFrame.")

    # pandas converts missing values to JSON null and numpy values to ordinary
    # JSON numbers and strings.
    return json.loads(
        dataframe.to_json(
            orient="records",
            date_format="iso",
        )
    )


def save_report_to_supabase(
    supabase_client,
    user_id: str,
    run_id: str,
    generated_at_utc: str,
    student_name: str,
    final_report: str,
    ranked_schools: pd.DataFrame,
    warnings: list[str],
    profile_snapshot: dict[str, Any],
) -> dict[str, Any]:
    """
    Insert one immutable report run for the authenticated user.

    The database's row-level security policy must require auth.uid() to equal
    user_id. A unique database constraint on (user_id, run_id) prevents the
    same report run from being inserted twice.
    """
    clean_user_id = str(user_id).strip()
    clean_run_id = str(run_id).strip()
    clean_generated_at = str(generated_at_utc).strip()
    clean_student_name = str(student_name).strip()
    clean_final_report = str(final_report).strip()

    if not clean_user_id:
        raise ValueError("A user_id is required.")

    if not clean_run_id:
        raise ValueError("A report run_id is required.")

    if not clean_generated_at:
        raise ValueError("generated_at_utc is required.")

    if not clean_student_name:
        raise ValueError("student_name is required.")

    if not clean_final_report:
        raise ValueError("final_report cannot be empty.")

    if not isinstance(profile_snapshot, dict):
        raise ValueError("profile_snapshot must be a dictionary.")

    payload = {
        "user_id": clean_user_id,
        "run_id": clean_run_id,
        "generated_at_utc": clean_generated_at,
        "student_name": clean_student_name,
        "final_report": clean_final_report,
        "ranked_schools": _dataframe_to_records(ranked_schools),
        "warnings": _json_safe(list(warnings)),
        "profile_snapshot": _json_safe(profile_snapshot),
    }

    response = (
        supabase_client
        .table("reports")
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Supabase did not return the saved report.")

    return response.data[0]


def load_report_from_supabase(
    supabase_client,
    user_id: str,
    run_id: str,
) -> dict[str, Any] | None:
    """
    Load one report run owned by the authenticated user.
    """
    clean_user_id = str(user_id).strip()
    clean_run_id = str(run_id).strip()

    if not clean_user_id:
        raise ValueError("A user_id is required.")

    if not clean_run_id:
        raise ValueError("A report run_id is required.")

    response = (
        supabase_client
        .table("reports")
        .select("*")
        .eq("user_id", clean_user_id)
        .eq("run_id", clean_run_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]
