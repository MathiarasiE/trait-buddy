import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000

# 🔥 Use SMALL or MEDIUM for better pronunciation
model = WhisperModel(
    "small",          # upgrade from base
    device="cpu",
    compute_type="int8"
)

def record(seconds=4):
    print(f"🎤 Recording {seconds}s...")
    audio = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    return audio.flatten()

def listen_whisper(seconds=4):
    audio = record(seconds)

    segments, info = model.transcribe(
        audio,
        language="en",   # ✅ FORCE language
        beam_size=5,
        vad_filter=True,  # ✅ remove silence
        initial_prompt=(
            "This is a voice command for an assistant named Trait Buddy. "
            "Commands include mark present, mark absent, attendance, student names."
        )
    )

    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text
