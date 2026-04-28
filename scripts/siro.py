from fastapi import FastAPI
from pydantic import BaseModel
from TTS.api import TTS
from typing import List

app = FastAPI()
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")

class Segment(BaseModel):
    speaker: str
    text_es: str
    ref_audio_path: str  # Inyectado vía n8n (ej. "/audio/refs/SPEAKER_00.wav")

class TTSRequest(BaseModel):
    segments: List[Segment]
    output_dir: str      # Inyectado vía n8n (ej. "/audio/temp")

@app.post("/synthesize_batch")
def synthesize(req: TTSRequest):
    rutas_generadas = []
    
    for i, seg in enumerate(req.segments):
        out_path = f"{req.output_dir}/{i:04d}_{seg.speaker}.wav"
        
        tts.tts_to_file(
            text=seg.text_es, 
            speaker_wav=seg.ref_audio_path, # Ruta dinámica
            language="es", 
            file_path=out_path
        )
        rutas_generadas.append(out_path)
        
    return {"rutas_wav": rutas_generadas}
