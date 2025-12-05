"""
Memory & Context Viewer
=======================
View and manage agent's memory, conversation history, and context
"""

import streamlit as st
import json
from datetime import datetime, timedelta

st.set_page_config(page_title="Memory & Context Viewer", page_icon="🧠", layout="wide")

st.title("🧠 Agent Memory & Context Viewer")
st.markdown("Monitor and manage your agent's memory and context")
st.markdown("---")

# Initialize session state
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = [
        {"timestamp": "2025-12-04 10:00:00", "role": "user", "content": "What is machine learning?", "tokens": 45, "embedding": [0.1, 0.2, 0.3]},
        {"timestamp": "2025-12-04 10:00:15", "role": "assistant", "content": "Machine learning is a subset of artificial intelligence...", "tokens": 120, "embedding": [0.2, 0.3, 0.4]},
        {"timestamp": "2025-12-04 10:01:30", "role": "user", "content": "Can you give me examples?", "tokens": 35, "embedding": [0.15, 0.25, 0.35]},
        {"timestamp": "2025-12-04 10:01:45", "role": "assistant", "content": "Sure! Examples include recommendation systems, image recognition...", "tokens": 150, "embedding": [0.25, 0.35, 0.45]},
    ]

if "long_term_memory" not in st.session_state:
    st.session_state.long_term_memory = {
        "user_preferences": {
            "preferred_language": "Python",
            "response_style": "detailed",
            "expertise_level": "intermediate"
        },
        "facts": [
            {"fact": "User is working on an AI project", "confidence": 0.95, "last_updated": "2025-12-04"},
            {"fact": "User prefers code examples", "confidence": 0.87, "last_updated": "2025-12-03"},
            {"fact": "User is interested in Streamlit", "confidence": 0.92, "last_updated": "2025-12-04"}
        ],
        "entities": [
            {"name": "Python", "type": "programming_language", "mentions": 15},
            {"name": "Streamlit", "type": "framework", "mentions": 8},
            {"name": "Machine Learning", "type": "domain", "mentions": 12}
        ]
    }

if "semantic_memory" not in st.session_state:
    st.session_state.semantic_memory = [
        {"id": "mem_001", "content": "User asked about ML algorithms", "category": "question", "relevance": 0.89, "timestamp": "2025-12-04 09:45:00"},
        {"id": "mem_002", "content": "Discussed neural networks in detail", "category": "concept", "relevance": 0.92, "timestamp": "2025-12-04 09:50:00"},
        {"id": "mem_003", "content": "User mentioned building a chatbot", "category": "project", "relevance": 0.95, "timestamp": "2025-12-04 09:55:00"},
    ]

# Sidebar - Memory Statistics
with st.sidebar:
    st.header("📊 Memory Statistics")
    
    total_messages = len(st.session_state.conversation_memory)
    total_tokens = sum(msg["tokens"] for msg in st.session_state.conversation_memory)
    total_facts = len(st.session_state.long_term_memory["facts"])
    total_entities = len(st.session_state.long_term_memory["entities"])
    
    st.metric("Total Messages", total_messages)
    st.metric("Total Tokens", f"{total_tokens:,}")
    st.metric("Stored Facts", total_facts)
    st.metric("Known Entities", total_entities)
    
    st.markdown("---")
    
    st.subheader("⚙️ Memory Settings")
    max_memory_size = st.number_input("Max Memory Size (MB)", 1, 100, 10)
    retention_days = st.number_input("Retention Period (days)", 1, 365, 30)
    
    st.markdown("---")
    
    st.subheader("🗑️ Actions")
    if st.button("Clear Conversation Memory", use_container_width=True):
        st.session_state.conversation_memory = []
        st.success("✅ Conversation memory cleared")
        st.rerun()
    
    if st.button("Clear Long-term Memory", use_container_width=True):
        st.session_state.long_term_memory = {"user_preferences": {}, "facts": [], "entities": []}
        st.success("✅ Long-term memory cleared")
        st.rerun()
    
    if st.button("Clear All Memory", use_container_width=True):
        st.session_state.conversation_memory = []
        st.session_state.long_term_memory = {"user_preferences": {}, "facts": [], "entities": []}
        st.session_state.semantic_memory = []
        st.success("✅ All memory cleared")
        st.rerun()

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Conversation Memory",
    "📚 Long-term Memory",
    "🔍 Semantic Memory",
    "🌐 Context Window",
    "📊 Memory Analytics"
])

