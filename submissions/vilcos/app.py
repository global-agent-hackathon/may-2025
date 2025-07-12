import os
from pathlib import Path
import chainlit as cl
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools
import logging # Import logging
import json
import subprocess

# Optional enhanced features
mem0_client = None
firecrawl_app = None

# Check for enhanced features
if os.getenv("ENABLE_MEM0", "false").lower() == "true":
    try:
        from mem0 import MemoryClient
        mem0_api_key = os.getenv("MEM0_API_KEY")
        if mem0_api_key:
            mem0_client = MemoryClient(api_key=mem0_api_key)
            logging.info("✅ Mem0 memory enabled")
            print(f"🔍 STARTUP DEBUG: mem0_client created: {mem0_client is not None}")
        else:
            logging.warning("⚠️  MEM0_API_KEY not found in environment")
    except ImportError:
        logging.warning("⚠️  Mem0 not installed. Run: pip install mem0ai")
    except Exception as e:
        logging.warning(f"⚠️  Mem0 initialization failed: {e}")

print(f"🔍 GLOBAL DEBUG: Final mem0_client value: {mem0_client is not None if 'mem0_client' in globals() else 'NOT DEFINED'}")

firecrawl_enabled = os.getenv("ENABLE_FIRECRAWL", "false").lower() == "true"
if firecrawl_enabled:
    try:
        # Just check if firecrawl is installed, Agno tools will handle the client
        import firecrawl
        logging.info("✅ Firecrawl web crawling enabled")
    except ImportError:
        logging.warning("⚠️  Firecrawl not installed. Run: pip install firecrawl-py")
        firecrawl_enabled = False

# --- Modern Agno Knowledge Base Imports ---
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.chroma import ChromaDb
from agno.embedder.openai import OpenAIEmbedder
# --- End Modern Imports ---

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Define base directory for templates
BASE_DIR = Path(os.getcwd())
TEMPLATES_DIR = BASE_DIR / "templates"
# Create templates directory if it doesn't exist
TEMPLATES_DIR.mkdir(exist_ok=True)

