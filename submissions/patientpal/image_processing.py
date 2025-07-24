import os
import tempfile
import base64
from pathlib import Path
from groq import Groq

class ImageProcessingService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = Groq(api_key=api_key)
        self.model_name = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    def extract_text(self, image_file):
        if isinstance(image_file, str):
            tmp_path = image_file
            need_cleanup = False
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(image_file.read())
                tmp_path = tmp_file.name
            need_cleanup = True
        
        try:
            with open(tmp_path, "rb") as image_file_content:
                image_data = image_file_content.read()
                
            encoded_image = base64.b64encode(image_data).decode("utf-8")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a medical OCR service. Extract text content from the image of medical consultation notes. Format it cleanly with proper line breaks for different sections."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Extract all text from this medical consultation note image:"},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }}
                    ]}
                ],
            )
            
            extracted_text = response.choices[0].message.content
            
            return extracted_text
        
        finally:
            if need_cleanup:
                os.unlink(tmp_path)
