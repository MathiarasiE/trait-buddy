import sqlite3

DB_PATH = "data/traitbuddy.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        uid TEXT,
        program TEXT
    )
    """)

    # Lightweight migration for older DBs created before the `program` column existed.
    cur.execute("PRAGMA table_info(students)")
    existing_cols = {row[1] for row in cur.fetchall()}  # row[1] == column name
    if "program" not in existing_cols:
        cur.execute("ALTER TABLE students ADD COLUMN program TEXT")

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

    conn.commit()
    conn.close()