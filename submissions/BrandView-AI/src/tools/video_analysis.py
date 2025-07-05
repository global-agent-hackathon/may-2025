import os
import torch
from typing import Dict, List, Optional, Tuple, Annotated, Callable, Any
import whisper
from transformers import AutoTokenizer, AutoModelForCausalLM
import requests
from pathlib import Path
import tempfile
import yt_dlp
from agno.tools import tool
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.tools.helper.helper import _video_to_text, _analyze_video_content

def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Pre-hook function that runs before the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result

@tool(
    name="video_to_text",
    description="Convert video content to text using Whisper speech recognition model.",
    show_result=True,
    stop_after_tool_call=True,
    tool_hooks=[logger_hook],
    cache_results=True,
    cache_dir="/tmp/agno_cache",
    cache_ttl=3600  # Cache for 1 hour
)
def video_to_text(
    video_id: Annotated[str, """
        The unique identifier of the YouTube video.
        This is the part of the YouTube URL after 'v='. For example:
        - For the URL 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', the `video_id` would be 'dQw4w9WgXcQ'.
    """]
) -> str:
    """
    Convert video content to text using Whisper.
    
    Args:
        video_id (str): YouTube video ID
        model_size (str): Size of the Whisper model to use
        
    Returns:
        str: Transcribed text from the video
        
    Raises:
        Exception: If video download or transcription fails
    """
    return _video_to_text(video_id)

@tool(
    name="analyze_video_content",
    description="Analyze video content with scene-based transcription and sponsor detection.",
    show_result=True,
    stop_after_tool_call=True,
    tool_hooks=[logger_hook],
    cache_results=False,
    cache_dir="/tmp/agno_cache",
    cache_ttl=3600  # Cache for 1 hour
)
def analyze_video_content(
    video_id: Annotated[str, """
        The unique identifier of the YouTube video.
        This is the part of the YouTube URL after 'v='. For example:
        - For the URL 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', the `video_id` would be 'dQw4w9WgXcQ'.
    """]
) -> Dict:
    """
    Analyze video content with scene-based transcription and sponsor detection.
    
    Args:
        video_id (str): YouTube video ID
        
    Returns:
        Dict: Analysis results including:
            - scenes: List of scenes with timestamps, transcriptions, summaries, and sponsor mentions
            - sponsors: List of detected sponsors
            - metadata: Dictionary containing video title and description
            
    Raises:
        Exception: If video download or analysis fails
    """
    return _analyze_video_content(video_id)