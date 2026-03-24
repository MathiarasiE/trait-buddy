import requests
import os

# 🔑 Add your Sarvam API Key here
SARVAM_API_KEY = "sk_gvxrfi85_xJ13r6NhY039asvqx2pOlpYd"

def speak(text):
    print("🗣️ TRAIT Buddy:", text)

    url = "https://api.sarvam.ai/text-to-speech"

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "voice": "female",
        "language": "en-IN"
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            with open("output.mp3", "wb") as f:
                f.write(response.content)

            os.system("mpg123 output.mp3")

        else:
            print("❌ Sarvam error:", response.text)

    except Exception as e:
        print(f"❌ Speech error: {e}")