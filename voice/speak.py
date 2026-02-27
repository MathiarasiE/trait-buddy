import pyttsx3

try:
    engine = pyttsx3.init(driverName='espeak')
except:
    engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    print("🗣️ TRAIT Buddy:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"❌ Speech error: {e}")
