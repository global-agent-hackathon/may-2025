"""
Remote Agent Implementation for VibeProto
This file implements a cloud-based remote agent system that can process tasks in the background.
"""

import os
import json
import uuid
import time
import sqlite3
import threading
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('remote_agent')

# Load environment variables
load_dotenv()

class AgentStatus:
    """Class to track the status of remote agents"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RemoteTask:
    """Class to represent a task that can be processed by a remote agent"""
    def __init__(self, task_id: str, task_type: str, prompt: str, prototype_type: str, 
                 user_id: str, session_id: str):
        self.task_id = task_id
        self.task_type = task_type  # enhance_prompt, generate_code, analyze_code
        self.prompt = prompt
        self.prototype_type = prototype_type
        self.user_id = user_id
        self.session_id = session_id
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.status = AgentStatus.IDLE
        self.result = None
        self.error = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for storage"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "prompt": self.prompt,
            "prototype_type": self.prototype_type,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "result": self.result,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RemoteTask':
        """Create task from dictionary"""
        task = cls(
            task_id=data["task_id"],
            task_type=data["task_type"],
            prompt=data["prompt"],
            prototype_type=data["prototype_type"],
            user_id=data["user_id"],
            session_id=data["session_id"]
        )
        task.created_at = data["created_at"]
        task.completed_at = data["completed_at"]
        task.status = data["status"]
        task.result = data["result"]
        task.error = data["error"]
        return task

class SimpleTaskStorage:
    """A simple SQLite storage for tasks"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            data TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        self.conn.commit()
    
    def save(self, id: str, data: Dict[str, Any]):
        """Save task data with ID"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # Check if record exists
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(
                "UPDATE tasks SET data = ?, updated_at = ? WHERE id = ?",
                (json.dumps(data), now, id)
            )
        else:
            cursor.execute(
                "INSERT INTO tasks (id, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (id, json.dumps(data), now, now)
            )
        
        self.conn.commit()
        return id
    
    def get(self, id: str) -> Dict[str, Any]:
        """Get task data by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM tasks WHERE id = ?", (id,))
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        return None
    
    def update(self, id: str, data: Dict[str, Any]):
        """Update existing task data"""
        existing = self.get(id)
        if existing:
            updated = {**existing, **data}
            self.save(id, updated)
            return True
        return False

class RemoteAgentPool:
    """
    A pool of remote agents that can process tasks in parallel
    """
    def __init__(self, max_agents: int = 5):
        self.max_agents = max_agents
        self.storage = SimpleTaskStorage("remote_tasks.db")
        self.task_queue = []
        self.active_tasks = {}
        self.lock = threading.Lock()
        self.running = False
        self.worker_thread = None

    def start(self):
        """Start the agent pool"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        logger.info(f"Started RemoteAgentPool with {self.max_agents} max agents")

    def stop(self):
        """Stop the agent pool"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Stopped RemoteAgentPool")

    def submit_task(self, task_type: str, prompt: str, prototype_type: str,
                    user_id: str, session_id: str) -> str:
        """
        Submit a task to be processed by the next available agent
        Returns the task ID
        """
        task_id = str(uuid.uuid4())
        task = RemoteTask(
            task_id=task_id,
            task_type=task_type,
            prompt=prompt,
            prototype_type=prototype_type,
            user_id=user_id,
            session_id=session_id
        )
        
        # Store the task in the database
        self.storage.save(task_id, task.to_dict())
        
        # Add to the queue
        with self.lock:
            self.task_queue.append(task_id)
        
        logger.info(f"Submitted task {task_id} of type {task_type}")
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task"""
        task_data = self.storage.get(task_id)
        if not task_data:
            return {"error": "Task not found"}
        
        task = RemoteTask.from_dict(task_data)
        return {
            "task_id": task.task_id,
            "status": task.status,
            "created_at": task.created_at,
            "completed_at": task.completed_at,
            "result": task.result,
            "error": task.error
        }

    def _process_queue(self):
        """Process tasks in the queue"""
        while self.running:
            # Check if we can start a new task
            with self.lock:
                if len(self.active_tasks) < self.max_agents and self.task_queue:
                    task_id = self.task_queue.pop(0)
                    self.active_tasks[task_id] = True
                    # Start task processing in a new thread
                    threading.Thread(
                        target=self._process_task,
                        args=(task_id,),
                        daemon=True
                    ).start()
            
            # Sleep to avoid high CPU usage
            time.sleep(0.1)

    def _process_task(self, task_id: str):
        """Process a single task"""
        # Get the task from storage
        task_data = self.storage.get(task_id)
        if not task_data:
            logger.error(f"Task {task_id} not found in storage")
            return
        
        task = RemoteTask.from_dict(task_data)
        
        # Update status to running
        task.status = AgentStatus.RUNNING
        self.storage.update(task_id, task.to_dict())
        
        try:
            # Create an event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Import the agent from agno_agent.py
            from agno_agent import agent as vibeproto_agent
            
            # Process the task based on type
            result = None
            if task.task_type == "enhance_prompt":
                result = loop.run_until_complete(
                    vibeproto_agent.enhance_prompt(task.prompt)
                )
                task.result = {"enhanced_prompt": result}
            
            elif task.task_type == "generate_code":
                result = loop.run_until_complete(
                    vibeproto_agent.process_request(task.prompt, task.prototype_type)
                )
                task.result = result
            
            elif task.task_type == "analyze_code":
                # Assuming the prompt contains the code to analyze
                result = loop.run_until_complete(
                    vibeproto_agent.analyze_code(task.prompt)
                )
                task.result = {"analysis": result}
            
            # Update status to completed
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            task.status = AgentStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
        
        finally:
            # Update the task in storage
            self.storage.update(task_id, task.to_dict())
            
            # Remove from active tasks
            with self.lock:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]

# Create a singleton instance
remote_agent_pool = RemoteAgentPool(max_agents=int(os.environ.get("MAX_AGENTS", "5"))) 