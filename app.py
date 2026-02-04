from flask import Flask, request
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_message():
    print("="*50)
    print("🔔 WEBHOOK POST REQUEST RECEIVED!")
    print("="*50)
    data = request.get_json()
    print("INCOMING DATA:", data)
    print("="*50)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        # ❌ Ignore non-message events (status, etc.)
        if "messages" not in value:
            return "EVENT_RECEIVED", 200

        message = value["messages"][0]

        # ❌ Ignore non-text messages for now
        if "text" not in message:
            return "EVENT_RECEIVED", 200

        text = message["text"]["body"]
        sender = message["from"]

        print("FROM:", sender)
        print("TEXT:", text)

        reply = handle_traitbuddy(text)
        send_message(sender, reply)

    except Exception as e:
        print("ERROR:", e)

    return "EVENT_RECEIVED", 200



def send_message(to, text):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }

    response = requests.post(url, json=payload, headers=headers)
    print("SEND STATUS:", response.status_code, response.text)


def handle_traitbuddy(text):
    text = text.lower()

    if "hi" in text or "hello" in text:
        return "👋 Hi! I am TRAIT Buddy. How can I help you today?"

    if "attendance" in text:
        return "📊 Attendance system is active."

    return "🤖 I’m TRAIT Buddy. Try typing *attendance* or *help*."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
