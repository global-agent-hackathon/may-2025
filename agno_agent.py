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
    
    async def enhance_prompt(self, prompt: str, media_type: str = None) -> str:
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
        
        # Add multimodal context if applicable
        if media_type:
            multimodal_context = {
                'image': """
                
MULTIMODAL CONTEXT: The user has provided an IMAGE along with their request.
Analyze the image carefully and incorporate:
- Visual design elements shown in the image
- UI/UX patterns and layouts from the image
- Color schemes and styling from the image
- Any specific components or features visible in the image
- Use the image as design inspiration for the generated code
                """,
                'audio': """
                
MULTIMODAL CONTEXT: The user has provided an AUDIO file along with their request.
Consider incorporating:
- Audio playback functionality if relevant
- Sound-based interactions or feedback
- Any requirements related to the audio content
- Audio visualization if appropriate
                """,
                'video': """
                
MULTIMODAL CONTEXT: The user has provided a VIDEO file along with their request.
CRITICAL: Analyze the video to extract and replicate the UI/UX design patterns shown.

VIDEO ANALYSIS REQUIREMENTS:
1. **Visual Design Extraction**:
   - Identify the color scheme, gradients, and visual theme
   - Note the typography hierarchy and font styles
   - Observe spacing, padding, and layout grid system
   - Extract button styles, card designs, and component patterns
   - Identify animation and transition effects

2. **Layout & Structure**:
   - Analyze the page structure and sections
   - Identify navigation patterns (header, sidebar, tabs, etc.)
   - Note responsive design breakpoints and behaviors
   - Extract grid layouts for listings/cards
   - Observe hero sections and feature areas

3. **Component Patterns**:
   - Card designs for listings/items
   - Search bars and filter interfaces
   - Image galleries and carousels
   - Forms and input designs
   - Modal/popup patterns
   - Loading states and skeletons

4. **User Experience Flow**:
   - Navigation and browsing patterns
   - Search and filter interactions
   - Detail view presentations
   - Booking/purchase flows
   - User feedback mechanisms

IMPLEMENTATION DIRECTIVE:
Create a web application that closely mimics the design language, layout patterns, and user experience shown in the video. The goal is to produce a professional-looking clone with similar visual appeal and functionality.

For Airbnb-style videos, focus on:
- Property listing cards with images, prices, and ratings
- Search interface with location, dates, and guest inputs
- Filter sidebar or modal with categories
- Map integration placeholder
- Responsive grid layouts
- Clean, modern aesthetic with plenty of whitespace
                """
            }
            
            if media_type in multimodal_context:
                system_prompt += multimodal_context[media_type]
        
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
    
    async def generate_code(self, prompt: str, prototype_type: str) -> Dict[str, Any]:
        """Generate code based on the enhanced prompt"""
        if prototype_type.lower() in ['web_app', 'webapp', 'web', 'web app']:
            system_prompt = """You are an expert full-stack developer specializing in creating beautiful, modern web applications.

REQUIREMENTS:
1. Generate a COMPLETE, WORKING HTML file with embedded CSS and JavaScript
2. Create exactly what the user asks for - NO default todo apps or hardcoded templates
3. Use modern design principles with stunning visual aesthetics
4. Implement responsive design that works on all devices
5. Include smooth animations and professional interactions
6. Add proper error handling and user feedback
7. Use semantic HTML and accessibility best practices
8. Ensure all functionality works without external dependencies (except CDN libraries)

DESIGN STANDARDS:
- Modern gradient backgrounds or sophisticated color schemes
- Card-based layouts with subtle shadows
- Rounded corners (12-24px)
- Custom-styled form elements (no browser defaults)
- Smooth transitions (0.3s ease)
- Hover effects on interactive elements
- Professional typography with clear hierarchy
- Proper spacing and visual balance

TECHNICAL REQUIREMENTS:
- Single HTML file with embedded CSS/JS
- Use CSS Grid/Flexbox for layouts
- Include CSS variables for theming
- Modern JavaScript (ES6+)
- Local storage for data persistence when relevant
- Keyboard navigation support
- Touch-friendly for mobile devices

OUTPUT: Return ONLY the complete HTML code - no explanations or descriptions."""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            code = response.choices[0].message.content
            
            # Quality enhancement step
            qa_prompt = f"""Review and enhance this code to ensure:
1. It perfectly matches the user's request
2. All interactive elements are properly sized (min 44px touch targets)
3. Beautiful, modern design with professional aesthetics
4. All functionality is working correctly
5. Responsive design for all screen sizes
6. Smooth animations and transitions
7. Remove any visible explanatory text from the page
8. Clean, production-ready code

User's original request: {prompt}

Current code:
{code}

Return ONLY the improved HTML code with no explanations."""
            
            qa_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior UI/UX developer. Enhance the code to be production-ready."},
                    {"role": "user", "content": qa_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            final_code = qa_response.choices[0].message.content
            
            reasoning = f"""Generated web application based on: {prompt}
- Created responsive, modern design
- Implemented all requested functionality
- Added professional styling and animations
- Ensured cross-device compatibility
- Included accessibility features"""
            
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
    
    async def process_request(self, prompt: str, prototype_type: str, media_type: str = None) -> Dict[str, Any]:
        """Process a user request from start to finish"""
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Use the internal method with the generated session ID
        return await self._process_request_internal(prompt, prototype_type, session_id, media_type)
    
    def enhance_prompt_sync(self, prompt: str, media_type: str = None) -> str:
        """Synchronous wrapper for enhance_prompt"""
        import asyncio
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.enhance_prompt(prompt, media_type))
        except Exception as e:
            print(f"Error in enhance_prompt_sync: {e}")
            raise e
        finally:
            if loop:
                loop.close()
            
    def process_request_sync(self, prompt: str, prototype_type: str, media_type: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for process_request"""
        import asyncio
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # We need to generate a session ID here in the same thread
            session_id = str(uuid.uuid4())
            
            # Process the request
            result = loop.run_until_complete(self._process_request_internal(prompt, prototype_type, session_id, media_type))
            return result
        except Exception as e:
            print(f"Error in process_request_sync: {e}")
            raise e
        finally:
            if loop:
                loop.close()
    
    async def _process_request_internal(self, prompt: str, prototype_type: str, session_id: str, media_type: str = None) -> Dict[str, Any]:
        """Internal method to process a request with a provided session ID"""
        # Enhance the prompt
        enhanced_prompt = await self.enhance_prompt(prompt, media_type)
        
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