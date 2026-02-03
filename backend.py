from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3

load_dotenv()

# -------------------
# 1. LLM
# -------------------
llm = ChatGroq(model="moonshotai/kimi-k2-instruct-0905")

# -------------------
# 2. Tools
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """Perform a basic arithmetic operation on two numbers."""
    try:
        if operation == "add": result = first_num + second_num
        elif operation == "sub": result = first_num - second_num
        elif operation == "mul": result = first_num * second_num
        elif operation == "div":
            if second_num == 0: return {"error": "Division by zero"}
            result = first_num / second_num
        else: return {"error": f"Unsupported operation '{operation}'"}
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

tools = [search_tool, calculator]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Checkpointer
# -------------------
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge('tools', 'chat_node')
chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helpers
# -------------------
def retrieve_all_threads():
    all_threads = set()
    try:
        for checkpoint in checkpointer.list(None):
            t_id = checkpoint.config["configurable"]["thread_id"]
            if t_id:
                all_threads.add(t_id)
    except sqlite3.OperationalError:
        return []
    return list(all_threads)

def delete_thread(thread_id):
    try:
        t_id_str = str(thread_id)
        cursor = conn.cursor()
        
        tables = ["checkpoints", "checkpoint_writes", "checkpoint_blobs"]
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table} WHERE thread_id = ?", (t_id_str,))
            except sqlite3.OperationalError as e:
                if "no such table" in str(e):
                    continue
                else:
                    raise e
                    
        conn.commit()
        print(f"Successfully deleted thread: {t_id_str}")
        return True
    except Exception as e:
        print(f"Error deleting thread: {e}")
        return False