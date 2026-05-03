# ==============================================================================
# Premium Multi-Purpose Dockerfile for Podcast Translation Pipeline (ROCm / AMD)
# ==============================================================================
# This Dockerfile optimizes deployments of Cora, Siro, and Milo agents on AMD
# Radeon GPUs using ROCm acceleration or on standard CPU-only configurations.
# ==============================================================================

FROM rocm/pytorch:latest

# Ensure unbuffered output and avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (ffmpeg, git, build essentials)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install shared Python core packages
RUN python3 -m pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.28.0 \
    pydantic==2.6.4 \
    pydub==0.25.1 \
    python-multipart==0.0.9

# Install Agent Cora dependencies (WhisperX)
RUN python3 -m pip install --no-cache-dir git+https://github.com/m-bain/whisperX.git

# Install Agent Siro dependencies (Coqui TTS)
RUN python3 -m pip install --no-cache-dir TTS

# Copy all source files to the container
COPY ./scripts /app
COPY ./audio /audio

# Expose FastAPI default port
EXPOSE 8000

# Set default agent to cora. It can be overridden at runtime:
# docker run -e AGENT=siro ...
ENV AGENT=cora

# Dynamic endpoint startup script
CMD if [ "$AGENT" = "cora" ]; then \
        echo "[SISTEMA] Iniciando Agente Cora (WhisperX Diarization & Transcription)..." && \
        uvicorn cora:app --host 0.0.0.0 --port 8000; \
    elif [ "$AGENT" = "siro" ]; then \
        echo "[SISTEMA] Iniciando Agente Siro (Coqui TTS Voice Cloning)..." && \
        uvicorn siro:app --host 0.0.0.0 --port 8000; \
    elif [ "$AGENT" = "milo" ]; then \
        echo "[SISTEMA] Iniciando Agente Milo (Mezclador Sincronizado de Audio)..." && \
        uvicorn milo:app --host 0.0.0.0 --port 8000; \
    else \
        echo "[ERROR] Variable de entorno AGENT no válida ('cora', 'siro' o 'milo')" && \
        exit 1; \
    fi
