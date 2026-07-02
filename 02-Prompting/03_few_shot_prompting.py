import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# few-shot prompting - with examples
SYSTEM_PROMPT = """You are an expert in python only. You know python and nothing else. You help users solve python doubts and nothing else. If a user asks anything other than python, you can just roast them.

Example :
User : How to make tea?
Assistant : Do you think I'm a chef?

Example :
User : How to write function in python?
Assistant : def func_name() # pass logic of the function

"""

# stateless - no history or chats is stored
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        { "role": "user", "content": "How can I make tea?" },
        { "role": "assistant", "content": "Do you think I'm a chef?" },
        { "role": "user", "content": "How to write factorial function in python" },
    ]
)

print(response.choices[0].message.content)