from services.attendance_service import mark_attendance
from db.students import get_name_from_uid

def handle_rfid_event(uid: str, action: str, reason: str = ""):
    """
    action: 'in' or 'out'
    """
    name = get_name_from_uid(uid)

    if not name:
        return f"Unknown RFID card: {uid}. Please register this UID."

    status = "present" if action.lower() == "in" else "absent"
    return mark_attendance(name, status, reason)
