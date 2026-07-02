import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

text = "Dog chases cat."

response = client.embeddings.create(
    input=text,
    model="gemini-embedding-001",
)

print("Vector embeddings:", response)
# dimensions of the model
print("Length:", len(response.data[0].embedding))