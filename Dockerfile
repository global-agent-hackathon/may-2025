# Use the official Python image as the base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Command to run the application
CMD ["python", "prototype_agent.py"] 