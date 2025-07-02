import sqlite3
import os

CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    actions TEXT,
    description TEXT,
    level TEXT,
    progress TEXT CHECK(progress IN ('in_progress', 'success', 'error'))
)
"""

CREATE_COURSES_TABLE = """
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    session_id TEXT,
    title TEXT,
    description TEXT,
    level TEXT,
    created_at INTEGER,
    completion_percentage REAL DEFAULT 0.0,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
)
"""

CREATE_SECTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sections (
    course_id TEXT,
    section_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    content TEXT,
    section_order INTEGER,
    created_at INTEGER,
    is_completed INTEGER DEFAULT 0, -- Renamed from 'completed' to 'is_completed' for consistency
    completed_at INTEGER,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
)
"""

def initialise_db(db_name="quip.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(CREATE_SESSIONS_TABLE)
    cursor.execute(CREATE_COURSES_TABLE)
    cursor.execute(CREATE_SECTIONS_TABLE)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    db_path = os.getenv("DB_PATH","quip.db")
    initialise_db(db_path)
