import os
import json
import time
from openai import OpenAI
import argparse
import sys  # Add sys import
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    timeout=60.0  # Increase timeout to avoid connection issues
)

# Set up paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROTOTYPES_DIR = BASE_DIR / 'prototypes'

# Ensure prototypes directory exists
PROTOTYPES_DIR.mkdir(exist_ok=True)

# --- Add Prompt Enhancement Function ---
def enhance_prompt(basic_prompt):
    """
    Enhances a basic prompt with detailed UI/UX and functionality specs using GPT.
    """
    if not basic_prompt or not basic_prompt.strip():
        raise ValueError("Empty prompt provided")

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert UI/UX designer and software architect. Enhance the given prompt with detailed specifications."
                },
                {
                    "role": "user",
                    "content": f"Enhance this basic web app prompt with UI/UX details: {basic_prompt}"
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        if not completion.choices:
            raise ValueError("No response received from OpenAI")
            
        enhanced_prompt = completion.choices[0].message.content
        if not enhanced_prompt or not enhanced_prompt.strip():
            raise ValueError("Empty response from OpenAI")
            
        return enhanced_prompt.strip()
        
    except Exception as e:
        error_msg = f"Error during prompt enhancement: {str(e)}"
        print(error_msg, file=sys.stderr)
        raise RuntimeError(error_msg)

def generate_prototype(prompt, prototype_type):
    """
    Generate a prototype based on the user's prompt and selected type.
    
    Args:
        prompt (str): The user's natural language prompt
        prototype_type (str): The type of prototype to generate (script, webapp, utility)
        
    Returns:
        dict: A dictionary containing the generated code and metadata
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert {prototype_type} developer. Generate complete, runnable code."
                },
                {
                    "role": "user",
                    "content": f"Create a {prototype_type} that does: {prompt}"
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        if not completion.choices:
            raise ValueError("No response received from OpenAI")
            
        generated_code = completion.choices[0].message.content
        if not generated_code or not generated_code.strip():
            raise ValueError("Empty response from OpenAI")
            
        timestamp = int(time.time())
        output_path = save_prototype(generated_code.strip(), prototype_type, timestamp)
        
        return {
            "success": True,
            "code": generated_code.strip(),
            "file_path": str(output_path),
            "timestamp": timestamp
        }
        
    except Exception as e:
        error_msg = f"Error generating prototype: {str(e)}"
        print(error_msg, file=sys.stderr)
        raise RuntimeError(error_msg)

def save_prototype(code, prototype_type, timestamp):
    """
    Save the generated prototype to a file.
    
    Args:
        code (str): The generated code
        prototype_type (str): The type of prototype
        timestamp (int): Timestamp for unique naming
        
    Returns:
        Path: The path to the saved file
    """
    # Determine file extension and directory based on prototype type
    extensions = {
        "script": ".py",
        "webapp": "",
        "utility": ".py"
    }
    
    ext = extensions.get(prototype_type, ".py")
    
    if prototype_type == "webapp":
        # For web apps, create a directory with multiple files
        prototype_dir = PROTOTYPES_DIR / f"webapp_{timestamp}"
        prototype_dir.mkdir(exist_ok=True)
        
        # Parse the code to extract HTML, CSS, and JS content
        # This is a simplified implementation; in real use, you'd need more robust parsing
        code_parts = code.split("```")
        
        for part in code_parts:
            if part.startswith("html") or part.startswith("HTML"):
                html_content = part.replace("html", "", 1).strip()
                with open(prototype_dir / "index.html", "w") as f:
                    f.write(html_content)
            
            elif part.startswith("css") or part.startswith("CSS"):
                css_content = part.replace("css", "", 1).strip()
                with open(prototype_dir / "style.css", "w") as f:
                    f.write(css_content)
            
            elif part.startswith("javascript") or part.startswith("js") or part.startswith("JavaScript"):
                js_content = part.replace("javascript", "", 1).replace("js", "", 1).replace("JavaScript", "", 1).strip()
                with open(prototype_dir / "script.js", "w") as f:
                    f.write(js_content)
        
        output_path = prototype_dir
    else:
        # For scripts and utilities, create a single file
        output_file = PROTOTYPES_DIR / f"{prototype_type}_{timestamp}{ext}"
        
        with open(output_file, "w") as f:
            f.write(code)
        
        output_path = output_file
    
    return output_path

if __name__ == "__main__":
    # Use argparse for better argument handling
    parser = argparse.ArgumentParser(description='Generate or enhance prototypes.')
    
    # Option 1: Enhance a prompt
    parser.add_argument('--enhance', type=str, help='Basic prompt to enhance.')
    
    # Option 2: Generate a prototype (original functionality)
    parser.add_argument('--generate', nargs=2, metavar=('PROMPT', 'TYPE'), help='Generate a prototype with a prompt and type (script, webapp, utility).')

    args = parser.parse_args()

    if args.enhance:
        # --- Handle Enhancement ---
        basic_prompt = args.enhance
        enhanced_result = enhance_prompt(basic_prompt)
        # IMPORTANT: Print *only* the result to stdout for the API
        print(enhanced_result) 
        
    elif args.generate:
        # --- Handle Generation ---
        prompt, prototype_type = args.generate
        
        # Validate prototype type
        allowed_types = ["script", "webapp", "utility"]
        if prototype_type not in allowed_types:
             # Print error as JSON to stderr to avoid polluting stdout
            print(json.dumps({"error": f"Invalid prototype type '{prototype_type}'. Allowed types: {', '.join(allowed_types)}"}), file=sys.stderr)
            sys.exit(1)
            
        try:
            result = generate_prototype(prompt, prototype_type)
            # Print result as JSON to stdout
            print(json.dumps(result))
        except Exception as e:
             # Print error as JSON to stderr
            print(json.dumps({"error": f"Error generating prototype: {str(e)}"}), file=sys.stderr)
            sys.exit(1)
            
    else:
        # No valid arguments provided
        parser.print_help(file=sys.stderr)
        sys.exit(1)

# Remove old sys.argv handling:
# if len(sys.argv) < 3:
#     print(json.dumps({"error": "Missing arguments. Usage: python generate.py 'prompt' 'type'"}))
#     sys.exit(1)
# 
# prompt = sys.argv[1]
# prototype_type = sys.argv[2]
# 
# result = generate_prototype(prompt, prototype_type)
# print(json.dumps(result)) 