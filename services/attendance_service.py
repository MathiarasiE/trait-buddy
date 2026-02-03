from datetime import datetime
from rules.status_rules import apply_status, INSIDE, OUTSIDE
from db.database import get_conn, init_db

# -------------------------
# Helpers
# -------------------------
def get_student_id(name):
    name = (name or "").strip().lower()
    if not name:
        return None

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM students WHERE name = %s AND is_active = TRUE LIMIT 1",
        (name,),
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_current_status(student_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT status FROM attendance
        WHERE student_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        (student_id,),
    )

    row = cur.fetchone()
    conn.close()

    return row[0] if row else OUTSIDE  # default OUTSIDE


# -------------------------
# ACTIONS
# -------------------------
def mark_present(name, activity_type="VOICE_COMMAND", reason=None):
    init_db()
    student_id = get_student_id(name)
    if not student_id:
        return f"I don't know {name}."

    current = get_current_status(student_id)
    new_status = apply_status(current, "MARK_PRESENT")

    if new_status is None:
        return f"{name.capitalize()} is already inside."

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO attendance (student_id, status, activity_type, reason)
        VALUES (%s, %s, %s, %s)
        """,
        (
            student_id,
            new_status,
            activity_type,
            reason,
        ),
    )

    conn.commit()
    conn.close()

    return f"{name.capitalize()} is marked present and is now inside."


def mark_absent(name, activity_type="VOICE_COMMAND", reason=None):
    init_db()
    student_id = get_student_id(name)
    if not student_id:
        return f"I don't know {name}."

    current = get_current_status(student_id)
    new_status = apply_status(current, "MARK_ABSENT")

    if new_status is None:
        return f"{name.capitalize()} is already outside."

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO attendance (student_id, status, activity_type, reason)
        VALUES (%s, %s, %s, %s)
        """,
        (
            student_id,
            new_status,
            activity_type,
            reason,
        ),
    )

    conn.commit()
    conn.close()

    return f"{name.capitalize()} has been marked absent and is now outside."


# -------------------------
# QUERIES
# -------------------------
def who_present_today():
    init_db()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT DISTINCT s.name
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        WHERE DATE(a.timestamp) = CURRENT_DATE
          AND a.status = %s
          AND s.is_active = TRUE
        """,
        (INSIDE,),
    )

    names = [r[0] for r in cur.fetchall()]
    conn.close()

    if not names:
        return "No one is inside today."

    return "Inside today: " + ", ".join(n.capitalize() for n in names)


def who_absent_today():
    init_db()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT s.name
        FROM students s
        WHERE s.is_active = TRUE
          AND s.id NOT IN (
              SELECT a.student_id
              FROM attendance a
              WHERE DATE(a.timestamp) = CURRENT_DATE
                AND a.status = %s
          )
        """,
        (INSIDE,),
    )

    names = [r[0] for r in cur.fetchall()]
    conn.close()

    if not names:
        return "Everyone is present today."

    return "Absent today: " + ", ".join(n.capitalize() for n in names)


def where_is(name):
    student_id = get_student_id(name)
    if not student_id:
        return f"I don't know {name}."

    status = get_current_status(student_id)

    if status == INSIDE:
        return f"{name.capitalize()} is inside."
    else:
        return f"{name.capitalize()} is outside."


def summary_today():
    inside = who_present_today()
    absent = who_absent_today()
    return f"{inside}. {absent}."
