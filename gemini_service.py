import os
import google.generativeai as genai
from prompt import SYSTEM_PROMPT

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(user_message):
    full_prompt = SYSTEM_PROMPT + "\nUser: " + user_message
    
    response = model.generate_content(full_prompt)
    
    return response.text