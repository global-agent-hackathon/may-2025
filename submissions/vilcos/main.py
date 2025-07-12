from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path # Import Path

app = FastAPI()

# Get the directory of the current file (main.py)
current_file_dir = Path(__file__).parent

# Serve static files from the 'dist' directory (output of 'npm run build')
# This assumes 'dist' is at the same level as main.py (i.e., vilcos/dist)
dist_dir = current_file_dir / "dist"

app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static_dist_files")

# If you want to run this directly using Python (though uvicorn command is more common for development):
if __name__ == "__main__":
    # Run from the 'vilcos' directory as: python main.py
    # Or, more typically: uvicorn main:app --reload --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000) 