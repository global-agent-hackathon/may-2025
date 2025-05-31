from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
from dotenv import load_dotenv
from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import streamlit as st
import tempfile
import subprocess
import shutil
import json # For parsing if needed, though Pydantic model might be direct
import time # For generating unique timestamps

load_dotenv()

# Define the persistent storage directory for videos relative to this utils.py file
# This will place 'static_videos' inside the 'backend' directory.
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PERSISTENT_VIDEO_DIR = os.path.join(BACKEND_DIR, "static_videos")

def clean_manim_code(code_str: str) -> str:
    """Cleans the raw output from Manim agents."""
    if not isinstance(code_str, str):
        st.warning(f"Code cleaning received non-string input: {type(code_str)}. Returning empty string.")
        return ""
        
    lines = code_str.strip().split('\n')
    
    # Remove markdown fences if they slip through
    if lines and lines[0].strip().startswith("```python"):
        lines.pop(0)
    if lines and lines[0].strip().startswith("```"):
        lines.pop(0)
    if lines and lines[-1].strip() == "```":
        lines.pop()

    cleaned_code = "\n".join(lines).strip()

    # Ensure `from manim import *`
    if not cleaned_code.startswith("from manim import *"):
        # Check if a more specific import is already there (e.g. from manim import Scene, Square)
        # This is a simple check, could be more robust
        is_manim_imported = any("from manim import" in line or "import manim" in line for line in cleaned_code.splitlines()[:5])
        if not is_manim_imported:
            cleaned_code = "from manim import *\n\n" + cleaned_code
            
    return cleaned_code

def extract_scene_class_name(manim_code: str) -> Optional[str]:
    """Extracts the first Manim scene class name from the code."""
    for line in manim_code.split("\n"):
        line_strip = line.strip()
        if line_strip.startswith("class ") and ("(Scene):" in line_strip or "(ThreeDScene):" in line_strip):
            try:
                class_name = line_strip.split("class ")[1].split("(")[0].strip()
                return class_name
            except IndexError:
                continue
    return None

def run_manim_code(manim_code: str, temp_dir: str, scene_name:str=None) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Runs the Manim code and returns (video_path, stdout, stderr).
    video_path is None if rendering fails or video not found.
    """
    script_filename = "generated_animation.py"

    # Ensure the temporary directory exists and has correct permissions before trying to write to it
    try:
        os.makedirs(temp_dir, exist_ok=True)
        os.chmod(temp_dir, 0o755) # Set permissions to ensure access
    except OSError as e:
        return None, None, f"Error creating or setting permissions for temp directory {temp_dir}: {e}"

    temp_file_path = os.path.join(temp_dir, script_filename)

    try:
        with open(temp_file_path, "w") as f:
            f.write(manim_code)
    except IOError as e:
        return None, None, f"Error writing Manim script to {temp_file_path}: {e}"

    scene_class_name = extract_scene_class_name(manim_code)
    if not scene_class_name:
        return None, None, "Could not automatically find a Scene class name in the generated code."

    manim_command = [
        "manim", "-pql", # Preview, low quality
        script_filename,
        scene_class_name
    ]

    try:
        # Ensure the persistent video directory exists
        os.makedirs(PERSISTENT_VIDEO_DIR, exist_ok=True)
        os.chmod(PERSISTENT_VIDEO_DIR, 0o755) # Ensure it's accessible

        # Generate a timestamp to make temporary Manim output filenames unique if needed by Manim internally
        # However, our final output will be consistently named 'current_video.mp4'
        # timestamp = str(int(time.time())) # Not strictly needed for final output name here
        
        result = subprocess.run(
            manim_command,
            check=False,
            capture_output=True,
            text=True,
            cwd=temp_dir, # Run Manim in the temp directory
            timeout=120 # Add a timeout to prevent indefinite hanging
        )

        if result.returncode != 0:
            error_message = f"Manim rendering failed (exit code {result.returncode})."
            error_message += f"\nStdout:\n{result.stdout}" if result.stdout else "\nNo stdout."
            error_message += f"\nStderr:\n{result.stderr}" if result.stderr else "\nNo stderr."
            return None, result.stdout, error_message

        # Manim default output path structure
        video_relative_path = os.path.join(
            "media", "videos", "generated_animation", "480p15", f"{scene_class_name}.mp4"
        )
        video_path = os.path.join(temp_dir, video_relative_path)

        if os.path.exists(video_path):
            # Define the path for the final, persistently stored video
            final_video_filename = scene_class_name+".mp4"# Consistent name for easy access
            persistent_final_video_path = os.path.join(PERSISTENT_VIDEO_DIR, final_video_filename)
            
            # Copy the rendered video from Manim's output in temp_dir to the persistent storage
            shutil.copy2(video_path, persistent_final_video_path)
            
            # Ensure permissions are set correctly on the copied file
            try:
                os.chmod(persistent_final_video_path, 0o644) # Readable by all
            except Exception as e:
                print(f"Warning: Could not set permissions on video file {persistent_final_video_path}: {e}")
            
            return persistent_final_video_path, result.stdout, result.stderr
        else:
            # Try to list the directory contents to check what was created
            try:
                output_dir = os.path.dirname(video_path)
                if os.path.exists(output_dir):
                    dir_contents = os.listdir(output_dir)
                    error_message = f"Animation process completed, but video file not found at {video_path}.\nDirectory contents: {dir_contents}"
                else:
                    error_message = f"Animation process completed, but output directory {output_dir} does not exist."
            except Exception as e:
                error_message = f"Animation process completed, but error listing directory: {str(e)}"
            
            error_message += f"\nManim Stdout:\n{result.stdout}" if result.stdout else ""
            error_message += f"\nManim Stderr:\n{result.stderr}" if result.stderr else ""
            # List files for debugging
            media_dir = os.path.join(temp_dir, "media")
            if os.path.exists(media_dir):
                error_message += f"\nFiles in {media_dir}: {os.listdir(media_dir)}"
                specific_video_dir = os.path.join(temp_dir, "media", "videos", "generated_animation", "480p15")
                if os.path.exists(specific_video_dir):
                     error_message += f"\nFiles in {specific_video_dir}: {os.listdir(specific_video_dir)}"
                else:
                    error_message += f"\nDirectory {specific_video_dir} not found."
            else:
                error_message += f"\nDirectory {media_dir} not found."

            return None, result.stdout, error_message

    except FileNotFoundError:
        return None, None, "Error: Manim command not found. Is Manim installed and in your system's PATH?"
    except subprocess.TimeoutExpired:
        return None, None, "Manim rendering timed out after 120 seconds."
    except Exception as e:
        return None, None, f"An unexpected error occurred during Manim execution: {str(e)}"
