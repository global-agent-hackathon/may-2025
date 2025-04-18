import os
import json
import time
import openai
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

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
    # Define the enhancement instructions
    # Tailor these instructions for better results
    enhancement_system_prompt = """
You are an expert UI/UX designer and software architect. 
Your task is to take a basic user prompt for a web application and enhance it with specific, modern UI/UX details and functionality specifications.
Focus on creating a clean, user-friendly interface.
The enhanced prompt should guide an AI code generator to produce a high-quality prototype.

Include these details where appropriate:
- **Layout:** Use a centered container (e.g., max-width 800px, margin auto) on a light gray background.
- **Main Content Area:** White background with a subtle box-shadow.
- **Responsiveness:** Ensure the layout adapts reasonably to different screen sizes (mention flexbox or grid).
- **Interactivity:** 
    - Buttons: Specify clear actions (e.g., 'Add Task', 'Submit'). Use a specific color like green (e.g., #4CAF50) with a slightly darker hover effect.
    - Input Fields: Clear placeholders, perhaps with labels above.
    - Lists/Items: Consider animations for adding/deleting items (e.g., subtle fade-in/out).
- **Functionality:** Break down the core features mentioned in the basic prompt into specific steps or components. For a to-do list, specify adding tasks, marking tasks as complete (with visual feedback like strikethrough), and deleting tasks.
- **Structure:** Output *only* the enhanced prompt text, suitable for direct use in another AI model. Do not add explanations or conversational text around it.
"""
    
    enhancement_user_prompt = f"Enhance this basic web app prompt: '{basic_prompt}'"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini", # Use a cost-effective but capable model
            messages=[
                {"role": "system", "content": enhancement_system_prompt},
                {"role": "user", "content": enhancement_user_prompt}
            ],
            temperature=0.5, # Lower temperature for more focused enhancement
            max_tokens=500  # Limit token usage
        )
        enhanced_prompt_text = response.choices[0].message.content.strip()
        return enhanced_prompt_text
    except Exception as e:
        print(f"Error during prompt enhancement: {e}", file=sys.stderr)
        return basic_prompt # Return original prompt on error

def generate_prototype(prompt, prototype_type):
    """
    Generate a prototype based on the user's prompt and selected type.
    
    Args:
        prompt (str): The user's natural language prompt
        prototype_type (str): The type of prototype to generate (script, webapp, utility)
        
    Returns:
        dict: A dictionary containing the generated code and metadata
    """
    # Create a timestamp for unique file naming
    timestamp = int(time.time())
    
    # Prepare the system prompt based on prototype type
    system_prompts = {
        "script": "You are an expert automation script creator. Generate a complete Python script that can be run immediately.",
        "webapp": "You are an expert web app developer. Generate a complete web application with HTML, CSS, and JavaScript.",
        "utility": "You are an expert utility developer. Generate a complete command-line utility in Python."
    }
    
    system_prompt = system_prompts.get(prototype_type, system_prompts["script"])
    
    # Add context to the user prompt
    enhanced_prompt = f"""
    Create a {prototype_type} based on this description: {prompt}
    
    For a script, include all necessary imports and make it runnable with clear documentation.
    For a web app, create HTML, CSS, and JavaScript files with a modern, responsive design.
    For a utility, create a command-line tool with proper argument parsing and error handling.
    
    Provide the complete code files needed for the prototype to work.
    """
    
    # Generate the prototype using OpenAI
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": enhanced_prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    
    # Extract code from the response
    generated_code = response.choices[0].message.content
    
    # Generate a simple analysis
    analysis = "Code generated successfully. Review the code and test it thoroughly before deployment."
    
    # Save the generated code to a file
    output_path = save_prototype(generated_code, prototype_type, timestamp)
    
    return {
        "success": True,
        "prototype_type": prototype_type,
        "file_path": str(output_path),
        "code": generated_code,
        "analysis": analysis,
        "timestamp": timestamp
    }

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