import os
import json
from typing import Dict, List, Optional, Any
from mem0 import MemoryClient
from utils.logger import get_logger

logger = get_logger()


class MemoryService:
    """Service for managing persistent memory using Mem0."""
    
    def __init__(self):
        """Initialize the Mem0 client with optimized settings."""
        self.mem0_api_key = os.getenv("MEM0_API_KEY")
        if not self.mem0_api_key:
            logger.warning("MEM0_API_KEY not found. Memory features will be disabled.")
            self.client = None
        else:
            try:
                # Initialize Mem0 client (timeout/retries handled at request level)
                self.client = MemoryClient(api_key=self.mem0_api_key)
                logger.info("Mem0 client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Mem0 client: {e}")
                self.client = None
    
    def is_enabled(self) -> bool:
        """Check if memory service is enabled."""
        return self.client is not None
    
    def add_conversation_memory(
        self, 
        user_id: str, 
        user_message: str, 
        assistant_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a conversation exchange in memory with optimized payload.
        
        Args:
            user_id: Unique identifier for the user
            user_message: The user's message
            assistant_response: The assistant's response
            context: Additional context (form_id, form_title, etc.)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            # Truncate long responses to reduce payload size and improve speed
            max_message_length = 1000
            truncated_user_message = user_message[:max_message_length]
            truncated_response = assistant_response[:max_message_length]
            
            if len(user_message) > max_message_length:
                truncated_user_message += "... [truncated]"
            if len(assistant_response) > max_message_length:
                truncated_response += "... [truncated]"
            
            # Simplified metadata for faster processing
            metadata = {
                "type": "conversation",
                "timestamp": "now"
            }
            
            # Add only essential context to reduce payload
            if context:
                if context.get("form_id"):
                    metadata["form_id"] = context["form_id"]
                if context.get("query_type"):
                    metadata["query_type"] = context["query_type"]
            
            # Store in Mem0 with minimal payload
            self.client.add(
                messages=[
                    {"role": "user", "content": truncated_user_message},
                    {"role": "assistant", "content": truncated_response}
                ],
                user_id=user_id,
                metadata=metadata
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store conversation memory: {e}")
            return False
    
    def add_form_interaction_memory(
        self,
        user_id: str,
        form_id: str,
        form_title: str,
        interaction_type: str,
        details: Dict[str, Any]
    ) -> bool:
        """
        Store form interaction memory.
        
        Args:
            user_id: Unique identifier for the user
            form_id: Form identifier
            form_title: Form title
            interaction_type: Type of interaction (created, filled, analyzed, etc.)
            details: Additional details about the interaction
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            # Format memory content as a message (like conversation memory)
            memory_content = f"User {interaction_type} form '{form_title}' (ID: {form_id})"
            
            if details:
                memory_content += f" with details: {json.dumps(details)}"
            
            # Use messages format like conversation memory
            self.client.add(
                messages=[
                    {"role": "user", "content": memory_content}
                ],
                user_id=user_id,
                metadata={
                    "type": "form_interaction",
                    "form_id": form_id,
                    "form_title": form_title,
                    "interaction_type": interaction_type,
                    **details
                }
            )
            
            logger.info(f"Stored form interaction memory for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store form interaction memory: {e}")
            return False
    
    def add_user_preference_memory(
        self,
        user_id: str,
        preference_type: str,
        preference_value: Any,
        context: Optional[str] = None
    ) -> bool:
        """
        Store user preference memory.
        
        Args:
            user_id: Unique identifier for the user
            preference_type: Type of preference (ui_theme, analysis_style, etc.)
            preference_value: The preference value
            context: Additional context about when this preference was observed
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            memory_content = f"User prefers {preference_type}: {preference_value}"
            if context:
                memory_content += f" (Context: {context})"
            
            # Use messages format like other memory methods
            self.client.add(
                messages=[
                    {"role": "user", "content": memory_content}
                ],
                user_id=user_id,
                metadata={
                    "type": "user_preference",
                    "preference_type": preference_type,
                    "preference_value": preference_value,
                    "context": context
                }
            )
            
            logger.info(f"Stored user preference memory for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store user preference memory: {e}")
            return False
    
    def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories with optimized performance.
        
        Args:
            user_id: Unique identifier for the user
            query: Search query
            limit: Maximum number of results
            memory_type: Filter by memory type (optional)
        
        Returns:
            List of relevant memories
        """
        if not self.is_enabled():
            return []
        
        try:
            # Truncate query for faster search
            truncated_query = query[:100]
            
            # Search memories with reduced limit for faster response
            memories = self.client.search(
                query=truncated_query,
                user_id=user_id,
                limit=min(limit, 5)  # Cap at 5 for faster response
            )
            
            # Filter by memory type if specified
            if memory_type and memories:
                memories = [
                    m for m in memories 
                    if m.get('metadata', {}).get('type') == memory_type
                ]
            
            logger.info(f"Found {len(memories)} relevant memories for user {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def get_user_context(self, user_id: str, query: str) -> str:
        """
        Get relevant user context for a query with timeout protection.
        
        Args:
            user_id: Unique identifier for the user
            query: Current user query
        
        Returns:
            Formatted context string
        """
        if not self.is_enabled():
            return ""
        
        try:
            # Use a smaller limit for faster context retrieval
            memories = self.search_memories(user_id, query, limit=3)
            
            if not memories:
                return ""
            
            context_parts = []
            for memory in memories:
                memory_text = memory.get('memory', '')
                if memory_text:
                    # Truncate memory text for faster processing
                    truncated_text = memory_text[:200]
                    if len(memory_text) > 200:
                        truncated_text += "..."
                    context_parts.append(f"- {truncated_text}")
            
            if context_parts:
                return "Relevant context from previous interactions:\n" + "\n".join(context_parts)
            
            return ""
            
        except Exception as e:
            logger.error(f"Failed to get user context: {e}")
            return ""
    
    def get_form_history(self, user_id: str, form_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get user's form interaction history.
        
        Args:
            user_id: Unique identifier for the user
            form_id: Specific form ID to filter by (optional)
        
        Returns:
            List of form interaction memories
        """
        if not self.is_enabled():
            return []
        
        try:
            # Search for form interactions
            query = f"form interaction {form_id}" if form_id else "form interaction"
            memories = self.search_memories(
                user_id=user_id,
                query=query,
                limit=20,
                memory_type="form_interaction"
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get form history: {e}")
            return []
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's stored preferences.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            Dictionary of user preferences
        """
        if not self.is_enabled():
            return {}
        
        try:
            memories = self.search_memories(
                user_id=user_id,
                query="user preference",
                limit=50,
                memory_type="user_preference"
            )
            
            preferences = {}
            for memory in memories:
                metadata = memory.get('metadata', {})
                pref_type = metadata.get('preference_type')
                pref_value = metadata.get('preference_value')
                
                if pref_type and pref_value is not None:
                    preferences[pref_type] = pref_value
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return {} 