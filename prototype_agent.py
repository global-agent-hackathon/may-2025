from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from openai import OpenAI
import os
import json
import uuid
from functools import wraps
from pathlib import Path
import re # Import regex module

app = Flask(__name__)
# Use a simpler, more permissive CORS configuration
CORS(app, origins=["*"], allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS"])

# Add a decorator to ensure CORS headers
def add_cors_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        resp.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return resp
    return decorated_function

# Setup OpenAI client
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key or api_key == "your-key-here":
    print("WARNING: No valid OpenAI API key found. Using mock responses.")
    USE_MOCK = True
else:
    USE_MOCK = False
    
client = OpenAI(api_key=api_key)

# Initialize sessions directory
SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

# Session management functions
def get_session_path(session_id):
    return SESSIONS_DIR / f"{session_id}.json"

def save_session(session_id, data):
    with open(get_session_path(session_id), 'w') as f:
        json.dump(data, f)

def load_session(session_id):
    path = get_session_path(session_id)
    if not path.exists():
        return None
    with open(path, 'r') as f:
        return json.load(f)

def get_all_sessions():
    result = []
    for file in SESSIONS_DIR.glob("*.json"):
        session_id = file.stem
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                data["id"] = session_id
                result.append(data)
        except Exception:
            # Skip corrupted files
            pass
    return result

def generate_session_name(prompt):
    """Generates a short descriptive name from the user prompt."""
    try:
        # Simple approach: Take first few meaningful words
        prompt_lower = prompt.lower()
        # Remove punctuation (optional, basic example)
        prompt_lower = re.sub(r'[^\w\s]', '', prompt_lower)
        
        words = prompt_lower.split()
        
        # Basic stop words list - extend as needed
        stop_words = {"a", "an", "the", "i", "want", "to", "build", "create", "make", "simple", "app", "script", "for", "of", "with", "about"}
        
        meaningful_words = [w for w in words if w not in stop_words]
        
        # Take first 2 meaningful words, capitalize
        name_words = [w.capitalize() for w in meaningful_words[:2]]
        
        if not name_words:
            return None # Fallback handled later
            
        return " ".join(name_words)
    except Exception:
        # In case of error, fallback to None
        return None

# Updated parser to also extract instructions
def parse_code_and_instructions(markdown_string):
    code_blocks = {
        "html": "",
        "css": "",
        "javascript": ""
    }
    instructions = ""
    code_part = markdown_string
    instruction_heading = None
    
    # Try to split by instruction headings
    headings = ["### How to Run", "### Instructions for Use"]
    for heading in headings:
        if heading in markdown_string:
            parts = markdown_string.split(heading, 1)
            code_part = parts[0]
            instructions = heading + parts[1] # Keep the heading
            instruction_heading = heading
            break
            
    # Regex to find ```language ... ``` blocks within the code part
    pattern = r"```(\w+)\s*\n(.*?)\n```"
    matches = re.findall(pattern, code_part, re.DOTALL)
    
    found_blocks = False
    for lang, code in matches:
        found_blocks = True
        lang_lower = lang.lower()
        if lang_lower == "html":
            code_blocks["html"] = code.strip()
        elif lang_lower == "css":
            code_blocks["css"] = code.strip()
        elif lang_lower == "javascript" or lang_lower == "js":
            code_blocks["javascript"] = code.strip()
            
    # Handle cases: Only instructions found, or single block code + instructions
    if not found_blocks and not any(code_blocks.values()):
        # If we split by heading, the remaining code_part might be the actual code
        # Or if no heading, the whole string might be just code or just instructions
        potential_code = code_part.strip()
        if instruction_heading: # Assume code_part is the script if heading was found
             code_blocks = potential_code # Store as single string
        elif "<html" in potential_code.lower() or "<div" in potential_code.lower(): # Guess HTML
             code_blocks["html"] = potential_code
        elif potential_code: # Assume it's script code if no blocks/HTML detected
             code_blocks = potential_code # Store as single string
        # If potential_code is empty but instructions exist, it's fine

    # If parsing failed for webapp but we have instructions, return raw code part
    if isinstance(code_blocks, dict) and not any(code_blocks.values()) and code_part:
         if "<html" in code_part.lower(): # Re-check for HTML
             code_blocks["html"] = code_part.strip()
         else: # Treat as single block if parsing failed
             code_blocks = code_part.strip() 

    return code_blocks, instructions.strip()

# Modify get_mock_code to include instructions
def get_mock_code(prompt, prototype_type):
    code = ""
    instructions = ""
    if prototype_type == "web_app":
        code = {"html": "<!-- Mock HTML -->", "css": "/* Mock CSS */", "javascript": "// Mock JS"}
        instructions = "### Instructions for Use\n1. Save HTML, CSS, JS in respective files.\n2. Open index.html in a browser."
    else: # automation_script
        code = "# Mock Python script\nprint('Hello Mock!')"
        instructions = "### How to Run\n1. Save as mock_script.py.\n2. Run `python mock_script.py`."
        
    # Add todo specifics if relevant (overrides generic mocks)
    if "todo" in prompt.lower() or "task" in prompt.lower():
        if prototype_type == "web_app":
             html_code = """<!DOCTYPE html>
<html>
<head>
    <title>Simple Todo App</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; }
        .todo-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; }
        .todo-item button { background: #ff4d4d; color: white; border: none; padding: 5px 10px; cursor: pointer; }
        input, button { padding: 8px; }
        #add-btn { background: #4CAF50; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Todo List</h1>
    <div>
        <input type="text" id="task-input" placeholder="Add a new task...">
        <button id="add-btn">Add</button>
    </div>
    <div id="todo-list">
        <!-- Tasks will be added here -->
    </div>

    <script>
        // Task management
        let tasks = [];
        
        function addTask() {
            const taskInput = document.getElementById('task-input');
            const taskText = taskInput.value.trim();
            
            if (taskText) {
                tasks.push(taskText);
                taskInput.value = '';
                renderTasks();
            }
        }
        
        function deleteTask(index) {
            tasks.splice(index, 1);
            renderTasks();
        }
        
        function renderTasks() {
            const todoList = document.getElementById('todo-list');
            todoList.innerHTML = '';
            
            tasks.forEach((task, index) => {
                const taskElement = document.createElement('div');
                taskElement.className = 'todo-item';
                
                const taskText = document.createElement('span');
                taskText.textContent = task;
                
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.onclick = () => deleteTask(index);
                
                taskElement.appendChild(taskText);
                taskElement.appendChild(deleteButton);
                todoList.appendChild(taskElement);
            });
        }
        
        // Event listeners
        document.getElementById('add-btn').addEventListener('click', addTask);
        document.getElementById('task-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addTask();
            }
        });
        
        // Initialize
        renderTasks();
    </script>
</body>
</html>"""
             css_code = """body { font-family: Arial, sans-serif; ... }"""
             js_code = """let tasks = []; ... renderTasks();"""
             code = {"html": html_code, "css": css_code, "javascript": js_code}
             instructions = "### Instructions for Use\n1. Save HTML as index.html, CSS as style.css, JS as script.js.\n2. Open index.html."
        else: 
             code = """# Simple Todo List CLI App ... main()""" # Shortened
             instructions = "### How to Run\n1. Save as todo.py.\n2. Run `python todo.py`."

    return code, instructions

# API Routes
@app.route('/create_session', methods=['POST', 'OPTIONS'])
@add_cors_headers
def create_session():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        
        # Initialize an empty session
        session_data = {
            "id": session_id,
            "name": f"Session {session_id[:8]}",
            "messages": [],
            "code": ""
        }
        
        # Save the session data
        save_session(session_id, session_data)
        
        return jsonify({"id": session_id})
    except Exception as e:
        app.logger.error(f"Error in create_session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_sessions', methods=['GET', 'OPTIONS'])
@add_cors_headers
def get_sessions():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        sessions = get_all_sessions()
        return jsonify(sessions)
    except Exception as e:
        app.logger.error(f"Error in get_sessions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_session/<session_id>', methods=['GET', 'OPTIONS'])
@add_cors_headers
def get_session(session_id):
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        session = load_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
        return jsonify(session)
    except Exception as e:
        app.logger.error(f"Error in get_session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST', 'OPTIONS'])
@add_cors_headers
def generate():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        prototype_type = data.get('type')
        session_id = data.get('session_id')

        if not prompt or not prototype_type or not session_id:
            return jsonify({"error": "Missing prompt, type, or session_id"}), 400

        # Load current session
        session = load_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
            
        # Add user message to session
        session["messages"].append({"role": "user", "content": prompt})
        
        # --- Generate Session Name if it's the first user message ---
        # Check if this is the first prompt (user message is the only one added so far)
        is_first_prompt = len(session["messages"]) == 1 
        # Also check if the name is still the default format
        is_default_name = session["name"].startswith("Session ") and len(session["id"]) >= 8 and session["name"].endswith(session["id"][:8])

        if is_first_prompt and is_default_name:
            new_name = generate_session_name(prompt)
            if new_name:
                session["name"] = new_name
                # No need to save immediately, will be saved later anyway

        # --- Generate code (using mock or real API) ---
        explanation = ""
        response_data = {}

        if USE_MOCK:
            mock_code, mock_instructions = get_mock_code(prompt, prototype_type)
            explanation = f"Generated mock {'web app' if prototype_type == 'web_app' else 'script'} code!"
            response_data = {"code": mock_code, "explanation": explanation, "instructions": mock_instructions}
            
            session["messages"].append({"role": "system", "content": explanation})
            session["code"] = response_data["code"] 
            session["instructions"] = response_data["instructions"] # Store instructions
            save_session(session_id, session)
            return jsonify(response_data)
        else:
            # --- Real API call --- 
            try:
                generated_code = ""
                generated_instructions = ""

                if prototype_type == "web_app":
                    # Specific prompt for web app with instructions
                    enhanced_prompt = f"Generate the HTML, CSS, and JavaScript for a simple web application based on this description: {prompt}. Provide the code for each language in separate markdown code blocks, clearly labeled (e.g., ```html ... ```, ```css ... ```, ```javascript ... ```).\\n\\nAfter all code blocks, add a section starting exactly with `### Instructions for Use:`.\\nIn this section, provide **detailed, step-by-step instructions suitable for a non-technical user** on how to run this web application. Explain:\\n1.  **Saving:** How to copy and paste the HTML code into a file named `index.html`, the CSS code into `style.css`, and the JavaScript code into `script.js` using a basic text editor (like Notepad or TextEdit) or an IDE.\\n2.  **Running:** How to locate the `index.html` file on their computer and double-click it to open it in their default web browser.\\n3.  **Prerequisites:** Mention that no special software is needed other than a text editor and a web browser.\\n\\nRespond ONLY with the code blocks and the detailed instructions section."
                    
                    api_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": enhanced_prompt}]
                    )
                    raw_response = api_response.choices[0].message.content
                    parsed_code, generated_instructions = parse_code_and_instructions(raw_response)
                    generated_code = parsed_code # This will be the dict or raw string
                    explanation = "Web app code generated!"
                    
                else: # automation_script or other types
                    enhanced_prompt = f"Generate a high-quality Python script for {prototype_type} based on the following description: {prompt}. Respond ONLY with the Python code inside a single markdown code block (```python ... ```).\\n\\nAfter the code block, add a section starting exactly with `### How to Run:`.\\nIn this section, provide **detailed, step-by-step instructions suitable for a non-technical user** on how to run this script. Assume the user might not be familiar with terminals. Explain:\\n1.  **Prerequisites:** Mention that Python needs to be installed on their computer (provide a link like https://www.python.org/downloads/ if possible).\\n2.  **Saving:** How to copy and paste the Python code into a file named `script.py` (or a more descriptive name if appropriate, like `automation_script.py`) using a basic text editor (like Notepad or TextEdit) or an IDE.\\n3.  **Running:**\\n    a.  How to open the command line interface (Terminal on macOS/Linux, Command Prompt or PowerShell on Windows).\\n    b.  How to navigate to the directory where they saved the file using the `cd` command (e.g., `cd Downloads` or `cd C:\\\\Users\\\\YourUsername\\\\Documents`).\\n    c.  How to run the script using the command `python script.py` (using the actual filename).\\n\\nRespond ONLY with the Python code block and the detailed instructions section."
                    api_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": enhanced_prompt}]
                    )
                    raw_response = api_response.choices[0].message.content
                    # For scripts, parse_code_and_instructions should return string code and instructions
                    generated_code, generated_instructions = parse_code_and_instructions(raw_response) 
                    explanation = "Script code generated!"

                response_data = {"code": generated_code, "explanation": explanation, "instructions": generated_instructions}
                
                # Add system message and code/instructions to session
                session["messages"].append({"role": "system", "content": explanation})
                session["code"] = response_data["code"] 
                session["instructions"] = response_data["instructions"]
                save_session(session_id, session)
                return jsonify(response_data)

            except Exception as e:
                app.logger.error(f"OpenAI API error: {str(e)}")
                app.logger.info("Falling back to mock response due to API error")
                mock_code, mock_instructions = get_mock_code(prompt, prototype_type)
                explanation = f"Generated using fallback (API error: {str(e)}). This is mock code."
                response_data = {"code": mock_code, "explanation": explanation, "instructions": mock_instructions}

                session["messages"].append({"role": "system", "content": explanation})
                session["code"] = response_data["code"]
                session["instructions"] = response_data["instructions"]
                save_session(session_id, session)
                return jsonify(response_data)
            
    except Exception as e:
        app.logger.error(f"Error in generate: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/enhance_prompt', methods=['POST', 'OPTIONS'])
@add_cors_headers
def enhance_prompt_route():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
        
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400
            
        # Check if we should use mock response (if API key is missing)
        if USE_MOCK:
            enhanced = f"Enhanced: {prompt} (MOCK RESPONSE - Add details for better results)"
            return jsonify({"enhanced_prompt": enhanced})
            
        # --- Real OpenAI API call for enhancement ---
        try:
            enhancement_instruction = f"Rewrite the following user request to make it a clear, detailed, and effective prompt for an AI code generation model. Focus on clarity, specificity, and including necessary details. Respond only with the rewritten prompt, nothing else:\n\nOriginal prompt: '{prompt}'"
            
            response = client.chat.completions.create(
                model="gpt-4o", # Or a cheaper/faster model if preferred for enhancement
                messages=[{"role": "user", "content": enhancement_instruction}],
                temperature=0.5 # Lower temperature for more focused rewriting
            )
            enhanced_prompt = response.choices[0].message.content.strip()
            
            # Basic validation/cleanup (sometimes models add quotes)
            if enhanced_prompt.startswith('"') and enhanced_prompt.endswith('"'):
                enhanced_prompt = enhanced_prompt[1:-1]
            
            return jsonify({"enhanced_prompt": enhanced_prompt})
            
        except Exception as api_error:
            app.logger.error(f"OpenAI API error during enhancement: {str(api_error)}")
            # Fallback: return original prompt or a simple modification
            enhanced = f"Enhanced: {prompt} (API ERROR - Could not enhance fully)"
            return jsonify({"enhanced_prompt": enhanced})
            
    except Exception as e:
        app.logger.error(f"Error in enhance_prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rename_session/<session_id>', methods=['POST', 'OPTIONS'])
@add_cors_headers
def rename_session(session_id):
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
        
    try:
        data = request.get_json()
        new_name = data.get('new_name')
        
        if not new_name:
            return jsonify({"error": "Missing new_name"}), 400
            
        # Load the session
        session = load_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
            
        # Update the name
        session['name'] = new_name
        
        # Save the updated session
        save_session(session_id, session)
        
        return jsonify({"message": "Session renamed successfully", "session": session})
        
    except Exception as e:
        app.logger.error(f"Error in rename_session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/delete_session/<session_id>', methods=['POST', 'OPTIONS']) # Using POST for simplicity
@add_cors_headers
def delete_session(session_id):
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
        
    try:
        session_path = get_session_path(session_id)
        
        if not session_path.exists():
            return jsonify({"error": "Session not found"}), 404
            
        # Delete the file
        session_path.unlink()
        
        return jsonify({"message": "Session deleted successfully"})
        
    except Exception as e:
        app.logger.error(f"Error in delete_session: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("VibeProto server starting...")
    print(f"OPENAI_API_KEY is {'set' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
    app.run(host='0.0.0.0', port=5000, debug=True) 