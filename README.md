# 🤖 LangGraph Agentic Chatbot with Tools & Memory

An **Agentic AI Chatbot** built using **LangGraph**, **LangChain**, **Groq LLM**, and **Streamlit**.  
This project demonstrates how to build a **multi-tool LLM agent** with **persistent memory**, **conversation threads**, and a **modern chat UI**.

---

## 🚀 Features

- 🔗 **LangGraph-based Agent Workflow**
- 🧠 **Persistent Memory** using SQLite Checkpointer
- 🛠️ **Tool Calling Support**
  - Web Search (DuckDuckGo)
  - Calculator Tool
- 🧵 **Multiple Chat Threads**
- 💾 **Conversation History Saved Automatically**
- 🗑️ **Delete Individual Chat Threads**
- ⚡ **Streaming Responses**
- 🖥️ **Streamlit Chat UI**
- ☁️ **Groq LLM Integration (Kimi K2 Model)**

---

## 🧠 Architecture Overview
User → Streamlit UI
→ LangGraph StateGraph
→ LLM (Groq - Kimi K2)
→ Tools (Search / Calculator)
→ SQLite Memory (Checkpointer)


## 📂 Project Structure

langgraph-agentic-chatbot/

── backend.py # LangGraph agent, tools, memory, graph

── app.py # Streamlit frontend

── chatbot.db # SQLite database (auto-generated)

── requirements.txt

── .env

── README.md



## 🛠️ Tech Stack

- **Python**
- **LangGraph**
- **LangChain**
- **Groq LLM**
- **Streamlit**
- **SQLite**
- **DuckDuckGo Search Tool**




