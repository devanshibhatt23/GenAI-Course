import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Literal 
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class classify_message(BaseModel):
    is_coding_ques: bool
    
class code_response_accuracy(BaseModel):
    accuracy_percent: str

class State(TypedDict):
    user_query: str
    llm_result: str | None
    accuracy_percent: str | None
    is_coding_ques: bool | None
    
def classify_query(state: State):
    print("➡️ Classifying query")
    query = state['user_query']
    
    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if user's query is related to coding question or not. Return result in JSON format.
    """
    
    response = client.beta.chat.completions.parse(
        model="gemini-2.5-flash-lite",
        response_format=classify_message,
        messages=[
            { "role": "system", "content": SYSTEM_PROMPT },
            { "role": "user", "content": query },
        ]
    )
    
    is_coding_ques = response.choices[0].message.parsed.is_coding_ques
    state["is_coding_ques"] = is_coding_ques
    
    return state

def route(state: State) -> Literal["general_query", "coding_query"]:
    print("➡️ Routing query")
    is_coding_query = state["is_coding_ques"]
    
    if is_coding_query :
        return "coding_query"
    else :
        return "general_query"

def general_query(state: State):
    print("➡️ Getting answer of query")
    query = state["user_query"]
    
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            { "role": "user", "content": query },
        ]
    )
    
    state["llm_result"] = response.choices[0].message.content
    
    return state
    
def coding_query(state: State):
    print("➡️ Coding query")
    query = state["user_query"]
    
    SYSTEM_PROMPT = """
    You are an AI assistant specialized in coding.
    """
    
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            { "role": "system", "content": SYSTEM_PROMPT },
            { "role": "user", "content": query },
        ]
    )
    
    state["llm_result"] = response.choices[0].message.content
    
    return state
    
def code_validation(state: State):
    print("➡️ Code validation")
    query = state["user_query"]
    res = state["llm_result"]
    
    SYSTEM_PROMPT = f"""
    You are an AI assistant expert in calculating accuracy of result or code according to the user query. You have to verify if the result of the LLM is correct or not. Return the code accuracy percentage.
    
    Query: {query}
    Response: {res}
    """
    
    response = client.beta.chat.completions.parse(
        model="gemini-2.5-flash",
        response_format=code_response_accuracy,
        messages=[
            { "role": "system", "content": SYSTEM_PROMPT },
            { "role": "user", "content": query },
        ]
    )
    
    state["accuracy_percent"] = response.choices[0].message.parsed.accuracy_percent
    
    return state
    
graph_builder = StateGraph(State)

graph_builder.add_node("classify_query", classify_query)
graph_builder.add_node("route", route)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("code_validation", code_validation)

graph_builder.add_edge(START, "classify_query")
graph_builder.add_conditional_edges("classify_query", route)
graph_builder.add_edge("general_query", END)
graph_builder.add_edge("coding_query", "code_validation")
graph_builder.add_edge("code_validation", END)

graph = graph_builder.compile()

def main():
    q = input("enter query")
    
    _state: State = {
        "user_query": q,
        "accuracy_percent": None,
        "is_coding_ques": False,
        "llm_result": None,
    }
    
    # response = graph.invoke(_state)
    # print(response)
    
    for event in graph.stream(_state):
        print("event: ", event)
    
main()