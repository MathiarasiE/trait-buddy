import re

def parse_command(text: str):
    raw = text.strip()
    t = raw.lower().strip()

    # Wake word not handled here (main.py will handle)

    # WHERE IS <name>
    m = re.search(r"(where\s+is)\s+([a-z]+)", t)
    if m:
        return {"intent": "WHERE_IS", "name": m.group(2)}

    # WHO PRESENT / WHO IN
    if ("who" in t or "who's" in t) and ("present" in t or "in" in t):
        return {"intent": "WHO_PRESENT"}

    if "who is present" in t or "whos present" in t:
        return {"intent": "WHO_PRESENT"}

    # WHO OUT / WHO ABSENT
    if ("who" in t or "who's" in t) and ("out" in t or "absent" in t):
        return {"intent": "WHO_ABSENT"}

    # SUMMARY
    if "summary" in t or "attendance summary" in t:
        return {"intent": "SUMMARY"}

    return {"intent": "UNKNOWN"}
