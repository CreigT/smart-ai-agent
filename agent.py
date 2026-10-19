import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from config import config

# Tools
@tool
def calculator(expression: str) -> str:
    """Evaluate a simple math expression. Example: '2 + 2 * 3'."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

search_tool = TavilySearchResults(max_results=3, tavily_api_key=config.TAVILY_API_KEY) if config.TAVILY_API_KEY else None

tools = [calculator]
if search_tool:
    tools.append(search_tool)

llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0, api_key=config.OPENAI_API_KEY)
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def should_continue(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

def call_model(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def call_tools(state: AgentState):
    tool_messages = []
    last = state["messages"][-1]
    for tool_call in last.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        selected = next((t for t in tools if t.name == tool_name), None)
        if selected:
            result = selected.invoke(tool_args)
            tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
    return {"messages": tool_messages}

# Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# Memory
memory = SqliteSaver.from_conn_string(config.SQLITE_DB)
graph = workflow.compile(checkpointer=memory)

def run_agent(user_input: str, thread_id: str = "default"):
    config_run = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=config_run)
    return result["messages"][-1].content
