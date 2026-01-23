from datetime import datetime
from db.database import get_conn

def mark_attendance(name: str, status: str, reason: str = "", uid: str = None):
    name = name.strip().lower()
    status = status.strip().lower()
    reason = (reason or "").strip()

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO attendance (uid, name, status, reason, date, time) VALUES (?, ?, ?, ?, ?, ?)",
        (uid, name, status, reason, date, time)
    )

    conn.commit()
    conn.close()

    if status == "absent" and reason:
        return f"{name} is OUT. Reason: {reason}"
    elif status == "absent":
        return f"{name} is OUT."
    else:
        return f"{name} is IN."

def who_absent_today():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT a1.name
        FROM attendance a1
        JOIN (
            SELECT name, MAX(id) AS max_id
            FROM attendance
            WHERE date = ?
            GROUP BY name
        ) a2
        ON a1.name = a2.name AND a1.id = a2.max_id
        WHERE a1.status = 'absent'
        ORDER BY a1.name ASC
    """, (today,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No one is OUT now."
    return "Out now: " + ", ".join([r[0] for r in rows])

def who_present_today():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT a1.name
        FROM attendance a1
        JOIN (
            SELECT name, MAX(id) AS max_id
            FROM attendance
            WHERE date = ?
            GROUP BY name
        ) a2
        ON a1.name = a2.name AND a1.id = a2.max_id
        WHERE a1.status = 'present'
        ORDER BY a1.name ASC
    """, (today,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No one is IN now."
    return "In now: " + ", ".join([r[0] for r in rows])

def where_is(name: str):
    name = name.strip().lower()
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT status, reason, time
        FROM attendance
        WHERE name = ? AND date = ?
        ORDER BY id DESC
        LIMIT 1
    """, (name, today))

    row = cur.fetchone()
    conn.close()

    if not row:
        return f"No status found for {name} today."

    status, reason, time = row
    status_word = "IN" if status == "present" else "OUT"

    if reason:
        return f"{name} is {status_word}. Reason: {reason}"
    return f"{name} is {status_word}."

def summary_today():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT a1.name, a1.status
        FROM attendance a1
        JOIN (
            SELECT name, MAX(id) AS max_id
            FROM attendance
            WHERE date = ?
            GROUP BY name
        ) a2
        ON a1.name = a2.name AND a1.id = a2.max_id
    """, (today,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No attendance data for today."

    present = [n for n, s in rows if s == "present"]
    absent = [n for n, s in rows if s == "absent"]

    return f"Today summary. In: {len(present)}. Out: {len(absent)}."
