from rapidfuzz import process, fuzz

def match_name(spoken_name: str, known_names: list, threshold=80):
    """
    Returns (best_match, confidence) or (None, 0)
    """
    if not spoken_name or not known_names:
        return None, 0

    match = process.extractOne(
        spoken_name,
        known_names,
        scorer=fuzz.WRatio
    )

    if not match:
        return None, 0

    best_name, score, _ = match

    if score >= threshold:
        return best_name, score

    return None, score
