from langgraph.graph import StateGraph
from local_llm import mini_instruct_model
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

class State(TypedDict):
    input: str
    output: str

def process_node(state: State):
    text = state["input"]
    result = text.upper()

    return {"output": result}

builder = StateGraph(State)

builder.add_node("process", process_node)

builder.set_entry_point("process")
builder.set_finish_point("process")

graph = builder.compile()
result = graph.invoke({"input": "hello world"})

print(result)

system_prompt = ChatPromptTemplate.from_messages(
    [
    ("system", "You are a singaporean female, mid teens."),
    ("user", "{query}")  
    ]
)
query = "Tell me a lame joke."

def llm_node(system_prompt:ChatPromptTemplate, query:str, state:State):

    response = mini_instruct_model(system_prompt=system_prompt,query=query)

    return {"output": response.content}


def router(state):
    if "error" in state:
        return "retry"
    return "success"

builder.add_conditional_edges(
    "validate",
    router,
    {
        "retry": "extract",
        "success": "finish"
    }
)

