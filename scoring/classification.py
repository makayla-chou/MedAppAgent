def classify_academic_z(composite_z: float | None) -> str:
    """
    Classify academic position relative to reported school averages.

    These are planning labels, not admission probabilities.
    """
    if composite_z is None:
        return "Insufficient Data"
    if composite_z >= 0.50:
        return "Academically Strong"
    if composite_z >= -0.50:
        return "Academically Plausible"
    if composite_z >= -1.25:
        return "Reach"
    return "High Reach"
