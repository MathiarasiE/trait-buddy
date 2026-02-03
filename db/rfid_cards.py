from __future__ import annotations

from typing import Optional
import psycopg2.extras

from db.database import get_conn, init_db


def get_user_from_uid(uid: str) -> Optional[dict]:
    uid = (uid or "").strip()
    if not uid:
        return None

    init_db()

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT s.id, s.name, s.uid, s.program
        FROM rfid_cards r
        JOIN students s ON s.id = r.user_id
                WHERE r.uid = %s
                    AND r.is_active = TRUE
                    AND s.is_active = TRUE
        LIMIT 1
        """,
        (uid,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
