import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    print("🗣️ TRAIT Buddy:", text)
    engine.say(text)
    engine.runAndWait()
