"""
Medication scheduling service for PatientPal.
Parses medication details and creates a structured schedule.
"""

import json
import os
import schedule
import time
import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from groq import Groq

class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str
    timing: str
    instructions: Optional[str] = None
    
class MedicationSchedule(BaseModel):
    medications: List[Medication]
    daily_schedule: dict

class MedicationSchedulingService:
    def __init__(self):
        """Initialize the medication scheduling service."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = Groq(api_key=api_key)
        self.schedules = {}  # Store user medication schedules
        
    def parse_medication_input(self, medication_text):
        """
        Parse medication details from user input.
        
        Args:
            medication_text (str): Text description of medication
            
        Returns:
            Medication: Structured medication information
        """
        system_prompt = """
        You are a medication parsing assistant. Extract structured medication information from the text.
        
        Format your response as JSON with the following structure:
        {
          "name": "Medication name",
          "dosage": "Dosage amount",
          "frequency": "How often to take",
          "timing": "When to take (e.g., morning, with meals)",
          "instructions": "Any special instructions"
        }
        """
        
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Parse this medication information: {medication_text}"}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return Medication(**result)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse medication information")
    
    def generate_schedule(self, medications):
        """
        Generate a structured daily medication schedule.
        
        Args:
            medications (List[Medication]): List of medications
            
        Returns:
            dict: Structured daily schedule
        """
        system_prompt = """
        You are a medication scheduling assistant. Create a daily schedule for medications.
        
        Format your response as JSON with the following structure:
        {
          "morningSchedule": [
            {"name": "Med1", "dosage": "10mg", "time": "8:00 AM", "instructions": "with food"}
          ],
          "afternoonSchedule": [...],
          "eveningSchedule": [...],
          "nightSchedule": [...]
        }
        """
        
        medications_json = json.dumps([med.dict() for med in medications])
        
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a daily schedule for these medications: {medications_json}"}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            daily_schedule = json.loads(response.choices[0].message.content)
            return daily_schedule
        except json.JSONDecodeError:
            return {
                "morningSchedule": [],
                "afternoonSchedule": [],
                "eveningSchedule": [],
                "nightSchedule": []
            }
    
    def setup_reminders(self, user_id, daily_schedule):
        """
        Set up medication reminders based on the daily schedule.
        In a real application, this would connect to a notification system.
        
        Args:
            user_id (str): Unique identifier for the user
            daily_schedule (dict): The daily medication schedule
            
        Returns:
            bool: Success status
        """
        self.schedules[user_id] = daily_schedule
        
        return True
    
    def get_upcoming_reminders(self, user_id):
        """
        Get upcoming medication reminders for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            list: List of upcoming medication reminders
        """
        if user_id not in self.schedules:
            return []
            
        schedule = self.schedules[user_id]
        current_time = datetime.datetime.now()
        
        upcoming = []
        
        if "morningSchedule" in schedule and schedule["morningSchedule"]:
            for med in schedule["morningSchedule"]:
                upcoming.append({
                    "name": med["name"],
                    "dosage": med["dosage"],
                    "time": med["time"],
                    "instructions": med.get("instructions", "")
                })
                
        return upcoming
