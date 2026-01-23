# Temporary mapping (later you can store in DB)
UID_TO_NAME = {
    "1234567890": "mathi",
    "9988776655": "hari",
    "1111222233": "john"
}

def get_name_from_uid(uid: str):
    uid = uid.strip()
    return UID_TO_NAME.get(uid, None)
