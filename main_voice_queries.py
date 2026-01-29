from voice.listen_whisper import listen_whisper
from voice.speak import speak
from services.name_matcher import get_all_student_names, match_name

from services.parser import parse_command
from services.attendance_service import (
    mark_present,
    mark_absent,
    who_present_today,
    who_absent_today,
    where_is,
    summary_today
)

# --------------------
# Wake word detection
# --------------------
def is_wake_word(text: str) -> bool:
    t = text.lower()
    return (
        "hey buddy" in t or
        (("hey" in t or "hi" in t) and ("buddy" in t or "body" in t))
    )

# --------------------
# Command router (RULE ENGINE ENTRY)
# --------------------
def run_query(cmd_text: str) -> str:
    parsed = parse_command(cmd_text)

    if not parsed:
        return "Sorry, I didn't understand."

    intent = parsed.get("intent")
    spoken_name = parsed.get("name")

    resolved_name = None
    confidence = 0

    # -------- FUZZY NAME RESOLUTION --------
    if spoken_name:
        known_names = get_all_student_names()   # from DB
        resolved_name, confidence = match_name(spoken_name, known_names)

        if not resolved_name:
            return f"I couldn't find a student named {spoken_name}."

        # OPTIONAL confirmation (enable later if you want)
        # if confidence < 90:
        #     speak(f"Did you mean {resolved_name}?")
        #     confirm = listen_whisper(seconds=3).lower()
        #     if "yes" not in confirm:
        #         return "Okay, please say the name again."

    # -------- STATUS QUERIES --------
    if intent == "WHO_PRESENT":
        return who_present_today()

    if intent == "WHO_ABSENT":
        return who_absent_today()

    if intent == "WHERE_IS" and resolved_name:
        return where_is(resolved_name)

    if intent == "SUMMARY":
        return summary_today()

    # -------- STATUS CHANGES (RULES) --------
    if intent == "MARK_PRESENT" and resolved_name:
        return mark_present(resolved_name)   # → INSIDE

    if intent == "MARK_ABSENT" and resolved_name:
        return mark_absent(resolved_name)    # → OUTSIDE

    return "Sorry, I didn't understand."


# --------------------
# Main loop
# --------------------
def main():
    speak("Buddy query mode ready. Say hey buddy.")

    while True:
        wake = listen_whisper(seconds=3)
        print("🎧 Heard:", wake)

        if not wake.strip():
            continue

        if is_wake_word(wake):
            speak("Yes. Ask your question.")
            cmd = listen_whisper(seconds=5)
            print("📝 Query:", cmd)

            if not cmd.strip():
                speak("I didn't hear the question.")
                continue

            response = run_query(cmd)
            speak(response)

# --------------------
# Entry point
# --------------------
if __name__ == "__main__":
    main()
