from collections import deque
from typing import Any

import pandas as pd

from repositories.school_repository import (
    normalize_region,
    normalize_state_code,
)


# Land-border connections are used as a transparent approximation of
# geographic proximity. They do not represent exact mileage or travel time.
STATE_NEIGHBORS: dict[str, set[str]] = {
    "AL": {"FL", "GA", "MS", "TN"},
    "AK": set(),
    "AZ": {"CA", "CO", "NM", "NV", "UT"},
    "AR": {"LA", "MO", "MS", "OK", "TN", "TX"},
    "CA": {"AZ", "NV", "OR"},
    "CO": {"AZ", "KS", "NE", "NM", "OK", "UT", "WY"},
    "CT": {"MA", "NY", "RI"},
    "DC": {"MD", "VA"},
    "DE": {"MD", "NJ", "PA"},
    "FL": {"AL", "GA"},
    "GA": {"AL", "FL", "NC", "SC", "TN"},
    "HI": set(),
    "IA": {"IL", "MN", "MO", "NE", "SD", "WI"},
    "ID": {"MT", "NV", "OR", "UT", "WA", "WY"},
    "IL": {"IA", "IN", "KY", "MO", "WI"},
    "IN": {"IL", "KY", "MI", "OH"},
    "KS": {"CO", "MO", "NE", "OK"},
    "KY": {"IL", "IN", "MO", "OH", "TN", "VA", "WV"},
    "LA": {"AR", "MS", "TX"},
    "MA": {"CT", "NH", "NY", "RI", "VT"},
    "MD": {"DC", "DE", "PA", "VA", "WV"},
    "ME": {"NH"},
    "MI": {"IN", "OH", "WI"},
    "MN": {"IA", "ND", "SD", "WI"},
    "MO": {"AR", "IA", "IL", "KS", "KY", "NE", "OK", "TN"},
    "MS": {"AL", "AR", "LA", "TN"},
    "MT": {"ID", "ND", "SD", "WY"},
    "NC": {"GA", "SC", "TN", "VA"},
    "ND": {"MN", "MT", "SD"},
    "NE": {"CO", "IA", "KS", "MO", "SD", "WY"},
    "NH": {"MA", "ME", "VT"},
    "NJ": {"DE", "NY", "PA"},
    "NM": {"AZ", "CO", "OK", "TX", "UT"},
    "NV": {"AZ", "CA", "ID", "OR", "UT"},
    "NY": {"CT", "MA", "NJ", "PA", "VT"},
    "OH": {"IN", "KY", "MI", "PA", "WV"},
    "OK": {"AR", "CO", "KS", "MO", "NM", "TX"},
    "OR": {"CA", "ID", "NV", "WA"},
    "PA": {"DE", "MD", "NJ", "NY", "OH", "WV"},
    "PR": set(),
    "RI": {"CT", "MA"},
    "SC": {"GA", "NC"},
    "SD": {"IA", "MN", "MT", "ND", "NE", "WY"},
    "TN": {"AL", "AR", "GA", "KY", "MS", "MO", "NC", "VA"},
    "TX": {"AR", "LA", "NM", "OK"},
    "UT": {"AZ", "CO", "ID", "NM", "NV", "WY"},
    "VA": {"DC", "KY", "MD", "NC", "TN", "WV"},
    "VT": {"MA", "NH", "NY"},
    "WA": {"ID", "OR"},
    "WI": {"IA", "IL", "MI", "MN"},
    "WV": {"KY", "MD", "OH", "PA", "VA"},
    "WY": {"CO", "ID", "MT", "NE", "SD", "UT"},
}


COMPONENT_WEIGHTS = {
    "degree_type": 0.15,
    "geographic_proximity": 0.35,
    "preferred_region": 0.25,
    "setting": 0.25,
}


SETTING_ORDER = {
    "Urban": 0,
    "Suburban": 1,
    "Town": 2,
    "Rural": 3,
}


DEALBREAKER_ALIASES = {
    "rural": "Rural location",
    "rural location": "Rural location",
    "large city": "Large city",
    "urban": "Large city",
    "strong in-state preference": "Strong in-state preference",
    "far from family": "Far from family",
    "very high tuition": "Very high tuition",
    "religious affiliation": "Religious affiliation",
    "mandatory research requirement": "Mandatory research requirement",
}


