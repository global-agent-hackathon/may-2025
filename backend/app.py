import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import the generator module
from generate import generate_prototype

# Load environment variables
load_dotenv()

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000) 