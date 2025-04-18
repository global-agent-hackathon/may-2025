# VibeProto Startup Script for Windows

# Activate Python virtual environment
Write-Host "Activating Python virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

# Start Flask backend (in a separate process)
Write-Host "Starting Flask backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\python.exe backend/app.py"

# Start Node.js server
Write-Host "Starting Node.js server..." -ForegroundColor Green
npm start 