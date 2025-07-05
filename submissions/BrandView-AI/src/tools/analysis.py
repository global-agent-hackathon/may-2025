from typing import List, Tuple
from typing import Annotated
from agno.tools import tool
from src.tools.helper.helper import _predict_next_video_views

@tool(
    name="predict_next_video_views",
    description="Predict view count ranges for the next video based on historical view data using a log-normal model.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600,
    cache_dir="/tmp/agno_cache"
)
def predict_next_video_views(
    historical_views: Annotated[List[int], """
        List of past view counts for videos. All values must be positive integers.
        Example: [1000, 2000, 1500, 3000]
    """],
    confidence_level: Annotated[float, """
        The desired confidence level for the prediction interval.
        Must be between 0 and 1. Default is 0.90 (90% confidence).
    """] = 0.90,
    interval_type: Annotated[str, """
        The type of confidence interval to compute. Valid values are:
        - "lower": one-sided lower bound (L, ∞)
        - "upper": one-sided upper bound (-∞, U)
        - "two-sided": central interval (L, U)
        Default is "two-sided".
    """] = "two-sided"
) -> Tuple[float, float]:
    """
    Predict a one‑ or two‑sided confidence interval for the next video's view count,
    assuming a log‑normal model.

    Args:
        historical_views (List[int]): Past view counts (must be >0)
        confidence_level (float): Coverage for the bound(s) (default 0.90)
        interval_type (str): 
            - "lower"      → one‑sided lower bound (L, ∞)
            - "upper"      → one‑sided upper bound (-∞, U)
            - "two-sided" → central interval (L, U)

    Returns:
        Tuple[float, float]:
            Depending on `interval_type`:
              - "lower":      (L, ∞)  with  P(X ≥ L) = confidence_level
              - "upper":      (-∞, U) with  P(X ≤ U) = confidence_level
              - "two-sided": (L, U)  with  P(L ≤ X ≤ U) = confidence_level

    Raises:
        ValueError: if list is empty, contains non‑positive values, or invalid `interval_type`
    """
    return _predict_next_video_views(historical_views, confidence_level, interval_type)