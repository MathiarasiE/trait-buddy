import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000

# Load once (base is good for Tamil+English)
model = WhisperModel("base", device="cpu", compute_type="int8")

def record(seconds=4):
    print(f"🎤 Recording {seconds}s...")
    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    return audio.flatten()

def listen_whisper(seconds=4):
    audio = record(seconds)

    # multilingual: DON'T force language, let Whisper detect
    segments, info = model.transcribe(audio, beam_size=5)

    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text
