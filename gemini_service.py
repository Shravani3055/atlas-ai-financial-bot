import os
import google.generativeai as genai
from prompt import SYSTEM_PROMPT

# ✅ Load API key safely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY is missing!")
else:
    print("✅ Gemini key loaded")

genai.configure(api_key=GEMINI_API_KEY)

# ✅ Initialize model
model = genai.GenerativeModel("gemini-1.5-flash")


def ask_gemini(user_message):
    try:
        if not GEMINI_API_KEY:
            return "⚠️ Gemini API key not configured."

        full_prompt = f"{SYSTEM_PROMPT}\nUser: {user_message}"

        print("📤 Sending to Gemini...")

        response = model.generate_content(full_prompt)

        # 🔴 HARD CHECK
        if not response:
            print("❌ Empty response object")
            return "⚠️ No response from AI"

        # Some responses come differently
        text = getattr(response, "text", None)

        if not text:
            print("❌ No text in response:", response)
            return "⚠️ AI returned empty response"

        clean_text = text.strip()

        print("📥 Gemini reply:", clean_text[:100])  # preview

        return clean_text

    except Exception as e:
        import traceback
        print("❌ GEMINI ERROR:", str(e))
        traceback.print_exc()
        return "⚠️ Gemini error occurred"
    
def ask_gemini(user_message):
    return "💡 Tip: Track your expenses, set a budget, and avoid unnecessary spending to save money."