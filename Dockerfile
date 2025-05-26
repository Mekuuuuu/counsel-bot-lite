FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies (only if needed for your backend)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code and .env file
COPY backend /app/backend
COPY .env /app/.env

# (Optional) Create a directory for model weights if your app downloads models at runtime
RUN mkdir -p /app/models

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "backend.api.inference:app", "--host", "0.0.0.0", "--port", "8000"] 