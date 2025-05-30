from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from agno.agent import Agent
from agno.models.openai import OpenAIChat
# from agno.models.anthropic import Claude  # Removed - using OpenAI only
from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.tools.reasoning import ReasoningTools
from agno.media import Image, Audio, Video
import base64
import os
import uuid
from datetime import datetime
import dotenv
from pathlib import Path
from openai import OpenAI
from agno_agent import agent
from remote_agent import remote_agent_pool
import warnings
import logging

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

# Suppress specific warnings
warnings.filterwarnings("ignore", message=".*SyncHttpxClientWrapper.*")
warnings.filterwarnings("ignore", category=ResourceWarning)

# Reduce logging noise
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

# -----------------------------------------------------------------------------
# Multimodal Processing Functions
# -----------------------------------------------------------------------------

def process_multimodal_input(multimodal_data):
    """
    Process multimodal input data and return appropriate Agno media objects
    Args:
        multimodal_data: Dict containing image, audio, or video data
    Returns:
        Processed media object or None
    """
    if not multimodal_data or not isinstance(multimodal_data, dict):
        return None
    
    try:
        if 'image' in multimodal_data:
            image_data = multimodal_data['image']
            if isinstance(image_data, str):
                # Assume base64 encoded string
                return Image(base64_encoded=image_data)
            elif isinstance(image_data, dict) and 'base64' in image_data:
                return Image(base64_encoded=image_data['base64'])
        
        elif 'audio' in multimodal_data:
            audio_data = multimodal_data['audio']
            if isinstance(audio_data, str):
                return Audio(base64_encoded=audio_data)
            elif isinstance(audio_data, dict) and 'base64' in audio_data:
                return Audio(base64_encoded=audio_data['base64'])
        
        elif 'video' in multimodal_data:
            video_data = multimodal_data['video']
            print(f"Processing video input with size: {len(video_data.get('base64', '')) if isinstance(video_data, dict) else len(video_data)} chars")
            if isinstance(video_data, str):
                return Video(base64_encoded=video_data)
            elif isinstance(video_data, dict) and 'base64' in video_data:
                return Video(base64_encoded=video_data['base64'])
    
    except Exception as e:
        print(f"Error processing multimodal input: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    return None

def enhance_prompt_with_multimodal_context(prompt, media_type=None):
    """
    Enhance the prompt with multimodal context information
    Args:
        prompt: Original text prompt
        media_type: Type of media (image, audio, video)
    Returns:
        Enhanced prompt with multimodal context
    """
    if not media_type:
        return prompt
    
    context_additions = {
        'image': """
        
**MULTIMODAL CONTEXT**: An image has been provided along with this request. 
Please analyze the image content and incorporate visual elements, layout, design patterns, 
or any relevant visual information into your code generation. Consider:
- UI/UX elements shown in the image
- Color schemes and design patterns
- Layout structures
- Any text or data visible in the image
- Design inspiration for the prototype
        """,
        'audio': """
        
**MULTIMODAL CONTEXT**: An audio file has been provided along with this request.
Please consider any audio-related requirements, speech content, or audio processing 
needs when generating the code. This might include:
- Audio playback functionality
- Speech-to-text processing
- Audio analysis features
- Sound-based interactions
        """,
        'video': """
        
**MULTIMODAL CONTEXT**: A video file has been provided along with this request.
Please analyze the video content carefully and extract:

1. **UI/UX PATTERNS**:
   - Layout structures and grid systems shown
   - Navigation patterns and menu designs
   - Card layouts and listing presentations
   - Search/filter interfaces
   - Hero sections and landing page designs
   - Color schemes and visual hierarchy
   - Typography and spacing patterns
   - Interactive elements and animations

2. **FUNCTIONALITY OBSERVED**:
   - Search and filtering mechanisms
   - Listing/browsing interfaces
   - Detail view layouts
   - Booking/reservation flows
   - Map integrations
   - Image galleries and carousels
   - User interaction patterns
   - Responsive design behaviors

3. **DESIGN INSPIRATION**:
   - Modern, clean aesthetic elements
   - Professional color palettes
   - Component structures (cards, buttons, forms)
   - Animation and transition styles
   - Mobile and desktop layouts
   - Visual feedback mechanisms

Use the video as a blueprint to create a similar web application with:
- The same level of polish and professionalism
- Similar layout and component structures
- Comparable user experience flows
- Modern, responsive design
- Beautiful animations and interactions

Note: Since this is a video demonstration, focus on recreating the visual design, layout patterns, and user experience rather than exact functionality.
        """
    }
    
    return prompt + context_additions.get(media_type, '')

app = Flask(__name__)
# Configure larger upload limits for video files
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max request size

# Configure CORS to handle preflight requests correctly
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:3000", "http://localhost:5000", "*"],
    "supports_credentials": True,
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "X-Requested-With", "Authorization", "Access-Control-Allow-Origin"],
    "expose_headers": ["Content-Type", "X-CSRFToken"]
}})

