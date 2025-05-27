FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app
ENV PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend /app/backend
COPY .env /app/.env

# Create directories for model weights and cache
RUN mkdir -p /app/models /app/cache

# Set up RunPod handler
COPY backend/runpod_handler.py /app/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the RunPod handler
CMD ["python3", "runpod_handler.py"] 