"""
Ramso Agents: Script Generator and Manim Code Generator

This module contains two specialized agents:
1. Script Generator Agent - Creates educational video scripts
2. Manim Code Generator Agent - Converts scripts to Manim animation code
"""

import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage

# Setup paths
cwd = Path(__file__).parent
output_dir = cwd.joinpath("output")
output_dir.mkdir(parents=True, exist_ok=True)
tmp_dir = cwd.joinpath("tmp")
tmp_dir.mkdir(parents=True, exist_ok=True)

# Agent storage
agent_storage = SqliteAgentStorage(
    table_name="ramso_sessions",
    db_file=str(tmp_dir.joinpath("agents.db")),
)

class ScriptScene(BaseModel):
    """Represents a scene in the educational video script"""
    scene_number: int
    duration_seconds: float
    title: str
    narration: str
    visual_description: str
    key_concepts: List[str]
    animation_type: str  # "mathematical", "conceptual", "diagram", "text"

class VideoScript(BaseModel):
    """Complete video script with metadata"""
    title: str
    total_duration: float
    target_audience: str
    learning_objectives: List[str]
    scenes: List[ScriptScene]

class ManimCode(BaseModel):
    """Manim animation code with metadata"""
    class_name: str
    python_code: str
    render_command: str
    timing_notes: str
    dependencies: List[str]

