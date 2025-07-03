import time
from typing import Any, Callable, Dict

from utils import get_logger

logger = get_logger("hooks")


def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Log the duration of the function call"""
    logger.info(f"About to call {function_name} with arguments: {arguments}")

    start_time = time.time()

    # Call the function
    result = function_call(**arguments)

    end_time = time.time()
    duration = end_time - start_time

    logger.info(f"Function {function_name} took {duration:.2f} seconds to execute")

    # Return the result
    return result


def confirmation_hook(
    function_name: str, function_call: Callable, arguments: Dict[str, Any]
):
    """Confirm the function call"""
    if function_name != "get_top_hackernews_stories":
        raise ValueError("This tool is not allowed to be called")
    return function_call(**arguments)
