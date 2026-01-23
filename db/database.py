import sqlite3

DB_PATH = "db/traitbuddy.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        reason TEXT,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )
    """)

    # safe migrations
    for col, coltype in [("uid", "TEXT"), ("reason", "TEXT")]:
        try:
            cur.execute(f"ALTER TABLE attendance ADD COLUMN {col} {coltype}")
        except Exception:
            pass

    conn.commit()
    conn.close()
