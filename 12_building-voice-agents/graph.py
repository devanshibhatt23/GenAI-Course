import os
from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition, ToolNode

load_dotenv()

@tool
def run_command(cmd: str) :
    """
    Takes a command line prompt and executes it in the user's device, and returns the output of the command
    for example: run_command(cmd="ls") returns the list of all files  
    """
    res = os.system(command=cmd)
    return res

available_tools = [run_command]

llm = init_chat_model(
    model_provider="google_genai", 
    model="gemini-3-flash-preview", 
)

llm_with_tool = llm.bind(tools=available_tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]   

def chat_bot(state: State):
    SYSTEM_PROMPT = """
        You are an AI coding assistant who takes user's query and based on available tools you choose the correct tool and execute the command.

        You can even execute the command and help the user with the output of the command.

        Always use run_command tool to run commands like:
        - ls to list all files 
        - cat to read files
        - echo to write files

        Always recheck your files after coding to validate the output

        Make sure to keep your generated codes and files in a chatgpt/ folder, make one if it doesnt exist.
         
    """

    messsages = [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]

    response = llm_with_tool.invoke(messsages)
    return {"messages": [response]}

tool_node = ToolNode(tools=available_tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chat_bot")
graph_builder.add_conditional_edges(
    "chat_bot",
    tools_condition
)
graph_builder.add_edge("tools", "chat_bot")
graph_builder.add_edge("chat_bot", END)

graph = graph_builder.compile()