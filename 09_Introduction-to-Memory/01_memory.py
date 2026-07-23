import os
from mem0 import Memory
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path="/workspaces/GenAI course/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "gemini",
        "config": {
            "api_key": GEMINI_API_KEY,
            "model": "gemini-embedding-001",
            "embedding_dims": 1536,
        }
    },
    
    "llm": {
        "provider": "gemini",
        "config": {
            "api_key": GEMINI_API_KEY,
            "model": "gemini-3-flash-preview",
        }
    },
    
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "vector-db",
            "port": 6333,
            "embedding_model_dims": 1536
        }
    },
    
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://neo4j:7687",
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829"
        }
    }
}

mem_client = Memory.from_config(config)

print("enable_graph:", getattr(mem_client, "enable_graph", "ATTRIBUTE NOT FOUND"))
print("version:", getattr(mem_client, "version", "ATTRIBUTE NOT FOUND"))

def chat():
    while True:
        query = input("enter query: ")
        
        relevant_memories = mem_client.search(query=query, user_id="devanshi")
        
        memories = [
            f"ID: {mems.get('id')}, Memory: {mems.get('memory')}"
            for mems in relevant_memories.get("results")
        ]
        
        SYSTEM_PROMPT = f"""
            You are a memory aware assistant which responds to user's query by getting stored information about the user from memory:
            {json.dumps(memories)}
        """
        
        result = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}]
        )
        
        answer = result.choices[0].message.content
        print(f"🤖: {answer}")
        
        res = mem_client.add([
            {"role": "user", "content": query},
            {"role": "assistant", "content": answer}],
            user_id="devanshi",
        )

        print(res)
chat()
