# chat_page.py
import streamlit as st
from llm.factory import create_llm_client

@st.cache_resource
def get_llm():
    return create_llm_client()

llm = get_llm()
SYSTEM_PROMPT = "You are a helpful assistant."


def get_response():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state["messages"]
    reply = llm.chat(messages)
    st.session_state["messages"].append(
        {"role": "assistant", "content": reply}
    )


def render_chat_page():
    st.header("💬 Multi-LLM Chatbot")
    st.caption("Backed by your wrapper (OpenAI / Gemini / TCS GenAI)")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Show history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                get_response()
                st.markdown(st.session_state["messages"][-1]["content"])
