import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import sys

# Add the project root to the path so we can import the prototype_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prototype_agent import save_session

# Import the generator module
from generate import generate_prototype, enhance_prompt

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    
    if not data or 'prompt' not in data or 'type' not in data:
        return jsonify({'error': 'Missing required fields: prompt and type'}), 400
    
    prompt = data['prompt']
    prototype_type = data['type']
    
    try:
        result = generate_prototype(prompt, prototype_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Missing required field: prompt'}), 400
    
    prompt = data['prompt']
    user_id = data.get('user_id', 'default_user')
    
    try:
        save_session(prompt, user_id)
        return jsonify({'success': True, 'message': 'Prompt saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.json
    
    if not data or 'prompt' not in data or 'type' not in data:
        return jsonify({'error': 'Missing required fields: prompt and type'}), 400
    
    prompt = data['prompt']
    prototype_type = data['type']
    
    try:
        # For now, just return a sample response
        if prototype_type == 'automation_script':
            code = """import requests
from pathlib import Path
import os
from datetime import datetime

def download_images(url, folder='images'):
    # Create folder if it doesn't exist
    Path(folder).mkdir(exist_ok=True)
    
    # Get images from website
    response = requests.get(url)
    # ... more image processing logic
    
    print(f"Images downloaded to {folder}")

if __name__ == "__main__":
    url = input("Enter website URL: ")
    download_images(url)"""
        else:
            code = """<!DOCTYPE html>
<html>
<head>
    <title>Simple Web App</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .gallery img { width: 100%; height: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Image Gallery</h1>
        <div class="gallery" id="gallery"></div>
    </div>
    <script>
        // JavaScript to populate gallery
        const gallery = document.getElementById('gallery');
        // ... more code to fetch and display images
    </script>
</body>
</html>"""
        
        return jsonify({'code': code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/enhance_prompt', methods=['POST'])
def enhance():
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Missing required field: prompt'}), 400
    
    prompt = data['prompt']
    
    try:
        enhanced_prompt = enhance_prompt(prompt)
        return jsonify({'enhanced_prompt': enhanced_prompt})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0') 