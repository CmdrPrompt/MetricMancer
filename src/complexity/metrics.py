def grade(value, threshold_low=10.0, threshold_high=20.0):
    if value <= threshold_low:
        return "Low ✅"
    elif value <= threshold_high:
        return "Medium ⚠️"
    else:
        return "High ❌"
