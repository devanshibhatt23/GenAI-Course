import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

def run_command(command : str) :
    return os.system(command)

def get_weather(city : str) : 
    url = f"https://wttr.in/{city}?format=%C+%t"

    respone = requests.get(url)

    if respone.status_code == 200 : 
        return respone.text
    else :
        return "something went wrong"

available_tools = {
    "get_weather" : get_weather,
    "run_command" : run_command,
}

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

SYSTEM_PROMPT = """
You are a helpful AI assistant specialized in resolving user query.
You work on start, plan, action and observe mode.

For the user query and available tools, plan step by step execution and select the required tools from the available tools. 

Rules :
- follow the output JSON format
- always perform one step at a time and wait for next input
- carefully analyse the user query

Output JSON format : 
{{
    "step" : "string",
    "content" : "string",
    "function" : "Name of the function if step used is action",
    "input" : "input parameter for the function",
    "output" : "output of the function",
}}

Tools : 
- "get_weather" : takes a city name as input and returns the current weather of the city
- "run_command" : takes a linux command as input and executes it and returns it

Examples : 
user : what is the weather of mumbai?
output : {{ "step" : "plan", "content" : "the user wants to know the weather of mumbai"}}
output : {{ "step" : "plan", "content" : "from the available tools, the relevant tool for user query is "get_weather" }}
output : {{ "step" : "action", "function": "get_weather", "input" : "mumbai" }}
output : {{ "step" : "observe", "output" "42 degrees" }}
output : {{ "step" : "output", "content" : "the weather of mumbai is 42 degrees" }}

"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

query = input("enter query")
messages.append({"role": "user", "content": query})

while True :
    respone = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={ "type" : "json_object" },
        messages=messages,
    )

    messages.append({"role": "assistant", "content": respone.choices[0].message.content})

    parsed_response = json.loads(respone.choices[0].message.content)

    if parsed_response.get("step") == "plan" : 
        print("         🧠", parsed_response.get("content"))

    elif parsed_response.get("step") == "action" : 
        tool_name = parsed_response.get("function")
        tool_input = parsed_response.get("input")

        if(available_tools.get(tool_name) != None) : 
            print(f"         🔨 Calling {tool_name} with input {tool_input}")

            output = available_tools[tool_name](tool_input)

            messages.append({ "role": "user", "content": json.dumps({"step" : "observe", "output" : output }) })
    
    else :
        print("🤖", parsed_response.get("content"))
        break


# input - find weather of dehli and write it in a weather.txt file in the same folder - lecture3