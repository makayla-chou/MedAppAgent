from typing import Any

import pandas as pd

from repositories.school_repository import normalize_state_code


def _to_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_bool(value: Any) -> bool:
    if value is None or pd.isna(value):
        return False

    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}

    return bool(value)


def _classify_public_out_of_state_access(
    matriculants_out_of_state_pct: float | None,
) -> tuple[str, float]:
    """
    Classify observed out-of-state access for a public school.

    The percentage is descriptive AAMC A-1 data, not an official residency
    eligibility rule. Priority values remain below the priority assigned to
    an out-of-state private school.
    """
    if matriculants_out_of_state_pct is None:
        return "Unknown out-of-state access", 0.8

    if matriculants_out_of_state_pct == 0:
        return "No reported out-of-state matriculants", 0.2

    if matriculants_out_of_state_pct < 10:
        return "Very limited out-of-state access", 0.6

    if matriculants_out_of_state_pct < 25:
        return "Limited out-of-state access", 1.0

    if matriculants_out_of_state_pct < 50:
        return "Moderate out-of-state access", 1.5

    return "High out-of-state access", 1.8


def evaluate_residency_context(
    student: dict[str, Any],
    school: pd.Series,
) -> dict[str, Any]:
    """
    Evaluate residency context separately from academic and preference scoring.

    School-specific AAMC A-1 application and matriculant percentages are used
    to describe observed out-of-state access. These percentages do not replace
    official school eligibility rules.
    """
    basic = student.get("basic_information", {})

    student_state_code = normalize_state_code(
        basic.get("state_residency")
    )
    school_state_code = normalize_state_code(
        school.get("school_state_code")
    )
    is_public = school.get("is_public_bool")

    aamc_match_status = school.get(
        "aamc_residency_match_status"
    )
    aamc_school_name = school.get(
        "aamc_a1_medical_school"
    )
    academic_year = school.get(
        "aamc_residency_academic_year"
    )
    aamc_residency_state_code = school.get(
        "aamc_residency_state_code"
    )
    aamc_residency_scope = school.get(
        "aamc_residency_scope"
    )
    aamc_residency_shared_across_campuses = _to_bool(
        school.get("aamc_residency_shared_across_campuses")
    )
    aamc_residency_state_mismatch = _to_bool(
        school.get("aamc_residency_state_mismatch")
    )

    applications_out_of_state_pct = _to_float(
        school.get("aamc_applications_out_of_state_pct")
    )
    matriculants_out_of_state_pct = _to_float(
        school.get("aamc_matriculants_out_of_state_pct")
    )

    reasons: list[str] = []
    warnings: list[str] = []

    base_result = {
        "aamc_residency_match_status": aamc_match_status,
        "aamc_residency_school_name": aamc_school_name,
        "aamc_residency_academic_year": academic_year,
        "aamc_residency_state_code": aamc_residency_state_code,
        "aamc_residency_scope": aamc_residency_scope,
        "aamc_residency_shared_across_campuses": (
            aamc_residency_shared_across_campuses
        ),
        "aamc_residency_state_mismatch": (
            aamc_residency_state_mismatch
        ),
        "applications_out_of_state_pct": applications_out_of_state_pct,
        "matriculants_out_of_state_pct": matriculants_out_of_state_pct,
    }

    if aamc_residency_shared_across_campuses:
        warnings.append(
            "AAMC residency statistics are reported at the institution level and are shared across multiple campus rows."
        )

    if aamc_residency_state_mismatch:
        state_note = (
            f" The AAMC record is associated with {aamc_residency_state_code}."
            if aamc_residency_state_code
            else ""
        )
        warnings.append(
            "The campus state differs from the state attached to the shared AAMC residency record."
            + state_note
        )

    if not student_state_code or not school_state_code:
        return {
            **base_result,
            "residency_context": "Unknown",
            "residency_access_category": "Unknown",
            "residency_priority": 0.0,
            "residency_eligibility_status": "Insufficient Data",
            "residency_reasons": reasons,
            "residency_warnings": [
                "Applicant or school state data is missing, so residency eligibility cannot be confirmed."
            ],
        }

    in_state = student_state_code == school_state_code

    if in_state and is_public is True:
        context = "In-state public"
        access_category = "In-state"
        priority = 4.0
        eligibility_status = "Eligible"
        reasons.append(
            "This is a public school in the applicant's state of residency."
        )

    elif in_state:
        context = "In-state"
        access_category = "In-state"
        priority = 3.0
        eligibility_status = "Eligible"
        reasons.append(
            "This school is in the applicant's state of residency."
        )

    elif is_public is False:
        context = "Out-of-state private"
        access_category = "Private school"
        priority = 2.0
        eligibility_status = "Eligible"
        reasons.append(
            "The school is private, so state residency is usually less central than at a public school."
        )

        if matriculants_out_of_state_pct is not None:
            reasons.append(
                f"AAMC A-1 reports {matriculants_out_of_state_pct:.1f}% of matriculants were out of state"
                + (
                    f" in {academic_year}."
                    if academic_year is not None and not pd.isna(academic_year)
                    else "."
                )
            )

    elif is_public is True:
        access_category, priority = (
            _classify_public_out_of_state_access(
                matriculants_out_of_state_pct
            )
        )
        context = f"Out-of-state public — {access_category.lower()}"

        if (
            matriculants_out_of_state_pct is not None
            and matriculants_out_of_state_pct > 0
        ):
            eligibility_status = "Verify Eligibility"
            reasons.append(
                "The school is public and out of state, but its AAMC A-1 data shows that out-of-state students matriculated."
            )
            reasons.append(
                f"AAMC A-1 reports {matriculants_out_of_state_pct:.1f}% of matriculants were out of state"
                + (
                    f" in {academic_year}."
                    if academic_year is not None and not pd.isna(academic_year)
                    else "."
                )
            )
            warnings.append(
                "Observed out-of-state matriculation does not guarantee eligibility or admission; official residency requirements should still be reviewed."
            )

        elif matriculants_out_of_state_pct == 0:
            eligibility_status = "Verify Eligibility"
            warnings.append(
                "AAMC A-1 reports no out-of-state matriculants for the available year. Verify whether the school restricts out-of-state applicants or simply enrolled none."
            )

        else:
            eligibility_status = "Verify Eligibility"
            warnings.append(
                "This is a public out-of-state school, but school-specific AAMC matriculant residency data is unavailable. Official out-of-state eligibility must be verified."
            )

        if applications_out_of_state_pct is not None:
            reasons.append(
                f"AAMC A-1 reports {applications_out_of_state_pct:.1f}% of applications were from out-of-state applicants."
            )

    else:
        context = "Public/private status unknown"
        access_category = "Unknown"
        priority = 0.0
        eligibility_status = "Insufficient Data"
        warnings.append(
            "The school's public/private status is missing, so out-of-state residency eligibility cannot be confirmed."
        )

    return {
        **base_result,
        "residency_context": context,
        "residency_access_category": access_category,
        "residency_priority": priority,
        "residency_eligibility_status": eligibility_status,
        "residency_reasons": reasons,
        "residency_warnings": warnings,
    }
