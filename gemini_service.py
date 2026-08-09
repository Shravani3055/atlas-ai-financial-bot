import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash-latest")

def ask_gemini(user_message):
    try:
        response = model.generate_content(user_message)

        if response and response.text:
            return response.text

        return "⚠️ No response from AI"

    except Exception as e:
        print("Gemini Error:", e)
        return "⚠️ AI failed"