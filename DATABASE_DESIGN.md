# PostgreSQL Database Design Guide for trait-buddy

## Current Schema Analysis

Your database currently has:

```
students table:
├── id (SERIAL PRIMARY KEY)
├── name (TEXT, UNIQUE)
├── uid (TEXT)
└── program (TEXT)

attendance table:
├── id (SERIAL PRIMARY KEY)
├── uid (TEXT)
├── name (TEXT)
├── status (TEXT)
├── reason (TEXT)
├── date (TEXT)
└── time (TEXT)
```

## Issues with Current Design

### 1. **Data Redundancy**
- `attendance.uid` and `attendance.name` repeat data from `students` table
- No foreign key relationship - data can become inconsistent

### 2. **Poor Data Types**
- `date` and `time` stored as TEXT instead of DATE/TIME types
- Makes querying and sorting difficult

### 3. **Missing Indexes**
- No indexes on frequently queried columns like `date`, `status`, `name`
- Slow performance on large datasets

### 4. **No Timestamps**
- Can't track when records were created/modified
- No audit trail

### 5. **Missing Constraints**
- No NOT NULL constraints where needed
- No CHECK constraints for valid values

---

## Improved Database Design

### Option 1: Normalized Schema (Recommended)

```sql
-- Students table (normalized)
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    uid VARCHAR(50) NOT NULL UNIQUE,
    program VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Status enum (better than storing TEXT)
CREATE TYPE attendance_status AS ENUM ('INSIDE', 'OUTSIDE');

-- Attendance table (with foreign key)
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    status attendance_status NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);
CREATE INDEX idx_attendance_status ON attendance(status);
CREATE INDEX idx_students_uid ON students(uid);
```

### Option 2: Enhanced Schema with Additional Features

```sql
CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    uid VARCHAR(50) NOT NULL UNIQUE,
    program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE attendance_status AS ENUM ('INSIDE', 'OUTSIDE');
CREATE TYPE activity_type AS ENUM ('CHECK_IN', 'CHECK_OUT', 'MANUAL_MARK', 'VOICE_COMMAND');

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    status attendance_status NOT NULL,
    activity_type activity_type NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recorded_by VARCHAR(50) -- who/what recorded this (voice assistant, RFID, etc)
);

CREATE TABLE attendance_summary (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    present BOOLEAN,
    inside_count INTEGER DEFAULT 0,
    outside_count INTEGER DEFAULT 0,
    last_status attendance_status,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);
CREATE INDEX idx_attendance_status ON attendance(status);
CREATE INDEX idx_attendance_summary_student_date ON attendance_summary(student_id, date);
CREATE INDEX idx_students_uid ON students(uid);
CREATE INDEX idx_students_active ON students(is_active);
```

---

## Migration from Current Schema

### Step 1: Backup Current Data

```sql
-- Backup current data
CREATE TABLE students_backup AS SELECT * FROM students;
CREATE TABLE attendance_backup AS SELECT * FROM attendance;
```

### Step 2: Create New Tables

```sql
-- Create ENUM type
CREATE TYPE attendance_status AS ENUM ('INSIDE', 'OUTSIDE');

-- Create new students table
CREATE TABLE students_new (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    uid VARCHAR(50) NOT NULL UNIQUE,
    program VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migrate data
INSERT INTO students_new (id, name, uid, program, created_at)
SELECT id, name, uid, program, CURRENT_TIMESTAMP FROM students;

-- Create new attendance table with foreign key
CREATE TABLE attendance_new (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students_new(id) ON DELETE CASCADE,
    status attendance_status NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Migrate attendance data
INSERT INTO attendance_new (id, student_id, status, reason, timestamp)
SELECT 
    a.id,
    s.id as student_id,
    CASE 
        WHEN a.status = 'present' THEN 'INSIDE'::attendance_status
        ELSE 'OUTSIDE'::attendance_status
    END,
    a.reason,
    (a.date || ' ' || a.time)::TIMESTAMP
FROM attendance a
LEFT JOIN students_new s ON a.name = s.name;

-- Drop old tables
DROP TABLE attendance CASCADE;
DROP TABLE students CASCADE;

-- Rename new tables
ALTER TABLE students_new RENAME TO students;
ALTER TABLE attendance_new RENAME TO attendance;

-- Create indexes
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);
CREATE INDEX idx_attendance_status ON attendance(status);
CREATE INDEX idx_students_uid ON students(uid);
```

