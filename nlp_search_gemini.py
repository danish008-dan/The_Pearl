import os
import json
from sys import api_version

from db import get_db_connection
from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(api_key=os.getenv(os.getenv("GEMINI_API_KEY")))

def ai_menu_search(user_query):
    # fetch menu
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, description, price, image FROM menu")
    menu = cursor.fetchall()
    cursor.close()
    conn.close()

    prompt = f"""
    You are a restaurant recommendation AI.

    User query: "{user_query}"

    Menu items: {menu}

    Select dishes matching user's intention.
    Consider:
    - spice level
    - veg / non-veg
    - dessert / sweet
    - keywords like 'ice cream', 'biryani', 'light food'

    Return ONLY valid JSON list of items:
    [
      {{"id": 1, "name": "...", "price": 200, "image": "..."}}
    ]

    If nothing matches return [] exactly.
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    text = response.candidates[0].content.parts[0].text

    try:
        return json.loads(text)
    except Exception:
        return []