# -----------------------------------------------------------------------------
# API Keys and Environment Setup
# -----------------------------------------------------------------------------
def load_api_keys():
    """Load API keys from environment"""
    return {
        "openai_key": os.environ.get("OPENAI_API_KEY"),
        "anthropic_key": os.environ.get("ANTHROPIC_API_KEY")
    }

def save_api_keys(openai_key=None, anthropic_key=None):
    """Save API keys to .env file"""
    env_path = Path('.env')
    
    # Read existing contents
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Update or add keys
    env_dict = {}
    for line in lines:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            env_dict[key] = value
    
    if openai_key is not None:
        env_dict['OPENAI_API_KEY'] = openai_key
    if anthropic_key is not None:
        env_dict['ANTHROPIC_API_KEY'] = anthropic_key
    
    # Write back to file
    with open(env_path, 'w') as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")
    
    # Update environment variables
    if openai_key is not None:
        os.environ['OPENAI_API_KEY'] = openai_key
    if anthropic_key is not None:
        os.environ['ANTHROPIC_API_KEY'] = anthropic_key
    
    # Reload dotenv
    dotenv.load_dotenv(override=True)

@app.route("/get_api_keys", methods=["GET"])
def get_api_keys():
    """Get API key status"""
    keys = load_api_keys()
    return jsonify({
        "openai_key": bool(keys["openai_key"]),
        "anthropic_key": bool(keys["anthropic_key"])
    })

@app.route("/save_api_keys", methods=["POST"])
def save_api_keys_route():
    """Save API keys"""
    try:
        data = request.get_json()
        openai_key = data.get("openai_key")
        anthropic_key = data.get("anthropic_key")
        
        # Only update keys that are provided
        save_api_keys(
            openai_key=openai_key if openai_key else None,
            anthropic_key=anthropic_key if anthropic_key else None
        )
        
        # Reinitialize clients with new keys
        global direct_openai_client
        direct_openai_client = init_openai_client()
        memory, reasoning_agent, code_agent = init_agents()
        
        return jsonify({"message": "API keys saved successfully"})
    except Exception as e:
        print(f"Error saving API keys: {e}")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# System prompts for different prototype types
# -----------------------------------------------------------------------------
WEB_APP_SYSTEM_PROMPT = """
You are a coding assistant designed to help non-tech founders create functional
web apps using HTML, CSS, and JavaScript. Follow these rules:
- Generate clean, simple, and beginner-friendly code that works out of the box.
- Use modern, widely-supported web technologies (e.g., vanilla JavaScript).
- Include inline CSS in the HTML file for simplicity, unless the user requests
  a separate file.
- Avoid adding comments unless requested, to keep the code concise.
- Ensure the code is responsive and visually appealing with a minimalistic
  design.
- After generating the code, append a short instruction block explaining:
  (1) how to run the code, (2) what the code does, and (3) how to modify it.
- If the prompt is vague, infer reasonable defaults.
- Do NOT generate malicious or harmful code.
"""

PYTHON_AUTOMATION_SYSTEM_PROMPT = """
You are a coding assistant designed to help non-tech founders create Python
scripts for automation tasks. Follow these rules:
- Generate clean, beginner-friendly Python code that works with minimal setup.
- Use standard libraries or widely-used packages and specify how to install
  them.
- Include basic error handling to make the script robust.
- Avoid adding comments unless requested, to keep the code concise.
- After generating the code, append a short instruction block explaining:
  (1) how to install dependencies, (2) how to run the script, and (3) what the
  script does.
- If the prompt is vague, infer reasonable defaults.
- Do NOT generate malicious or harmful code.
"""

