# PostgreSQL Setup Guide

## Migration from SQLite to PostgreSQL

Your database has been converted from SQLite to PostgreSQL. Follow these steps to set up:

## Prerequisites

1. **Install PostgreSQL**
   - Download from: https://www.postgresql.org/download/
   - Or use Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres --name traitbuddy-db postgres`

## Setup Steps

### 1. Create the Database

Connect to PostgreSQL and create the database:

```bash
# Using psql command line
psql -U postgres
CREATE DATABASE traitbuddy;
\q
```

Or using pgAdmin (GUI tool included with PostgreSQL installation).

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
DB_NAME=traitbuddy
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

The database tables will be created automatically when you first run the application:

```bash
python main.py
```

Or manually initialize:

```python
from db.database import init_db
init_db()
```

## Key Changes Made

1. **Database Driver**: Changed from `sqlite3` to `psycopg2-binary`
2. **Connection**: Now uses connection parameters instead of file path
3. **SQL Syntax**:
   - `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
   - Query placeholders: `?` → `%s`
   - `excluded` → `EXCLUDED` (uppercase in PostgreSQL)
4. **Environment Configuration**: Added `.env` support for database credentials

## Files Modified

- `db/database.py` - PostgreSQL connection and schema
- `db/students.py` - Updated queries for PostgreSQL
- `services/attendance_service.py` - Updated queries for PostgreSQL
- `services/name_matcher.py` - Updated connection method
- `requirements.txt` - Added psycopg2-binary and python-dotenv

## Troubleshooting

### Connection Errors

If you get "could not connect to server":
- Ensure PostgreSQL service is running
- Check that port 5432 is not blocked by firewall
- Verify credentials in `.env` file

### Permission Errors

If you get permission denied errors:
```bash
# Grant privileges to your user
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE traitbuddy TO your_username;
```

## Data Migration (Optional)

If you have existing SQLite data to migrate:

1. Export data from SQLite:
```python
import sqlite3
import csv

conn = sqlite3.connect('data/traitbuddy.db')
cursor = conn.cursor()

# Export students
cursor.execute("SELECT name, uid, program FROM students")
with open('students.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'uid', 'program'])
    writer.writerows(cursor.fetchall())

# Export attendance
cursor.execute("SELECT uid, name, status, reason, date, time FROM attendance")
with open('attendance.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['uid', 'name', 'status', 'reason', 'date', 'time'])
    writer.writerows(cursor.fetchall())

conn.close()
```

2. Import into PostgreSQL:
```bash
psql -U postgres -d traitbuddy

\COPY students(name, uid, program) FROM 'students.csv' WITH CSV HEADER;
\COPY attendance(uid, name, status, reason, date, time) FROM 'attendance.csv' WITH CSV HEADER;
```
