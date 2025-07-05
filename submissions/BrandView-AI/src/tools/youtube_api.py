# YouTube API Wrapper
# This module will handle YouTube API interactions 
from typing import Annotated, Callable, Any
from agno.agent import Agent
from agno.tools import tool
from typing import Dict, List

from src.tools.helper.helper import _download_video, _resolve_channel_id, _fetch_video_details, _search_youtube_channel_videos, _fetch_channel_info, _fetch_videos, _fetch_comments, _introspect_channel, _search_youtube_channels, _search_and_introspect_channel, _fetch_video_statistics


def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Pre-hook function that runs before the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result

@tool(
    name="download_video",                                   # Custom name for the tool
    description="Download a YouTube video using yt-dlp.",      # Custom description
    show_result=True,                                         # Show result after function call
    stop_after_tool_call=True,                                # Return the result immediately after the tool call
    tool_hooks=[logger_hook],                                 # Hook to run before and after execution
    cache_results=False,                                      # No caching for downloading videos
)
def download_video(
    video_id: Annotated[str, "The unique identifier of the YouTube video. It is the part of the YouTube URL after 'v='. Example: For the URL 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', the 'video_id' is 'dQw4w9WgXcQ.'"],
    output_path: Annotated[str, "The directory where the video will be saved. Defaults to 'downloads'. If not provided, a directory named 'downloads' will be created. Example: 'videos' or 'C:/Users/YourName/Videos'"] = "downloads",
    quality: Annotated[str, "The desired video quality. Options include 'best', 'worst', or specific resolutions like '720p', '1080p'. Defaults to 'best'. Example: '720p', 'best', '1080p'"] = "best"
) -> str:
    """
    Download a YouTube video using yt-dlp.
    
    Args:
        video_id (str): The YouTube video ID
        output_path (str): Directory to save the video (default: "downloads")
        quality (str): Video quality to download (default: "best")
            Options: "best", "worst", "720p", "1080p", etc.
            
    Returns:
        str: Path to the downloaded video file
        
    Raises:
        Exception: If download fails
    """
    return _download_video(video_id, output_path, quality)

@tool(
    name="resolve_channel_id",
    description=(
        "Resolves a YouTube channel identifier (handle, custom URL, or channel ID) "
        "to the official YouTube channel ID. Useful for ensuring downstream APIs get the correct ID."
    ),
    show_result=True,
    stop_after_tool_call=False,
    tool_hooks=[logger_hook],
    cache_results=True,
    cache_dir="/tmp/agno_cache",
    cache_ttl=3600  # Cache result for 1 hour
)
def resolve_channel_id(
    channel_identifier: Annotated[str, """
        The identifier of the YouTube channel, which can be one of the following:
        - Channel handle (e.g., "@channelname")
        - Custom URL (e.g., "youtube.com/c/channelname")
        - Channel ID (e.g., "UC...")
        The function will resolve this identifier to the YouTube channel ID.
        Example: For "@channelname", "youtube.com/c/channelname", or "UCxxxxxxx", it will return the resolved channel ID.
    """]
) -> str:
    """
    Resolve a YouTube channel handle, custom URL, or channel ID to a channel ID.
    
    Args:
        channel_identifier (str): Can be:
            - Channel handle (e.g., "@channelname")
            - Custom URL (e.g., "youtube.com/c/channelname")
            - Channel ID (e.g., "UC...")
            
    Returns:
        str: The resolved channel ID
        
    Raises:
        ValueError: If the channel cannot be found
    """
    return _resolve_channel_id(channel_identifier)

@tool(
    name="fetch_video_details",
    description="Fetches detailed metadata about a YouTube video, including view count, likes, duration, etc.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600,
    cache_dir="/tmp/agno_cache"
)
def fetch_video_details(video_id: str) -> Dict:
    """
    Fetch detailed information about a specific video.
    
    Args:
        video_id (str): The YouTube video ID
        
    Returns:
        Dict: Video information including:
            - id: Video ID
            - title: Video title
            - description: Video description
            - publishedAt: Publication date
            - viewCount: Number of views
            - likeCount: Number of likes
            - commentCount: Number of comments
            - duration: Video duration
            - thumbnails: Video thumbnails
    """
    return _fetch_video_details(video_id)

