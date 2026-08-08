import os
import google.generativeai as genai
from prompt import SYSTEM_PROMPT

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(user_message):
    try:
        full_prompt = SYSTEM_PROMPT + "\nUser: " + user_message

        response = model.generate_content(full_prompt)

        if not response or not response.text:
            return "⚠️ No response from AI"

        return response.text

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "⚠️ Gemini error occurred"