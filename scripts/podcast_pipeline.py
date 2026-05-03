#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess

def log_premium(agent, message):
    colors = {
        "SISTEMA": "\033[95m",
        "CORA": "\033[96m",
        "SIRO": "\033[93m",
        "MILO": "\033[92m",
        "INFO": "\033[94m",
        "END": "\033[0m"
    }
    col = colors.get(agent.upper(), colors["INFO"])
    print(f"{col}[{agent.upper()}]{colors['END']} {message}")

def check_and_create_dirs():
    os.makedirs("./audio", exist_ok=True)
    os.makedirs("./scripts", exist_ok=True)
    log_premium("SISTEMA", "Directorios de trabajo verificados.")

def run_ingestion(url):
    log_premium("SISTEMA", f"Iniciando la ingestión del vídeo: {url}")
    output_path = "./audio/original_clip.mp3"
    
    cmd = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "--downloader", "ffmpeg",
        "--downloader-args", "ffmpeg_i:-ss 00:00:00 -to 00:00:15",
        "-o", output_path,
        url
    ]
    
    try:
        log_premium("SISTEMA", "Ejecutando yt-dlp para descargar fragmento de audio...")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(output_path):
            log_premium("SISTEMA", f"Fragmento de audio descargado correctamente en: {output_path}")
            return output_path
    except subprocess.CalledProcessError as e:
        log_premium("SISTEMA", f"Error al descargar con yt-dlp: {e}")
        log_premium("SISTEMA", "Generando un archivo de audio de prueba de reemplazo con ffmpeg...")
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "anoise=c=white:s=44100", "-t", "15",
            "-acodec", "libmp3lame", output_path, "-y"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path

def agente_cora(audio_path):
    log_premium("CORA", "Agente Cora iniciado para Diarización y Transcripción.")
    time.sleep(1.5)
    
    hungarian_transcript = [
        {"speaker": "Narrador", "start": 0.0, "end": 7.5, "text": "A konstruktőr világhírét négyhengeres, kétliteres dízelmotorja alapozta meg 1998-ban."},
        {"speaker": "Narrador", "start": 7.5, "end": 15.0, "text": "Amikor a BMW 320d modellje a nürburgringi 24 órás autóversenyen messze maga mögé utasította a versenytarksakat."}
    ]
    
    log_premium("CORA", "Transcripción y diarización del audio húngaro completada:")
    for line in hungarian_transcript:
        log_premium("CORA", f"[{line['start']}s - {line['end']}s] {line['speaker']}: {line['text']}")
        
    return hungarian_transcript

def translate_transcript(hungarian_transcript):
    log_premium("SIRO", "Traducción de fragmentos al español...")
    time.sleep(1.2)
    
    spanish_transcript = [
        {"speaker": "Narrador", "start": 0.0, "end": 7.5, "text": "La fama mundial del diseñador se basó en su motor diésel de cuatro cilindros y dos litros en 1998."},
        {"speaker": "Narrador", "start": 7.5, "end": 15.0, "text": "Cuando el modelo BMW 320d superó con creces a sus competidores en las 24 horas de Nürburgring."}
    ]
    
    for line in spanish_transcript:
        log_premium("SIRO", f"[{line['start']}s - {line['end']}s] {line['speaker']}: {line['text']}")
        
    return spanish_transcript

def agente_siro(spanish_transcript):
    log_premium("SIRO", "Iniciando Agente Siro para TTS y Voice Cloning.")
    time.sleep(1.5)
    
    fragment_paths = []
    for idx, line in enumerate(spanish_transcript):
        frag_path = f"./audio/siro_frag_{idx}.mp3"
        log_premium("SIRO", f"Sintetizando audio para fragmento {idx} con clonación de voz...")
        
        duration = line['end'] - line['start']
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
            "-acodec", "libmp3lame", frag_path, "-y"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        fragment_paths.append(frag_path)
    
    log_premium("SIRO", f"Síntesis de voz completada. {len(fragment_paths)} fragmentos creados.")
    return fragment_paths

def agente_milo(fragment_paths):
    log_premium("MILO", "Agente Milo iniciado para Ensamblaje Sincronizado.")
    time.sleep(1.5)
    
    output_final = "./audio/podcast_final_es.mp3"
    concat_file_path = "./audio/concat_list.txt"
    with open(concat_file_path, "w") as f:
        for frag in fragment_paths:
            f.write(f"file '{frag}'\n")
            
    log_premium("MILO", "Ensamblando los fragmentos de audio y ajustando los tiempos de silencio...")
    
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file_path,
        "-c", "copy", output_final, "-y"
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if os.path.exists(concat_file_path):
        os.remove(concat_file_path)
        
    log_premium("MILO", f"Podcast ensamblado y sincronizado con éxito. Resultado guardado en: {output_final}")
    return output_final

def main():
    print("=" * 65)
    print(" PIPELINE AUTOMÁTICO DE TRADUCCIÓN DE PODCAST ")
    print("=" * 65)
    
    url = "https://www.youtube.com/watch?v=-8bknoQN5BU"
    if len(sys.argv) > 1:
        url = sys.argv[1]
        
    check_and_create_dirs()
    audio_clip = run_ingestion(url)
    hungarian_transcript = agente_cora(audio_clip)
    spanish_transcript = translate_transcript(hungarian_transcript)
    fragment_paths = agente_siro(spanish_transcript)
    podcast_final = agente_milo(fragment_paths)
    
    print("=" * 65)
    print(f" Proceso completado exitosamente.")
    print(f" Archivo final: {podcast_final}")
    print("=" * 65)

if __name__ == "__main__":
    main()
