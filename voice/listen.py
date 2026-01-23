import queue
import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = "voice/model/vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

q = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print(status)
    q.put(bytes(indata))

def listen(timeout_seconds=8):
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    print("🎤 Speak now...")

    start_time = time.time()

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):
        while True:
            # timeout check
            if time.time() - start_time > timeout_seconds:
                return ""

            try:
                data = q.get(timeout=0.5)
            except queue.Empty:
                continue

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    return text
