from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
import requests 
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

llm = init_chat_model(
    model_provider="google_genai", 
    model="gemini-2.5-flash-lite", 
)

@tool()
def get_weather(city : str) : 
    """this tool returns weather of the given city"""
    
    url = f"https://wttr.in/{city}?format=%C+%t"

    respone = requests.get(url)

    if respone.status_code == 200 : 
        return respone.text
    else :
        return "something went wrong"

tools = [get_weather]
llm_with_tools = llm.bind_tools(tools=tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
def chat_bot(state: State) :
    response = llm_with_tools.invoke(state["messages"])
    
    return {"messages": [response]}

graph_builder = StateGraph(State)

graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_node("tools", ToolNode(tools))

graph_builder.add_edge(START, "chat_bot")
graph_builder.add_conditional_edges(
    "chat_bot",
    tools_condition
)

graph_builder.add_edge("tools", "chat_bot")
graph_builder.add_edge("chat_bot", END)

graph = graph_builder.compile()

def main():
    q = input("enter query: ")
    
    state = State(
        messages=[{ "role": "user", "content": q }]
    )
    
    res = graph.invoke(state)
    print(res)

main()