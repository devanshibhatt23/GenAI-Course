from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

load_dotenv()

@tool
def human_assistance(query: str) -> str :
    """Request assistance from a human"""
    
    human_response = interrupt({ "query": query})
    return human_response["data"]

tools = [human_assistance]

llm = init_chat_model(
    model_provider="google_genai", 
    model="gemini-2.5-flash-lite", 
)

llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
def chat_bot(state: State):
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

def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer
        
def user_chat():
    MONGODB_URI = "mongodb://admin:admin@mongo-db:27017"
    config = {
        "configurable": {
            "thread_id": "4"
        }
    }
    
    with MongoDBSaver.from_conn_string(MONGODB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)
        
        while True:
            q = input("enter query ")
            
            state = State(
                messages = [{ "role": "user", "content": q }],
            )
            
            for event in graph_with_mongo.stream(state, config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()


def admin_call():
    MONGODB_URI = "mongodb://admin:admin@mongo-db:27017"
    config = {
        "configurable": {
            "thread_id": "4"
        }
    }
    
    with MongoDBSaver.from_conn_string(MONGODB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)
        
        snapshot = graph_with_mongo.get_state(config)
        
        if not snapshot.next:
            print("Nothing is waiting for human input right now.")
            return
        
        last_mssg = snapshot.values["messages"][-1]
        user_query = None
        
        print("last mssg ", last_mssg)
        
        tool_calls = last_mssg.tool_calls
        print("tool calls ", tool_calls)
        
        for call in tool_calls:
            if call["name"] == "human_assistance":
                user_query = call["args"].get("query")
        
        print("user has a question: ", user_query)
        
        solution = input("enter solution: ")
        
        resume_command = Command(resume={"data": solution})

        for event in graph_with_mongo.stream(resume_command, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()

user_chat()
# admin_call()