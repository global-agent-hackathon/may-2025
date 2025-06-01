
.PHONY: install update run clean

install:
	@echo "Installing frontend Node.js dependencies..."
	npm install

update:
	@echo "Updating frontend Node.js dependencies..."
	npm update

run:
	@echo "Starting frontend development server..."
	@echo "Access the frontend (usually at http://localhost:5173 or similar)."
	@echo "Press Ctrl+C to stop the frontend."
	npm run dev

clean:
	@echo "Cleaning frontend Node.js modules and .env file..."
	rm -rf node_modules
	rm -f .env