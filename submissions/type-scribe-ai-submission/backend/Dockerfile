# Use a slim Buster-based Python image as the base
FROM python:alpine


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Prevents pip from storing cache, reducing image size
# -r requirements.txt: Installs all packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the /app/app directory in the container
# This assumes your main FastAPI application entry point is in 'app/main.py'
COPY ./app /app/app

# Expose the port on which the FastAPI application will listen
# Google Cloud Run expects the application to listen on 8080 by default,
# but 8000 is also common and can be configured. We'll stick to 8000.
EXPOSE 8000

# Command to run the application 

CMD [ "fastapi","run","app/main.py","--port","8000" ]