import os
import google.generativeai as genai
import traceback

# ✅ Load API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found")
else:
    print("✅ Gemini key loaded")

genai.configure(api_key=api_key)

# ✅ Use stable model
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def ask_gemini(user_message):
    try:
        print("📤 Sending to Gemini...")

        response = model.generate_content(user_message)

        print("📥 Raw response:", response)

        # ✅ SAFE extraction
        if hasattr(response, "text") and response.text:
            return response.text

        # fallback
        return "⚠️ No response from AI"

    except Exception as e:
        print("❌ Gemini ERROR:")
        traceback.print_exc()

        return "⚠️ AI failed (check logs)"