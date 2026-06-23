from typing import Any

import pandas as pd

from config import (
    ACADEMIC_GPA_WEIGHT,
    ACADEMIC_MCAT_WEIGHT,
    GPA_COMPARISON_SCALE,
    MCAT_COMPARISON_SCALE,
)
from repositories.school_repository import parse_number
from scoring.classification import classify_academic_z
from scoring.utils import z_to_score


def calculate_academic_score(
    student: dict[str, Any],
    school: pd.Series,
) -> dict[str, Any]:
    academics = student.get("academics", {})
    student_gpa = parse_number(academics.get("overall_gpa"))
    student_mcat = parse_number(academics.get("mcat_total"))
    school_gpa = parse_number(school.get("school_gpa"))
    school_mcat = parse_number(school.get("school_mcat"))
    minimum_mcat = parse_number(school.get("minimum_mcat_numeric"))

    reasons: list[str] = []
    warnings: list[str] = []

    gpa_z = None
    gpa_position_score = None
    if student_gpa is not None and school_gpa is not None:
        gpa_difference = round(student_gpa - school_gpa, 2)
        gpa_z = gpa_difference / GPA_COMPARISON_SCALE
        gpa_position_score = z_to_score(gpa_z)
        reasons.append(
            f"Applicant GPA is {gpa_difference:+.2f} relative to the school's reported average GPA of {school_gpa:.2f}."
        )
    else:
        gpa_difference = None
        warnings.append("Applicant or school GPA data is missing.")

    mcat_z = None
    mcat_position_score = None
    if student_mcat is not None and school_mcat is not None:
        mcat_difference = round(student_mcat - school_mcat, 1)
        mcat_z = mcat_difference / MCAT_COMPARISON_SCALE
        mcat_position_score = z_to_score(mcat_z)
        reasons.append(
            f"Applicant MCAT is {mcat_difference:+.0f} relative to the school's reported average MCAT of {school_mcat:.0f}."
        )
    else:
        mcat_difference = None
        if student_mcat is None:
            warnings.append(
                "Applicant MCAT is missing, so academic competitiveness cannot be classified."
            )
        else:
            warnings.append("The school's reported average MCAT is missing.")

    below_minimum = False
    if student_mcat is not None and minimum_mcat is not None:
        below_minimum = student_mcat < minimum_mcat
        if below_minimum:
            warnings.append(
                f"Applicant MCAT of {student_mcat:.0f} is below the listed minimum of {minimum_mcat:.0f}."
            )
        else:
            reasons.append(
                f"Applicant meets the listed minimum MCAT of {minimum_mcat:.0f}."
            )

    if below_minimum:
        academic_eligibility_status = "Not Eligible"
    elif student_mcat is None and minimum_mcat is not None:
        academic_eligibility_status = "Insufficient Data"
        warnings.append(
            "The school lists a minimum MCAT, but the applicant has no MCAT score to compare."
        )
    else:
        academic_eligibility_status = "Eligible"

    composite_z = None
    academic_score = None
    if gpa_z is not None and mcat_z is not None:
        composite_z = (
            ACADEMIC_GPA_WEIGHT * gpa_z
            + ACADEMIC_MCAT_WEIGHT * mcat_z
        )
        academic_score = z_to_score(composite_z)

    return {
        "academic_score": academic_score,
        "academic_category": classify_academic_z(composite_z),
        "academic_composite_z": round(composite_z, 3) if composite_z is not None else None,
        "gpa_difference": gpa_difference,
        "mcat_difference": mcat_difference,
        "gpa_position_score": gpa_position_score,
        "mcat_position_score": mcat_position_score,
        "below_minimum_mcat": below_minimum,
        "academic_eligibility_status": academic_eligibility_status,
        "academic_reasons": reasons,
        "academic_warnings": warnings,
    }
