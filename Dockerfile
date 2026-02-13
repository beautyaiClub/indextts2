# RunPod Serverless Dockerfile for IndexTTS2
FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    sox \
    libsox-dev \
    git-lfs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for TTS and RunPod serverless
RUN pip install --no-cache-dir \
    runpod \
    librosa \
    soundfile \
    pydub \
    scipy \
    requests \
    huggingface_hub

# Set working directory
WORKDIR /app

# Clone IndexTTS2 repository
RUN git clone https://github.com/index-tts/index-tts.git /app/index-tts && \
    cd /app/index-tts && \
    pip install --no-cache-dir -r requirements.txt || true

# Download IndexTTS2 models from Hugging Face
RUN mkdir -p /app/models && \
    huggingface-cli download IndexTeam/IndexTTS-2 \
    --local-dir /app/models \
    --local-dir-use-symlinks False

# Alternative: Download specific model files only (uncomment if needed)
# RUN mkdir -p /app/models && \
#     huggingface-cli download IndexTeam/IndexTTS-2 gpt.pth --local-dir /app/models && \
#     huggingface-cli download IndexTeam/IndexTTS-2 s2mel.pth --local-dir /app/models && \
#     huggingface-cli download IndexTeam/IndexTTS-2 config.yaml --local-dir /app/models && \
#     huggingface-cli download IndexTeam/IndexTTS-2 bigvgan_discriminator.pth --local-dir /app/models

# Set model path environment variable
ENV MODEL_PATH=/app/models

# Copy handler
COPY handler.py /app/handler.py

# Expose RunPod serverless port
EXPOSE 8000

# Start RunPod handler
CMD ["python", "-u", "handler.py"]
