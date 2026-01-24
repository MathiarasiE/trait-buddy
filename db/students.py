from __future__ import annotations

import sqlite3
from typing import Iterable, Optional, Sequence, Tuple

from db.database import get_conn, init_db


def get_name_from_uid(uid: str) -> Optional[str]:
    uid = (uid or "").strip()
    if not uid:
        return None

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM students WHERE uid = ? LIMIT 1", (uid,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def upsert_student(name: str, uid: str, program: str | None = None) -> None:
    name = (name or "").strip().lower()
    uid = (uid or "").strip()
    program = (program or "").strip() or None

    if not name:
        raise ValueError("Student name cannot be empty")
    if not uid:
        raise ValueError("Student UID cannot be empty")

    init_db()

    conn = get_conn()
    cur = conn.cursor()

    # Prefer an UPSERT (SQLite >= 3.24). Fall back to SELECT+UPDATE for older builds.
    try:
        cur.execute(
            """
            INSERT INTO students (name, uid, program)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                uid = excluded.uid,
                program = excluded.program
            """,
            (name, uid, program),
        )
    except sqlite3.OperationalError:
        cur.execute("SELECT id FROM students WHERE name = ? LIMIT 1", (name,))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE students SET uid = ?, program = ? WHERE name = ?",
                (uid, program, name),
            )
        else:
            cur.execute(
                "INSERT INTO students (name, uid, program) VALUES (?, ?, ?)",
                (name, uid, program),
            )

    conn.commit()
    conn.close()


def bulk_upsert_students(
    students: Iterable[Tuple[str, str, str | None]],
) -> int:
    """Insert/update many students. Returns how many rows were processed."""
    count = 0
    for name, uid, program in students:
        upsert_student(name, uid, program)
        count += 1
    return count


def get_all_student_names() -> Sequence[str]:
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM students ORDER BY name ASC")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]
