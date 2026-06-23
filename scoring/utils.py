from statistics import NormalDist


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def z_to_score(z_value: float) -> float:
    """Convert a standardized difference to a 0-100 comparison index."""
    return round(NormalDist().cdf(z_value) * 100, 1)
