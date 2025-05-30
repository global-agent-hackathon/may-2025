from typing import Dict, List

GEMINI_FLASH = "gemini-2.0-flash"
GEMINI_FLASH_LITE = "gemini-2.0-flash-lite"

LLM_TEMPERATURE = 0.2
LLM_SELECTOR_TEMPERATURE = 0.1

NEEDS_MORE_CONTEXT_PHRASES = [
    "need more context", 
    "more information needed",
    "additional context",
    "more details required",
    "not enough information"
]

DEFAULT_PARAMS = {
    "crypto_news": {
        "limit": 25,
        "hours_back": 24
    },
    "crypto_search": {
        "limit": 10
    },
    "twitter": {
        "limit": 10
    }
}