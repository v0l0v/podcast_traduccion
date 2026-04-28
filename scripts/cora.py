from fastapi import FastAPI
from pydantic import BaseModel
import whisperx

app = FastAPI()
device = "cuda"

# Carga de modelo Whisper (Transcripción)
model = whisperx.load_model("large-v3", device, compute_type="float16")

# Carga de modelo Pyannote (Diarización) apuntando al YAML local
LOCAL_DIARIZE_CONFIG = "/models/pyannote/diarization/config.yaml"
diarize_model = whisperx.DiarizationPipeline(model_name=LOCAL_DIARIZE_CONFIG, device=device)

class AudioRequest(BaseModel):
    file_path: str

@app.post("/diarize")
def diarize_audio(req: AudioRequest):
    audio = whisperx.load_audio(req.file_path)
    result = model.transcribe(audio, batch_size=8)
    
    # Ejecución offline
    diarize_segments = diarize_model(audio)
    result_assigned = whisperx.assign_word_speakers(diarize_segments, result)
    
    output = [{"speaker": s["speaker"], "start": s["start"], "end": s["end"], "text": s["text"]} 
              for s in result_assigned["segments"] if "speaker" in s]
    
    return output
