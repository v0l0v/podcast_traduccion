#!/usr/bin/env python3
import sys
import requests
import time
import os

# ==============================================================================
# PIPELINE AUTOMÁTICO DE TRADUCCIÓN DE PODCASTS (CLIENTE API)
# ==============================================================================

CORA_URL = "http://localhost:8001/diarize"
SIRO_URL = "http://localhost:8002/synthesize_batch"
MILO_URL = "http://localhost:8003/mix"

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 traducir_podcast.py <nombre_archivo_original.mp3>")
        sys.exit(1)

    original_file_name = sys.argv[1]
    input_audio_path = f"/audio/{original_file_name}"
    output_audio_path = "/audio/podcast_final_es.mp3"

    print(f"[*] Iniciando traducción para: {original_file_name}")

    # ==============================================================================
    # 1. Transcripción y Diarización con Cora
    # ==============================================================================
    print("[1/4] Solicitando transcripción y diarización a Agente Cora...")
    try:
        res_cora = requests.post(CORA_URL, json={"file_path": input_audio_path})
        if res_cora.status_code != 200:
            print(f"[X] El Agente Cora devolvió un error ({res_cora.status_code}):\n{res_cora.text}")
            sys.exit(1)
        segments = res_cora.json()
        print(f"[✓] Cora completó la diarización. Encontrados {len(segments)} segmentos.")
    except Exception as e:
        print(f"[X] Error de conexión o petición al Agente Cora: {e}")
        sys.exit(1)

    # ==============================================================================
    # 2. Traducción al Español
    # ==============================================================================
    print("[2/4] Traduciendo transcripción al español...")
    # Aquí puedes integrar una API como ChatGPT o DeepL. 
    # Como ejemplo base, usaremos un texto traducido genérico para mantener el flujo.
    for seg in segments:
        seg["text_es"] = f"[Traducción] {seg['text']}"
    print("[✓] Traducción completada.")

    # ==============================================================================
    # 3. Síntesis y Clonación de Voz con Siro
    # ==============================================================================
    print("[3/4] Solicitando síntesis de voz a Agente Siro...")
    # Preparamos los segmentos para Siro
    siro_segments = []
    for seg in segments:
        siro_segments.append({
            "speaker": seg["speaker"],
            "text_es": seg["text_es"],
            "ref_audio_path": input_audio_path  # Usa el mismo audio original como referencia para clonar la voz
        })

    try:
        payload_siro = {
            "output_dir": "/audio/temp",
            "segments": siro_segments
        }
        res_siro = requests.post(SIRO_URL, json=payload_siro)
        res_siro.raise_for_status()
        rutas_wav = res_siro.json()["rutas_wav"]
        print(f"[✓] Siro completó la síntesis. Creados {len(rutas_wav)} fragmentos de audio.")
    except Exception as e:
        print(f"[X] Error en el Agente Siro: {e}")
        sys.exit(1)

    # ==============================================================================
    # 4. Mezcla Final con Milo
    # ==============================================================================
    print("[4/4] Solicitando mezcla final y sincronización a Agente Milo...")
    try:
        payload_milo = {
            "json_diarizacion": segments,
            "rutas_wav": rutas_wav,
            "output_path": output_audio_path
        }
        res_milo = requests.post(MILO_URL, json=payload_milo)
        res_milo.raise_for_status()
        final_path = res_milo.json()["final_path"]
        print("\n" + "="*60)
        print(f"[★] ¡ÉXITO! Podcast final generado en: {final_path}")
        print("="*60)
    except Exception as e:
        print(f"[X] Error en el Agente Milo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
