import streamlit as st
from backend import chatbot, retrieve_all_threads, delete_thread
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# =========================== Utilities ===========================
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    try:
        state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
        return state.values.get("messages", [])
    except Exception:
        return []

def get_thread_name(messages):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            words = msg.content.split()
            return " ".join(words[:5]) + ("..." if len(words) > 5 else "")
    return "New Chat"

# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

st.session_state["chat_threads"] = retrieve_all_threads()


add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================
st.sidebar.title("LangGraph Chatbot 🤖")

if st.sidebar.button("➕ New Chat", key="new_chat_btn"):
    reset_chat()
    st.rerun()

st.sidebar.header("My Conversations 🗂️")

for thread_id in sorted(st.session_state["chat_threads"], reverse=True):
    messages = load_conversation(thread_id)
    if not messages and thread_id != st.session_state["thread_id"]:
        continue
        
    thread_name = get_thread_name(messages)

    cols = st.sidebar.columns([4, 1])
    
    # Select Thread Button
    if cols[0].button(f"💬 {thread_name}", key=f"thread_{thread_id}"):
        st.session_state["thread_id"] = thread_id
        st.session_state["message_history"] = [
            {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
            for msg in messages if not isinstance(msg, ToolMessage)
        ]
        st.rerun()


    if cols[1].button("❌", key=f"delete_{thread_id}"):
        if delete_thread(thread_id):
            st.session_state["chat_threads"] = [t for t in st.session_state["chat_threads"] if t != thread_id]
            
            if st.session_state["thread_id"] == thread_id:
                st.session_state["thread_id"] = generate_thread_id()
                st.session_state["message_history"] = []
            
            st.sidebar.success("Deleted!")
            st.rerun()

# ============================ Main UI ============================
st.title("ChatBot Assistant 🤖")

chat_container = st.container()

with chat_container:
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_input = st.chat_input("Type here… ✍️")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}

    with st.chat_message("assistant"):
        full_response = ""
        placeholder = st.empty()
        
        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages",
        ):
            if isinstance(message_chunk, AIMessage) and message_chunk.content:
                full_response += message_chunk.content
                placeholder.markdown(full_response)

    st.session_state["message_history"].append({"role": "assistant", "content": full_response})
    st.rerun()