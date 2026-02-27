import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000

# 🔥 Use SMALL or MEDIUM for better pronunciation
model = WhisperModel(
    "tiny.en",          # upgrade from base
    device="cpu",
    compute_type="int8"
)

def record(seconds=4):
    print(f"🎤 Recording {seconds}s...")
    try:
        audio = sd.rec(
            int(seconds * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocking=True
        )
        return audio.flatten()
    except Exception as e:
        print(f"❌ Audio error: {e}")
        return np.zeros(int(seconds * SAMPLE_RATE), dtype="float32")

def listen_whisper(seconds=4):
    audio = record(seconds)
    
    if np.max(np.abs(audio)) < 0.01:
        return ""

    segments, info = model.transcribe(
        audio,
        language="en",   # ✅ FORCE language
        beam_size=5,
        vad_filter=True,  # ✅ remove silence
        initial_prompt=(
            "This is a voice command for an assistant named Trait Buddy. "
            "Commands include mark present, mark absent, attendance, student names, "
            "trait center info, guest welcome note, and ongoing projects."
        )
    )

    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text
