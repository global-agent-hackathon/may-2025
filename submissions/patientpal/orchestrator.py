"""
Agent orchestration for PatientPal using Agno.
Coordinates the workflow between different services.
"""

import os
import json
from typing import Dict, List, Any, Optional
import uuid

class AgnoOrchestrator:
    def __init__(self, transcription_service, image_processing_service, summary_service, explanation_service, 
                 medication_service, memory_service):
        """
        Initialize the orchestrator with all required services.
        
        Args:
            transcription_service: Service for audio transcription
            image_processing_service: Service for extracting text from images
            summary_service: Service for consultation summarization
            explanation_service: Service for term explanation
            medication_service: Service for medication scheduling
            memory_service: Service for persistent memory
        """
        self.transcription_service = transcription_service
        self.image_processing_service = image_processing_service
        self.summary_service = summary_service
        self.explanation_service = explanation_service
        self.medication_service = medication_service
        self.memory_service = memory_service
        
        self.api_key = os.getenv("AGNO_API_KEY")
        if not self.api_key:
            print("Warning: AGNO_API_KEY not set. Using simulated orchestration.")
            self._use_simulation = True
        else:
            self._use_simulation = False
    
    def process_consultation(self, user_id, audio_file=None, text_input=None, image_file=None):
        """
        Process a consultation from either audio, text, or image.
        
        Args:
            user_id (str): Unique identifier for the user
            audio_file: Audio file object, if provided
            text_input (str): Text input, if provided
            image_file: Image file object containing consultation notes, if provided
            
        Returns:
            dict: Processed consultation data with summary and terms
        """
        if audio_file is not None:
            transcription = self.transcription_service.transcribe(audio_file)
        elif image_file is not None:
            transcription = self.image_processing_service.extract_text(image_file)
        elif text_input is not None:
            transcription = text_input
        else:
            raise ValueError("Either audio_file, image_file, or text_input must be provided")
        
        consultation_data = self.summary_service.summarize(transcription)
        
        consultation_id = self.memory_service.store_consultation(user_id, consultation_data)
        
        return {
            "id": consultation_id,
            "transcription": transcription,
            "summary": consultation_data["summary"],
            "terms": consultation_data["terms"]
        }
    
    def explain_term(self, user_id, term, context=None):
        """
        Get or generate an explanation for a medical term.
        
        Args:
            user_id (str): Unique identifier for the user
            term (str): The medical term to explain
            context (str, optional): Context in which the term was used
            
        Returns:
            dict: Term explanation data
        """
        existing_explanations = self.memory_service.get_term_explanations(user_id, term)
        
        if existing_explanations:
            return existing_explanations[0]
        
        explanation_data = self.explanation_service.explain_term(term, context)
        
        explanation_id = self.memory_service.store_term_explanation(user_id, term, explanation_data)
        
        return {
            "id": explanation_id,
            "term": term,
            "explanation": explanation_data["explanation"],
            "sources": explanation_data["sources"]
        }
    
    def process_medication(self, user_id, medication_inputs):
        """
        Process medication inputs and generate a schedule.
        
        Args:
            user_id (str): Unique identifier for the user
            medication_inputs (List[str]): List of medication descriptions
            
        Returns:
            dict: Generated medication schedule
        """
        medications = []
        for med_input in medication_inputs:
            try:
                medication = self.medication_service.parse_medication_input(med_input)
                medications.append(medication)
            except ValueError as e:
                print(f"Error parsing medication: {e}")
                continue
        
        daily_schedule = self.medication_service.generate_schedule(medications)
        
        self.medication_service.setup_reminders(user_id, daily_schedule)
        
        schedule_id = self.memory_service.store_medication_schedule(
            user_id, 
            {"medications": [med.dict() for med in medications], "schedule": daily_schedule}
        )
        
        return {
            "id": schedule_id,
            "medications": [med.dict() for med in medications],
            "schedule": daily_schedule
        }
    
    def get_user_history(self, user_id):
        """
        Get the user's consultation and medication history.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            dict: User history data
        """
        consultations = self.memory_service.get_user_consultations(user_id)
        medications = self.memory_service.get_user_medication_schedules(user_id)
        explanations = self.memory_service.get_term_explanations(user_id)
        
        return {
            "consultations": consultations,
            "medications": medications,
            "explanations": explanations
        }
    
    def get_upcoming_reminders(self, user_id):
        """
        Get upcoming medication reminders for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            list: List of upcoming medication reminders
        """
        return self.medication_service.get_upcoming_reminders(user_id)
