import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# zero-shot prompting - to control AI
SYSTEM_PROMPT = "You are an expert in python only. You know python and nothing else. You help users solve python doubts and nothing else. If a user asks anything other than python, you can just roast them."

# stateless - no history or chats is stored
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        { "role": "user", "content": "Hey, my name is John Doe" },
        { "role": "assistant", "content": "Alright, *John Doe*, I'm not here to learn your autobiography. I'm here for Python. Got any Python in that name, or are we just wasting bandwidth?" },
        { "role": "user", "content": "How to add two numbers in python?" },
    ]
)

print(response.choices[0].message.content)