def get_score(total):
    if total < 5000:
        return "low"
    elif total >= 5000 and total < 8000:
        return "medium"
    elif total >= 8000 and total < 10000:
        return "high"
    else:
        return "critical"