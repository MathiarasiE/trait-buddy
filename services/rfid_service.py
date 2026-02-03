from services.attendance_service import mark_present, mark_absent
from db.rfid_cards import get_user_from_uid

def handle_rfid_event(uid: str, action: str, reason: str = ""):
    """
    action: 'in' or 'out'
    """
    user = get_user_from_uid(uid)

    if not user:
        return f"Unknown RFID card: {uid}. Please register this UID."

    name = user["name"]

    if action.lower() == "in":
        mark_present(name, activity_type="RFID", reason=reason or None)
        return f"{name} marked present."
    else:
        mark_absent(name, activity_type="RFID", reason=reason or None)
        return f"{name} marked absent."
