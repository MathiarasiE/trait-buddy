import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from scipy.signal import resample

# ===============================
# Audio Settings
# ===============================
INPUT_RATE = 48000
WHISPER_RATE = 16000

# ===============================
# Auto-detect Bluetooth mic
# ===============================
def get_bt_mic_index():
    devices = sd.query_devices()

    for i, dev in enumerate(devices):
        if "bluez" in dev["name"].lower() and dev["max_input_channels"] > 0:
            print(f"? Using Bluetooth mic: {dev['name']} (index {i})")
            return i

    print("?? Bluetooth mic not found, using default")
    return None


MIC_DEVICE = get_bt_mic_index()

# ===============================
# Load Whisper Model
# ===============================
model = WhisperModel(
    "tiny.en",
    device="cpu",
    compute_type="int8"
)

# ===============================
# Record Audio
# ===============================
def record(seconds=3):

    print(f"??? Recording {seconds}s...")

    try:
        audio = sd.rec(
            int(seconds * INPUT_RATE),
            samplerate=INPUT_RATE,
            channels=1,
            dtype="float32",
            device=MIC_DEVICE
        )

        sd.wait()

        audio = audio.flatten()

        # Convert 48k ? 16k
        num_samples = int(len(audio) * WHISPER_RATE / INPUT_RATE)
        audio = resample(audio, num_samples)

        return audio

    except Exception as e:
        print("Audio error:", e)
        return np.zeros(int(seconds * WHISPER_RATE), dtype="float32")

# ===============================
# Whisper transcription
# ===============================
def listen_whisper(seconds=3):

    audio = record(seconds)

    max_level = np.max(np.abs(audio))
    print("Max audio level:", max_level)

    # ignore silence
    if max_level < 0.002:
        return ""

    try:
        segments, _ = model.transcribe(
            audio,
            beam_size=5,
            vad_filter=True
        )

        text = "".join(seg.text for seg in segments)
        return text.strip()

    except Exception as e:
        print("Whisper error:", e)
        return ""
