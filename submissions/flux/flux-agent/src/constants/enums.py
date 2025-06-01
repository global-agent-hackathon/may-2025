from enum import Enum, IntEnum
from typing import Final


class FieldType(str, Enum):
    TEXT = "text"
    LONG_ANSWER = "long_answer"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    TIME = "time"
    CHECKBOX = "checkbox"
    MULTIPLE_CHOICE = "multiple_choice"
    DROPDOWN = "dropdown"
    FILE = "file"
    MULTI_SELECT = "multi_select"
    LINK = "link"
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    AI = "ai"


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ContentType(str, Enum):
    TEXT = "text"
    CSV = "csv"


class AnalysisType(str, Enum):
    SENTIMENT = "sentiment analysis"
    TREND = "trend analysis"
    COMPARATIVE = "comparative analysis"
    GENERAL = "data analysis"


class ScoreRange(IntEnum):
    MIN = 1
    MAX = 10
    POOR_MAX = 3
    AVERAGE_MAX = 6
    GOOD_MAX = 8


class DatabaseConfig:
    BATCH_SIZE: Final[int] = 50
    MAX_WORKERS: Final[int] = 5
    SSL_MODE: Final[str] = "require"


class ModelConfig:
    GPT_4_NANO: Final[str] = "gpt-4.1-nano"
    LLAMA_70B: Final[str] = "llama-3.3-70b-versatile"
    MAX_RETRIES: Final[int] = 3
    TIMEOUT: Final[int] = 30


class LogMessages:
    FORM_GENERATION_START: Final[str] = "Starting form generation"
    SQL_EXECUTION_SUCCESS: Final[str] = "SQL execution successful"
    AI_FIELD_COMPUTATION: Final[str] = "Computing AI field"
    BATCH_PROCESSING: Final[str] = "Processing batch"
    URL_SCRAPING: Final[str] = "Scraping URL content"


class ErrorMessages:
    MISSING_API_KEY: Final[str] = "API key is required"
    MISSING_DATABASE_URL: Final[str] = "DATABASE_URL environment variable is required"
    INVALID_FIELD_STRUCTURE: Final[str] = "Invalid field structure"
    QUERY_EXECUTION_FAILED: Final[str] = "Query execution failed"
    AI_COMPUTATION_FAILED: Final[str] = "AI field computation failed" 