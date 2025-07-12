# db_utils.py
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

def init_db(DB_CONFIG):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chess_news (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source_links TEXT[] NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL
                );
            """)
        conn.commit()

def fetch_news_from_db(DB_CONFIG) -> List[Dict[str, Any]]:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, title, description, source_links, timestamp FROM chess_news ORDER BY timestamp DESC LIMIT 3")
            return cur.fetchall()

def add_entry_in_db(DB_CONFIG, item: Dict[str, Any]) -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chess_news (title, description, source_links, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (item["data"]["title"], item["data"]["description"], item["data"]["source_links"], item["timestamp"]))
        conn.commit()

def update_entry_in_db(DB_CONFIG, replace_id: int, item: Dict[str, Any]) -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE chess_news
                SET title = %s, description = %s, source_links = %s, timestamp = %s
                WHERE id = %s
            """, (
                item["data"]["title"],
                item["data"]["description"],
                item["data"]["source_links"],
                item["timestamp"],
                replace_id
            ))
        conn.commit()