from typing import List, Union, Dict, Any
from typing import Annotated
from agno.tools import tool
from src.tools.helper.helper import _sentiment_score

@tool(
    name="sentiment_score",
    description="Calculate the average sentiment score for text using TextBlob's sentiment analysis.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600,
    cache_dir="/tmp/agno_cache"
)
def sentiment_score(
    texts: Annotated[Union[str, List[str]], """
        A single text string or a list of text strings to analyze.
        The function will calculate the average sentiment across all provided texts.
        Example: "Great video!" or ["Great video!", "This was terrible", "I learned a lot"]
    """]
) -> float:
    """
    Calculate the average sentiment score for a single text or a list of texts using TextBlob.
    The sentiment score ranges from -1.0 (most negative) to 1.0 (most positive).
    
    Args:
        texts (Union[str, List[str]]): A single text string or a list of text strings to analyze
        
    Returns:
        float: Average sentiment score for the given text(s)
        
    Example:
        >>> sentiment_score("Great video!")
        0.8
        >>> comments = ["Great video!", "This was terrible", "I learned a lot"]
        >>> sentiment_score(comments)
        -0.06666666666666667
    """
    return _sentiment_score(texts)