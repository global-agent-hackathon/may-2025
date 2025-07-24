"""
Memory service for PatientPal using Mem0.
Stores and retrieves user data, medical terms, and medication schedules.
"""

import os
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional
import requests

class Mem0Service:
    def __init__(self):
        """Initialize the memory service using Mem0 API."""
        self.api_key = os.getenv("MEM0_API_KEY")
        if not self.api_key:
            print("Warning: MEM0_API_KEY not set. Using simulated memory service.")
            self._use_simulation = True
        else:
            self._use_simulation = False
            
        self._memory_store = {}
    
    def store_consultation(self, user_id, consultation_data):
        """
        Store a consultation summary and terms for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            consultation_data (dict): Contains summary and terms
            
        Returns:
            str: ID of the stored consultation
        """
        consultation_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        data = {
            "id": consultation_id,
            "userId": user_id,
            "timestamp": timestamp,
            "summary": consultation_data.get("summary", ""),
            "terms": consultation_data.get("terms", []),
            "type": "consultation"
        }
        
        if self._use_simulation:
            if user_id not in self._memory_store:
                self._memory_store[user_id] = {"consultations": [], "medications": [], "explanations": []}
            self._memory_store[user_id]["consultations"].append(data)
        else:
            # mem0_client.store(data)
            pass
            
        return consultation_id
    
    def store_medication_schedule(self, user_id, medication_data):
        """
        Store a medication schedule for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            medication_data (dict): Contains medications and schedule
            
        Returns:
            str: ID of the stored medication schedule
        """
        schedule_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        data = {
            "id": schedule_id,
            "userId": user_id,
            "timestamp": timestamp,
            "medications": medication_data.get("medications", []),
            "schedule": medication_data.get("schedule", {}),
            "type": "medication_schedule"
        }
        
        if self._use_simulation:
            if user_id not in self._memory_store:
                self._memory_store[user_id] = {"consultations": [], "medications": [], "explanations": []}
            self._memory_store[user_id]["medications"].append(data)
        else:
            # mem0_client.store(data)
            pass
            
        return schedule_id
    
    def store_term_explanation(self, user_id, term, explanation_data):
        """
        Store a term explanation for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            term (str): The medical term
            explanation_data (dict): Contains explanation and sources
            
        Returns:
            str: ID of the stored explanation
        """
        explanation_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        data = {
            "id": explanation_id,
            "userId": user_id,
            "timestamp": timestamp,
            "term": term,
            "explanation": explanation_data.get("explanation", ""),
            "sources": explanation_data.get("sources", []),
            "type": "explanation"
        }
        
        if self._use_simulation:
            if user_id not in self._memory_store:
                self._memory_store[user_id] = {"consultations": [], "medications": [], "explanations": []}
            self._memory_store[user_id]["explanations"].append(data)
        else:
            # mem0_client.store(data)
            pass
            
        return explanation_id
    
    def get_user_consultations(self, user_id):
        """
        Retrieve all consultation data for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            list: List of consultation data
        """
        if self._use_simulation:
            if user_id in self._memory_store:
                return self._memory_store[user_id]["consultations"]
            return []
        else:
            # return mem0_client.query({"userId": user_id, "type": "consultation"})
            return []
    
    def get_user_medication_schedules(self, user_id):
        """
        Retrieve all medication schedules for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            list: List of medication schedule data
        """
        if self._use_simulation:
            if user_id in self._memory_store:
                return self._memory_store[user_id]["medications"]
            return []
        else:
            # return mem0_client.query({"userId": user_id, "type": "medication_schedule"})
            return []
    
    def get_term_explanations(self, user_id, term=None):
        """
        Retrieve term explanations for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            term (str, optional): If provided, get explanations for this term only
            
        Returns:
            list: List of explanation data
        """
        if self._use_simulation:
            if user_id in self._memory_store:
                explanations = self._memory_store[user_id]["explanations"]
                if term:
                    return [exp for exp in explanations if exp["term"].lower() == term.lower()]
                return explanations
            return []
        else:
            # query = {"userId": user_id, "type": "explanation"}
            # if term:
            #     query["term"] = term
            # return mem0_client.query(query)
            return []