@tool(
    name="search_youtube_channel_videos",
    description=(
        "Search for videos within a specific YouTube channel that match a given term. "
        "Returns a list of videos."
    ),
    show_result=True,
    stop_after_tool_call=True,
    tool_hooks=[logger_hook],
    cache_results=True,
    cache_dir="/tmp/agno_cache",
    cache_ttl=3600
)
def search_youtube_channel_videos(
    channel_id: Annotated[str, "The unique identifier of the YouTube channel. This can be obtained from the channel's URL. Example: For the URL 'https://www.youtube.com/channel/UCXgGY0w3hN4+Vq3po9q7mn' the 'channel_id' is 'UCXgGY0w3hN4+Vq3po9q7mn'."],
    search_term: Annotated[str, "The term to search for in video titles and descriptions. This is the keyword or phrase to look for within the channel's videos. Example: 'python tutorial' or 'travel vlog'."],
    max_results: Annotated[int, "The maximum number of search results to return. This limits the number of videos that will be retrieved from the search. Default is 10. Example: 5 or 20." ] = 10
) -> List[Dict]:
    """
    Search for videos within a specific channel that match the search term.
    
    Args:
        channel_id (str): The YouTube channel ID
        search_term (str): The term to search for in video titles and descriptions
        max_results (int): Maximum number of videos to return (default: 10)
        
    Returns:
        List[Dict]: List of video information including:
            - id: Video ID
            - title: Video title
            - description: Video description
            - publishedAt: Publication date
            - viewCount: Number of views
            - likeCount: Number of likes
            - commentCount: Number of comments
            - duration: Video duration
            - thumbnails: Video thumbnails
    """
    return _search_youtube_channel_videos(channel_id, search_term, max_results)

@tool(
    name="fetch_channel_info",
    description="Fetches basic metadata about a YouTube channel such as title, subscriber count, view count, and thumbnails.",
    show_result=True,
    stop_after_tool_call=False,
    tool_hooks=[logger_hook],
    cache_results=True,
    cache_dir="/tmp/agno_cache",
    cache_ttl=3600  # Cache for 1 hour
)
def fetch_channel_info(
    channel_id: Annotated[str, """
        The unique identifier of the YouTube channel. 
        This is the part of the YouTube URL after '/channel/'. For example:
        - For the URL 'https://www.youtube.com/channel/UCxxxxxxx', the `channel_id` would be 'UCxxxxxxx'.
        - This can also be the channel ID directly (e.g., 'UC1234567890').
    """]
) -> Dict:
    """
    Fetch basic channel information including subscriber count, view count, and video count.
    
    Args:
        channel_id (str): The YouTube channel ID
        
    Returns:
        Dict: Channel information including:
            - id: Channel ID
            - title: Channel title
            - description: Channel description
            - subscriberCount: Number of subscribers
            - viewCount: Total view count
            - videoCount: Number of videos
            - thumbnails: Channel thumbnails
    """
    return _fetch_channel_info(channel_id)

@tool(
    name="fetch_videos",
    description="Fetches information about the videos on a YouTube channel based on the channel ID given the max number of videos to fetch.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600,
    cache_dir="/tmp/agno_cache"
)
def fetch_videos(
    channel_id: Annotated[str, """
        The unique identifier of the YouTube channel. 
        This is the part of the YouTube URL after '/channel/'. For example:
        - For the URL 'https://www.youtube.com/channel/UCxxxxxxx', the `channel_id` would be 'UCxxxxxxx'.
        - This can also be the channel ID directly (e.g., 'UC1234567890').
    """],
    max_results: Annotated[int, """
        The maximum number of videos to fetch from the channel. 
        This value controls how many recent videos will be returned.
        Default is 10, but can be set to any integer value.
    """ ] = 10
) -> List[Dict]:
    """
    Fetch recent videos from a channel.
    
    Args:
        channel_id (str): The YouTube channel ID
        max_results (int): Maximum number of videos to fetch (default: 10)
        
    Returns:
        List[Dict]: List of video information including:
            - id: Video ID
            - title: Video title
            - description: Video description
            - publishedAt: Publication date
            - viewCount: Number of views
            - likeCount: Number of likes
            - commentCount: Number of comments
            - duration: Video duration
            - thumbnails: Video thumbnails
    """
    return _fetch_videos(channel_id, max_results)

