# Production Dockerfile for Live Cloud Deployment (Render / Railway / Docker)
FROM python:3.11-slim

# Install Tesseract OCR Engine and OpenCV dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Set default port
ENV PORT=5000
EXPOSE 5000

# Start production WSGI server with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "backend.app:app"]
