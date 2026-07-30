from dotenv import load_dotenv
import speech_recognition as sr
from .graph import graph
from pathlib import Path
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer
import os
import asyncio

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

async def text_to_speech(text: str):
    async with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        response_format="pcm"
    ) as response:
        await LocalAudioPlayer().play(response)        

def main():
    # speech to text
    r = sr.Recognizer()
    
    # mic access
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 4
    
        print("Listening...")
        audio = r.listen(source)
        
        print("Processing audio...")
        stt = r.recognize_google(audio)
        
        print("You said: ", stt)

        for event in graph.stream({ "messages": [{"role": "user", "content": stt}] }, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()

# main()

asyncio.run(text_to_speech(text="hey how are u"))