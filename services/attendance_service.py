import sqlite3
from datetime import datetime
from rules.status_rules import apply_status, INSIDE, OUTSIDE

DB_PATH = "data/traitbuddy.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

# -------------------------
# Helpers
# -------------------------
def get_current_status(name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT status FROM attendance
        WHERE name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (name,))

    row = cur.fetchone()
    conn.close()

    return row[0] if row else OUTSIDE  # default OUTSIDE


def student_exists(name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM students WHERE name = ?", (name,))
    exists = cur.fetchone() is not None

    conn.close()
    return exists


# -------------------------
# ACTIONS
# -------------------------
def mark_present(name):
    if not student_exists(name):
        return f"I don't know {name}."

    current = get_current_status(name)
    new_status = apply_status(current, "MARK_PRESENT")

    if new_status is None:
        return f"{name.capitalize()} is already inside."

    now = datetime.now()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attendance (name, status, date, time)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        new_status,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return f"{name.capitalize()} is marked present and is now inside."


def mark_absent(name):
    if not student_exists(name):
        return f"I don't know {name}."

    current = get_current_status(name)
    new_status = apply_status(current, "MARK_ABSENT")

    if new_status is None:
        return f"{name.capitalize()} is already outside."

    now = datetime.now()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attendance (name, status, date, time)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        new_status,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return f"{name.capitalize()} has been marked absent and is now outside."


# -------------------------
# QUERIES
# -------------------------
def who_present_today():
    conn = get_conn()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT DISTINCT name FROM attendance
        WHERE date = ? AND status = ?
    """, (today, INSIDE))

    names = [r[0] for r in cur.fetchall()]
    conn.close()

    if not names:
        return "No one is inside today."

    return "Inside today: " + ", ".join(n.capitalize() for n in names)


def who_absent_today():
    conn = get_conn()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT name FROM students
        WHERE name NOT IN (
            SELECT name FROM attendance
            WHERE date = ? AND status = ?
        )
    """, (today, INSIDE))

    names = [r[0] for r in cur.fetchall()]
    conn.close()

    if not names:
        return "Everyone is present today."

    return "Absent today: " + ", ".join(n.capitalize() for n in names)


def where_is(name):
    status = get_current_status(name)

    if status == INSIDE:
        return f"{name.capitalize()} is inside."
    else:
        return f"{name.capitalize()} is outside."


def summary_today():
    inside = who_present_today()
    absent = who_absent_today()
    return f"{inside}. {absent}."
