# Use Python 3.12 slim image as the base
FROM python:3.12-slim

# Set  working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libgomp1 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy the requirements file
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml

# Install the requirements.txt
RUN uv sync

# Copy the app source code
COPY src /app/src

# Set PYTHONPATH environment variable to include /app/src and /app (project root)
ENV PYTHONPATH=/app/src:/app

# Port accessible
EXPOSE 8080

# Run code
CMD ["uv", "run", "uvicorn", "src.app:fastapi_app", "--host", "0.0.0.0", "--port", "8080"]
