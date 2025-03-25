def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None
