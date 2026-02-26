import os
from google import genai

# Create client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_ai_response(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"AI error: {e}"
