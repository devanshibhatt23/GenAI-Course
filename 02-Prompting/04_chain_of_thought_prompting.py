import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Chain-of-thought (CoT) prompting - model is encouraged to break down reasoning step by step
SYSTEM_PROMPT = """
You are a helpful AI assistant specialized in solving user's doubts.
Analyse the user's question in detail and break down the problem step by step.

The steps are - you get an input, you analyse the input and think, and think again several times and then return final output with an explaination.

Follow the steps in sequence - "analyse", "think", "output", "validate", "result"
Rules : 
1. follow the below json output as per schema
2. perform 1 step at a time
3. analyse the user output

output format : {{ "step" : "string", "content" : "string" }}

Example :
input : what's 2 + 2 * 5 / 3
output : {{ "step" : "analyse", "content" : "the user asked an arithmetic question"}}
output : {{ "step" : "think", "content" : "i should perform the operations from left to right according to BODMAS"}}
output : {{ "step" : "validate", "content" : "correct, using BODMAS here is right approach"}}
output : {{ "step" : "think", "content" : "i need to solve the multiplication part first, then division and finally addition"}}
output : {{ "step" : "output", "content" : "5.33333"}}
output : {{ "step" : "validate", "content" : "seems like 5.33333 is a valid answer"}}
output : {{ "step" : "result", "content" : "5.33333"}}


"""

# stateless - no history or chats is stored

# response = client.chat.completions.create(
#     response_format={"type" : "json_object"},
#     model="gemini-2.5-flash",
#     messages=[
#         {"role": "system", "content": SYSTEM_PROMPT},
#         { "role": "user", "content": "what's (5/3*2) to power 4" },
#         { "role": "user", "content": json.dumps({
#             "step": "analyse",
#             "content": "The user wants to calculate the value of the expression `(5/3 * 2)` raised to the power of 4. This involves division, multiplication, and exponentiation. I need to follow the order of operations."
#             })
#         },
#         { "role": "assistant", "content": json.dumps({
#             "step": "think",
#             "content": "First, evaluate the expression inside the parentheses: (5/3 * 2). 5/3 is approximately 1.66666. Multiplying this by 2 gives approximately 3.33333. As a fraction, (5/3 * 2) = 10/3. Next, raise this result to the power of 4: (10/3)^4. This means (10^4) / (3^4). 10^4 = 10000. 3^4 = 81. So the expression becomes 10000/81."
#             })
#         },
#         { "role" : "assistant", "content" : json.dumps({
#             "step": "output",
#             "content": "The exact value is 10000/81. As a decimal, this is approximately 123.456790123."
#             })
#         },
#         { "role" : "assistant", "content" : json.dumps({
#             "step": "validate", "content": "I have performed the calculations: 5/3 = 1.666..., 1.666... * 2 = 3.333... or 10/3. Then (10/3)^4 = 10^4 / 3^4 = 10000 / 81. The calculation seems correct. The decimal approximation also appears consistent."
#             })
#         },
#         { "role" : "assistant", "content" : json.dumps({
#             "step": "result", "content": "(5/3 * 2)^4 = (10/3)^4 = 10^4 / 3^4 = 10000/81. As a decimal, this is approximately 123.45679."
#             })
#         },
#     ]
# )

# print(response.choices[0].message.content)

messages = [
    { "role": "system", "content": SYSTEM_PROMPT},
]

query = input("enter input")
messages.append({ "role": "user", "content": query})

while True:
    respone = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={ "type" : "json_object" },
        messages=messages,
    )

    messages.append({ "role": "assistant", "content": respone.choices[0].message.content})
    parsed_response = json.loads(respone.choices[0].message.content)

    if parsed_response.get("step") != "result" :
        print("         🧠", parsed_response.get("content"))
        continue

    print("🤖", parsed_response.get("content"))
    break
