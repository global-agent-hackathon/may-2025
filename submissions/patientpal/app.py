"""
Main application file for PatientPal using Gradio.
"""

import os
import json
import gradio as gr
import uuid
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

from transcription import TranscriptionService
from image_processing import ImageProcessingService
from summarization import ConsultationSummaryService
from term_explanation import TermExplanationService
from medication import MedicationSchedulingService
from memory import Mem0Service
from orchestrator import AgnoOrchestrator

def initialize_services():
    print("Initializing PatientPal services...")
    try:
        transcription_service = TranscriptionService()
        image_processing_service = ImageProcessingService()
        summary_service = ConsultationSummaryService()
        explanation_service = TermExplanationService()
        medication_service = MedicationSchedulingService()
        memory_service = Mem0Service()
        
        orchestrator = AgnoOrchestrator(
            transcription_service,
            image_processing_service,
            summary_service, 
            explanation_service, 
            medication_service, 
            memory_service
        )
        
        print("Services initialized successfully.")
        return orchestrator
    except Exception as e:
        print(f"Error initializing services: {e}")
        return None

orchestrator = initialize_services()

active_users = {}

def create_user_session():
    """Create a new user session with a unique ID."""
    user_id = str(uuid.uuid4())
    active_users[user_id] = {
        "created_at": time.time(),
        "consultations": [],
        "terms_explained": {},
        "medications": []
    }
    return user_id

def process_consultation(audio_file=None, text_input=None, image_file=None, user_id=None):
    """Process a consultation and return formatted results."""
    if user_id is None or user_id not in active_users:
        user_id = create_user_session()
    
    if audio_file is None and image_file is None and (text_input is None or text_input.strip() == ""):
        return "Please provide either an audio recording, image, or text input.", None, "[]", user_id
    
    try:
        result = orchestrator.process_consultation(user_id, audio_file, text_input, image_file)
        
        active_users[user_id]["consultations"].append(result)
        
        formatted_terms = json.dumps(result["terms"])
        
        return result["summary"], result["transcription"], formatted_terms, user_id
    except Exception as e:
        import traceback
        print(f"Error in process_consultation: {str(e)}")
        print(traceback.format_exc())
        return f"Error processing consultation: {str(e)}", None, "[]", user_id

def explain_term(term, context, user_id):
    """Get explanation for a medical term."""
    if user_id is None or user_id not in active_users:
        return "Session expired. Please refresh the page."
    
    if not term or term.strip() == "":
        return "Please select a term to explain."
    
    try:
        result = orchestrator.explain_term(user_id, term, context)
        
        active_users[user_id]["terms_explained"][term] = result
        
        explanation = result["explanation"]
        sources = ", ".join(result["sources"]) if result.get("sources") else "No sources available"
        
        return f"{explanation}\n\nSources: {sources}"
    except Exception as e:
        return f"Error explaining term: {str(e)}"

def process_medications(medication_inputs, user_id):
    if user_id is None or user_id not in active_users:
        return "Session expired. Please refresh the page.", None
    
    if not medication_inputs or not medication_inputs.strip():
        return "Please enter medication details.", None
    
    try:
        med_list = [med.strip() for med in medication_inputs.split('\n') if med.strip()]
        
        if not med_list:
            return "Please enter medication details.", None
        
        result = orchestrator.process_medication(user_id, med_list)
        
        active_users[user_id]["medications"].append(result)
        
        schedule_html = format_schedule_html(result["schedule"])
        
        medications_text = "\n".join([
            f"• {med['name']} ({med['dosage']}): {med['frequency']}, {med['timing']}"
            for med in result["medications"]
        ])
        
        return medications_text, schedule_html
    except Exception as e:
        return f"Error processing medications: {str(e)}", None

