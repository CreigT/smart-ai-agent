import ast
import operator
import sqlite3
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from config import config

_OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        if abs(node.value) > 1e12:
            raise ValueError("Number too large")
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
        value = _evaluate(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATIONS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        result = _OPERATIONS[type(node.op)](left, right)
        if abs(result) > 1e12:
            raise ValueError("Result too large")
        return result
    raise ValueError("Unsupported expression")

@tool
def calculator(expression: str) -> str:
    """Calculate basic arithmetic, such as 2 + 2 * 3."""
    try:
        if len(expression) > 100:
            raise ValueError("Expression too long")
        return str(_evaluate(ast.parse(expression, mode="eval")))
    except Exception as exc:
        return f"Calculation error: {exc}"

tools = [calculator]
if config.TAVILY_API_KEY:
    tools.append(TavilySearchResults(max_results=3, tavily_api_key=config.TAVILY_API_KEY))
tool_map = {item.name: item for item in tools}

llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0, api_key=config.OPENAI_API_KEY)
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def should_continue(state: AgentState):
    return "tools" if getattr(state["messages"][-1], "tool_calls", None) else END

def call_model(state: AgentState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def call_tools(state: AgentState):
    results = []
    for call in state["messages"][-1].tool_calls:
        try:
            selected = tool_map.get(call["name"])
            if selected is None:
                raise ValueError(f"Unknown tool: {call['name']}")
            output = selected.invoke(call["args"])
        except Exception as exc:
            output = f"Tool error: {exc}"
        results.append(ToolMessage(content=str(output), tool_call_id=call["id"]))
    return {"messages": results}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

# Keep the connection alive for the lifetime of the application.
_connection = sqlite3.connect(config.SQLITE_DB, check_same_thread=False)
memory = SqliteSaver(_connection)
graph = workflow.compile(checkpointer=memory)

def run_agent(user_input: str, thread_id: str = "default"):
    run_config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=run_config)
    return result["messages"][-1].content
