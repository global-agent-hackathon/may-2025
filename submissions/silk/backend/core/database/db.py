import os
import sqlite3
import logging
import json
import time
from datetime import timedelta
from core.database.initialise import initialise_db

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = os.getenv("DB_PATH","quip.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.health_check()

    def health_check(self) -> bool:
        try:
            query = """
                SELECT COUNT(name)
                FROM sqlite_master
                WHERE type='table'
                AND name IN ('courses', 'sections', 'sessions');
            """
            self.cursor.execute(query)
            table_count = self.cursor.fetchone()[0]
            if table_count < 3:
                logger.info("Tables missing. Initializing DB...")
                initialise_db(self.db_path)
            return True
        except Exception as e:
            logger.exception(f"Health check failed: {e}")
            return False

    def create_session(self, session_id, actions, description, level, progress):
        query = """
        INSERT INTO sessions (session_id, actions, description, level, progress)
        VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (session_id, json.dumps(actions), description, level, progress))
        self.conn.commit()

    def get_session(self, session_id):
        query = "SELECT * FROM sessions WHERE session_id = ?"
        self.cursor.execute(query, (session_id,))
        row = self.cursor.fetchone()
        if row:
            result = dict(row)
            result["actions"] = json.loads(result["actions"])
            return result
        return None

    def get_all_sessions(self):
        query = "SELECT * FROM sessions"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        sessions = []
        for row in rows:
            session = dict(row)
            session["actions"] = json.loads(session["actions"])
            sessions.append(session)
        return sessions

    def update_session_progress(self, session_id, new_progress):
        if new_progress not in ("in_progress", "success", "error"):
            raise ValueError("Invalid progress status")

        query = """
        UPDATE sessions
        SET progress = ?
        WHERE session_id = ?
        """
        self.cursor.execute(query, (new_progress, session_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_session_actions(self, session_id, actions):
        query = "UPDATE sessions SET actions = ? WHERE session_id = ?"
        self.cursor.execute(query, (json.dumps(actions), session_id))
        self.conn.commit()

    def update_and_get_session(self, session_id):
        self.cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None


    def create_course(self, course_id, session_id, title, description, level, created_at):
        query = """
        INSERT INTO courses (course_id, session_id, title, description, level, created_at, completion_percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (course_id, session_id, title, description, level, created_at, 0.0))
        self.conn.commit()


    def delete_course(self, course_id):
        query = "DELETE FROM courses WHERE course_id = ?"
        self.cursor.execute(query, (course_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0 
    
    def get_course(self, course_id):
        query = "SELECT * FROM courses WHERE course_id = ?"
        self.cursor.execute(query, (course_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_courses(self):
        query = "SELECT * FROM courses"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]

    def update_course_completion_percentage(self, course_id: str, percentage: float) -> bool:
        if not (0.0 <= percentage <= 1.0):
            raise ValueError("Completion percentage must be between 0.0 and 1.0")

        query = """
        UPDATE courses
        SET completion_percentage = ?
        WHERE course_id = ?
        """
        self.cursor.execute(query, (percentage, course_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_incomplete_courses(self):
        query = "SELECT * FROM courses WHERE completion_percentage < 1.0"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]


    def create_section(self, section_id, course_id, title, description, content, section_order, created_at):
        query = """
        INSERT INTO sections (section_id, course_id, title, description, content, section_order, created_at, is_completed, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (section_id, course_id, title, description, content, section_order, created_at, 0, None))
        self.conn.commit()

    def get_all_sections_for_course(self, course_id):
        query = "SELECT * FROM sections WHERE course_id = ? ORDER BY section_order"
        self.cursor.execute(query, (course_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_section(self, section_id: str):
        query = "SELECT * FROM sections WHERE section_id = ?"
        self.cursor.execute(query, (section_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def complete_section(self, section_id: str):
        completed_at = int(time.time())
        query = """
        UPDATE sections
        SET is_completed = 1, completed_at = ?
        WHERE section_id = ?
        """
        self.cursor.execute(query, (completed_at, section_id))
        self.conn.commit()

        course_id_query = "SELECT course_id FROM sections WHERE section_id = ?"
        self.cursor.execute(course_id_query, (section_id,))
        row = self.cursor.fetchone()
        if row:
            course_id = row["course_id"]
            self.update_course_completion(course_id)
        else:
            logger.warning(f"Section {section_id} not found, unable to update course completion.")


    def update_course_completion(self, course_id: str):
        total_query = "SELECT COUNT(*) as total FROM sections WHERE course_id = ?"
        completed_query = "SELECT COUNT(*) as completed FROM sections WHERE course_id = ? AND is_completed = 1"

        self.cursor.execute(total_query, (course_id,))
        total = self.cursor.fetchone()["total"]

        if total == 0:
            percentage = 0.0
        else:
            self.cursor.execute(completed_query, (course_id,))
            completed = self.cursor.fetchone()["completed"]
            percentage = completed / total

        update_query = """
        UPDATE courses
        SET completion_percentage = ?
        WHERE course_id = ?
        """
        self.cursor.execute(update_query, (percentage, course_id))
        self.conn.commit()

    def get_incomplete_sections(self, course_id: str):
        query = """
        SELECT * FROM sections
        WHERE course_id = ? AND is_completed = 0
        ORDER BY section_order
        """
        self.cursor.execute(query, (course_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_analytics_data(self):
        analytics_data = {}
        courses_query = """
            SELECT
                c.course_id,
                c.title,
                c.completion_percentage,
                MAX(s.completed_at) AS latest_completed_at
            FROM courses c
            LEFT JOIN sections s ON c.course_id = s.course_id AND s.is_completed = 1
            GROUP BY c.course_id, c.title, c.completion_percentage
            ORDER BY c.title;
        """
        self.cursor.execute(courses_query)
        courses_data = []
        for row in self.cursor.fetchall():
            course = dict(row)
            if course['latest_completed_at']:
                course['latest_completed_at_readable'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(course['latest_completed_at']))
            else:
                course['latest_completed_at_readable'] = None
            courses_data.append(course)
        analytics_data['courses_table'] = courses_data

        avg_completion_time_query = """
            SELECT
                AVG(latest_completed_at - created_at) AS avg_time_to_complete
            FROM (
                SELECT
                    c.created_at,
                    MAX(s.completed_at) AS latest_completed_at
                FROM courses c
                JOIN sections s ON c.course_id = s.course_id
                WHERE c.completion_percentage = 1.0
                GROUP BY c.course_id, c.created_at
            ) AS completed_course_times;
        """
        self.cursor.execute(avg_completion_time_query)
        avg_completion_time = self.cursor.fetchone()['avg_time_to_complete']
        analytics_data['average_course_completion_time_seconds'] = avg_completion_time
        if avg_completion_time:
            analytics_data['average_course_completion_time_readable'] = str(timedelta(seconds=int(avg_completion_time)))
        else:
            analytics_data['average_course_completion_time_readable'] = None

        total_courses_query = "SELECT COUNT(*) FROM courses;"
        completed_courses_query = "SELECT COUNT(*) FROM courses WHERE completion_percentage = 1.0;"
        self.cursor.execute(total_courses_query)
        total_courses = self.cursor.fetchone()[0]
        self.cursor.execute(completed_courses_query)
        completed_courses = self.cursor.fetchone()[0]
        analytics_data['course_counts'] = {
            'total': total_courses,
            'completed': completed_courses
        }

        total_sections_query = "SELECT COUNT(*) FROM sections;"
        completed_sections_query = "SELECT COUNT(*) FROM sections WHERE is_completed = 1;"
        self.cursor.execute(total_sections_query)
        total_sections = self.cursor.fetchone()[0]
        self.cursor.execute(completed_sections_query)
        completed_sections = self.cursor.fetchone()[0]
        analytics_data['section_counts'] = {
            'total': total_sections,
            'completed': completed_sections
        }

        daily_completions_query = """
            SELECT
                strftime('%Y-%m-%d', completed_at, 'unixepoch') AS completion_date,
                COUNT(*) AS completed_sections_count
            FROM sections
            WHERE is_completed = 1 AND completed_at IS NOT NULL
            GROUP BY completion_date
            ORDER BY completion_date;
        """
        self.cursor.execute(daily_completions_query)
        daily_completions = [dict(row) for row in self.cursor.fetchall()]
        analytics_data['daily_section_completions'] = daily_completions

        return analytics_data