# --- Add publish functionality ---
async def publish_site():
    """Run the publish script and return the result"""
    logging.info("Attempting to publish site...")
    
    try:
        # Get the publish script path
        publish_script = BASE_DIR / "publish.sh"
        
        # Check if the script exists
        if not publish_script.exists():
            return "❌ Error: publish.sh script not found. Please make sure it exists in the root directory."
        
        # Make the script executable
        os.chmod(publish_script, 0o755)
        
        # Set the publish directory
        publish_dir = BASE_DIR / "public"
        
        # Run the publish script
        result = subprocess.run(
            [str(publish_script), str(publish_dir)],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Check the result
        if result.returncode == 0:
            success_message = "✅ Site successfully published to public directory!\n\n"
            success_message += "**Quick Deploy (Recommended):**\n"
            success_message += "1. Navigate to the public directory: `cd public`\n"
            success_message += "2. Run: `docker compose up -d`\n"
            success_message += "3. Your site will be available at: http://localhost\n\n"
            success_message += "**Advanced Options:**\n"
            success_message += "- Cloud deployment (Fly.io): See DEPLOY.md for instructions\n"
            success_message += "- Custom server: Use any web server to serve the static files"
            return success_message
        else:
            # If the script failed, return the error
            return f"❌ Publishing failed with exit code {result.returncode}:\n{result.stderr}"
    
    except Exception as e:
        logging.error(f"Error publishing site: {e}")
        return f"❌ An error occurred during publishing: {str(e)}"
# --- End publish functionality ---

# --- Modern Agno Knowledge Base Setup ---
# Initialize the vector database with Agno's native ChromaDB implementation
# Using in-memory version without persistence to avoid file-related issues
vector_db = ChromaDb(
    collection="templates",
    embedder=OpenAIEmbedder()
)

# Create a knowledge base for templates
def create_template_knowledge():
    """
    Creates a knowledge base from template files using Agno's native DocumentKnowledgeBase.
    Returns a knowledge base instance that can be directly used with an Agent.
    """
    logging.info(f"Creating knowledge base from templates directory: {TEMPLATES_DIR}")
    
    # Check if the templates directory exists
    if not TEMPLATES_DIR.exists() or not TEMPLATES_DIR.is_dir():
        logging.warning(f"Templates directory {TEMPLATES_DIR} does not exist or is not a directory")
        return DocumentKnowledgeBase(documents=[], vector_db=vector_db)
    
    # Get HTML files only to simplify the approach 
    html_files = list(TEMPLATES_DIR.glob("**/*.html"))
    
    # Load the files directly
    documents = []
    for file_path in html_files:
        try:
            # Read the file content
            content = file_path.read_text(encoding='utf-8')
            
            # Create a simple document dictionary with page_content and metadata
            document = {
                "content": content,
                "metadata": {"source": str(file_path)}
            }
            
            documents.append(document)
            logging.info(f"Loaded file: {file_path}")
        except Exception as e:
            logging.error(f"Error loading file {file_path}: {e}")
    
    if not documents:
        logging.warning("No documents found for knowledge base")
        return DocumentKnowledgeBase(documents=[], vector_db=vector_db)
    
    logging.info(f"Successfully loaded {len(documents)} documents")
    
    # Create the knowledge base with the loaded documents
    knowledge_base = DocumentKnowledgeBase(
        documents=documents,  # List of document dictionaries
        vector_db=vector_db
    )
    
    # Load the knowledge base (process and index the documents)
    try:
        knowledge_base.load(recreate=False)
        logging.info("Knowledge base loaded successfully")
    except Exception as e:
        logging.error(f"Error loading knowledge base: {e}")
    
    return knowledge_base

# Create the template knowledge base
template_knowledge = create_template_knowledge()
# --- End Modern Knowledge Base Setup ---

# Create src directory for CSS and JS files if it doesn't exist
SRC_DIR = TEMPLATES_DIR / "src"
SRC_DIR.mkdir(exist_ok=True)

def scan_templates_directory():
    """
    Scan the templates directory and return a formatted string with its contents.
    Only includes relevant files like HTML, CSS, JS.
    """
    template_contents = []
    
    # Define file types to include
    relevant_extensions = ['.html', '.css', '.js', '.json', '.svg', '.png', '.jpg', '.jpeg', '.gif']
    
    # List files in templates root directory
    template_contents.append("Files in templates directory:")
    root_files = [f.name for f in TEMPLATES_DIR.glob("*") if f.is_file() and 
                 (f.suffix.lower() in relevant_extensions and not f.name.startswith('.'))]
    for f in sorted(root_files):
        template_contents.append(f"  - {f}")
    
    # List files in src directory if it exists
    if SRC_DIR.exists():
        template_contents.append("\nFiles in templates/src directory:")
        src_files = [f.name for f in SRC_DIR.glob("*") if f.is_file() and 
                    (f.suffix.lower() in relevant_extensions and not f.name.startswith('.'))]
        for f in sorted(src_files):
            template_contents.append(f"  - {f}")
    
    return "\n".join(template_contents)

def get_html_pages():
    """
    Get a list of all HTML pages in the templates directory.
    """
    return [f for f in TEMPLATES_DIR.glob("*.html")]

def get_vilcos_logo_svg():
    """
    Get the Vilcos logo as inline SVG code.
    This makes it easy to include the logo in templates.
    """
    logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <!-- Elegant "V" shape with gradient -->
  <defs>
    <linearGradient id="v-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#10b981" />
    </linearGradient>
  </defs>
  
  <!-- Simple V shape -->
  <path d="M20,20 L50,80 L80,20" 
        fill="none" 
        stroke="url(#v-gradient)" 
        stroke-width="8" 
        stroke-linecap="round" 
        stroke-linejoin="round" />
</svg>"""
    return logo_svg

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """Handle authentication."""
    # Simple auth using environment variables
    expected_username = os.getenv("CHAINLIT_USERNAME", "admin")
    expected_password = os.getenv("CHAINLIT_PASSWORD", "password")
    
    if username == expected_username and password == expected_password:
        return cl.User(identifier=username, metadata={"role": "admin"})
    return None

# --- Specific Action Callbacks --- 

@cl.action_callback("view_page")
async def handle_view_page(action):
    """Handles the 'view_page' action."""
    payload = action.payload
    page_name = payload.get("file")

    if not page_name:
        logging.error("Missing file name for view action.")
        await cl.Message(content="Error: Missing file name for view action.").send()
        return
        
    full_path = TEMPLATES_DIR / page_name
    
    if full_path.exists() and full_path.is_file():
        content = full_path.read_text()
        await cl.Message(content=f"Content of **{page_name}**:\n```html\n{content}\n```").send()
    else:
        logging.warning(f"File not found for view action: {page_name}")
        await cl.Message(content=f"File {page_name} not found").send()

@cl.action_callback("edit_page")
async def handle_edit_page(action):
    """Handles the 'edit_page' action."""
    payload = action.payload
    page_name = payload.get("file")

    if not page_name:
        logging.error("Missing file name for edit action.")
        await cl.Message(content="Error: Missing file name for edit action.").send()
        return
        
    await cl.Message(content=f"What changes would you like to make to {page_name}?").send()

@cl.action_callback("create_new_page")
async def handle_create_new_page(action):
    """Handles the 'create_new_page' action."""
    # Set a flag to indicate we're in page creation mode
    cl.user_session.set("creating_new_page", True)
    await cl.Message(content="Please provide a name for the new page and describe its content.").send()

@cl.action_callback("publish_site")
async def handle_publish_site(action):
    """Handles the 'publish_site' action."""
    # Send a message indicating that publishing is in progress
    await cl.Message(content="🔄 Publishing site... This may take a moment.").send()
    
    # Run the publish operation
    result = await publish_site()
    
    # Send the result
    await cl.Message(content=result).send()

@cl.action_callback("direct_preview")
async def handle_direct_preview(action):
    """Simple handler for the preview action."""
    preview_url = "http://localhost:3000"
    await cl.Message(
        content=f"🌐 [Open website preview]({preview_url})"
    ).send()

# --- End Specific Action Callbacks ---

def create_action_buttons():
    """Create a list of action buttons for the UI"""
    # Get HTML pages for buttons
    html_pages = get_html_pages()
    
    # Create action buttons for each page
    actions = []
    for page in html_pages:
        page_name = page.name
        # Check if this is the README file
        if page_name.lower() == 'readme.md' or page_name.lower() == 'readme.html':
            # Add README view button
            actions.append(
                cl.Action(
                    name="view_page",
                    value=page_name,
                    description=f"View the content of {page_name}",
                    label=f"📚 View {page_name}",
                    payload={"file": page_name}
                )
            )
            
            # Add preview button right after README
            actions.append(
                cl.Action(
                    name="direct_preview",
                    value="direct_preview",
                    description="Open website preview",
                    label="🔍 Live Preview",
                    payload={}
                )
            )
            
            # Then add the edit button for README
            actions.append(
                cl.Action(
                    name="edit_page",
                    value=page_name,
                    description=f"Edit {page_name}",
                    label=f"✏️ Edit {page_name}",
                    payload={"file": page_name}
                )
            )
        else:
            # For non-README files, add view and edit buttons as usual
            actions.append(
                cl.Action(
                    name="view_page",
                    value=page_name,
                    description=f"View the content of {page_name}",
                    label=f"👁️ View {page_name}",
                    payload={"file": page_name}
                )
            )
            actions.append(
                cl.Action(
                    name="edit_page",
                    value=page_name,
                    description=f"Edit {page_name}",
                    label=f"✏️ Edit {page_name}",
                    payload={"file": page_name}
                )
            )
    
    # Add button to create a new page
    actions.append(
        cl.Action(
            name="create_new_page",
            value="new_page",
            description="Create a new HTML page",
            label="🆕 Create New Page",
            payload={"action": "create_new"}
        )
    )
    
    # Add publish button at the end
    actions.append(
        cl.Action(
            name="publish_site",
            value="publish",
            description="Publish the website as static files",
            label="📦 Publish Website",
            payload={"action": "publish"}
        )
    )
    
    # If there's no README, add the preview button here
    if not any(page.name.lower() in ['readme.md', 'readme.html'] for page in html_pages):
        # Insert preview button at the beginning of actions
        actions.insert(0, 
            cl.Action(
                name="direct_preview",
                value="direct_preview",
                description="Open website preview",
                label="🔍 Live Preview",
                payload={}
            )
        )
    
    return actions

@cl.on_chat_start
async def start():
    """Initialize the chat session and setup the agent."""
    # Get current directory contents for context
    template_contents = scan_templates_directory()
    
    # Initialize session flags
    cl.user_session.set("creating_new_page", False)
    
    # Set up file tools with restricted access to only the templates directory
    file_tools = FileTools(
        base_dir=TEMPLATES_DIR,
        save_files=True,
        read_files=True,
        list_files=True
    )
    
    # Prepare tools list
    agent_tools = [file_tools]
    
    # Add Firecrawl tool if enabled
    if firecrawl_enabled:
        from agno.tools.firecrawl import FirecrawlTools
        firecrawl_tools = FirecrawlTools(
            api_key=os.getenv("FIRECRAWL_API_KEY"),
            scrape=True,
            crawl=False  # Only enable scraping for now
        )
        agent_tools.append(firecrawl_tools)
        logging.info("🌐 Firecrawl tools added to agent")
    
    # Simple function to fix path issues
    def normalize_path(path):
        """Normalize path to prevent nested templates directories."""
        path_str = str(path)
        if '/templates/templates/' in path_str:
            path_str = path_str.replace('/templates/templates/', '/templates/')
        return path_str
    
    # Log configuration
    logging.info(f"FileTools configured with base_dir: {TEMPLATES_DIR}")
    
    # Load existing memories for this user session
    # Use a consistent user ID instead of the dynamic Chainlit session ID
    # This ensures memories persist across different sessions
    user_id = "vilcos_user"  # Fixed user ID for consistency
    cl.user_session.set("memory_user_id", user_id)  # Store for later use
    memory_context = ""
    
    # Initialize Mem0 client and load memories if enabled
    if os.getenv("ENABLE_MEM0", "false").lower() == "true":
        try:
            from mem0 import MemoryClient
            memory_client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
            logging.info(f"🧠 Loading existing memories for user: {user_id}")
            
            # First, let's check what users exist and try to find any existing memories
            try:
                users_info = memory_client.users()
                logging.info(f"🧠 Available users in system: {users_info}")
                
                # If there are existing users, try to get memories from the first one
                if users_info and 'results' in users_info and len(users_info['results']) > 0:
                    existing_user_id = users_info['results'][0]['name']  # The actual user ID
                    logging.info(f"🧠 Found existing user: {existing_user_id}, trying to load their memories")
                    
                    existing_memories = memory_client.get_all(user_id=existing_user_id)
                    if existing_memories and len(existing_memories) > 0:
                        logging.info(f"🧠 Found {len(existing_memories)} existing memories, using existing user ID: {existing_user_id}")
                        user_id = existing_user_id  # Use the existing user ID
                        cl.user_session.set("memory_user_id", user_id)
            except Exception as users_error:
                logging.warning(f"Could not check existing users: {users_error}")
            
            # Get all memories for this user
            memories = memory_client.get_all(user_id=user_id)
            logging.info(f"🧠 Found {len(memories) if memories else 0} existing memories for user: {user_id}")
            
            if memories and len(memories) > 0:
                memory_context = "\n\n🧠 **What I remember about you:**\n"
                for memory in memories[:5]:  # Limit to 5 most recent memories
                    # Handle different memory formats
                    memory_text = ""
                    if isinstance(memory, dict):
                        if 'memory' in memory:
                            memory_text = memory['memory']
                        elif 'text' in memory:
                            memory_text = memory['text']
                        elif 'content' in memory:
                            memory_text = memory['content']
                        else:
                            memory_text = str(memory)
                    else:
                        memory_text = str(memory)
                    
                    if memory_text:
                        memory_context += f"- {memory_text}\n"
                
                logging.info(f"🧠 Loaded memory context: {memory_context}")
            else:
                logging.info("🧠 No existing memories found for this user")
        except Exception as e:
            logging.warning(f"Failed to load memories: {e}")
            logging.warning(f"Error details: {type(e).__name__}: {str(e)}")
    
    # Prepare enhanced instructions
    enhanced_instructions = [
        # Clear, direct instructions for file operations
        "USE THE FILE TOOLS to save and read files in the templates directory.",
        "When asked to create or edit a file, ALWAYS USE save_file to save the changes.",
        "ALWAYS save files with their direct filename, like 'index.html' or 'src/style.css'.",
        "After saving a file, respond with: 'Done: [brief description of changes]'.",
        
        # Template guidance
        "Create HTML files with proper Tailwind CSS structure.",
        "HTML files should link to /src/main.js using <script type='module' src='/src/main.js'></script>.",
        "CSS should use Tailwind classes. Custom CSS goes in /src/style.css.",
        "JavaScript files should be placed in the /src directory.",
        
        # Logo guidance
        "For the Vilcos logo, use this inline SVG code:",
        get_vilcos_logo_svg(),
        "You can adjust width/height attributes as needed.",
        
        # Important context
        f"Current directory structure:\n{template_contents}\n"
    ]
    
    # Add memory context to instructions if available
    if memory_context:
        enhanced_instructions.insert(0, f"IMPORTANT - User Context: {memory_context}")
    
    # Add enhanced features info if available
    if mem0_client:
        enhanced_instructions.append("🧠 Memory enabled: I can remember your preferences across sessions.")
    if firecrawl_enabled:
        enhanced_instructions.append("🌐 Web scraping enabled: I can analyze websites for inspiration when you provide URLs.")

    # Create an Agno agent for template editing with integrated knowledge base
    agent = Agent(
        model=OpenAIChat(id="gpt-4.1"),
        description="Website template editor that creates and edits HTML/CSS/JS files.",
        instructions=enhanced_instructions,
        tools=agent_tools,
        knowledge=template_knowledge,
        add_history_to_messages=True,
        show_tool_calls=True,
        markdown=True,
    )
    
    # Store the agent in user session
    cl.user_session.set("agent", agent)
    
    # Create action buttons
    actions = create_action_buttons()
    
    # Prepare welcome message with memory context
    welcome_content = f"""**Available Templates:**

I'll help you create and edit website templates. Use the buttons below to view or edit existing pages, or tell me what changes you'd like to make.

**Directory Structure:**
```text
{template_contents}
```

{memory_context if memory_context else ""}

What would you like to do?"""
    
    # First message to show the directory structure and page actions
    await cl.Message(
        content=welcome_content,
        actions=actions
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages with Mem0 integration."""
    # Get the agent from user session
    agent = cl.user_session.get("agent")
    user_id = cl.user_session.get("memory_user_id", "vilcos_user")
    
    # Check if we're in page creation mode
    creating_new_page = cl.user_session.get("creating_new_page", False)
    if creating_new_page:
        # Clear the flag
        cl.user_session.set("creating_new_page", False)
        # Add context to the message for page creation
        contextual_message = f"Create a new HTML page named '{message.content}'. Make it a complete, well-structured page with proper HTML structure, Tailwind CSS styling, and any appropriate content for a page with this name."
    else:
        contextual_message = message.content

    # Create a message for streaming the response
    response_message = cl.Message(content="")
    
    try:
        # Process the message with Agno and stream the response
        logging.info(f"Running agent with message: {contextual_message}")
        
        # Run the agent with the message
        response_content = ""
        for chunk in await cl.make_async(agent.run)(
            contextual_message,
            stream=True
        ):
            chunk_content = chunk.get_content_as_string()
            response_content += chunk_content
            await response_message.stream_token(chunk_content)
        
        # Store interaction in memory if available
        if os.getenv("ENABLE_MEM0", "false").lower() == "true" and response_content:
            try:
                from mem0 import MemoryClient
                memory_client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
                logging.info(f"🧠 Storing new memory for user: {user_id}")
                
                # Store as messages format that Mem0 expects
                messages = [
                    {"role": "user", "content": message.content},
                    {"role": "assistant", "content": response_content}
                ]
                result = memory_client.add(messages, user_id=user_id)
                logging.info(f"🧠 Memory stored successfully: {result}")
            except Exception as e:
                logging.warning(f"Failed to store memory: {e}")
        
        # Send the response and add action buttons back
        actions = create_action_buttons()
        response_message.actions = actions
        await response_message.send()
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await cl.Message(content=f"Error: {str(e)}").send()

# Running instructions: 
# chainlit run app.py -w 