from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

llm = init_chat_model(
    model_provider="google_genai", 
    model="gemini-2.5-flash-lite", 
)

class state(TypedDict):
    messages: Annotated[list, add_messages]
    
def chat(state: state):
    response = llm.invoke(state["messages"])
    
    return {"messages": [response]}

graph_builder = StateGraph(state)

graph_builder.add_node("chat", chat)

graph_builder.add_edge(START, "chat")
graph_builder.add_edge("chat", END)

graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer
        
def main():
    MONGODB_URI = "mongodb://admin:admin@mongo-db:27017"
    config = {
        "configurable": {
            "thread_id": "1"
        }
    }
    
    with MongoDBSaver.from_conn_string(MONGODB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)
        
        q = input("enter query ")
        
        res = graph_with_mongo.invoke(
            {"messages": [{ "role": "user", "content": q }]},
            config,
        )
        print(res)

main()