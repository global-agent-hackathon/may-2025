from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import tempfile
import shutil
from agents.code_agent import manim_agent
from agents.debugger_agent import debugger_agent
from agents.decompose_agent import animation_decomposer_agent
from agents.updater_agent import updater_agent
from utils import run_manim_code, extract_scene_class_name, clean_manim_code
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Added 127.0.0.1
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)
STATIC_VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static_videos")

if not os.path.exists(STATIC_VIDEOS_DIR):
    os.makedirs(STATIC_VIDEOS_DIR)
app.mount("/videos", StaticFiles(directory=STATIC_VIDEOS_DIR), name="static_videos")

@app.get("/generate-animation")
async def generate_animation(query: str):
    logger.info(f"Received request for /generate-animation with query: '{query}'")
    temp_dir = tempfile.mkdtemp()
    video_url = None
    manim_code_result = ""
    manim_code = ""
    scene_name = ""
    stdout = ""
    stderr = ""
    try:
        enhanced_query = animation_decomposer_agent.run(query).content
        logger.info(f"Enhanced query: '{enhanced_query}'")
        manim_code_result = manim_agent.run(enhanced_query).content
        logger.info(f"Initial Manim code result from agent: '{manim_code_result[:200]}...'") # Log snippet
        manim_code = clean_manim_code(manim_code_result)
        logger.info(f"Cleaned Manim code: '{manim_code[:200]}...'") # Log snippet
        scene_name = extract_scene_class_name(manim_code)
        logger.info(f"Extracted scene name: '{scene_name}'")
        
        if not scene_name:
            stderr = "Could not automatically find a Scene class name in the generated code."
            logger.warning(stderr)
            response_data = {
                "manim_code": manim_code,
                "video_path": None,
                "stdout": "",
                "stderr": stderr
            }
            logger.info(f"Returning response (no scene name): {response_data}")
            return response_data
            
        video_fs_path, stdout, stderr = run_manim_code(manim_code, temp_dir, scene_name)
        logger.info(f"run_manim_code initial attempt - video_fs_path: {video_fs_path}, stdout: '{stdout[:200]}...', stderr: '{stderr[:200]}...'")
        
        if video_fs_path:
            video_url = f"/videos/{os.path.basename(video_fs_path)}"
        elif stderr: 
            logger.warning(f"Initial run_manim_code failed. Attempting debug. Error: {stderr}")
            for i in range(1, 3): # Max 2 debug attempts
                logger.info(f"Debug attempt {i}")
                debug_input = f"Code: {manim_code}\\nError: {stderr}"
                manim_code_result = debugger_agent.run(debug_input).content
                logger.info(f"Debugger agent Manim code result (attempt {i}): '{manim_code_result[:200]}...'")
                manim_code = clean_manim_code(manim_code_result)
                logger.info(f"Cleaned Manim code after debug (attempt {i}): '{manim_code[:200]}...'")
                scene_name = extract_scene_class_name(manim_code)
                logger.info(f"Extracted scene name after debug (attempt {i}): '{scene_name}'")
                if not scene_name:
                    stderr = stderr + "\\nDebugger failed to produce a valid scene name."
                    logger.warning(f"Debugger failed to find scene name (attempt {i})")
                    break 
                video_fs_path, stdout, stderr = run_manim_code(manim_code, temp_dir, scene_name)
                logger.info(f"run_manim_code after debug (attempt {i}) - video_fs_path: {video_fs_path}, stdout: '{stdout[:200]}...', stderr: '{stderr[:200]}...'")
                if video_fs_path:
                    video_url = f"videos/{os.path.basename(video_fs_path)}" # Original had /videos/, this seems like a typo
                    logger.info(f"Debug successful (attempt {i}), video_url: {video_url}")
                    break
                elif i < 2: # Log if not the last debug attempt and still failing
                     logger.warning(f"Debug attempt {i} failed. Error: {stderr}")


        response_data = {
            "manim_code": manim_code,
            "video_path": video_url, 
            "stdout": stdout,
            "stderr": stderr
        }
        logger.info(f"Returning final response: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"Exception in /generate-animation: {str(e)}", exc_info=True)
        # Ensure some response is returned even on unexpected error
        return {
            "manim_code": manim_code, # Return whatever code was generated, if any
            "video_path": None,
            "stdout": stdout,
            "stderr": stderr + f"\\nServer error: {str(e)}"
        }
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.get("/update-animation")
async def update_animation(query: str, manim_code_input:str): 
    logger.info(f"Received request for /update-animation with query: '{query}' and manim_code_input: '{manim_code_input[:200]}...'")
    temp_dir = tempfile.mkdtemp()
    video_url = None 
    manim_code_to_return = manim_code_input 
    current_manim_code = manim_code_input # Initialize
    scene_name = ""
    stdout = ""
    stderr = ""
    try:
        enhanced_query = animation_decomposer_agent.run(query).content
        logger.info(f"Enhanced query for update: '{enhanced_query}'")
        updater_input = f"Query to make changes: {enhanced_query}\\nManim code: {manim_code_input}"
        updated_manim_code_result = updater_agent.run(updater_input).content
        logger.info(f"Updater agent Manim code result: '{updated_manim_code_result[:200]}...'")
        current_manim_code = clean_manim_code(updated_manim_code_result)
        manim_code_to_return = current_manim_code 
        logger.info(f"Cleaned Manim code after update: '{current_manim_code[:200]}...'")
        scene_name = extract_scene_class_name(current_manim_code)
        logger.info(f"Extracted scene name for update: '{scene_name}'")

        if not scene_name:
            stderr = "Could not automatically find a Scene class name in the updated code."
            logger.warning(stderr)
            response_data = {
                "manim_code": manim_code_to_return,
                "video_path": None,
                "stdout": "",
                "stderr": stderr
            }
            logger.info(f"Returning response from update (no scene name): {response_data}")
            return response_data

        video_fs_path, stdout, stderr = run_manim_code(current_manim_code, temp_dir, scene_name)
        logger.info(f"run_manim_code initial update attempt - video_fs_path: {video_fs_path}, stdout: '{stdout[:200]}...', stderr: '{stderr[:200]}...'")
        
        if video_fs_path:
            video_url = f"/videos/{os.path.basename(video_fs_path)}"
        elif stderr: 
            logger.warning(f"Initial run_manim_code for update failed. Attempting debug. Error: {stderr}")
            for i in range(1, 3): # Max 2 debug attempts
                logger.info(f"Update debug attempt {i}")
                debug_input = f"Code: {current_manim_code}\\nError: {stderr}"
                debugged_code_result = debugger_agent.run(debug_input).content
                logger.info(f"Debugger agent Manim code result for update (attempt {i}): '{debugged_code_result[:200]}...'")
                current_manim_code = clean_manim_code(debugged_code_result)
                manim_code_to_return = current_manim_code 
                logger.info(f"Cleaned Manim code after update debug (attempt {i}): '{current_manim_code[:200]}...'")
                scene_name = extract_scene_class_name(current_manim_code)
                logger.info(f"Extracted scene name after update debug (attempt {i}): '{scene_name}'")
                if not scene_name:
                    stderr = stderr + "\\nDebugger failed to produce a valid scene name during update."
                    logger.warning(f"Debugger failed to find scene name for update (attempt {i})")
                    break
                video_fs_path, stdout, stderr = run_manim_code(current_manim_code, temp_dir, scene_name)
                logger.info(f"run_manim_code after update debug (attempt {i}) - video_fs_path: {video_fs_path}, stdout: '{stdout[:200]}...', stderr: '{stderr[:200]}...'")
                if video_fs_path:
                    video_url = f"/videos/{os.path.basename(video_fs_path)}"
                    logger.info(f"Update debug successful (attempt {i}), video_url: {video_url}")
                    break
                elif i < 2:
                     logger.warning(f"Update debug attempt {i} failed. Error: {stderr}")

        response_data = {
            "manim_code": manim_code_to_return,
            "video_path": video_url, 
            "stdout": stdout,
            "stderr": stderr
        }
        logger.info(f"Returning final response from update: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"Exception in /update-animation: {str(e)}", exc_info=True)
        return {
            "manim_code": manim_code_to_return, # Return whatever code was generated/updated, if any
            "video_path": None,
            "stdout": stdout,
            "stderr": stderr + f"\\nServer error: {str(e)}"
        }
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
