import re

STOPWORDS = {
    "present", "absent", "mark", "is", "the", "a", "an",
    "student", "inside", "outside", "in", "out",
    "guest", "welcome", "note", "project", "projects",
    "trait", "center", "vision", "mission", "location",
    "contact", "info", "about", "details", "ongoing",
    "list", "show", "tell", "me", "please", "purpose"
}

def normalize(text: str) -> str:
    return text.lower().strip().replace(".", "")

def extract_name(text: str):
    words = text.split()
    name_words = [w for w in words if w not in STOPWORDS]
    return " ".join(name_words) if name_words else None


def extract_after_keyword(text: str, keyword: str) -> str | None:
    words = text.split()
    if keyword not in words:
        return None

    idx = words.index(keyword)
    remainder = [w for w in words[idx + 1 :] if w not in STOPWORDS]
    return " ".join(remainder) if remainder else None

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
    # TRAIT INFO
    # -------------------------
    if "trait" in t or "trait center" in t or "about" in t and "trait" in t:
        if "vision" in t:
            return {"intent": "TRAIT_INFO", "field": "vision"}
        if "mission" in t:
            return {"intent": "TRAIT_INFO", "field": "mission"}
        if "location" in t:
            return {"intent": "TRAIT_INFO", "field": "location"}
        if "contact" in t or "email" in t:
            return {"intent": "TRAIT_INFO", "field": "contact"}
        return {"intent": "TRAIT_INFO"}

    # -------------------------
    # GUEST WELCOME NOTE
    # -------------------------
    if "guest" in t or "welcome" in t:
        name = extract_after_keyword(t, "guest") or extract_after_keyword(t, "for")
        if not name:
            name = extract_name(t)
        return {"intent": "GUEST_WELCOME", "name": name}

    # -------------------------
    # PROJECTS
    # -------------------------
    if "project" in t or "projects" in t:
        if "list" in t or "ongoing" in t or "show" in t or "what" in t:
            return {"intent": "PROJECTS_LIST"}
        title = extract_after_keyword(t, "project") or extract_name(t)
        if title:
            return {"intent": "PROJECT_DETAILS", "title": title}
        return {"intent": "PROJECTS_LIST"}

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
