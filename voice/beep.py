import numpy as np
import sounddevice as sd

def beep(duration=0.15, freq=900, sample_rate=16000):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * 2 * np.pi * t) * 0.2
    sd.play(tone, sample_rate)
    sd.wait()
