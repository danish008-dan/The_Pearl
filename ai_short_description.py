import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_short_description(food_name: str) -> str:
    """
    PURPOSE:
    Generate a short (5–7 words) food description using Gemini
    Works for ANY food item
    NO database
    """

    if not food_name:
        return "Freshly prepared delicious dish"

    prompt = f"""
    You are a restaurant menu writer.

    Write ONLY a short description (5 to 7 words).
    No punctuation.
    No emojis.
    No quotes.

    Food item: {food_name}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        # SAFE text extraction
        text = response.candidates[0].content.parts[0].text.strip()

        # If Gemini gives something weird
        if len(text.split()) < 3:
            return f"Tasty {food_name} dish"

        return text

    except Exception as e:
        print("Gemini short description error:", e)
        return f"Tasty {food_name} dish"
