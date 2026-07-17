from dotenv import load_dotenv
import os

from google import genai

load_dotenv()

api = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key = api)

def ask_gemma(text):
    resp = client.models.generate_content(
        model = "gemma-4-26b-a4b-it",
        contents = text
    )

    return resp.text