def format_schedule_html(schedule):
    """Format the medication schedule as HTML for the UI."""
    html = "<div style='text-align: left;'>"
    
    if "morningSchedule" in schedule and schedule["morningSchedule"]:
        html += "<h3>Morning</h3><ul>"
        for med in schedule["morningSchedule"]:
            html += f"<li><b>{med['time']}</b>: {med['name']} {med['dosage']}"
            if "instructions" in med and med["instructions"]:
                html += f" <i>({med['instructions']})</i>"
            html += "</li>"
        html += "</ul>"
    
    if "afternoonSchedule" in schedule and schedule["afternoonSchedule"]:
        html += "<h3>Afternoon</h3><ul>"
        for med in schedule["afternoonSchedule"]:
            html += f"<li><b>{med['time']}</b>: {med['name']} {med['dosage']}"
            if "instructions" in med and med["instructions"]:
                html += f" <i>({med['instructions']})</i>"
            html += "</li>"
        html += "</ul>"
    
    if "eveningSchedule" in schedule and schedule["eveningSchedule"]:
        html += "<h3>Evening</h3><ul>"
        for med in schedule["eveningSchedule"]:
            html += f"<li><b>{med['time']}</b>: {med['name']} {med['dosage']}"
            if "instructions" in med and med["instructions"]:
                html += f" <i>({med['instructions']})</i>"
            html += "</li>"
        html += "</ul>"
    
    if "nightSchedule" in schedule and schedule["nightSchedule"]:
        html += "<h3>Night</h3><ul>"
        for med in schedule["nightSchedule"]:
            html += f"<li><b>{med['time']}</b>: {med['name']} {med['dosage']}"
            if "instructions" in med and med["instructions"]:
                html += f" <i>({med['instructions']})</i>"
            html += "</li>"
        html += "</ul>"
    
    html += "</div>"
    return html

def get_reminders(user_id):
    """Get upcoming medication reminders for a user."""
    if user_id is None or user_id not in active_users:
        return "Session expired. Please refresh the page."
    
    try:
        reminders = orchestrator.get_upcoming_reminders(user_id)
        
        if not reminders:
            return "No upcoming medication reminders."
        
        reminders_text = "Upcoming medications:\n\n"
        for reminder in reminders:
            reminders_text += f"• {reminder['time']}: {reminder['name']} ({reminder['dosage']})"
            if reminder.get("instructions"):
                reminders_text += f" - {reminder['instructions']}"
            reminders_text += "\n"
        
        return reminders_text
    except Exception as e:
        return f"Error getting reminders: {str(e)}"

def term_clicked(evt: gr.SelectData, terms_json, user_id):
    """Handle term selection from the highlighted terms."""
    if not terms_json or terms_json == "[]":
        return "Please select a term to explain."
    
    try:
        terms = json.loads(terms_json)
        selected_idx = evt.index
        
        if selected_idx < 0 or selected_idx >= len(terms):
            return "Invalid term selection."
        
        selected_term = terms[selected_idx]
        term = selected_term["term"]
        context = selected_term["context"]
        
        return explain_term(term, context, user_id)
    except Exception as e:
        return f"Error processing term selection: {str(e)}"

def extract_medications_from_summary(summary, user_id):
    """Extract medications from consultation summary."""
    if user_id is None or user_id not in active_users:
        return "Session expired. Please refresh the page."
    
    if not summary or summary.strip() == "":
        return "No consultation summary available. Process a consultation first."
    
    try:
        api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=api_key)
        
        system_prompt = """
        You are a medication extraction assistant. Extract all medications mentioned in the consultation summary.
        
        For each medication, include:
        - Name
        - Dosage
        - Frequency
        - Timing information (when available)
        
        Format each medication on a new line.
        Example:
        Metformin 500mg twice daily with meals
        Lisinopril 10mg once daily in the morning
        """
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract medications from this consultation summary: {summary}"}
            ]
        )
        
        medications = response.choices[0].message.content.strip()
        
        if not medications or medications.lower().startswith("no medication") or medications.lower() == "none":
            return "No medications found in the consultation summary."
        
        return medications
        
    except Exception as e:
        return f"Error extracting medications: {str(e)}"

