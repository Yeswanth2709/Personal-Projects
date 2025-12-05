"""
Streamlit Chat Interface for Agentic AI
========================================
A professional chat UI for agent conversations with message history,
streaming responses, and multi-turn conversations.
"""

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="AI Agent Chat", page_icon="🤖", layout="wide")

st.title("🤖 AI Agent Chat Interface")
st.markdown("---")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_thinking" not in st.session_state:
    st.session_state.agent_thinking = False

# Sidebar for chat settings
with st.sidebar:
    st.header("⚙️ Chat Settings")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # Chat parameters
    st.subheader("Response Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.number_input("Max Tokens", 100, 4000, 1000, 100)
    
    st.markdown("---")
    
    # Agent persona
    st.subheader("Agent Persona")
    system_prompt = st.text_area(
        "System Prompt",
        "You are a helpful AI assistant that provides clear and concise answers.",
        height=150
    )
    
    st.markdown("---")
    
    # Export chat
    st.subheader("Export")
    if st.button("📥 Export Chat", use_container_width=True):
        if st.session_state.messages:
            chat_export = "\n\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in st.session_state.messages
            ])
            st.download_button(
                "Download Chat",
                chat_export,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

# Main chat area
chat_container = st.container()

# Display chat messages
with chat_container:
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show timestamp
            if "timestamp" in message:
                st.caption(f"🕐 {message['timestamp']}")
            
            # Show thinking/tool usage if available
            if "thinking" in message and message["thinking"]:
                with st.expander("🧠 Agent Thinking Process"):
                    st.info(message["thinking"])
            
            if "tools_used" in message and message["tools_used"]:
                with st.expander("🔧 Tools Used"):
                    for tool in message["tools_used"]:
                        st.code(f"• {tool}", language=None)

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"🕐 {timestamp}")
    
    # Simulate agent response (replace with actual agent call)
    with st.chat_message("assistant"):
        # Show thinking indicator
        with st.spinner("🤔 Agent is thinking..."):
            # Simulate thinking process
            thinking_process = f"Analyzing query: '{prompt}'\nSearching knowledge base...\nGenerating response..."
            
            # Simulate streaming response
            response = f"This is a simulated response to: '{prompt}'\n\nTo integrate with a real agent:\n1. Replace this section with your agent's API call\n2. Use st.write_stream() for streaming responses\n3. Capture tool usage and thinking logs\n\nSettings: Temperature={temperature}, Max Tokens={max_tokens}"
            
            st.markdown(response)
            
            # Show timestamp
            response_time = datetime.now().strftime("%H:%M:%S")
            st.caption(f"🕐 {response_time}")
            
            # Show thinking process
            with st.expander("🧠 Agent Thinking Process"):
                st.info(thinking_process)
            
            # Show tools used
            with st.expander("🔧 Tools Used"):
                st.code("• search_knowledge_base\n• generate_response", language=None)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": response_time,
        "thinking": thinking_process,
        "tools_used": ["search_knowledge_base", "generate_response"]
    })

# Footer with statistics
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Messages", len(st.session_state.messages))
with col2:
    user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.metric("User Messages", user_msgs)
with col3:
    agent_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    st.metric("Agent Messages", agent_msgs)
