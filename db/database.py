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
        name VARCHAR(255) NOT NULL,
        uid VARCHAR(50) NOT NULL UNIQUE,
        program VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'attendance_status') THEN
            CREATE TYPE attendance_status AS ENUM ('INSIDE', 'OUTSIDE');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'activity_type') THEN
            CREATE TYPE activity_type AS ENUM ('VOICE_COMMAND', 'RFID');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'project_status') THEN
            CREATE TYPE project_status AS ENUM ('ONGOING');
        END IF;
    END$$;
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY,
        student_id INTEGER NOT NULL
            REFERENCES students(id) ON DELETE CASCADE,
        status attendance_status NOT NULL,
        activity_type activity_type DEFAULT 'VOICE_COMMAND',
        reason TEXT,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance_summary (
        id SERIAL PRIMARY KEY,
        student_id INTEGER NOT NULL
            REFERENCES students(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        inside_count INTEGER DEFAULT 0,
        outside_count INTEGER DEFAULT 0,
        last_status attendance_status,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (student_id, date)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rfid_cards (
        id SERIAL PRIMARY KEY,
        uid VARCHAR(50) UNIQUE NOT NULL,
        user_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
        is_active BOOLEAN DEFAULT TRUE,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS guests (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        designation VARCHAR(255),
        organization VARCHAR(255),
        visit_purpose TEXT,
        welcome_note TEXT NOT NULL,
        visit_date DATE DEFAULT CURRENT_DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS trait_info (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        vision TEXT,
        mission TEXT,
        location VARCHAR(255),
        contact_email VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        domain VARCHAR(100),
        status project_status DEFAULT 'ONGOING',
        mentor VARCHAR(255),
        start_date DATE,
        end_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_students_uid ON students(uid)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_students_active ON students(is_active)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance(timestamp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status)")

    conn.commit()
    conn.close()