# Tab 1: Conversation Memory
with tab1:
    st.header("💬 Conversation History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_role = st.selectbox("Filter by Role", ["All", "user", "assistant"])
    with col2:
        sort_order = st.selectbox("Sort Order", ["Newest First", "Oldest First"])
    with col3:
        max_messages = st.number_input("Max Messages", 1, 100, 20)
    
    st.markdown("---")
    
    # Display conversation memory
    messages = st.session_state.conversation_memory.copy()
    if sort_order == "Newest First":
        messages = messages[::-1]
    
    for idx, msg in enumerate(messages[:max_messages]):
        if filter_role == "All" or msg["role"] == filter_role:
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            role_color = "blue" if msg["role"] == "user" else "green"
            
            with st.container():
                col1, col2 = st.columns([1, 20])
                with col1:
                    st.markdown(f"### {role_icon}")
                with col2:
                    st.markdown(f"**:{role_color}[{msg['role'].upper()}]** - {msg['timestamp']}")
                    st.markdown(msg["content"])
                    
                    # Token count and embedding info
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.caption(f"🔤 Tokens: {msg['tokens']}")
                    with col_b:
                        if st.button(f"View Embedding", key=f"embed_{idx}"):
                            st.json(msg["embedding"])
                
                st.markdown("---")

# Tab 2: Long-term Memory
with tab2:
    st.header("📚 Long-term Memory Storage")
    
    # User Preferences
    st.subheader("👤 User Preferences")
    with st.expander("View/Edit Preferences", expanded=True):
        prefs = st.session_state.long_term_memory["user_preferences"]
        
        col1, col2 = st.columns(2)
        with col1:
            for key, value in list(prefs.items())[:len(prefs)//2 + 1]:
                new_value = st.text_input(f"{key.replace('_', ' ').title()}", value=value, key=f"pref_{key}")
                prefs[key] = new_value
        with col2:
            for key, value in list(prefs.items())[len(prefs)//2 + 1:]:
                new_value = st.text_input(f"{key.replace('_', ' ').title()}", value=value, key=f"pref_{key}")
                prefs[key] = new_value
        
        # Add new preference
        col_a, col_b, col_c = st.columns([2, 2, 1])
        with col_a:
            new_pref_key = st.text_input("New Preference Key", key="new_pref_key")
        with col_b:
            new_pref_value = st.text_input("Value", key="new_pref_value")
        with col_c:
            st.write("")
            st.write("")
            if st.button("➕ Add"):
                if new_pref_key and new_pref_value:
                    prefs[new_pref_key] = new_pref_value
                    st.rerun()
    
    st.markdown("---")
    
    # Stored Facts
    st.subheader("📝 Stored Facts")
    facts = st.session_state.long_term_memory["facts"]
    
    for idx, fact in enumerate(facts):
        with st.container():
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                st.markdown(f"**{fact['fact']}**")
            with col2:
                st.metric("Confidence", f"{fact['confidence']:.0%}")
            with col3:
                st.caption(f"📅 {fact['last_updated']}")
            
            if st.button(f"🗑️ Delete", key=f"del_fact_{idx}"):
                facts.pop(idx)
                st.rerun()
        st.markdown("---")
    
    # Add new fact
    with st.expander("➕ Add New Fact"):
        new_fact = st.text_input("Fact")
        new_confidence = st.slider("Confidence", 0.0, 1.0, 0.8)
        if st.button("Add Fact"):
            if new_fact:
                facts.append({
                    "fact": new_fact,
                    "confidence": new_confidence,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("✅ Fact added")
                st.rerun()
    
    st.markdown("---")
    
    # Entities
    st.subheader("🏷️ Known Entities")
    entities = st.session_state.long_term_memory["entities"]
    
    # Display as table
    entity_data = []
    for entity in entities:
        entity_data.append({
            "Entity": entity["name"],
            "Type": entity["type"],
            "Mentions": entity["mentions"]
        })
    
    if entity_data:
        st.dataframe(entity_data, use_container_width=True)

# Tab 3: Semantic Memory
with tab3:
    st.header("🔍 Semantic Memory")
    st.markdown("Memory organized by semantic meaning and relevance")
    
    # Search semantic memory
    search_query = st.text_input("🔍 Search Memory", placeholder="Enter keywords...")
    
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.multiselect(
            "Filter by Category",
            ["question", "concept", "project", "task", "insight"],
            default=["question", "concept", "project"]
        )
    with col2:
        min_relevance = st.slider("Minimum Relevance", 0.0, 1.0, 0.5)
    
    st.markdown("---")
    
    # Display semantic memories
    semantic_memories = st.session_state.semantic_memory
    
    for mem in semantic_memories:
        if mem["category"] in category_filter and mem["relevance"] >= min_relevance:
            if not search_query or search_query.lower() in mem["content"].lower():
                with st.container():
                    col1, col2, col3 = st.columns([6, 2, 2])
                    with col1:
                        st.markdown(f"**{mem['content']}**")
                    with col2:
                        relevance_color = "green" if mem["relevance"] > 0.8 else "orange" if mem["relevance"] > 0.6 else "red"
                        st.markdown(f":{relevance_color}[Relevance: {mem['relevance']:.0%}]")
                    with col3:
                        st.caption(f"📅 {mem['timestamp']}")
                    
                    st.caption(f"🏷️ Category: {mem['category']}")
                    st.markdown("---")

# Tab 4: Context Window
with tab4:
    st.header("🌐 Current Context Window")
    st.markdown("Active context being used for agent responses")
    
    # Context configuration
    col1, col2, col3 = st.columns(3)
    with col1:
        context_size = st.number_input("Context Window Size", 1000, 32000, 8000, 1000)
    with col2:
        include_messages = st.number_input("Include Last N Messages", 1, 50, 10)
    with col3:
        include_facts = st.checkbox("Include Facts", value=True)
    
    st.markdown("---")
    
    # Build context
    st.subheader("📋 Context Components")
    
    # System prompt
    with st.expander("🤖 System Prompt", expanded=True):
        system_prompt = st.text_area(
            "System Instructions",
            "You are a helpful AI assistant with access to conversation history and user preferences.",
            height=100
        )
        st.caption(f"Tokens: ~{len(system_prompt.split()) * 1.3:.0f}")
    
    # Recent messages
    with st.expander("💬 Recent Messages", expanded=True):
        recent_messages = st.session_state.conversation_memory[-include_messages:]
        for msg in recent_messages:
            st.markdown(f"**{msg['role']}**: {msg['content'][:100]}...")
        st.caption(f"Tokens: {sum(m['tokens'] for m in recent_messages)}")
    
    # User preferences
    with st.expander("👤 User Preferences"):
        st.json(st.session_state.long_term_memory["user_preferences"])
        st.caption(f"Tokens: ~50")
    
    # Relevant facts
    if include_facts:
        with st.expander("📝 Relevant Facts"):
            for fact in st.session_state.long_term_memory["facts"][:5]:
                st.markdown(f"- {fact['fact']} (confidence: {fact['confidence']:.0%})")
            st.caption(f"Tokens: ~{len(st.session_state.long_term_memory['facts'][:5]) * 20}")
    
    # Context summary
    st.markdown("---")
    st.subheader("📊 Context Summary")
    
    total_context_tokens = (
        len(system_prompt.split()) * 1.3 +
        sum(m['tokens'] for m in recent_messages) +
        50 +
        (len(st.session_state.long_term_memory["facts"][:5]) * 20 if include_facts else 0)
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tokens", f"{total_context_tokens:.0f}")
    with col2:
        st.metric("Available Tokens", f"{context_size - total_context_tokens:.0f}")
    with col3:
        usage_pct = (total_context_tokens / context_size) * 100
        st.metric("Context Usage", f"{usage_pct:.1f}%")
    
    # Progress bar
    st.progress(min(usage_pct / 100, 1.0))

# Tab 5: Memory Analytics
with tab5:
    st.header("📊 Memory Analytics")
    
    # Token usage over time
    st.subheader("📈 Token Usage Over Time")
    
    # Simulate time series data
    import pandas as pd
    
    dates = pd.date_range(start="2025-12-01", end="2025-12-04", freq="6H")
    token_data = pd.DataFrame({
        "Timestamp": dates,
        "Tokens": [100, 250, 400, 550, 700, 850, 950, 1050, 1200, 1350, 1500, 1650, 1800]
    })
    
    st.line_chart(token_data.set_index("Timestamp"))
    
    st.markdown("---")
    
    # Memory distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💬 Message Distribution")
        message_counts = {
            "User": len([m for m in st.session_state.conversation_memory if m["role"] == "user"]),
            "Assistant": len([m for m in st.session_state.conversation_memory if m["role"] == "assistant"])
        }
        st.bar_chart(message_counts)
    
    with col2:
        st.subheader("🏷️ Entity Mentions")
        entity_counts = {
            entity["name"]: entity["mentions"]
            for entity in st.session_state.long_term_memory["entities"]
        }
        st.bar_chart(entity_counts)
    
    st.markdown("---")
    
    # Memory efficiency
    st.subheader("⚡ Memory Efficiency")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Tokens/Message", f"{total_tokens/total_messages:.0f}")
    with col2:
        st.metric("Memory Compression", "78%")
    with col3:
        st.metric("Retrieval Speed", "45ms")
    with col4:
        st.metric("Hit Rate", "92%")

# Export memory
st.markdown("---")
st.subheader("💾 Export Memory")

if st.button("📥 Export All Memory", use_container_width=True):
    memory_export = {
        "conversation_memory": st.session_state.conversation_memory,
        "long_term_memory": st.session_state.long_term_memory,
        "semantic_memory": st.session_state.semantic_memory,
        "exported_at": datetime.now().isoformat()
    }
    
    memory_json = json.dumps(memory_export, indent=2)
    st.download_button(
        "Download Memory",
        memory_json,
        file_name=f"agent_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