### Step 3: Update Python Code

Update [db/database.py](db/database.py):

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

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

    # Create ENUM type
    cur.execute("""
    DO $$ BEGIN
        CREATE TYPE attendance_status AS ENUM ('INSIDE', 'OUTSIDE');
    EXCEPTION WHEN duplicate_object THEN null;
    END $$;
    """)

    # Create students table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        uid VARCHAR(50) NOT NULL UNIQUE,
        program VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create attendance table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        status attendance_status NOT NULL,
        reason TEXT,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create indexes
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_attendance_student_id 
    ON attendance(student_id)
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_attendance_timestamp 
    ON attendance(timestamp)
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_students_uid 
    ON students(uid)
    """)

    conn.commit()
    conn.close()
```

---

## PostgreSQL Best Practices

### 1. **Use Appropriate Data Types**
```sql
-- Good
CREATE TABLE example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    birth_date DATE,
    created_at TIMESTAMP,
    age INTEGER,
    salary DECIMAL(10, 2),
    is_active BOOLEAN
);

-- Bad
CREATE TABLE example (
    id TEXT PRIMARY KEY,
    name TEXT,
    birth_date TEXT,
    created_at TEXT,
    age TEXT,
    salary TEXT,
    is_active TEXT
);
```

### 2. **Use ENUMs for Fixed Values**
```sql
-- Good
CREATE TYPE status_type AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED');
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    status status_type
);

-- Bad
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    status TEXT -- can be anything!
);
```

### 3. **Add Constraints**
```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    uid VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    age INTEGER CHECK (age >= 16),
    gpa DECIMAL(3,2) CHECK (gpa >= 0 AND gpa <= 4.0)
);
```

### 4. **Use Foreign Keys**
```sql
-- Links data together and prevents inconsistency
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    status TEXT NOT NULL
);
```

### 5. **Add Timestamps**
```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. **Create Indexes for Performance**
```sql
-- Add indexes on columns you frequently query
CREATE INDEX idx_students_name ON students(name);
CREATE INDEX idx_students_uid ON students(uid);
CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);

-- Composite index for range queries
CREATE INDEX idx_attendance_student_date ON attendance(student_id, timestamp);
```

### 7. **Use Transactions for Data Consistency**
```python
def upsert_student(name, uid, program):
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute("BEGIN")
        
        # Your operations here
        cur.execute("""
            INSERT INTO students (name, uid, program)
            VALUES (%s, %s, %s)
            ON CONFLICT(name) DO UPDATE SET
                uid = EXCLUDED.uid,
                program = EXCLUDED.program
        """, (name, uid, program))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
```

---

## Useful PostgreSQL Queries

### Check Database Size
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Table Structure
```sql
\d students
\d attendance
```

### View Indexes
```sql
SELECT * FROM pg_indexes WHERE schemaname = 'public';
```

### Find Slow Queries
```sql
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

### Count Records
```sql
SELECT 
    'students' as table_name, COUNT(*) as row_count FROM students
UNION ALL
SELECT 
    'attendance', COUNT(*) FROM attendance;
```

---

## Next Steps

1. **Decide on Schema**: Choose Option 1 (Simple) or Option 2 (Enhanced)
2. **Backup Data**: Always backup before migration
3. **Run Migration**: Execute the migration scripts
4. **Update Code**: Update Python files to work with new schema
5. **Test Thoroughly**: Test all features before going to production

Would you like me to implement any of these changes?