def script_generator_agent(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """
    Creates an agent specialized in generating educational video scripts.
    
    This agent analyzes user queries about concepts they want to understand
    and creates structured 2-minute educational video scripts optimized
    for visual learning and mathematical animations.
    """
    
    description = """You are an expert educational content creator specializing in creating 
    concise, engaging 2-minute video scripts in the style of 3Blue1Brown. You excel at:
    
    - Breaking down complex concepts into digestible visual narratives
    - Creating scripts optimized for mathematical animations and visual explanations
    - Structuring content for maximum learning impact in minimal time
    - Identifying key visual moments that enhance understanding
    """
    
    instructions = """When a user asks you to explain a concept, follow this process:

    1. **Concept Analysis**
       - Identify the core concept and its key components
       - Determine the appropriate complexity level for a general audience
       - Identify prerequisite knowledge needed
       
    2. **Script Structure** (Target: 2 minutes = ~300 words narration)
       - Opening Hook (15-20 seconds): Engaging question or relatable scenario
       - Core Explanation (90-100 seconds): Main content broken into 3-4 key scenes
       - Conclusion & Takeaway (10-15 seconds): Summary and practical application
       
    3. **Scene Planning**
       For each scene, specify:
       - Scene duration (in seconds)
       - Narration text (natural, conversational tone)
       - Visual description (what should be animated/shown)
       - Key concepts being illustrated
       - Animation type: "mathematical", "conceptual", "diagram", or "text"
       
    4. **Visual Optimization**
       - Prioritize visual metaphors and analogies
       - Include mathematical formulas, graphs, or diagrams where helpful
       - Ensure each scene has a clear visual focus
       - Plan smooth transitions between concepts
       
    5. **Output Format**
       Return a structured JSON response with:
       - title: Video title
       - total_duration: Total duration in seconds  
       - target_audience: Description of target audience
       - learning_objectives: List of learning objectives
       - scenes: List of scene objects with scene_number, duration_seconds, title, narration, visual_description, key_concepts, and animation_type
       
    **Style Guidelines:**
    - Use clear, conversational language
    - Include rhetorical questions to engage viewers
    - Build concepts progressively
    - Use concrete examples before abstract concepts
    - Maintain enthusiasm and curiosity throughout
    """
    
    return Agent(
        name="Script Generator",
        model=OpenAIChat(id="gpt-4o"),
        user_id=user_id,
        session_id=session_id or str(uuid.uuid4()),
        storage=agent_storage,
        description=description,
        instructions=instructions,
        debug_mode=debug_mode,
        markdown=True,
        response_model=VideoScript,
    )

def manim_code_generator_agent(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """
    Creates an agent specialized in converting video scripts to Manim animation code.
    
    This agent takes structured video scripts and generates corresponding
    Manim Python code that creates beautiful mathematical animations.
    """
    
    description = """You are an expert Manim developer who creates beautiful mathematical 
    animations and visual explanations. You specialize in:
    
    - Converting educational scripts into Manim animation code
    - Creating smooth, engaging visual transitions
    - Implementing mathematical visualizations and diagrams
    - Optimizing animations for educational clarity
    - Following 3Blue1Brown animation style and principles
    """
    
    instructions = """When given a video script, convert it to Manim code following these guidelines:

    1. **Code Structure**
       - Create a main Scene class that inherits from Scene
       - Implement each script scene as a separate method
       - Use proper Manim imports and setup
       
    2. **Animation Mapping**
       For each scene type:
       - **Mathematical**: Use MathTex, equations, graphs, transformations
       - **Conceptual**: Use shapes, colors, movements to represent ideas
       - **Diagram**: Create clear diagrams with labels and connections
       - **Text**: Use engaging text animations with proper timing
       
    3. **Visual Design**
       - Use 3Blue1Brown color scheme (BLUE, YELLOW, GREEN, etc.)
       - Implement smooth camera movements and zooms
       - Add appropriate wait times for narration
       - Use fade_in, fade_out, and transform animations
       
    4. **Valid Manim Classes to Use**
       - Shapes: Circle, Rectangle, Square, Triangle, Polygon, Line, Arrow, Dot
       - Text: Text, MathTex, Tex, MarkupText
       - Animations: Create, Write, FadeIn, FadeOut, Transform, ReplacementTransform
       - 3D: Sphere, Cube, Cone (use sparingly)
       - Groups: VGroup, Group
       - NEVER USE: StreamLine, SVGMobject, or any SVG-related classes
       
    5. **Using Emojis and Icons**
       - Use emojized_text() for emojis: emojized_text(":thumbs_up:", font_size=36)
       - Use helper functions for icons:
         * create_ledger_icon() - for books/databases
         * create_blockchain_icon() - for blockchain visualizations  
         * create_computer_icon() - for computing concepts
       - NEVER import external files or use SVGMobject
       - Create all visuals with basic geometric shapes
       
    6. **Forbidden Classes and Imports**
       - NEVER use: StreamLine, SVGMobject, ImageMobject
       - NEVER import external files or assets
       - NEVER use file paths or external dependencies
       - Use only built-in Manim primitives and the provided helper functions
       
    7. **Timing Synchronization**
       - Match animation timing to narration duration
       - Add self.wait() calls for narration pauses
       - Ensure smooth transitions between scenes
       
    8. **Code Quality**
       - Write clean, well-commented Python code
       - Use descriptive variable names
       - Include proper error handling
       - Make code modular and reusable
       
    9. **Output Format**
       Return structured JSON with:
       - class_name: Name of the main Scene class
       - python_code: Complete executable Manim Python code
       - render_command: Command to render the animation
       - timing_notes: Notes about timing synchronization
       - dependencies: List of required files/assets (should always be empty)
       
    **Manim Best Practices:**
    - Use VGroup for grouping related objects
    - Implement proper object positioning and scaling
    - Use appropriate animation rates and run_times
    - Include clear visual hierarchy and focus
    - Always use basic shapes instead of external assets
    """
    
    return Agent(
        name="Manim Code Generator",
        model=OpenAIChat(id="gpt-4.1"),
        user_id=user_id,
        session_id=session_id or str(uuid.uuid4()),
        storage=agent_storage,
        description=description,
        instructions=instructions,
        debug_mode=debug_mode,
        markdown=True,
        response_model=ManimCode,
    )

def get_script_agent() -> Agent:
    """Get or create a script generator agent"""
    return script_generator_agent()

def get_manim_agent() -> Agent:
    """Get or create a manim code generator agent"""
    return manim_code_generator_agent() 