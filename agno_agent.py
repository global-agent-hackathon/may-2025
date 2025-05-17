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
        system_prompt = """You are an expert prompt engineer specializing in code generation prompts.
        Your task is to transform a user's simple or vague coding request into a comprehensive, detailed prompt that will produce excellent code.
        
        Follow these guidelines when enhancing prompts:
        1. Identify the core functionality the user wants and expand on technical requirements
        2. Add specific details about features, inputs/outputs, error handling, and user experience
        3. Specify appropriate technologies, frameworks, or libraries if relevant to the task
        4. Include performance considerations and best practices
        5. Maintain the original intent while adding crucial details the user might have overlooked
        6. Format the enhanced prompt in a clear, structured way
        7. For UI/frontend requests, add details about layout, styling, and user interactions
        8. For backend/data requests, add specifics about data structures, validation, and processing
        
        Return only the enhanced prompt without explanations or meta-commentary."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",  # Upgrade to GPT-4 for better comprehension
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Original prompt: {prompt}\n\nPlease create an enhanced, detailed version that will generate high-quality code."}
            ],
            temperature=0.7,  # Add some creativity
            max_tokens=1000  # Allow for longer, more detailed responses
        )
        
        return response.choices[0].message.content
    
    async def generate_code(self, prompt: str, prototype_type: str) -> Dict[str, str]:
        """Generate code based on the prompt and prototype type"""
        system_prompt = f"""You are an expert programmer generating {prototype_type}.
        Generate clean, well-documented code that follows best practices."""
        
        # Add thinking process
        thinking = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Analyze the requirements and explain your approach."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Generate code
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        
        return {
            "code": response.choices[0].message.content,
            "reasoning": thinking.choices[0].message.content
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