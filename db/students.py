from __future__ import annotations

import psycopg2
from typing import Iterable, Optional, Sequence, Tuple

from db.database import get_conn, init_db


def get_name_from_uid(uid: str) -> Optional[str]:
    uid = (uid or "").strip()
    if not uid:
        return None

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM students WHERE uid = %s AND is_active = TRUE LIMIT 1", (uid,))
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

    # Use PostgreSQL UPSERT with ON CONFLICT (uid is unique)
    try:
        cur.execute(
            """
            INSERT INTO students (name, uid, program)
            VALUES (%s, %s, %s)
            ON CONFLICT(uid) DO UPDATE SET
                name = EXCLUDED.name,
                program = EXCLUDED.program,
                is_active = TRUE,
                updated_at = CURRENT_TIMESTAMP
            """,
            (name, uid, program),
        )
    except psycopg2.Error as e:
        conn.rollback()
        conn.close()
        raise

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
    cur.execute("SELECT name FROM students WHERE is_active = TRUE ORDER BY name ASC")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]
