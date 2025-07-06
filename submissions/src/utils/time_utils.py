import logging
from typing import Optional
from datetime import datetime, timedelta
import dateparser
from dateutil.relativedelta import relativedelta
import datefinder

logger = logging.getLogger(__name__)

def extract_time_period(query: str) -> Optional[int]:
    """
    Extract time period from query and convert to hours.
    Uses multiple libraries to improve accuracy.
    """
    logger.debug(f"Extracting time period from query: {query}")
    
    try:
        settings = {
            'RELATIVE_BASE': datetime.now(),
            'PREFER_DATES_FROM': 'past'
        }
        parsed_date = dateparser.parse(query, settings=settings)
        
        if parsed_date:
            delta = datetime.now() - parsed_date
            hours_back = max(1, int(delta.total_seconds() // 3600))
            logger.info(f"Extracted time period using dateparser: {hours_back} hours")
            return hours_back
            
        matches = list(datefinder.find_dates(query))
        if matches:
            date_match = matches[0]
            delta = datetime.now() - date_match
            hours_back = max(1, int(delta.total_seconds() // 3600))
            logger.info(f"Extracted time period using datefinder: {hours_back} hours")
            return hours_back
        
        query_lower = query.lower()
        time_keywords = {
            "hour": 1, "hours": 1,
            "today": 24, "yesterday": 48,
            "this week": 168, "last week": 336,
            "this month": 720, "last month": 1440,
            "this year": 8760, "recent": 72,
            "latest": 24, "now": 12,
            "currently": 12, "right now": 12
        }
        
        for keyword, hours in time_keywords.items():
            if keyword in query_lower:
                logger.info(f"Found time keyword '{keyword}' in query: {hours} hours")
                return hours
        
        logger.debug("No time period found in query")
        return None
        
    except Exception as e:
        logger.warning(f"Error parsing time period: {str(e)}", exc_info=True)
        return None