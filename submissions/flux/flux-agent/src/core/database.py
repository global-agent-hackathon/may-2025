import os
import psycopg
from psycopg import rows
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from constants.enums import DatabaseConfig, ErrorMessages
from utils.logger import get_logger

logger = get_logger()


class DatabaseService:
    def __init__(self):
        self._connection_url = self._build_connection_url()
        logger.info("Database service initialized successfully")
    
    def _build_connection_url(self) -> str:
        raw_db_url = os.getenv("DATABASE_URL")
        if not raw_db_url:
            raise ValueError(ErrorMessages.MISSING_DATABASE_URL)

        parsed = urlparse(raw_db_url.strip().strip('"'))
        db_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?sslmode={DatabaseConfig.SSL_MODE}"
        
        logger.info(f"Database connection configured: {db_url.replace(parsed.netloc, '[REDACTED]')}")
        return db_url
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as list of dictionaries."""
        try:
            with psycopg.connect(self._connection_url) as conn:
                with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                    if params:
                        cur.execute(query, params)
                    else:
                        cur.execute(query)
                    
                    rows = cur.fetchall()
                    logger.info(f"Query executed successfully, returned {len(rows)} rows")
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    def fetch_form_response(self, form_response_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific form response by ID."""
        query = 'SELECT * FROM "FormResponse" WHERE "id" = %s'
        results = self.execute_query(query, (form_response_id,))
        return results[0] if results else None 