from services.attendance_service import mark_present, mark_absent
from db.students import get_name_from_uid

def handle_rfid_event(uid: str, action: str, reason: str = ""):
    """
    action: 'in' or 'out'
    """
    name = get_name_from_uid(uid)

    if not name:
        return f"Unknown RFID card: {uid}. Please register this UID."

    if action.lower() == "in":
        return mark_present(name)
    else:
        return mark_absent(name)
