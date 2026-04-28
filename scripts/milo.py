from fastapi import FastAPI
from pydantic import BaseModel
from pydub import AudioSegment
from typing import List, Dict, Any

app = FastAPI()

class MixRequest(BaseModel):
    json_diarizacion: List[Dict[str, Any]]
    rutas_wav: List[str]
    output_path: str

@app.post("/mix")
def mix_audio(req: MixRequest):
    mix_final = AudioSegment.silent(duration=0)
    cursor_ms = 0

    for i, (seg_info, wav_path) in enumerate(zip(req.json_diarizacion, req.rutas_wav)):
        audio_tts = AudioSegment.from_wav(wav_path)
        
        if i == 0:
            pos_insercion = 0
        else:
            prev_seg = req.json_diarizacion[i-1]
            diff_ms = (seg_info["start"] - prev_seg["end"]) * 1000
            pos_insercion = max(0, int(cursor_ms + diff_ms))

        mix_final = mix_final.overlay(audio_tts, position=pos_insercion)
        cursor_ms = pos_insercion + len(audio_tts)

    mix_final.export(req.output_path, format="mp3")
    return {"final_path": req.output_path}