# -----------------------------------------------------------------------------
# Agno initialisation (storage + memory + agents)
# -----------------------------------------------------------------------------

# In-memory session storage (bypassing SqliteStorage API issues)
session_store = {}  # Simple in-memory dictionary to store sessions

def create_new_session():
    """Create a new session with empty messages and code"""
    session_id = str(uuid.uuid4())
    session_store[session_id] = {
        "messages": [],
        "code": "",
        "created_at": datetime.now().isoformat()
    }
    return session_id

def get_all_sessions():
    """Get all sessions from storage"""
    return [{"id": session_id, **data} for session_id, data in session_store.items()]

def get_session(session_id):
    """Get session by ID"""
    return session_store.get(session_id)

def save_session(session_id, data):
    """Save session data"""
    session_store[session_id] = data

# Memory DB for user-specific long-term memory
memory_db = SqliteMemoryDb(table_name="user_memories", db_file="memories.db")

# Define memory and agents as global variables
memory = None
reasoning_agent = None
code_agent = None

def init_agents():
    """Initialize agents with current API keys"""
    global memory, reasoning_agent, code_agent
    
    keys = load_api_keys()
    openai_key = keys["openai_key"]
    anthropic_key = keys["anthropic_key"]
    
    if not openai_key:
        print("WARNING: OPENAI_API_KEY not set. The application will not function correctly.")
        return None, None, None
    
    # Initialize OpenAI client with better error handling
    try:
        openai_client = OpenAI(api_key=openai_key)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        openai_client = None
    
    # Disable memory system temporarily to avoid pickle errors
    print("Memory system disabled to avoid threading/pickle issues")
    memory = None
    
    # Initialize reasoning agent without memory
    try:
        reasoning_agent = Agent(
            model=OpenAIChat(id="gpt-4", api_key=openai_key, client=openai_client),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Analyze the user prompt, clarify the intent, and provide a detailed "
                "description for code generation. If the 'think' option is enabled, "
                "explain the reasoning process step-by-step."
            ],
            memory=None,
            enable_agentic_memory=False,
            enable_user_memories=False,
            enable_session_summaries=False,
        )
        print("Reasoning agent initialized successfully")
    except Exception as e:
        print(f"Error initializing reasoning agent: {e}")
        reasoning_agent = None

    # Initialize code generation agent without memory  
    try:
        code_agent = Agent(
            model=OpenAIChat(id="gpt-4", api_key=openai_key, client=openai_client),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Generate high-quality, working code based on the provided description. "
                "Include all necessary imports, error handling, and documentation."
            ],
            memory=None,
            enable_agentic_memory=False,
            enable_user_memories=False,
            enable_session_summaries=False,
        )
        print("Code agent initialized successfully")
    except Exception as e:
        print(f"Error initializing code agent: {e}")
        code_agent = None

    return memory, reasoning_agent, code_agent

# Initialize agents
memory, reasoning_agent, code_agent = init_agents()

# -----------------------------------------------------------------------------
# Helper: pick system prompt based on prototype type
# -----------------------------------------------------------------------------

def _select_system_prompt(prototype_type: str) -> str:
    p = (prototype_type or "").lower()
    if p in {"web_app", "webapp", "web"}:
        return WEB_APP_SYSTEM_PROMPT
    if p in {"automation_script", "script", "python"}:
        return PYTHON_AUTOMATION_SYSTEM_PROMPT
    return ""

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.route("/create_session", methods=["POST"])
def create_session():
    try:
        session_id = create_new_session()
        print(f"Created new session with ID: {session_id}")
        return jsonify({"id": session_id})
    except Exception as e:
        print(f"Error creating session: {e}")
        return jsonify({"error": "Failed to create session"}), 500

# Create a direct OpenAI client for operations that don't use agno
direct_openai_client = None

def init_openai_client():
    """Initialize a direct OpenAI client"""
    global direct_openai_client
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            direct_openai_client = OpenAI(api_key=openai_key)
            print("Direct OpenAI client initialized successfully")
        except Exception as e:
            print(f"Error initializing direct OpenAI client: {e}")
            direct_openai_client = None
    else:
        print("No OpenAI API key found")
        direct_openai_client = None
    return direct_openai_client

