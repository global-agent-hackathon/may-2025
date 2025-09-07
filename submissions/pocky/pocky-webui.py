from flask import Flask, render_template, request, jsonify
import os
import re
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_poc', methods=['POST'])
def get_poc():
    cve_id = request.json.get('cve_id', '')
    
    # Validate CVE ID format
    if not re.match(r'^CVE-\d{4}-\d{4,}$', cve_id, re.IGNORECASE):
        return jsonify({'error': 'Invalid CVE ID format, please use CVE-YYYY-NNNNN format'}), 400
    
    # Normalize CVE ID format
    cve_id = cve_id.upper()
    
    # Check if file exists
    file_path = os.path.join('results', f"{cve_id}_PoC.txt")
    
    if not os.path.exists(file_path):
        subprocess.run(f"python pocky.py {cve_id}", shell=True)
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500

if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000) 