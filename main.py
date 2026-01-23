from db.database import init_db
from services.rfid_service import handle_rfid_event
from voice.listen_whisper import listen_whisper
from voice.speak import speak

# SIMULATION: type UID + action in laptop terminal
# Later on Raspberry Pi, this will come from RFID reader automatically.

init_db()
speak("RFID mode ready. Waiting for scans.")

while True:
    print("\n📌 Enter RFID UID (or type exit):")
    uid = input("UID: ").strip()
    if uid.lower() == "exit":
        break

    action = input("Action (in/out): ").strip().lower()
    if action not in ["in", "out"]:
        print("❌ Invalid action. Use in/out.")
        continue

    # If OUT → ask reason using voice
    reason = ""
    if action == "out":
        speak("Why is the student out?")
        reason = listen_whisper(seconds=4).strip()
        if not reason:
            reason = "No reason given"

    result = handle_rfid_event(uid, action, reason)
    speak(result)
    print("✅", result)
