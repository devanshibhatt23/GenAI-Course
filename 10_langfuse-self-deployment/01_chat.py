import os
from dotenv import load_dotenv
from langfuse.openai import OpenAI
from datetime import datetime

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

SYSTEM_PROMPT = f"""
you are a helpful AI assistant
today's date = {datetime.now()}
"""

response = client.chat.completions.create(
    model="gemini-3-flash-preview",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "what is the date and time right now?"},
    ]
)

print(response.choices[0].message.content)