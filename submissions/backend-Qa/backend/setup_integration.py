import os
import subprocess
import sys
import shutil
import time

def run_command(command, cwd=None):
    """Run a command and return its output"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            text=True, 
            capture_output=True,
            cwd=cwd
        )
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return None

def setup_backend():
    """Set up the backend"""
    print("\n=== Setting up backend ===")
    
    # Install backend dependencies
    run_command("pip install -r requirements.txt")
    
    # Make sure the features directory exists
    os.makedirs("features", exist_ok=True)
    
    print("Backend setup complete!")

def setup_frontend():
    """Set up the gherkin-genai-dash-main frontend"""
    print("\n=== Setting up frontend ===")
    
    # Get the parent directory (project root)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(parent_dir, "gherkin-genai-dash-main")
    
    # Install frontend dependencies
    run_command("npm install", cwd=frontend_dir)
    
    print("Frontend setup complete!")

def start_services():
    """Start the backend and frontend services"""
    print("\n=== Starting services ===")
    
    # Start backend in a separate process
    backend_process = subprocess.Popen(
        "python main.py", 
        shell=True
    )
    
    print("Backend started!")
    
    # Wait for backend to initialize
    time.sleep(3)
    
    # Get the parent directory (project root)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(parent_dir, "gherkin-genai-dash-main")
    
    # Start frontend in a separate process
    frontend_process = subprocess.Popen(
        "npm run dev", 
        shell=True, 
        cwd=frontend_dir
    )
    
    print("Frontend started!")
    
    print("\n=== Integration complete! ===")
    print("Backend running at: http://localhost:8000")
    print("Frontend running at: http://localhost:5173")
    print("\nPress Ctrl+C to stop both services")
    
    try:
        # Keep the script running to maintain the processes
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Services stopped!")

def main():
    """Main function to set up the integration"""
    print("=== Setting up QA Test Generation Integration ===")
    
    # Get the parent directory (project root)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if we're in the right directory structure
    if not os.path.exists(os.path.join(parent_dir, "gherkin-genai-dash-main")):
        print("Error: gherkin-genai-dash-main directory not found in the project root")
        print("Please make sure the directory structure is correct")
        return
    
    # Set up backend
    setup_backend()
    
    # Set up frontend
    setup_frontend()
    
    # Start services
    start_services()

if __name__ == "__main__":
    main()
