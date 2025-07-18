FROM agnohq/python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "openjourney_agent.authenticated_agent:app", "--host", "0.0.0.0", "--port", "8000"]

