import os
from pathlib import Path
import tempfile
from groq import Groq

class TranscriptionService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = Groq(api_key=api_key)
        
    def transcribe(self, audio_file):
        if isinstance(audio_file, str):
            # If it's already a path (from Gradio), use it directly
            tmp_path = audio_file
            need_cleanup = False
        else:
            # If it's a file-like object, read and save it
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_path = tmp_file.name
            need_cleanup = True
        
        try:
            # Use Groq's Whisper API for transcription
            with open(tmp_path, "rb") as audio_file_obj:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file_obj,
                    model="whisper-large-v3",
                    prompt="This is a medical consultation recording. Please transcribe accurately including medical terminology.",
                    response_format="text",
                    language="en",
                    temperature=0.0
                )
            
            return transcription
        
        finally:
            if need_cleanup:
                os.unlink(tmp_path)
