import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# print(os.getenv("GEMINI_API_KEY"))

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# stateless - no history or chats is stored
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        { "role": "user", "content": "Hey, my name is John Doe" },
        { "role": "assistant", "content": "Hi John! How may I assist you today?" },
        { "role": "user", "content": "What's my name?" },
    ]
)

print(response.choices[0].message.content)