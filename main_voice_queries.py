from voice.listen_whisper import listen_whisper
from voice.speak import speak
from services.name_matcher import get_all_student_names, match_name
from services.ai_service import get_ai_response
from datetime import datetime

from services.parser import parse_command
from services.attendance_service import (
    mark_present,
    mark_absent,
    who_present_today,
    who_absent_today,
    where_is,
    summary_today
)
from services.info_service import (
    get_trait_response,
    get_guest_welcome_note,
    get_projects_summary,
    get_project_details,
)

import sounddevice as sd
# =====================
# MoM (Meeting Mode)
# =====================
meeting_mode = False
meeting_transcript = []


def is_start_meeting(text: str) -> bool:
    t = text.lower()
    return "start meeting" in t

def is_end_meeting(text: str) -> bool:
    t = text.lower()
    return "end meeting" in t


# ? FORCE BLUETOOTH MIC (IMPORTANT)
def setup_audio():
    devices = sd.query_devices()
    bt_index = None

    for i, dev in enumerate(devices):
        if "bluez" in dev["name"].lower():
            bt_index = i
            print(f"? Bluetooth mic found: {dev['name']} (index {i})")
            break

    if bt_index is not None:
        sd.default.device = (bt_index, None)
    else:
        print("?? Bluetooth mic not found, using default")

# --------------------
# Wake word detection
# --------------------
def is_wake_word(text: str) -> bool:
    t = text.lower()
    return (
        "hey buddy" in t or
        (("hey" in t or "hi" in t) and ("buddy" in t or "body" in t))
    )

def is_ai_mode_trigger(text: str) -> bool:
    t = text.lower()
    return (
        "ai mode" in t or
        "turn on ai mode" in t or
        "enter ai mode" in t or
        "start ai" in t
    )

# --------------------
# Command router
# --------------------
def run_query(cmd_text: str) -> str:
    parsed = parse_command(cmd_text)

    if not parsed:
        return "Sorry, I didn't understand."

    intent = parsed.get("intent")
    spoken_name = parsed.get("name")

    resolved_name = None

    if spoken_name:
        known_names = get_all_student_names()
        resolved_name, _ = match_name(spoken_name, known_names)

        if not resolved_name:
            return f"I couldn't find a student named {spoken_name}."

    if intent == "WHO_PRESENT":
        return who_present_today()

    if intent == "WHO_ABSENT":
        return who_absent_today()

    if intent == "WHERE_IS" and resolved_name:
        return where_is(resolved_name)

    if intent == "SUMMARY":
        return summary_today()

    if intent == "TRAIT_INFO":
        return get_trait_response(parsed.get("field"))

    if intent == "GUEST_WELCOME":
        return get_guest_welcome_note(parsed.get("name"))

    if intent == "PROJECTS_LIST":
        return get_projects_summary()

    if intent == "PROJECT_DETAILS":
        title = parsed.get("title")
        return get_project_details(title) if title else get_projects_summary()

    if intent == "MARK_PRESENT" and resolved_name:
        return mark_present(resolved_name)

    if intent == "MARK_ABSENT" and resolved_name:
        return mark_absent(resolved_name)

    return "Sorry, I didn't understand."

def generate_mom(transcript_list):
    if not transcript_list:
        return "No meeting data recorded."

    lines = transcript_list

    key_points = lines[:5]
    actions = [l for l in lines if "will" in l.lower() or "do" in l.lower()]

    mom = f"Meeting Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    mom += "Key Points:\n"
    for kp in key_points:
        mom += f"- {kp}\n"

    mom += "\nAction Items:\n"
    for act in actions[:5]:
        mom += f"- {act}\n"

    mom += "\nSummary:\nDiscussion was recorded and summarized."

    # ✅ Safe save
    os.makedirs("data", exist_ok=True)

    filename = f"data/meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w") as f:
        f.write(mom)

    return mom

# --------------------
# Main loop
# --------------------
def main():
    global meeting_mode, meeting_transcript   # ✅ IMPORTANT

    setup_audio()

    speak("Buddy query mode ready. Say hey buddy.")
    ai_mode = False

    while True:
        wake = listen_whisper(seconds=3)
        print("👂 Heard:", wake)

        if not wake.strip():
            continue

        # =====================
        # MEETING MODE CONTROL (FIRST)
        # =====================
        if is_start_meeting(wake):
            meeting_mode = True
            meeting_transcript.clear()
            speak("Meeting recording started.")
            continue

        if is_end_meeting(wake):
            meeting_mode = False
            speak("Generating meeting summary.")

            mom = generate_mom(meeting_transcript)
            print("\n===== MOM =====\n", mom)

            speak("Meeting summary is ready.")
            speak(mom[:500])

            continue

        # =====================
        # MEETING RECORDING
        # =====================
        if meeting_mode:
            print("📌 Recording meeting content...")
            meeting_text = listen_whisper(seconds=15)  # ✅ better chunk

            if meeting_text.strip():
                print("📝 Meeting:", meeting_text)
                meeting_transcript.append(meeting_text)

            continue

        # =====================
        # AI MODE
        # =====================
        if is_ai_mode_trigger(wake):
            ai_mode = True
            speak("AI mode activated. Ask me anything.")
            continue

        if ai_mode:
            if "exit" in wake.lower() or "stop" in wake.lower():
                ai_mode = False
                speak("AI mode deactivated.")
                continue

            response = get_ai_response(wake)
            speak(response)
            continue

        # =====================
        # NORMAL MODE
        # =====================
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
