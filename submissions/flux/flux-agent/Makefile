# Setup: create virtual environment and install dependencies
setup:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Setup complete! Activate with: source venv/bin/activate"

# Production: run the application
run:
	python3 -m src.main

# Development: auto-reload on code changes
run-dev:
	watchmedo auto-restart --patterns="*.py" --recursive -- python3 -m src.main

# Install dependencies
install:
	pip3 install -r requirements.txt

# Usage:
# make setup    - Create venv and install dependencies
# make run      - Run in production mode
# make run-dev  - Run in development mode with auto-reload
# make install  - Install dependencies 