UNSCORABLE_DEALBREAKERS = {
    "Very high tuition": (
        "Tuition data is unavailable, so the very-high-tuition dealbreaker "
        "requires verification."
    ),
    "Religious affiliation": (
        "Religious-affiliation data is unavailable, so this dealbreaker "
        "requires verification."
    ),
    "Mandatory research requirement": (
        "Mandatory-research-requirement data is unavailable, so this "
        "dealbreaker requires verification."
    ),
}


SUPPORTED_DEALBREAKERS = {
    "Rural location",
    "Large city",
    "Strong in-state preference",
    "Far from family",
    *UNSCORABLE_DEALBREAKERS.keys(),
}


DEALBREAKER_STATUS_CLEAR = "No Dealbreaker Conflict"
DEALBREAKER_STATUS_VERIFY = "Verify Dealbreaker"
DEALBREAKER_STATUS_EXCLUDED = "Excluded by Dealbreaker"


def _normalize_setting(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip().title()
    if not text:
        return None

    aliases = {
        "City": "Urban",
        "Large City": "Urban",
        "Small City": "Urban",
        "Suburb": "Suburban",
        "Small Town": "Town",
    }
    normalized = aliases.get(text, text)
    return normalized if normalized in SETTING_ORDER else None


def _normalize_dealbreaker(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    return DEALBREAKER_ALIASES.get(text.casefold(), text)


def _state_border_hops(
    student_state_code: str,
    school_state_code: str,
) -> int | None:
    """
    Return the fewest state-border crossings between two state codes.

    Returns -1 when both codes are known but no land-border path exists,
    such as a mainland state to Alaska, Hawaii, or Puerto Rico.
    """
    if (
        student_state_code not in STATE_NEIGHBORS
        or school_state_code not in STATE_NEIGHBORS
    ):
        return None

    if student_state_code == school_state_code:
        return 0

    queue: deque[tuple[str, int]] = deque([(student_state_code, 0)])
    visited = {student_state_code}

    while queue:
        current_state, hops = queue.popleft()

        for neighboring_state in STATE_NEIGHBORS[current_state]:
            if neighboring_state == school_state_code:
                return hops + 1

            if neighboring_state not in visited:
                visited.add(neighboring_state)
                queue.append((neighboring_state, hops + 1))

    return -1


def _proximity_score(border_hops: int) -> float:
    if border_hops < 0:
        return 20.0

    score_by_hops = {
        0: 100.0,
        1: 92.0,
        2: 80.0,
        3: 68.0,
        4: 56.0,
        5: 44.0,
        6: 32.0,
    }
    return score_by_hops.get(border_hops, 20.0)


def _setting_score(
    preferred_setting: str,
    school_setting: str,
) -> float:
    preferred_position = SETTING_ORDER.get(preferred_setting)
    school_position = SETTING_ORDER.get(school_setting)

    if preferred_position is None or school_position is None:
        return 0.0

    difference = abs(preferred_position - school_position)
    score_by_difference = {
        0: 100.0,
        1: 70.0,
        2: 40.0,
        3: 10.0,
    }
    return score_by_difference[difference]


def _weighted_component_average(
    components: dict[str, float],
) -> float | None:
    available_weights = {
        name: COMPONENT_WEIGHTS[name]
        for name in components
        if name in COMPONENT_WEIGHTS
    }

    total_weight = sum(available_weights.values())
    if total_weight == 0:
        return None

    weighted_total = sum(
        components[name] * weight
        for name, weight in available_weights.items()
    )
    return weighted_total / total_weight


def calculate_preference_fit(
    student: dict[str, Any],
    school: pd.Series,
) -> dict[str, Any]:
    preferences = student.get("school_preferences", {})
    basic = student.get("basic_information", {})

    allowed_types = {
        str(value).strip().upper()
        for value in preferences.get("school_types", [])
        if str(value).strip()
    }
    preferred_regions = {
        normalized
        for value in preferences.get("preferred_regions", [])
        if (normalized := normalize_region(value))
    }
    preferred_setting = _normalize_setting(
        preferences.get("setting_preference", "No preference")
    )
    dealbreakers = {
        normalized
        for value in preferences.get("dealbreakers", [])
        if (normalized := _normalize_dealbreaker(value))
    }

    raw_school_type = school.get("school_degree_type")
    school_type = (
        None
        if raw_school_type is None or pd.isna(raw_school_type)
        else str(raw_school_type).strip().upper()
    )
    school_region = normalize_region(school.get("school_region"))
    school_setting = _normalize_setting(school.get("school_setting"))

    student_state_code = normalize_state_code(
        basic.get("state_residency")
    )
    school_state_code = normalize_state_code(
        school.get("school_state_code")
    )

    reasons: list[str] = []
    warnings: list[str] = []
    verification: list[str] = []
    dealbreaker_conflicts: list[str] = []
    dealbreaker_verification: list[str] = []
    components: dict[str, float] = {}

    program_eligibility_status = "Eligible"

    if not school_type:
        program_eligibility_status = "Insufficient Data"
        verification.append(
            "School degree type is missing, so program eligibility cannot be confirmed."
        )
    elif not allowed_types:
        components["degree_type"] = 100.0
        program_eligibility_status = "Insufficient Data"
        verification.append(
            "The applicant did not select any program types, so program eligibility cannot be confirmed."
        )
    elif school_type not in allowed_types:
        components["degree_type"] = 0.0
        program_eligibility_status = "Not Eligible"
        warnings.append(
            f"The applicant did not select {school_type} programs."
        )
    else:
        components["degree_type"] = 100.0
        reasons.append(
            "Program type matches the applicant's selected options: "
            f"{school_type}."
        )

    border_hops: int | None = None
    if student_state_code and school_state_code:
        border_hops = _state_border_hops(
            student_state_code,
            school_state_code,
        )

        if border_hops is None:
            verification.append(
                "Geographic proximity could not be calculated from the "
                "available state codes."
            )
        else:
            components["geographic_proximity"] = _proximity_score(
                border_hops
            )

            if border_hops == 0:
                reasons.append(
                    "School is in the applicant's state of residency."
                )
            elif border_hops == -1:
                warnings.append(
                    "No land-border path exists between the applicant and "
                    "school states; the lowest proximity band was used."
                )
            else:
                reasons.append(
                    "State-based geographic proximity is approximately "
                    f"{border_hops} border crossing(s)."
                )
    else:
        verification.append(
            "Applicant or school state is missing, so geographic proximity "
            "was not scored."
        )

    has_no_region_preference = (
        "No geographic preference" in preferred_regions
    )
    active_region_preferences = {
        region
        for region in preferred_regions
        if region != "No geographic preference"
    }

    if active_region_preferences and not has_no_region_preference:
        if school_region:
            region_match = school_region in active_region_preferences
            components["preferred_region"] = (
                100.0 if region_match else 25.0
            )

            if region_match:
                reasons.append(
                    f"School is in a preferred region: {school_region}."
                )
            else:
                warnings.append(
                    "School is outside the preferred regions: "
                    f"{school_region}."
                )
        else:
            verification.append(
                "School region is missing, so regional preference was not "
                "scored."
            )

    if preferred_setting:
        if school_setting:
            setting_score = _setting_score(
                preferred_setting,
                school_setting,
            )
            components["setting"] = setting_score

            if setting_score == 100.0:
                reasons.append(
                    "School setting exactly matches the preference: "
                    f"{school_setting}."
                )
            else:
                warnings.append(
                    f"School setting is {school_setting}, compared with the "
                    f"preferred setting of {preferred_setting}."
                )
        else:
            verification.append(
                "School setting is missing or unsupported, so setting "
                "preference was not scored."
            )

    has_hard_dealbreaker_conflict = False
    requires_dealbreaker_verification = False

    if "Rural location" in dealbreakers:
        if school_setting is None:
            requires_dealbreaker_verification = True
            dealbreaker_verification.append(
                "The applicant selected rural location as a dealbreaker, but "
                "the school's setting is missing or unsupported."
            )
        elif school_setting == "Rural":
            has_hard_dealbreaker_conflict = True
            message = (
                "School is in a rural setting, which conflicts with the "
                "applicant's rural-location dealbreaker."
            )
            dealbreaker_conflicts.append(message)
            warnings.append(message)

    if "Large city" in dealbreakers:
        if school_setting is None:
            requires_dealbreaker_verification = True
            dealbreaker_verification.append(
                "The applicant selected large city as a dealbreaker, but the "
                "school's setting is missing or unsupported."
            )
        elif school_setting == "Urban":
            has_hard_dealbreaker_conflict = True
            message = (
                "School is in an urban setting, which conflicts with the "
                "applicant's large-city dealbreaker."
            )
            dealbreaker_conflicts.append(message)
            warnings.append(message)

    if "Strong in-state preference" in dealbreakers:
        if not student_state_code or not school_state_code:
            requires_dealbreaker_verification = True
            dealbreaker_verification.append(
                "The applicant selected strong in-state preference as a "
                "dealbreaker, but applicant or school state data is missing."
            )
        elif student_state_code != school_state_code:
            has_hard_dealbreaker_conflict = True
            message = (
                "School is outside the applicant's state of residency, which "
                "conflicts with the strong in-state dealbreaker."
            )
            dealbreaker_conflicts.append(message)
            warnings.append(message)

    if "Far from family" in dealbreakers:
        if not active_region_preferences or has_no_region_preference:
            requires_dealbreaker_verification = True
            dealbreaker_verification.append(
                "The far-from-family dealbreaker cannot be evaluated because "
                "the applicant did not provide usable preferred regions."
            )
        elif not school_region:
            requires_dealbreaker_verification = True
            dealbreaker_verification.append(
                "The far-from-family dealbreaker cannot be evaluated because "
                "the school's region is missing."
            )
        elif school_region not in active_region_preferences:
            requires_dealbreaker_verification = True
            dealbreaker_verification.append(
                "School is outside the applicant's preferred regions. Region "
                "is only a proxy for family distance, so the conflict requires "
                "user verification rather than automatic exclusion."
            )

    for dealbreaker, message in UNSCORABLE_DEALBREAKERS.items():
        if dealbreaker in dealbreakers:
            requires_dealbreaker_verification = True
            dealbreaker_verification.append(message)

    unsupported_dealbreakers = sorted(
        dealbreakers - SUPPORTED_DEALBREAKERS
    )
    for dealbreaker in unsupported_dealbreakers:
        requires_dealbreaker_verification = True
        dealbreaker_verification.append(
            f"Dealbreaker '{dealbreaker}' is not currently supported and "
            "requires user verification."
        )

    if has_hard_dealbreaker_conflict:
        dealbreaker_status = DEALBREAKER_STATUS_EXCLUDED
    elif requires_dealbreaker_verification:
        dealbreaker_status = DEALBREAKER_STATUS_VERIFY
    else:
        dealbreaker_status = DEALBREAKER_STATUS_CLEAR

    raw_preference_score = _weighted_component_average(components)
    basic_preference_score = (
        None
        if raw_preference_score is None
        else round(raw_preference_score, 1)
    )

    if basic_preference_score is None:
        basic_preference_category = "No scored preferences"
    elif basic_preference_score >= 80:
        basic_preference_category = "Strong Basic Preference Match"
    elif basic_preference_score >= 55:
        basic_preference_category = "Moderate Basic Preference Match"
    else:
        basic_preference_category = "Weak Basic Preference Match"

    used_weights = {
        component: COMPONENT_WEIGHTS[component]
        for component in components
        if component in COMPONENT_WEIGHTS
    }

    return {
        "program_eligibility_status": program_eligibility_status,
        "dealbreaker_status": dealbreaker_status,
        "basic_preference_score": basic_preference_score,
        "basic_preference_category": basic_preference_category,
        "preference_components": components,
        "preference_component_weights": used_weights,
        # Retained for backward compatibility. Dealbreakers are now handled
        # through eligibility instead of subtracting from the score.
        "preference_penalty": 0.0,
        "dealbreaker_conflicts": dealbreaker_conflicts,
        "dealbreaker_verification": dealbreaker_verification,
        "geographic_proximity_hops": border_hops,
        "preference_score_basis": (
            "Weighted available components: degree type 15%, state-border "
            "proximity 35%, preferred region 25%, and setting 25%. "
            "Dealbreakers are evaluated separately as eligibility or "
            "verification rules and do not reduce this score."
        ),
        "preference_reasons": reasons,
        "preference_warnings": warnings,
        "preference_verification": verification,
    }