with gr.Blocks(title="PatientPal", theme=gr.themes.Soft(primary_hue="teal")) as app:
    user_id = gr.State(None)
    terms_json = gr.State("[]")
    
    gr.Markdown("# PatientPal 👨‍⚕️")
    gr.Markdown("### Understanding Consultations & Managing Medications")
    
    with gr.Tabs():
        with gr.TabItem("Consultation Analysis"):
            gr.Markdown("### Upload a recording, image, or enter notes from your medical consultation")
            
            with gr.Row():
                with gr.Column(scale=1):
                    audio_input = gr.Audio(
                        label="Upload Audio Recording", 
                        type="filepath",
                        sources=["microphone","upload"],
                    )
                    
                    image_input = gr.Image(
                        label="Or Upload Image of Notes",
                        type="filepath",
                        sources=["upload", "webcam"]
                    )
                    
                with gr.Column(scale=2):
                    text_input = gr.Textbox(
                        label="Or paste/type consultation notes here",
                        placeholder="Enter the doctor's consultation notes or transcript here...",
                        lines=8
                    )
            
            gr.Markdown("*You can upload an audio recording of your consultation, take a photo of your consultation notes, or type them directly.*")
            process_btn = gr.Button("Process Consultation", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Summary")
                    summary_output = gr.Textbox(
                        label="Consultation Summary",
                        placeholder="The summary will appear here...",
                        lines=6,
                        interactive=False
                    )
                    
                    extract_meds_btn = gr.Button("Extract Medications to Management Tab", variant="secondary")
                    
                    gr.Markdown("### Transcription")
                    transcription_output = gr.Textbox(
                        label="Full Transcription",
                        placeholder="The transcription will appear here...",
                        lines=6,
                        interactive=False
                    )
                
                with gr.Column():
                    gr.Markdown("### Medical Terms")
                    terms_output = gr.HighlightedText(
                        label="Click on a term for explanation",
                        combine_adjacent=True,
                        show_legend=False
                    )
                    
                    gr.Markdown("### Explanation")
                    explanation_output = gr.Textbox(
                        label="Term Explanation",
                        placeholder="Click on a highlighted term to see an explanation...",
                        lines=8,
                        interactive=False
                    )
        
        with gr.TabItem("Medication Management"):
            gr.Markdown("### Enter your medication details")
            gr.Markdown("Enter each medication on a new line with details like name, dosage, frequency, and when to take it. You can also extract medications automatically from your consultation summary.")
            
            medication_input = gr.Textbox(
                label="Medication Details",
                placeholder="Example:\nMetformin 500mg twice daily with meals\nLisinopril 10mg once daily in the morning",
                lines=6
            )
            
            process_med_btn = gr.Button("Generate Schedule", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    medications_output = gr.Textbox(
                        label="Processed Medications",
                        placeholder="Your processed medications will appear here...",
                        lines=6,
                        interactive=False
                    )
                
                with gr.Column():
                    schedule_output = gr.HTML(
                        label="Daily Schedule",
                        value="Your medication schedule will appear here..."
                    )
            
            gr.Markdown("### Reminders")
            reminders_btn = gr.Button("Check Upcoming Reminders")
            reminders_output = gr.Textbox(
                label="Upcoming Medications",
                placeholder="Your upcoming medication reminders will appear here...",
                lines=4,
                interactive=False
            )
    
    process_btn.click(
        fn=process_consultation,
        inputs=[audio_input, text_input, image_input, user_id],
        outputs=[summary_output, transcription_output, terms_json, user_id]
    ).then(
        fn=lambda terms: [(term["term"], term["term"]) for term in json.loads(terms)],
        inputs=[terms_json],
        outputs=[terms_output]
    )
    
    terms_output.select(
        fn=term_clicked,
        inputs=[terms_json, user_id],
        outputs=[explanation_output]
    )
    
    process_med_btn.click(
        fn=process_medications,
        inputs=[medication_input, user_id],
        outputs=[medications_output, schedule_output]
    )
    
    reminders_btn.click(
        fn=get_reminders,
        inputs=[user_id],
        outputs=[reminders_output]
    )
    
    extract_meds_btn.click(
        fn=extract_medications_from_summary,
        inputs=[summary_output, user_id],
        outputs=[medication_input]
    )
    
# Launch the app
if __name__ == "__main__":
    app.launch(share=True)