# Initialize direct OpenAI client
direct_openai_client = init_openai_client()

@app.route("/enhance_prompt", methods=["POST", "OPTIONS"])
def enhance_prompt():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response
        
    try:
        data = request.json
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Call the async method using a synchronous wrapper
        enhanced_prompt = agent.enhance_prompt_sync(prompt)
        response = jsonify({"enhanced_prompt": enhanced_prompt})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        print(f"Error enhancing prompt: {e}")
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500

@app.route("/get_sessions", methods=["GET", "OPTIONS"])
def get_sessions():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response
        
    try:
        # Combine sessions from agent storage and in-memory store
        agent_sessions = []
        try:
            agent_sessions = agent.storage.get_all()
        except Exception as e:
            print(f"Error getting sessions from agent storage: {e}")
        
        # Get sessions from in-memory store
        memory_sessions = [{"id": sid, **data} for sid, data in session_store.items()]
        
        # Combine and deduplicate sessions
        all_sessions = {}
        for session in agent_sessions:
            session_id = session.get("id")
            if session_id:
                all_sessions[session_id] = session
                
        for session in memory_sessions:
            session_id = session.get("id")
            if session_id:
                all_sessions[session_id] = session
        
        sessions_list = list(all_sessions.values())
        print(f"Returning {len(sessions_list)} sessions")
        response = jsonify(sessions_list)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        print(f"Error getting sessions: {e}")
        response = jsonify({"error": f"Failed to get sessions: {str(e)}"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500

@app.route("/get_session/<session_id>", methods=["GET"])
def get_session_route(session_id):
    try:
        # First try to get from in-memory session store
        session = session_store.get(session_id)
        if session:
            print(f"Found session {session_id} in session store")
            return jsonify(session)
        
        # If not found, try from agent storage
        session = agent.storage.get(session_id)
        if not session:
            print(f"Session {session_id} not found in either store")
            return jsonify({"error": "Session not found"}), 404
            
        print(f"Found session {session_id} in agent storage")
        return jsonify(session)
    except Exception as e:
        print(f"Error getting session {session_id}: {e}")
        return jsonify({"error": f"Failed to get session: {str(e)}"}), 500

@app.route("/get_user_memories", methods=["GET"])
def get_user_memories():
    try:
        user_id = request.args.get("user_id", "default_user")
        
        # Check if memory is initialized
        if memory:
            try:
                memories = memory.get_user_memories(user_id=user_id)
                return jsonify(memories)
            except Exception as e:
                print(f"Error getting memories from memory object: {e}")
                return jsonify(["Memory system error - memories not available"])
        else:
            return jsonify(["Memory not initialized - no persistent memories available"])
            
    except Exception as e:
        print(f"Error in get_user_memories route: {e}")
        return jsonify({"error": "Failed to get user memories"}), 500

@app.route("/generate", methods=["POST", "OPTIONS"])
def generate():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response
        
    try:
        data = request.json
        prompt = data.get('prompt')
        prototype_type = data.get('type', 'Python Script')
        session_id = data.get('session_id')
        multimodal_input = data.get('multimodal_input')
        
        if not prompt:
            response = jsonify({"error": "No prompt provided"})
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response, 400

        print(f"Processing request for prompt: {prompt[:50]}...")
        
        # Process multimodal input if provided
        media_object = None
        media_type = None
        if multimodal_input:
            media_object = process_multimodal_input(multimodal_input)
            if media_object:
                # Determine media type
                for key in ['image', 'audio', 'video']:
                    if key in multimodal_input:
                        media_type = key
                        break
                print(f"Processed multimodal input: {media_type}")
                
                # Enhance prompt with multimodal context
                prompt = enhance_prompt_with_multimodal_context(prompt, media_type)
        
        # Call the synchronous wrapper method with media_type
        result = agent.process_request_sync(prompt, prototype_type, media_type)
        
        # Make sure we have a session ID
        if not session_id:
            session_id = result.get("session_id")
            if not session_id:
                session_id = str(uuid.uuid4())
        
        # Also save to our in-memory session store for redundancy
        session_data = {
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "system", "content": "Generated code successfully!"}
            ],
            "code": result["code"],
            "reasoning": result["reasoning"],
            "enhanced_prompt": result.get("enhanced_prompt", ""),
            "analysis": result.get("analysis", ""),
            "id": session_id,
            "name": f"Session {datetime.now().strftime('%b %d, %I:%M %p')}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to in-memory session store
        session_store[session_id] = session_data
        
        print(f"Successfully processed request, returning result. Session ID: {session_id}")
        response = jsonify({
            "code": result["code"],
            "reasoning": result["reasoning"],
            "analysis": result["analysis"],
            "enhanced_prompt": result.get("enhanced_prompt", ""),
            "session_id": session_id
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        print(f"Error generating code: {str(e)}")
        import traceback
        traceback.print_exc()
        response = jsonify({"error": f"Failed to generate code: {str(e)}"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500

@app.route("/rename_session/<session_id>", methods=["POST"])
def rename_session(session_id):
    try:
        data = request.json
        new_name = data.get('name')
        if not new_name:
            return jsonify({"error": "No name provided"}), 400
        
        # First, check if session exists in in-memory store
        if session_id in session_store:
            session_store[session_id]["name"] = new_name
            print(f"Session {session_id} renamed to '{new_name}' in session store")
            
        # Also try to update in agent storage
        try:
            agent.storage.update(session_id, {"name": new_name})
            print(f"Session {session_id} renamed to '{new_name}' in agent storage")
        except Exception as e:
            print(f"Error updating session in agent storage: {e}")
            # Continue anyway since we might have updated the in-memory store
            
        return jsonify({"message": "Session renamed"})
    except Exception as e:
        print(f"Error renaming session: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/delete_session/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    try:
        agent.storage.delete(session_id)
        return jsonify({"message": "Session deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# Remote Agent Routes
# -----------------------------------------------------------------------------
@app.route("/submit_remote_task", methods=["POST"])
def submit_remote_task():
    """Submit a task to be processed by a remote agent"""
    try:
        data = request.get_json()
        task_type = data.get("task_type")
        prompt = data.get("prompt")
        prototype_type = data.get("type", "Python Script")
        user_id = data.get("user_id", "default_user")
        session_id = data.get("session_id")
        
        if not task_type or not prompt or not session_id:
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Ensure remote agent pool is running
        if not remote_agent_pool.running:
            remote_agent_pool.start()
        
        # Submit the task
        task_id = remote_agent_pool.submit_task(
            task_type=task_type,
            prompt=prompt,
            prototype_type=prototype_type,
            user_id=user_id,
            session_id=session_id
        )
        
        return jsonify({
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully"
        })
    
    except Exception as e:
        print(f"Error submitting remote task: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get_remote_task_status/<task_id>", methods=["GET"])
def get_remote_task_status(task_id):
    """Get the status of a remote task"""
    try:
        status = remote_agent_pool.get_task_status(task_id)
        return jsonify(status)
    
    except Exception as e:
        print(f"Error getting remote task status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/remote_enhance_prompt", methods=["POST"])
def remote_enhance_prompt():
    """Submit a prompt enhancement task to be processed by a remote agent"""
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        session_id = data.get("session_id")
        user_id = data.get("user_id", "default_user")
        
        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400
        
        # Create a session if none provided
        if not session_id:
            session_id = create_new_session()
        
        # Ensure remote agent pool is running
        if not remote_agent_pool.running:
            remote_agent_pool.start()
        
        # Submit the task
        task_id = remote_agent_pool.submit_task(
            task_type="enhance_prompt",
            prompt=prompt,
            prototype_type="",  # Not applicable for enhance_prompt
            user_id=user_id,
            session_id=session_id
        )
        
        return jsonify({
            "task_id": task_id,
            "status": "submitted",
            "message": "Prompt enhancement task submitted"
        })
    
    except Exception as e:
        print(f"Error submitting remote enhance prompt task: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/remote_generate", methods=["POST"])
def remote_generate():
    """Submit a code generation task to be processed by a remote agent"""
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        prototype_type = data.get("type", "Python Script")
        user_id = data.get("user_id", "default_user")
        multimodal_input = data.get("multimodal_input")
        
        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400
        
        # Process multimodal input if provided
        media_type = None
        if multimodal_input:
            media_object = process_multimodal_input(multimodal_input)
            if media_object:
                # Determine media type
                for key in ['image', 'audio', 'video']:
                    if key in multimodal_input:
                        media_type = key
                        break
                print(f"Processed multimodal input for remote generation: {media_type}")
                
                # Enhance prompt with multimodal context
                prompt = enhance_prompt_with_multimodal_context(prompt, media_type)
        
        # Create a session
        session_id = create_new_session()
        
        # Ensure remote agent pool is running
        if not remote_agent_pool.running:
            remote_agent_pool.start()
        
        # Submit the task
        task_id = remote_agent_pool.submit_task(
            task_type="generate_code",
            prompt=prompt,
            prototype_type=prototype_type,
            user_id=user_id,
            session_id=session_id
        )
        
        return jsonify({
            "task_id": task_id,
            "session_id": session_id,
            "status": "submitted",
            "message": "Code generation task submitted"
        })
    
    except Exception as e:
        print(f"Error submitting remote generate task: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/push_to_zed", methods=["POST"])
def push_to_zed():
    """Execute/run the generated code"""
    try:
        data = request.get_json()
        code = data.get("code")
        file_type = data.get("fileType", "")
        file_name = data.get("fileName", "generated_code")
        
        if not code:
            return jsonify({"error": "No code provided"}), 400
        
        print(f"Executing code of type: {file_type}")
        
        # Handle different file types
        if file_type == "html" or code.strip().startswith("<!DOCTYPE") or "<html" in code:
            # For HTML files, save and open in browser
            import tempfile
            import webbrowser
            import os
            
            # Create a temporary HTML file with UTF-8 encoding
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Open in default browser
            webbrowser.open(f'file://{os.path.abspath(temp_file_path)}')
            
            return jsonify({
                "message": "HTML code opened in browser successfully",
                "file_path": temp_file_path
            })
            
        elif code.strip().startswith("import ") or "def " in code or "print(" in code:
            # For Python files, save and optionally run
            import tempfile
            import subprocess
            import os
            
            # Create a temporary Python file with UTF-8 encoding
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Try to run the Python code
                result = subprocess.run(
                    ['python', temp_file_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=30  # 30 second timeout
                )
                
                if result.returncode == 0:
                    return jsonify({
                        "message": "Python code executed successfully",
                        "output": result.stdout,
                        "file_path": temp_file_path
                    })
                else:
                    return jsonify({
                        "message": "Python code saved but execution had errors",
                        "error": result.stderr,
                        "file_path": temp_file_path
                    })
                    
            except subprocess.TimeoutExpired:
                return jsonify({
                    "message": "Python code saved but execution timed out",
                    "file_path": temp_file_path
                })
            except Exception as e:
                return jsonify({
                    "message": f"Python code saved but couldn't execute: {str(e)}",
                    "file_path": temp_file_path
                })
        
        else:
            # For other code types, just save to a file
            import tempfile
            
            # Determine file extension
            extension = ".txt"
            if "function" in code and "{" in code:
                extension = ".js"
            elif "def " in code:
                extension = ".py"
            elif "<" in code and ">" in code:
                extension = ".html"
            
            # Create temporary file with UTF-8 encoding
            with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            return jsonify({
                "message": f"Code saved to file successfully",
                "file_path": temp_file_path
            })
    
    except Exception as e:
        print(f"Error executing code: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "message": "VibeProto server is running",
        "version": "1.0.0",
        "agents_status": {
            "reasoning_agent": reasoning_agent is not None,
            "code_agent": code_agent is not None,
            "memory": memory is not None,
            "direct_openai_client": direct_openai_client is not None
        }
    })

@app.route("/favicon.ico", methods=["GET"])
def favicon():
    """Return empty favicon to avoid 404 errors"""
    return '', 204

@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response, 200

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors"""
    return jsonify({
        "error": "File too large. Maximum upload size is 100MB.",
        "details": "Please use a smaller video file or compress it before uploading."
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({
        "error": "Internal server error",
        "details": str(error)
    }), 500

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Starting VibeProto server on port 5000...")
    # Start the remote agent pool
    remote_agent_pool.start()
    
    # Add a hook to stop the remote agent pool when the app stops
    import atexit
    atexit.register(remote_agent_pool.stop)
    
    app.run(host='0.0.0.0', port=5000, debug=True) 