import logging
import requests
from io import BytesIO
from PIL import Image
import torch
import numpy as np
from transformers import CLIPProcessor, CLIPModel
import torch.nn.functional as F
from typing import Annotated
from agno.tools import tool
from src.tools.helper.helper import _score_thumbnail

# ─── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CLIP model and processor globally
CLIP_MODEL_NAME = "openai/clip-vit-large-patch14"
logger.info(f"Loading CLIP model {CLIP_MODEL_NAME}…")
model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)

# Global parameters
TEMPERATURE = 0.07
SCALE = 5.0

# Prompts covering design, clarity, emotion, composition
POSITIVE_PROMPTS = [
    "eye-catching thumbnail",
    "bold, vibrant colors",
    "clear, readable text",
    "prominent faces",
    "professional design"
]
NEGATIVE_PROMPTS = [
    "blurry or out of focus",
    "dark or underexposed",
    "dull colors",
    "small or unreadable text",
    "cluttered layout"
]

def _download_image(url: str) -> Image.Image:
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")

@tool(
    name="score_thumbnail",
    description="Analyzes a YouTube video thumbnail and returns a score indicating its visual appeal and effectiveness.",
    show_result=True,
    cache_results=True,
    cache_ttl=3600,
    cache_dir="/tmp/agno_cache"
)
def score_thumbnail(
    thumbnail_url: Annotated[str, """
        The URL of the YouTube video thumbnail to analyze.
        This should be a direct URL to the image file.
        Example: 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
    """]
) -> float:
    """
    Compute a 0–1 score for how "attractive" a thumbnail is.
    """
    return _score_thumbnail(thumbnail_url)