@tool(
    name="fetch_video_statistics",
    description="Fetches statistics (views, likes, comments, favorites) for recent videos on a YouTube channel, filtered by recency and duration.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600,
    cache_dir="/tmp/agno_cache"
)
def fetch_video_statistics(
    channel_id: Annotated[str, """
        The unique identifier of the YouTube channel. 
        This is the part of the YouTube URL after '/channel/'. For example:
        - For the URL 'https://www.youtube.com/channel/UCxxxxxxx', the `channel_id` would be 'UCxxxxxxx'.
        - This can also be the channel ID directly (e.g., 'UC1234567890').
    """],
    max_results: Annotated[int, """
        The maximum number of videos to fetch statistics for. 
        This value controls how many recent videos will be analyzed.
        Default is 10, but can be set to any integer value.
    """ ] = 10,
    months: Annotated[int, """
        Only include videos published within this number of months.
        Default is 6 months.
    """ ] = 6,
    min_duration_minutes: Annotated[int, """
        Only include videos that are at least this many minutes long.
        Default is 3 minutes.
    """ ] = 3
) -> List[Dict]:
    """
    Fetch statistics for recent videos on a channel.
    
    Args:
        channel_id (str): The YouTube channel ID
        max_results (int): Maximum number of videos to fetch statistics for (default: 10)
        months (int): Only include videos from the last X months (default: 6)
        min_duration_minutes (int): Minimum video duration in minutes (default: 3)
        
    Returns:
        List[Dict]: List of video statistics including:
            - videoId: Video ID
            - viewCount: Number of views
            - likeCount: Number of likes
            - commentCount: Number of comments
            - favoriteCount: Number of times the video was favorited
            - durationMinutes: Duration of the video in minutes
            - publishedAt: Publication date of the video
    """
    return _fetch_video_statistics(channel_id, max_results, months, min_duration_minutes)

@tool(
    name="fetch_comments",
    description="Fetches top-level comments from a YouTube video using its video ID.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600,
    cache_dir="/tmp/agno_cache"
)
def fetch_comments(
    video_id: Annotated[str, """
        The unique identifier of the YouTube video.
        This is the part of the YouTube URL after 'v='. For example:
        - For the URL 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', the `video_id` would be 'dQw4w9WgXcQ'.
        - This ID is used to fetch the comments for the specific video.
    """],
    max_results: int = 100
) -> List[Dict]:
    """
    Fetch comments for a video.
    
    Args:
        video_id (str): The YouTube video ID
        max_results (int): Maximum number of comments to fetch (default: 100)
        
    Returns:
        List[Dict]: List of comment information including:
            - id: Comment ID
            - author: Author name
            - text: Comment text
            - likeCount: Number of likes
            - publishedAt: Publication date
    """
    return _fetch_comments(video_id, max_results)
    
@tool(
    name="introspect_channel",
    description="Fetch comprehensive channel data including basic info and recent videos using either a channel handle or full URL.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600
)
def introspect_channel(
    identifier: Annotated[str, """
        A YouTube channel identifier, which can be one of the following:
        - A full channel URL (e.g., https://www.youtube.com/channel/UCxxxxxx or https://www.youtube.com/@handle)
        - A channel handle (e.g., @veritasium)
        - A direct channel ID (e.g., UCxxxxxxx)
    """],
    max_videos: Annotated[int, """
        The maximum number of recent videos to fetch from the channel.
    """] = 10
) -> Dict:
    """
    Resolve the identifier to a channel ID, fetch channel info and recent videos.
    """
    return _introspect_channel(identifier, max_videos)

@tool(
    name="search_youtube_channels",
    description="Search for YouTube channels using a keyword or topic.",
    show_result=True,
    cache_results=True,
    cache_ttl=1800
)
def search_youtube_channels(
        query: Annotated[str, """
        The search query to find relevant YouTube channels. 
        For example, 'AI education', 'finance tips', or 'Veritasium'.
    """],
        max_results: Annotated[int, """
        The maximum number of channel search results to return.
        Default is 5, max is 50.
    """] = 5
) -> List[Dict]:
    """
    Search YouTube for channels related to the query.
    Returns a list of channel summaries including ID, title, description, and thumbnail.
    """
    return _search_youtube_channels(query, max_results)

@tool(
        name="search_and_introspect_channel",
        description="Search YouTube channels by keyword, then fetch full info and recent videos for the top match.",
        show_result=True,
        cache_results=True,
        cache_ttl=1800
)
def search_and_introspect_channel(
            query: Annotated[str, """
            A keyword or topic to search for relevant YouTube channels. 
            Example: 'machine learning', 'music reviews', 'travel vlogs'.
        """],
            video_count: Annotated[int, """
            Number of recent videos to fetch from the top-matching channel.
            Defaults to 5.
        """] = 5
    ) -> Dict:
        """
        Searches for YouTube channels by query, then fetches full info and videos for the top result.
        """
        return _search_and_introspect_channel(query, video_count)