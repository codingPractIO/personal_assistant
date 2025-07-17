# Use Python base image
FROM python:3.10.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies needed for OpenCV
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 libzbar0 libzbar-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Default command
CMD ["python3", "bot_main.py"]
