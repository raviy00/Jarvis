# ===================================================
# Jarvis AI Assistant - Docker Container
# Compatible with Oracle Cloud Free Tier (ARM64/AMD64)
# ===================================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
# - ffmpeg: for audio processing (Whisper)
# - portaudio: for PyAudio
# - espeak: fallback TTS
# - libsndfile: audio file handling
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1 \
    espeak \
    gcc \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
# torch CPU-only to save space on Oracle Cloud
RUN pip install --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Expose web dashboard port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000 || exit 1

# Run Jarvis
CMD ["python", "main.py"]
