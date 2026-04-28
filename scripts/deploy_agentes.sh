#!/bin/bash

# ==========================================
# Despliegue de Agentes de Audio (ROCm + CPU)
# ==========================================

# Variables de entorno con rutas absolutas
DIR_SCRIPTS="/home/operador_ia/proyectos/podcast_traduccion/scripts"
DIR_AUDIO="/home/operador_ia/proyectos/podcast_traduccion/audio"
DIR_MODELOS="/home/operador_ia/proyectos/podcast_traduccion/modelos"

echo "Inicializando infraestructura Docker..."

# Generación de la estructura de subdirectorios en el host
mkdir -p "$DIR_AUDIO"/{in,refs,temp,out}

# 1. Red de resolución DNS interna
docker network inspect podcast_net >/dev/null 2>&1 || docker network create podcast_net

# 2. Despliegue Agente Cora (Transcripción - GPU)
docker run -d --name cora_whisperx --network podcast_net \
  --device=/dev/kfd --device=/dev/dri --group-add video --shm-size 8G \
  -p 8001:8000 \
  -v "$DIR_SCRIPTS:/app" -v "$DIR_AUDIO:/audio" -v "$DIR_MODELOS:/models" \
  rocm/pytorch:latest \
  bash -c "pip install fastapi uvicorn whisperx pydantic && cd /app && uvicorn cora:app --host 0.0.0.0 --port 8000"

# 3. Despliegue Agente Siro (TTS - GPU)
docker run -d --name siro_tts --network podcast_net \
  --device=/dev/kfd --device=/dev/dri --group-add video --shm-size 8G \
  -p 8002:8000 \
  -v "$DIR_SCRIPTS:/app" -v "$DIR_AUDIO:/audio" -v "$DIR_MODELOS:/models" \
  rocm/pytorch:latest \
  bash -c "pip install fastapi uvicorn TTS pydantic && cd /app && uvicorn siro:app --host 0.0.0.0 --port 8000"

# 4. Despliegue Agente Milo (Mezcla - CPU)
docker run -d --name milo_mixer --network podcast_net \
  -p 8003:8000 \
  -v "$DIR_SCRIPTS:/app" -v "$DIR_AUDIO:/audio" \
  python:3.10-slim \
  bash -c "apt-get update && apt-get install -y ffmpeg && pip install fastapi uvicorn pydub pydantic && cd /app && uvicorn milo:app --host 0.0.0.0 --port 8000"

echo "Despliegue finalizado. Contenedores en background."
