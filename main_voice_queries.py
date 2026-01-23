from voice.listen_whisper import listen_whisper
from voice.speak import speak

from services.parser import parse_command
from services.attendance_service import who_present_today, who_absent_today, where_is, summary_today

def is_wake_word(text: str) -> bool:
    t = text.lower()
    return ("hey buddy" in t) or (("hey" in t or "hi" in t) and ("buddy" in t or "body" in t))

def run_query(cmd_text: str) -> str:
    parsed = parse_command(cmd_text)

    if parsed["intent"] == "WHO_PRESENT":
        return who_present_today()

    if parsed["intent"] == "WHO_ABSENT":
        return who_absent_today()

    if parsed["intent"] == "WHERE_IS":
        return where_is(parsed["name"])

    if parsed["intent"] == "SUMMARY":
        return summary_today()

    return "Sorry, I didn't understand."

speak("Buddy query mode ready. Say hey buddy.")

while True:
    wake = listen_whisper(seconds=3)
    print("🎧 Heard:", wake)

    if is_wake_word(wake):
        speak("Yes. Ask your question.")
        cmd = listen_whisper(seconds=5)
        print("📝 Query:", cmd)

        if not cmd.strip():
            speak("I didn't hear the question.")
            continue

        response = run_query(cmd)
        speak(response)
