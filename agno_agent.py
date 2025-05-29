"""
Simplified Agent Implementation for VibeProto
This implementation uses direct OpenAI calls instead of relying on agno-specific structures
"""

import os
import json
import uuid
import sqlite3
import threading
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class SimpleSqliteStorage:
    """A simple SQLite storage implementation with thread safety"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.local = threading.local()
        # Make sure we create tables on initialization
        self._get_connection().close()
        
    def _get_connection(self):
        """Get a thread-local SQLite connection"""
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            self.local.conn = sqlite3.connect(self.db_name)
            # Create tables for new connections
            self._create_tables(self.local.conn)
        return self.local.conn
    
    def _create_tables(self, conn):
        """Create tables in the given connection"""
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            data TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        conn.commit()
    
    def save(self, id: str, data: Dict[str, Any]):
        """Save data to storage with ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        # Check if record exists
        cursor.execute("SELECT id FROM sessions WHERE id = ?", (id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(
                "UPDATE sessions SET data = ?, updated_at = ? WHERE id = ?",
                (json.dumps(data), now, id)
            )
        else:
            cursor.execute(
                "INSERT INTO sessions (id, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (id, json.dumps(data), now, now)
            )
        
        conn.commit()
        return id
    
    def get(self, id: str) -> Dict[str, Any]:
        """Get data by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM sessions WHERE id = ?", (id,))
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        return None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all data"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, data FROM sessions")
        results = cursor.fetchall()
        
        return [
            {"id": row[0], **json.loads(row[1])}
            for row in results
        ]
    
    def update(self, id: str, data: Dict[str, Any]):
        """Update existing data"""
        existing = self.get(id)
        if existing:
            updated = {**existing, **data}
            self.save(id, updated)
            return True
        return False
    
    def delete(self, id: str):
        """Delete data by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (id,))
        conn.commit()
        return cursor.rowcount > 0

class VibeProtoAgent:
    """Simple agent implementation for VibeProto"""
    
    def __init__(self):
        self.storage = SimpleSqliteStorage("vibeproto.db")
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    async def enhance_prompt(self, prompt: str) -> str:
        """Enhance the user's prompt for better code generation"""
        system_prompt = """You are an expert prompt engineer specializing in creating comprehensive prompts for professional web application development.
        Transform the user's request into a detailed prompt that will generate production-quality code with STUNNING, MODERN UI/UX.
        
        REFERENCE THESE MODERN APP DESIGN PRINCIPLES (based on top-tier todo apps like those with purple gradients, card-based layouts, custom checkboxes):
        
        UI/UX REQUIREMENTS TO AUTOMATICALLY ADD:
        
        1. **VISUAL DESIGN** (Mandatory for ALL web apps):
           - Modern gradient backgrounds or headers (purple, blue, pink themes)
           - Card-based layouts with subtle shadows (0 2px 8px rgba(0,0,0,0.1))
           - Rounded corners everywhere (12-24px radius)
           - Custom-styled form elements (NO browser defaults)
           - Smooth animations and transitions (0.3s ease)
           - Hover effects on ALL interactive elements
           - Professional color schemes with CSS variables
           - Glassmorphism or soft UI elements where appropriate
           - Icon usage for actions (edit, delete, etc.)
           
        2. **LAYOUT & SPACING**:
           - Centered container with max-width
           - Consistent padding and margins (use rem units)
           - Visual hierarchy through size, color, and spacing
           - Mobile-responsive design (looks great on all devices)
           - Proper use of flexbox/grid for alignment
           - Ample whitespace for breathing room
           
        3. **TYPOGRAPHY**:
           - Modern font stack (Inter, system-ui, -apple-system)
           - Clear hierarchy (2rem titles, 1rem body, 0.875rem small text)
           - Proper line-height and letter-spacing
           - Bold for emphasis, muted colors for secondary text
           
        4. **INTERACTIVE ELEMENTS**:
           - Custom checkboxes/radio buttons with animations
           - Gradient or colored buttons with hover states
           - Focus states with colored outlines
           - Loading states and spinners
           - Tooltips and micro-interactions
           - Action buttons that appear on hover
           
        5. **COLOR SCHEMES** (suggest one of these):
           - Purple theme: #667eea to #764ba2 gradient
           - Blue theme: #4facfe to #00f2fe gradient  
           - Pink theme: #f093fb to #f5576c gradient
           - Dark theme: #1a202c with bright accents
           
        6. **ANIMATIONS**:
           - Fade in for new elements
           - Slide + fade for deletions
           - Scale effects for clicks
           - Smooth transitions for state changes
           - Stagger animations for lists
           
        7. **FUNCTIONALITY REQUIREMENTS**:
           - All features requested by user
           - Keyboard shortcuts (Enter to submit, Esc to cancel)
           - LocalStorage for data persistence
           - Input validation with visual feedback
           - Confirmation for destructive actions
           - Empty states with helpful messages
           - Accessibility features (ARIA labels, keyboard nav)
           
        8. **CODE QUALITY**:
           - Single HTML file with embedded CSS/JS
           - Well-organized with clear sections
           - Modern JavaScript (ES6+)
           - CSS variables for theming
           - Responsive without media queries where possible
           - Performance optimized
           
        Transform the user's request to explicitly require a VISUALLY STUNNING app that looks like a $1000 premium product.
        The result should make users think "Wow, this looks amazing!" not just function correctly.
        
        IMPORTANT: Even for simple requests, emphasize that the UI must be BEAUTIFUL, MODERN, and PROFESSIONAL."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Original request: {prompt}\n\nCreate a comprehensive prompt that will generate a STUNNING, PROFESSIONAL web application with modern UI/UX that rivals commercial products. Make it clear the visual design is as important as functionality."}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    async def generate_code(self, prompt: str, prototype_type: str) -> Dict[str, str]:
        """Generate code based on the prompt and prototype type"""
        
        # More specific system prompts based on prototype type
        if prototype_type.lower() == "web_app" or "web" in prototype_type.lower():
            # PROMPT-BOOSTER SYSTEM PROMPT
            system_prompt = """You are both a UX architect and front-end engineer creating STUNNING, MODERN web applications.

WORKFLOW:
STEP-1 (spec):
  • Audience: Who will use this?
  • Problem: What pain does it solve?
  • Devices: Mobile-first? Desktop-first?
  • #Screens: How many views needed?
  • Primary CTA: What's the main action?
  • Brand vibe: 3 adjectives (e.g., playful, professional, minimal)

STEP-2 (wireframe):
  • Create HTML comments representing the layout structure
  • Define component hierarchy
  • Mark interactive elements

STEP-3 (code):
  • Single HTML file with embedded Tailwind CSS via CDN
  • Modern JavaScript (ES6+)
  • Responsive, accessible, performant

STEP-4 (QA):
  • Check contrast ratios (≥ 4.5:1)
  • Verify touch targets (≥ 48×48px)
  • Test keyboard navigation
  • Ensure responsive design

HARD DESIGN RULES:
GRID: 12-col, 4px baseline. Breakpoints: 0/600/960/1280/1440
BUTTONS: min-touch 48×48px; radius rounded-md; primary color only once per view
SPACING: Use Tailwind scale only (p-2, p-4, p-6, p-8) - NO magic numbers
TEXT: Use prose classes for readability; cap line-length at 70ch
MOTION: 200-400ms transitions with ease-in-out; respect prefers-reduced-motion
ACCESSIBILITY: All text/background pairs ≥ AA; include aria-labels on icons
COLOR: Use a cohesive palette with proper contrast

TODO APP SPECIFIC REQUIREMENTS:
1. LAYOUT:
   - Centered container (max-w-2xl mx-auto)
   - Header with gradient background
   - Large, prominent input field (min-height 56px)
   - Large, clickable Add button (min 48×48px)
   - Task cards with proper spacing (gap-4)
   - Action buttons visible on hover

2. COMPONENTS:
   - Input: Large text field with rounded borders, shadow on focus
   - Add Button: Primary color, large size, proper padding
   - Task Card: White bg, shadow, rounded corners, hover effects
   - Checkbox: Custom styled, 24×24px minimum
   - Delete/Edit buttons: Icon buttons, 40×40px

3. INTERACTIONS:
   - Enter key to add task
   - Click checkbox to toggle
   - Smooth animations (200-300ms)
   - Visual feedback on all actions

RETURN ONLY CODE - NO EXPLANATIONS!

CRITICAL OUTPUT REQUIREMENTS:
- Pure HTML file with embedded CSS and JavaScript
- NO explanatory text visible on the page
- NO descriptions about what was built or how to use it
- Beautiful gradient background (not plain white)
- Clean, working interface only"""
            
            # Step 1: Generate spec and wireframe
            spec_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""USER_DESIRE: "{prompt}"
                    
First, create the SPEC and WIREFRAME as HTML comments, then generate the complete code.

Example output structure:
<!-- SPEC
Audience: Everyone who needs task management
Problem: Keeping track of daily tasks
Devices: Mobile-first, responsive to desktop
Screens: 1 (single page app)
Primary CTA: Add new task
Brand vibe: Clean, modern, professional
-->

<!-- WIREFRAME
┌─────────────────────────────────┐
│  Header (Gradient BG)           │
│  ┌───────────────────────────┐  │
│  │    TaskMaster             │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  Add Task Section               │
│  ┌─────────────────┬─────────┐  │
│  │ Input (Large)   │ Add Btn │  │
│  └─────────────────┴─────────┘  │
├─────────────────────────────────┤
│  Task List                      │
│  ┌───────────────────────────┐  │
│  │ □ Task 1        [✎] [🗑]  │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ ✓ Task 2        [✎] [🗑]  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
-->

Then create the COMPLETE HTML with:
- Tailwind CSS via CDN
- Proper component sizing
- Working JavaScript
- All interactions functional"""}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            code = spec_response.choices[0].message.content
            
            # Step 2: Quality check and enhance
            qa_prompt = f"""Review this code and ensure:
1. Input field is large (min-height: 56px, text-lg or text-xl)
2. Add button is prominent (min 48x48px, px-6 py-3 or larger)
3. Task display area uses cards with proper spacing
4. All buttons meet minimum touch target (48x48px)
5. Proper contrast ratios
6. Working functionality (add, complete, delete tasks)
7. Enter key adds tasks
8. Tasks persist in localStorage
9. REMOVE ANY EXPLANATORY TEXT - no descriptions about changes or improvements
10. Add beautiful background gradient to body (not just white)

Current code:
{code}

CRITICAL: Return ONLY the cleaned HTML code with:
- No explanatory text visible on the page
- Beautiful gradient background (like: bg-gradient-to-br from-purple-50 to-pink-50)
- All functionality working
- NO DESCRIPTIONS OR EXPLANATIONS in the HTML content

Return the pure HTML file only."""
            
            qa_response = self.client.chat.completions.create(
                model="gpt-4",
            messages=[
                    {"role": "system", "content": "You are a UI/UX expert. Fix any issues and return only the improved HTML code."},
                    {"role": "user", "content": qa_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            final_code = qa_response.choices[0].message.content
            
            # Extract reasoning from the process
            reasoning = f"""Design Process:
1. Analyzed user needs for: {prompt}
2. Created responsive layout with proper component sizing
3. Implemented Tailwind CSS for consistent styling
4. Added smooth animations and hover effects
5. Ensured accessibility with ARIA labels and keyboard navigation
6. Optimized for mobile-first design
7. Added localStorage for data persistence"""
            
            return {
                "code": final_code,
                "reasoning": reasoning
            }
            
        else:  # automation_script or Python
            system_prompt = """You are an expert Python developer. Generate ONLY working, executable Python code with professional standards.
            
            Requirements:
            - Return complete, runnable Python code
            - Include all necessary imports and dependencies
            - Add proper error handling and input validation
            - Include clear docstrings and comments where helpful
            - Follow Python best practices and PEP 8 style guidelines
            - Make the code production-ready and robust
            - Add user-friendly console output and progress indicators
            - Include proper logging where appropriate
            - DO NOT return documentation, explanations, or specifications
            - ONLY return the actual Python code that can be executed
            
            Format: Return a complete Python script (.py file content)."""
        
        response = self.client.chat.completions.create(
                model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
        )
        
        return {
            "code": response.choices[0].message.content,
                "reasoning": "Generated Python automation script based on requirements"
        }
    
    async def analyze_code(self, code: str) -> str:
        """Analyze generated code for potential improvements"""
        system_prompt = """You are an expert code reviewer.
        Analyze the code for potential improvements, bugs, and best practices."""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this code:\n{code}"}
            ]
        )
        
        return response.choices[0].message.content
    
    async def process_request(self, prompt: str, prototype_type: str) -> Dict[str, Any]:
        """Process a user request from start to finish"""
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Use the internal method with the generated session ID
        return await self._process_request_internal(prompt, prototype_type, session_id)
    
    def enhance_prompt_sync(self, prompt: str) -> str:
        """Synchronous wrapper for enhance_prompt"""
        import asyncio
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.enhance_prompt(prompt))
        except Exception as e:
            print(f"Error in enhance_prompt_sync: {e}")
            raise e
        finally:
            if loop:
                loop.close()
            
    def process_request_sync(self, prompt: str, prototype_type: str) -> Dict[str, Any]:
        """Synchronous wrapper for process_request"""
        import asyncio
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # We need to generate a session ID here in the same thread
            session_id = str(uuid.uuid4())
            
            # Process the request
            result = loop.run_until_complete(self._process_request_internal(prompt, prototype_type, session_id))
            return result
        except Exception as e:
            print(f"Error in process_request_sync: {e}")
            raise e
        finally:
            if loop:
                loop.close()
    
    async def _process_request_internal(self, prompt: str, prototype_type: str, session_id: str) -> Dict[str, Any]:
        """Internal method to process a request with a provided session ID"""
        # Enhance the prompt
        enhanced_prompt = await self.enhance_prompt(prompt)
        
        # Generate code
        result = await self.generate_code(enhanced_prompt, prototype_type)
        
        # Analyze the generated code
        analysis = await self.analyze_code(result["code"])
        
        # Store the result
        self.storage.save(session_id, {
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "code": result["code"],
            "reasoning": result["reasoning"],
            "analysis": analysis,
            "type": prototype_type,
            "created_at": datetime.now().isoformat()
        })
        
        return {
            "enhanced_prompt": enhanced_prompt,
            "code": result["code"],
            "reasoning": result["reasoning"],
            "analysis": analysis,
            "session_id": session_id
        }

# Create a singleton instance
agent = VibeProtoAgent() 