from flask import Flask, request, jsonify
from flask_cors import CORS
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.tools.reasoning import ReasoningTools
import os
import uuid
from datetime import datetime
import dotenv
from pathlib import Path
from openai import OpenAI
from agno_agent import agent
from remote_agent import remote_agent_pool

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

app = Flask(__name__)
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
    
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=openai_key)
    
    # Initialize memory with OpenAI
    try:
        memory = Memory(
            model=OpenAIChat(id="gpt-4", api_key=openai_key, client=openai_client),
            db=memory_db
        )
    except Exception as e:
        print(f"Error initializing memory: {e}")
        memory = None
    
    # Initialize reasoning agent
    try:
        if anthropic_key:
            reasoning_agent = Agent(
                model=Claude(id="claude-3-sonnet", api_key=anthropic_key),
                tools=[ReasoningTools(add_instructions=True)],
                instructions=[
                    "Analyze the user prompt, clarify the intent, and provide a detailed "
                    "description for code generation. If the 'think' option is enabled, "
                    "explain the reasoning process step-by-step."
                ],
                memory=memory,
                enable_agentic_memory=True,
                enable_user_memories=True,
                enable_session_summaries=True,
            )
        else:
            # Fallback to OpenAI if Anthropic key is not available
            reasoning_agent = Agent(
                model=OpenAIChat(id="gpt-4", api_key=openai_key, client=openai_client),
                tools=[ReasoningTools(add_instructions=True)],
                instructions=[
                    "Analyze the user prompt, clarify the intent, and provide a detailed "
                    "description for code generation. If the 'think' option is enabled, "
                    "explain the reasoning process step-by-step."
                ],
                memory=memory,
                enable_agentic_memory=True,
                enable_user_memories=True,
                enable_session_summaries=True,
            )
    except Exception as e:
        print(f"Error initializing reasoning agent: {e}")
        reasoning_agent = None

    # Initialize code generation agent
    try:
        code_agent = Agent(
            model=OpenAIChat(id="gpt-4", api_key=openai_key, client=openai_client),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Generate high-quality, working code based on the provided description. "
                "Include all necessary imports, error handling, and documentation."
            ],
            memory=memory,
            enable_agentic_memory=True,
            enable_user_memories=True,
            enable_session_summaries=True,
        )
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
        direct_openai_client = OpenAI(api_key=openai_key)
    return direct_openai_client

# Initialize direct OpenAI client
direct_openai_client = init_openai_client()

@app.route("/enhance_prompt", methods=["POST"])
def enhance_prompt():
    try:
        data = request.json
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Call the async method using a synchronous wrapper
        enhanced_prompt = agent.enhance_prompt_sync(prompt)
        return jsonify({"enhanced_prompt": enhanced_prompt})
    except Exception as e:
        print(f"Error enhancing prompt: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get_sessions", methods=["GET"])
def get_sessions():
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
        return jsonify(sessions_list)
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return jsonify({"error": f"Failed to get sessions: {str(e)}"}), 500

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
            memories = memory.get_user_memories(user_id=user_id)
        else:
            memories = ["Memory not initialized. Check API keys."]
            
        return jsonify(memories)
    except Exception as e:
        print(f"Error getting memories for user {user_id}: {e}")
        return jsonify({"error": "Failed to get user memories"}), 500

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt')
        prototype_type = data.get('type', 'Python Script')
        session_id = data.get('session_id')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        print(f"Processing request for prompt: {prompt[:50]}...")
        
        # Call the synchronous wrapper method
        result = agent.process_request_sync(prompt, prototype_type)
        
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
        return jsonify({
            "code": result["code"],
            "reasoning": result["reasoning"],
            "analysis": result["analysis"],
            "enhanced_prompt": result.get("enhanced_prompt", ""),
            "session_id": session_id
        })
    except Exception as e:
        print(f"Error generating code: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate code: {str(e)}"}), 500

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
        
        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400
        
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

# Add a specific route to handle OPTIONS requests
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 204

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