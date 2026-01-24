import re

STOPWORDS = {
    "present", "absent", "mark", "is", "the", "a", "an",
    "student", "inside", "outside", "in", "out"
}

def normalize(text: str) -> str:
    return text.lower().strip().replace(".", "")

def extract_name(text: str):
    words = text.split()
    name_words = [w for w in words if w not in STOPWORDS]
    return " ".join(name_words) if name_words else None

def parse_command(text: str):
    raw = text.strip()
    t = normalize(raw)

    # -------------------------
    # WHERE IS <name>
    # -------------------------
    m = re.search(r"where\s+is\s+([a-z]+)", t)
    if m:
        return {
            "intent": "WHERE_IS",
            "name": m.group(1)
        }

    # -------------------------
    # WHO IS INSIDE / PRESENT
    # -------------------------
    if "who" in t and ("present" in t or "inside" in t or "in" in t):
        return {"intent": "WHO_PRESENT"}

    # -------------------------
    # WHO IS OUTSIDE / ABSENT
    # -------------------------
    if "who" in t and ("absent" in t or "outside" in t or "out" in t):
        return {"intent": "WHO_ABSENT"}

    # -------------------------
    # SUMMARY
    # -------------------------
    if "summary" in t:
        return {"intent": "SUMMARY"}

    # -------------------------
    # MARK PRESENT  (INSIDE RULE)
    # Examples:
    #   "varshani present"
    #   "mark ravi present"
    # -------------------------
    if "present" in t:
        name = extract_name(t)
        if name:
            return {
                "intent": "MARK_PRESENT",
                "name": name
            }

    # -------------------------
    # MARK ABSENT (OUTSIDE RULE)
    # Examples:
    #   "varshani absent"
    #   "mark ravi absent"
    # -------------------------
    if "absent" in t:
        name = extract_name(t)
        if name:
            return {
                "intent": "MARK_ABSENT",
                "name": name
            }

    # -------------------------
    # FALLBACK
    # -------------------------
    return {"intent": "UNKNOWN"}
