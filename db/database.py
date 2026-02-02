import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection parameters from environment variables
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'traitbuddy'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        uid TEXT,
        program TEXT
    )
    """)

    # Check if program column exists (for migration)
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'students' AND column_name = 'program'
    """)
    if not cur.fetchone():
        cur.execute("ALTER TABLE students ADD COLUMN program TEXT")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY,
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