# Use Python 3.11 slim
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy our FastAPI app
COPY app/ ./app/

# Expose port 8000
EXPOSE 8000

# Launch UVicorn on startup
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
