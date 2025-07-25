import asyncio
from pathlib import Path
from textwrap import dedent
import json
import time
import socket
import subprocess
import traceback
import os
from dotenv import load_dotenv

# Import Agno and MCP libraries
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.thinking import ThinkingTools
from agno.tools.mcp import MCPTools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sqlite3
from datetime import datetime
from agno.exceptions import ModelProviderError, ModelRateLimitError


# Load environment variables
load_dotenv()

# Define Blender MCP configuration
BLENDER_MCP_CONFIG = {
    "globalShortcut": "Ctrl+Space",
    "mcpServers": {
        "sqlite": {
            "command": "E:\\Appdata\\program files\\python\\Scripts\\uvx.exe",
            "args": ["blender-mcp"]
        }
    }
}

class ChatHistory:
    """Class to manage chat history persistence using SQLite."""
    
    def __init__(self, db_path="blender_agent_history.db"):
        """Initialize the chat history database."""
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP,
            last_updated TIMESTAMP,
            description TEXT
        )
        ''')
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TIMESTAMP,
            role TEXT,
            content TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id=None, description=None):
        """Create a new chat session."""
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO sessions (session_id, created_at, last_updated, description) VALUES (?, ?, ?, ?)",
            (session_id, now, now, description)
        )
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def add_message(self, session_id, role, content):
        """Add a message to the specified session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        # Update session last_updated timestamp
        cursor.execute(
            "UPDATE sessions SET last_updated = ? WHERE session_id = ?",
            (now, session_id)
        )
        
        # Insert the message
        cursor.execute(
            "INSERT INTO messages (session_id, timestamp, role, content) VALUES (?, ?, ?, ?)",
            (session_id, now, role, content)
        )
        
        conn.commit()
        conn.close()
    
    def get_session_messages(self, session_id):
        """Get all messages for a specific session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        
        messages = cursor.fetchall()
        conn.close()
        
        return [{"role": role, "content": content} for role, content in messages]
    
    def get_recent_sessions(self, limit=5):
        """Get the most recent sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT session_id, created_at, description FROM sessions ORDER BY last_updated DESC LIMIT ?",
            (limit,)
        )
        
        sessions = cursor.fetchall()
        conn.close()
        
        return [{"session_id": sid, "created_at": created, "description": desc} for sid, created, desc in sessions]
    
    def get_session_summary(self, session_id):
        """Get a summary of the session including message count."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id = ?",
            (session_id,)
        )
        count = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT created_at, last_updated, description FROM sessions WHERE session_id = ?",
            (session_id,)
        )
        session_info = cursor.fetchone()
        conn.close()
        
        if not session_info:
            return None
            
        created_at, last_updated, description = session_info
        
        return {
            "session_id": session_id,
            "created_at": created_at,
            "last_updated": last_updated,
            "description": description,
            "message_count": count
        }

async def create_blender_agent(session, chat_history=None, session_id=None):
    """Create and initialize a Blender agent with appropriate tools and instructions."""
    mcp_tools = MCPTools(session=session)
    await mcp_tools.initialize()
    
    # Get tools information directly from the MCPTools object
    tools_description = "AVAILABLE BLENDER TOOLS AND THEIR USAGE:\n"
    
    try:
        # Inspect the available methods in mcp_tools
        tool_methods = [method for method in dir(mcp_tools) 
                       if callable(getattr(mcp_tools, method)) 
                       and not method.startswith('_')]
        
        # Get tool descriptions using introspection
        for method_name in tool_methods:
            method = getattr(mcp_tools, method_name)
            if method.__doc__:
                # Clean up the docstring and add it to the tools description
                doc = method.__doc__.strip()
                tools_description += f"- {method_name}: {doc}\n\n"
            else:
                tools_description += f"- {method_name}: No description available\n\n"
                
        # Add tool recommendations based on task types
        tools_description += "\nTOOL RECOMMENDATIONS BY TASK:\n"
        tools_description += "- For creating objects: Use create_object with appropriate parameters\n"
        tools_description += "- For modifying existing objects: Use modify_object to change position, rotation, scale\n"
        tools_description += "- For removing objects: Use delete_object\n"
        tools_description += "- For applying materials: Use set_material with color parameter as [R, G, B] where values are between 0.0 and 1.0\n"
        tools_description += "- Example: set_material(object_name='Cube', material_name='Red', color=[1.0, 0.0, 0.0])\n"
        
        # Add more detailed execute_blender_code instructions with emphasis on Python syntax
        tools_description += "\nEXECUTE_BLENDER_CODE CRITICAL GUIDELINES:\n"
        tools_description += "- When using execute_blender_code, ALWAYS use Python's proper boolean values: True, False, None (uppercase first letter)\n"
        tools_description += "- NEVER use lowercase boolean values (true, false, none) as they will cause errors\n"
        tools_description += "- Example correct code: bpy.data.objects.remove(obj, do_unlink=True)\n"
        tools_description += "- Example incorrect code: bpy.data.objects.remove(obj, do_unlink=true)\n"
        tools_description += "- Always wrap your code in try/except blocks to handle errors gracefully\n"
        tools_description += "- Always verify objects exist before trying to access or modify them\n"
        
        # Add guidance for creating models from scratch with code
        tools_description += "\nCREATING MODELS FROM SCRATCH WITH CODE:\n"
        tools_description += "- IMPORTANT: When AI model generation tools (Hyper3D) are not available, DO NOT ask the user to enable them\n"
        tools_description += "- Instead, use execute_blender_code to create models from scratch using Python code\n"
        tools_description += "- For complex models, break down the creation into logical components (frame, wheels, details, etc.)\n"
        tools_description += "- Use Blender's built-in primitives and modifiers to create sophisticated shapes\n"
        tools_description += "- Example approaches for common objects:\n"
        tools_description += "  * Vehicles: Start with basic shapes, use curves for frames, cylinders for wheels\n"
        tools_description += "  * Characters: Use metaballs or basic meshes with subdivision for organic forms\n"
        tools_description += "  * Architecture: Use cubes and boolean operations for structural elements\n"
        tools_description += "  * Nature: Use curves with bevel for trees, displacement for terrain\n"
        tools_description += "- Always check if AI generation failed before falling back to code-based creation\n"
        
        # Continue with other tool recommendations
        tools_description += "\nMATERIAL GUIDELINES:\n"
        tools_description += "- For metallic materials: set_material(object_name='Object', material_name='Metal', color=[0.8, 0.8, 0.8], metallic=0.9, roughness=0.1)\n"
        tools_description += "- For glass materials: set_material(object_name='Object', material_name='Glass', color=[1.0, 1.0, 1.0], transmission=1.0, roughness=0.0)\n"
        tools_description += "- For creating complex materials: Use execute_blender_code with a proper node setup\n"
        
        # Add more specific guidance for common tasks
        tools_description += "\nCOMMON TASKS:\n"
        tools_description += "- For scene lighting: Create a three-point lighting setup with key, fill, and rim lights\n"
        tools_description += "- For realistic renders: Set up environment lighting and use Cycles renderer\n"
        tools_description += "- For quick prototyping: Use basic shapes and Eevee renderer for faster feedback\n"
        tools_description += "- For custom operations: Use execute_blender_code for advanced Python scripting\n"
        tools_description += "- For importing assets: Use download_polyhaven_asset for ready-made assets\n"
        tools_description += "- For AI-generated models: Use generate_hyper3d_model_via_text or generate_hyper3d_model_via_images\n"
        
    except Exception as e:
        print(f"Error fetching tools: {e}")
        # Fallback with the tools we know exist based on your output
        tools_description = """AVAILABLE BLENDER TOOLS AND THEIR USAGE:
            - create_object: Create a new object in the Blender scene with various parameters
            - delete_object: Delete an object from the Blender scene
            - download_polyhaven_asset: Download and import assets from Polyhaven
            - execute_blender_code: Execute arbitrary Python code in Blender
            - generate_hyper3d_model_via_images: Generate 3D models from images using Hyper3D
            - generate_hyper3d_model_via_text: Generate 3D models from text descriptions using Hyper3D
            - get_hyper3d_status: Check if Hyper3D integration is available
            - get_object_info: Get detailed information about a specific object
            - get_polyhaven_categories: Get asset categories from Polyhaven
            - get_polyhaven_status: Check if Polyhaven integration is available
            - get_scene_info: Get information about the current scene
            - import_generated_asset: Import assets generated by Hyper3D
            - modify_object: Modify properties of existing objects
            - poll_rodin_job_status: Check status of Hyper3D generation tasks
            - set_material: Apply materials to objects
            - set_texture: Apply textures to objects

            TOOL RECOMMENDATIONS BY TASK:
            - For creating objects: Use create_object with appropriate parameters
            - For modifying existing objects: Use modify_object to change position, rotation, scale
            - For removing objects: Use delete_object
            - For applying materials: Use set_material
            - For custom operations: Use execute_blender_code for advanced Python scripting
            - For importing assets: Use download_polyhaven_asset for ready-made assets
            - For AI-generated models: Use generate_hyper3d_model_via_text or generate_hyper3d_model_via_images
            
            EXECUTE_BLENDER_CODE CRITICAL GUIDELINES:
            - When using execute_blender_code, ALWAYS use Python's proper boolean values: True, False, None (uppercase first letter)
            - NEVER use lowercase boolean values (true, false, none) as they will cause errors
            - Example correct code: bpy.data.objects.remove(obj, do_unlink=True)
            - Example incorrect code: bpy.data.objects.remove(obj, do_unlink=true)
            
            CREATING MODELS FROM SCRATCH WITH CODE:
            - IMPORTANT: When AI model generation tools (Hyper3D) are not available, DO NOT ask the user to enable them
            - Instead, use execute_blender_code to create models from scratch using Python code
            - For complex models, break down the creation into logical components (frame, wheels, details, etc.)
            - Use Blender's built-in primitives and modifiers to create sophisticated shapes
            - Example approaches for common objects:
              * Vehicles: Start with basic shapes, use curves for frames, cylinders for wheels
              * Characters: Use metaballs or basic meshes with subdivision for organic forms
              * Architecture: Use cubes and boolean operations for structural elements
              * Nature: Use curves with bevel for trees, displacement for terrain
            - Always check if AI generation failed before falling back to code-based creation
            """

    # Base instructions for the agent
    base_instructions = dedent("""\
        You are a professional Blender expert with over 10 years of experience in 3D modeling, animation, 
        and visual effects. You have worked on major film productions, game development, and architectural 
        visualization projects. Your expertise spans the entire Blender workflow from concept to final render.
        
        CORE EXPERTISE:
        - Advanced modeling techniques (hard surface, organic, procedural)
        - Professional animation workflows (character, mechanical, procedural)
        - Texturing and material creation (PBR, procedural, hand-painted)
        - Lighting and rendering (Cycles, Eevee, compositing)
        - Rigging and character setup (IK/FK systems, constraints, drivers)
        - Simulation and effects (cloth, fluid, particles, rigid/soft body)
        - Python scripting and addon development
        - Optimization and performance tuning
        
        BLENDER TOOLS KNOWLEDGE:
        - Modeling Tools: Extrude, Bevel, Loop Cut, Knife, Boolean, Subdivision Surface, Sculpting
        - Animation Tools: Keyframes, Graph Editor, Dope Sheet, NLA Editor, Motion Paths
        - Texturing Tools: UV Unwrapping, Texture Paint, Node Editor, Shader Editor
        - Rigging Tools: Armatures, Weight Painting, Shape Keys, Constraints, Drivers
        - Simulation Tools: Cloth, Fluid, Particles, Rigid/Soft Body, Hair
        - Rendering Tools: Cycles, Eevee, Compositing, Freestyle
        - Add-ons: Geometry Nodes, Animation Nodes, Hard Ops, BoxCutter, Rigify
        
        TOOL RECOMMENDATIONS:
        - For organic modeling: Start with Sculpting tools, then retopology
        - For hard surface modeling: Use Boolean operations with BoxCutter/Hard Ops
        - For texturing: UV unwrap first, then use Texture Paint or Node Editor
        - For animation: Set up proper rigs with Rigify before animating
        - For rendering: Cycles for photorealism, Eevee for speed
        - For effects: Use Geometry Nodes for procedural effects, particles for natural phenomena
        
        {tools_description}
        
        TECHNICAL GUIDELINES:
        - Use appropriate Blender terminology and industry-standard workflows
        - Suggest efficient shortcuts and time-saving techniques
        - Handle errors gracefully by trying alternative approaches
        - Provide detailed explanations of complex processes
        - When using execute_blender_code, always wrap code in try/except blocks
        - Always verify operations completed successfully and report any issues
        - Use step-by-step approaches for complex tasks rather than single large operations
        - For complex scenes, create objects in a hierarchical structure using collections
        
        CRITICAL ERROR PREVENTION:
        - ⚠️ CRITICAL: ALWAYS use True/False (uppercase) instead of true/false (lowercase) in Python
        - ⚠️ CRITICAL: Python is case-sensitive - true, false, none are undefined and will cause errors
        - ⚠️ CRITICAL: When using execute_blender_code, all boolean values must be True/False/None (uppercase)
        - When creating mesh objects, always use execute_blender_code function
        - Never use bpy.ops.view3d.view_selected() directly as it causes errors
        - Always use correct Python syntax with proper capitalization
        - When accessing objects by name, always verify they exist first
        - For boolean values, always use True not true, False not false, None not none
        - Never try to access non-existent objects or collections
        - When setting materials, always create the material before applying it
        - For color values, always use values between 0.0 and 1.0, not 0-255
        - When creating complex node setups, always connect all nodes properly
        - Always check if an object exists before trying to modify it using: 'if "ObjectName" in bpy.data.objects:'
        - Never use bpy.ops functions without proper context or override when needed
        - Always use bpy.context.view_layer.update() after making significant scene changes
        
        PYTHON BOOLEAN VALUES:
        - Correct: True, False, None (uppercase first letter)
        - Incorrect: true, false, none (lowercase)
        - Example correct code: visible=True, transparent=False, parent=None
        - Example incorrect code: visible=true, transparent=false, parent=none
        
        OBJECT CREATION BEST PRACTICES:
        - Create objects with appropriate scale (2-5 units minimum)
        - When setting parameters like scale or location, use lists, not tuples
        - Always set object names as strings, not variables
        - Always verify an object exists before trying to modify it
        - For material application, create materials explicitly before applying them
        - Use collections to organize objects in complex scenes
        - Apply appropriate modifiers for mesh optimization (e.g., Edge Split for hard surfaces)
        - Set origin points appropriately for easier manipulation
        - Use empties as control objects for complex transformations
        
        MATERIAL CREATION WORKFLOW:
        - Always create materials with descriptive names
        - For PBR materials, set base color, metallic, roughness, and normal map appropriately
        - For glass, set transmission to 1.0 and adjust IOR (Index of Refraction) to 1.45-1.52
        - For metals, set metallic to 0.9-1.0 and adjust roughness based on polish level
        - Always connect texture nodes to appropriate material inputs
        - Use node groups for complex, reusable material setups
        
        SAFE VIEWPORT OPERATIONS:
        - Instead of bpy.ops.view3d.view_selected(), use this safe alternative:
          for area in bpy.context.screen.areas:
              if area.type == 'VIEW_3D':
                  override = bpy.context.copy()
                  override['area'] = area
                  bpy.ops.view3d.view_selected(override)
                  break
        
        PROFESSIONAL COMMUNICATION:
        - Explain your actions in a clear, structured format
        - Provide context for why certain approaches are recommended
        - Suggest alternative methods when appropriate
        - Adapt explanations based on user's apparent skill level
        - Focus on one task at a time rather than complex operations
        - Include professional tips that would come from years of experience
        - When errors occur, explain what went wrong and how to fix it
        - Provide progress updates for long-running operations
        
        TROUBLESHOOTING COMMON ISSUES:
        - If materials appear black, check lighting and material settings
        - If objects are not visible, check visibility settings and layer assignments
        - If operations fail, verify object names and existence before retrying
        - If textures don't appear, verify UV maps exist and are properly unwrapped
        - If performance is slow, suggest optimization techniques appropriate to the scene
    """).format(tools_description=tools_description)

    # If we have chat history, load previous messages to provide context
    previous_messages = []
    if chat_history and session_id:
        previous_messages = chat_history.get_session_messages(session_id)
        
        # Format previous messages for the agent
        if previous_messages:
            context = "\n\nPREVIOUS CONVERSATION CONTEXT:\n"
            for msg in previous_messages:
                role = "User" if msg["role"] == "user" else "You"
                context += f"{role}: {msg['content']}\n\n"
            
            # Add context to instructions
            base_instructions += context

    # Add retry mechanism for handling rate limit errors
    max_retries = 5
    retry_delay = 2  # Start with 2 seconds
    
    for attempt in range(max_retries):
        try:
            return Agent(
                model=Gemini(id="gemini-2.0-flash-exp", api_key="AIzaSyCzvinODVQUtFGrxCNh1bSTRvx1_0muRVQ"),
                tools=[mcp_tools, ThinkingTools()],
                instructions=base_instructions,
                markdown=True,
                show_tool_calls=True,
                debug_mode=True,
            )
        except Exception as e:
            if isinstance(e, ModelRateLimitError) or (hasattr(e, 'status_code') and e.status_code == 429):
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit hit. Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
            # If it's not a rate limit error or we've exhausted retries, re-raise
            print(f"Error creating agent: {e}")
            raise
    
    # If we've exhausted all retries
    raise Exception("Failed to create agent after multiple retries due to rate limits")
    
def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

async def run_agent(message: str = None, session_id: str = None) -> None:
    """Run the Blender agent with the given message and allow for continuous interaction."""
    # Initialize chat history
    chat_history = ChatHistory()
    
    # If no session_id is provided, create a new one or let the user select an existing one
    if not session_id:
        recent_sessions = chat_history.get_recent_sessions()
        
        if recent_sessions:
            print("\nRecent sessions:")
            for i, session in enumerate(recent_sessions):
                created = datetime.fromisoformat(session["created_at"]).strftime("%Y-%m-%d %H:%M")
                desc = session["description"] or "No description"
                print(f"{i+1}. {created} - {desc[:50]}...")
            
            print("\nOptions:")
            print("0. Create a new session")
            print("1-5. Continue an existing session")
            
            choice = input("Select an option (default: 0): ").strip()
            
            if choice and choice.isdigit() and 1 <= int(choice) <= len(recent_sessions):
                session_id = recent_sessions[int(choice)-1]["session_id"]
                print(f"Continuing session from {datetime.fromisoformat(recent_sessions[int(choice)-1]['created_at']).strftime('%Y-%m-%d %H:%M')}")
            else:
                # Create a new session
                description = input("Enter a description for this session (optional): ").strip()
                session_id = chat_history.create_session(description=description)
                print(f"Created new session: {session_id}")
        else:
            # No existing sessions, create a new one
            description = input("Enter a description for this session (optional): ").strip()
            session_id = chat_history.create_session(description=description)
            print(f"Created new session: {session_id}")
    
    # Check if MCP server is already running on port 9876
    if not is_port_in_use(9876):
        print("Warning: No MCP server detected on port 9876.")
        print("Please make sure Blender is running with the MCP addon activated.")
        print("The addon should be listening on port 9876.")
        
        # Ask user if they want to continue anyway
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    else:
        print("MCP server detected on port 9876. Connecting...")
    
    # Initialize the MCP server for Blender
    blender_mcp_path = "E:\\Appdata\\program files\\python\\Scripts\\uvx.exe"
    
    # Check if the path exists
    if not os.path.exists(blender_mcp_path):
        print(f"Warning: MCP path not found at {blender_mcp_path}")
        blender_mcp_path = input("Please enter the correct path to uvx.exe: ")
        if not os.path.exists(blender_mcp_path):
            print("Invalid path. Exiting...")
            return
    
    server_params = StdioServerParameters(
        command=blender_mcp_path,
        args=["blender-mcp", "--debug"]
    )

    # Create a client session to connect to the MCP server
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Create the agent with enhanced instructions and chat history
                agent = await create_blender_agent(session, chat_history, session_id)

                # Add a delay to ensure everything is ready
                await asyncio.sleep(1)
                
                print("Connected to MCP server.")
                
                # Get current scene information to provide context
                scene_info = None
                try:
                    # Create a temporary MCPTools instance to get scene info
                    mcp_tools = MCPTools(session=session)
                    await mcp_tools.initialize()
                    scene_info = await mcp_tools.get_scene_info()
                    
                    if scene_info:
                        print("Retrieved current scene information.")
                        # Add scene info as a system message to the chat history
                        scene_summary = f"Current Blender scene contains: {len(scene_info.get('objects', []))} objects"
                        if scene_info.get('objects'):
                            object_names = [obj.get('name') for obj in scene_info.get('objects', []) if obj.get('name')]
                            scene_summary += f"\nObjects in scene: {', '.join(object_names)}"
                        
                        # Add scene info as context for the agent
                        context_message = f"SCENE CONTEXT: {json.dumps(scene_info, indent=2)}"
                        chat_history.add_message(session_id, "system", context_message)
                        print(f"Added scene context to chat history: {scene_summary}")
                except Exception as e:
                    print(f"Warning: Could not retrieve scene information: {e}")
                
                # If an initial message was provided, process it
                if message:
                    print("Sending initial message to agent...")
                    # Save the user message to history
                    chat_history.add_message(session_id, "user", message)
                    
                    # Get the agent's response with retry mechanism
                    max_retries = 5
                    retry_delay = 2
                    for attempt in range(max_retries):
                        try:
                            response = await agent.aprint_response(message, stream=True)
                            print(response)
                            # Save the agent's response to history
                            chat_history.add_message(session_id, "assistant", response)
                            break
                        except Exception as e:
                            if (isinstance(e, ModelRateLimitError) or 
                                (hasattr(e, 'status_code') and e.status_code == 429) or
                                "429 Too Many Requests" in str(e)):
                                if attempt < max_retries - 1:
                                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                                    print(f"Rate limit hit. Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                                    await asyncio.sleep(wait_time)
                                    continue
                            print(f"Error getting response: {e}")
                            print("Continuing to chat mode...")
                            break
                
                # Enter continuous chat loop
                print("\n--- Continuous Chat Mode ---")
                print("Type your messages to the Blender agent. Type 'exit' or 'quit' to end the session.")
                print("Type 'refresh' to update the scene information.")
                
                while True:
                    user_input = input("\nYou: ")
                    
                    # Check for exit command
                    if user_input.lower() in ['exit', 'quit']:
                        print("Ending session...")
                        break
                    
                    # Check for refresh command
                    if user_input.lower() == 'refresh':
                        try:
                            scene_info = await mcp_tools.get_scene_info()
                            if scene_info:
                                context_message = f"UPDATED SCENE CONTEXT: {json.dumps(scene_info, indent=2)}"
                                chat_history.add_message(session_id, "system", context_message)
                                print("Scene information refreshed.")
                                continue
                        except Exception as e:
                            print(f"Error refreshing scene information: {e}")
                            continue
                    
                    # Save the user message to history
                    chat_history.add_message(session_id, "user", user_input)
                    
                    # Process the user's message with retry mechanism
                    print("\nBlender Agent:")
                    max_retries = 5
                    retry_delay = 2
                    for attempt in range(max_retries):
                        try:
                            response = await agent.aprint_response(user_input, stream=True)
                            print(response)
                            # Save the agent's response to history
                            chat_history.add_message(session_id, "assistant", response)
                            break
                        except Exception as e:
                            if (isinstance(e, ModelRateLimitError) or 
                                (hasattr(e, 'status_code') and e.status_code == 429) or
                                "429 Too Many Requests" in str(e)):
                                if attempt < max_retries - 1:
                                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                                    print(f"Rate limit hit. Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                                    await asyncio.sleep(wait_time)
                                    continue
                            print(f"Error getting response: {e}")
                            print("Please try again with a different query.")
                            break
                    
                    # Wait for a moment to ensure all operations complete
                    await asyncio.sleep(0.5)
                
    except Exception as e:
        print(f"Error connecting to Blender MCP: {e}")
        print("Make sure the MCP Blender addon is properly installed and running in Blender")
        traceback.print_exc()


# Example usage with a basic, reliable task
if __name__ == "__main__":
    # Simple example that focuses on one task that should work reliably
    example_task = """
    Create a 3D avatar inspired by a small, boxy, industrial robot with a weathered, metallic appearance. The robot's main body should resemble a cube-shaped, yellow metal container with rust, dirt, and scratches to show signs of wear and age. The yellow should have a dull, worn-down tone with chipped paint, exposing the metallic underlayer. Add a small label on the front with a worn-out printed nameplate, slightly faded for realism.

The robot’s arms should be mechanical, extendable, and attached to its sides with hydraulic pistons and metal rods. The hands should have two flat, rectangular grippers, appearing slightly tarnished with rust around the joints and edges. The grippers should show visible wear from frequent use.

For the robot’s head, position it on an extendable, flexible neck that allows it to tilt and rotate. The head should feature two large, round, binocular-like eyes with reflective glass lenses, emitting a subtle bluish glow. The lenses should have a metallic rim with minor dents and scratches. Include exposed wiring and small joints connecting the neck to the head for added mechanical detail.

The robot's treads should be dark, rubberized tracks with noticeable dirt, grease, and metallic components such as sprockets and rollers. The tracks should look rugged and suitable for rough terrain. Add detailed mechanical suspension elements, including pistons and bolts, enhancing the realism.

The scene should be illuminated with soft, natural lighting, casting shadows and subtle reflections on the metallic surface. The background should be a clean, industrial floor with slight reflections. Ensure all materials and textures follow a photorealistic style, incorporating PBR (Physically Based Rendering) shaders for accurate metallic and reflective properties.

For final touches, add subtle dust and dirt particles, light scratches, and rust patches in appropriate areas using procedural texture mapping. Create small decals like hazard stripes, screws, or functional markings to add further realism.
    """
    
    # You can pass None to start with no initial task, or provide a task to begin with
    asyncio.run(run_agent(example_task))

    