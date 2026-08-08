from google import genai
from google.genai import types
import time

from config import GEMINI_API_KEY
from prompt import SYSTEM_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(user_message):
    
    start = time.time()
    
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            
        ),
    )
    end = time.time()
    print(f"Gemini API took: {end - start:.2f} seconds")

    return response.text