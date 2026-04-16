THRESHOLDS = {
    8: (5000, 8000, 10000),
    9: (6000, 9000, 11000),
}


def get_effort(total, shift=8):
    """Returns effort level based on total EPS and shift duration (8 or 9 hours)."""
    low, medium, high = THRESHOLDS.get(shift, THRESHOLDS[8])
    if total < low:
        return "low"
    elif total < medium:
        return "medium"
    elif total < high:
        return "high"
    else:
        return "critical"
