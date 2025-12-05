"""
Agent Configuration UI
======================
Configure agent parameters, model settings, and behavior controls
"""

import streamlit as st
import json

st.set_page_config(page_title="Agent Configuration", page_icon="⚙️", layout="wide")

st.title("⚙️ Agent Configuration")
st.markdown("Configure your AI agent's behavior, parameters, and capabilities")
st.markdown("---")

# Initialize session state for configuration
if "config" not in st.session_state:
    st.session_state.config = {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "system_prompt": "You are a helpful AI assistant.",
        "agent_name": "AI Assistant",
        "agent_role": "General Purpose",
        "enable_memory": True,
        "memory_window": 10,
        "enable_reasoning": True,
        "reasoning_depth": "medium",
        "safety_mode": "balanced"
    }

# Create tabs for different configuration sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 Model Settings",
    "💭 Behavior",
    "🧠 Memory & Context",
    "🛡️ Safety & Constraints",
    "💾 Save/Load Config"
])

# Tab 1: Model Settings
with tab1:
    st.header("Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Selection")
        model = st.selectbox(
            "Choose Model",
            ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            index=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"].index(st.session_state.config["model"])
        )
        st.session_state.config["model"] = model
        
        st.markdown("---")
        
        st.subheader("Generation Parameters")
        temperature = st.slider(
            "Temperature",
            0.0, 2.0, st.session_state.config["temperature"], 0.1,
            help="Controls randomness. Higher = more creative, Lower = more focused"
        )
        st.session_state.config["temperature"] = temperature
        
        max_tokens = st.number_input(
            "Max Tokens",
            100, 8000, st.session_state.config["max_tokens"], 100,
            help="Maximum length of generated response"
        )
        st.session_state.config["max_tokens"] = max_tokens
    
    with col2:
        st.subheader("Advanced Parameters")
        
        top_p = st.slider(
            "Top P (Nucleus Sampling)",
            0.0, 1.0, st.session_state.config["top_p"], 0.05,
            help="Alternative to temperature for controlling randomness"
        )
        st.session_state.config["top_p"] = top_p
        
        frequency_penalty = st.slider(
            "Frequency Penalty",
            -2.0, 2.0, st.session_state.config["frequency_penalty"], 0.1,
            help="Reduces repetition of token sequences"
        )
        st.session_state.config["frequency_penalty"] = frequency_penalty
        
        presence_penalty = st.slider(
            "Presence Penalty",
            -2.0, 2.0, st.session_state.config["presence_penalty"], 0.1,
            help="Increases likelihood of talking about new topics"
        )
        st.session_state.config["presence_penalty"] = presence_penalty
        
        st.markdown("---")
        
        st.info("💡 **Tip**: Use temperature for creativity vs precision control. Combine with top_p for fine-tuned control.")

# Tab 2: Behavior
with tab2:
    st.header("Agent Behavior Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Identity")
        agent_name = st.text_input(
            "Agent Name",
            st.session_state.config["agent_name"]
        )
        st.session_state.config["agent_name"] = agent_name
        
        agent_role = st.selectbox(
            "Agent Role",
            ["General Purpose", "Code Assistant", "Research Assistant", "Creative Writer", "Data Analyst", "Customer Support"],
            index=["General Purpose", "Code Assistant", "Research Assistant", "Creative Writer", "Data Analyst", "Customer Support"].index(st.session_state.config["agent_role"])
        )
        st.session_state.config["agent_role"] = agent_role
        
        st.markdown("---")
        
        st.subheader("System Prompt")
        system_prompt = st.text_area(
            "Define agent's core instructions and personality",
            st.session_state.config["system_prompt"],
            height=200,
            help="This prompt defines how the agent behaves and responds"
        )
        st.session_state.config["system_prompt"] = system_prompt
    
    with col2:
        st.subheader("Response Style")
        
        verbosity = st.select_slider(
            "Verbosity Level",
            options=["Minimal", "Concise", "Balanced", "Detailed", "Comprehensive"],
            value="Balanced"
        )
        
        formality = st.select_slider(
            "Formality",
            options=["Casual", "Friendly", "Professional", "Formal", "Academic"],
            value="Professional"
        )
        
        st.markdown("---")
        
        st.subheader("Reasoning")
        enable_reasoning = st.checkbox(
            "Enable Chain-of-Thought Reasoning",
            st.session_state.config["enable_reasoning"],
            help="Agent shows its thinking process"
        )
        st.session_state.config["enable_reasoning"] = enable_reasoning
        
        if enable_reasoning:
            reasoning_depth = st.select_slider(
                "Reasoning Depth",
                options=["shallow", "medium", "deep"],
                value=st.session_state.config["reasoning_depth"]
            )
            st.session_state.config["reasoning_depth"] = reasoning_depth

# Tab 3: Memory & Context
with tab3:
    st.header("Memory & Context Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Conversation Memory")
        enable_memory = st.checkbox(
            "Enable Conversation Memory",
            st.session_state.config["enable_memory"],
            help="Agent remembers previous messages in the conversation"
        )
        st.session_state.config["enable_memory"] = enable_memory
        
        if enable_memory:
            memory_window = st.slider(
                "Memory Window (messages)",
                1, 50, st.session_state.config["memory_window"],
                help="Number of previous messages to remember"
            )
            st.session_state.config["memory_window"] = memory_window
            
            memory_type = st.radio(
                "Memory Type",
                ["Sliding Window", "Summary-based", "Semantic Search"],
                help="How to manage conversation history"
            )
        
        st.markdown("---")
        
        st.subheader("Context Sources")
        enable_web_search = st.checkbox("Enable Web Search", value=False)
        enable_document_search = st.checkbox("Enable Document Search", value=True)
        enable_code_search = st.checkbox("Enable Code Search", value=False)
    
    with col2:
        st.subheader("Context Settings")
        
        max_context_length = st.number_input(
            "Max Context Length (tokens)",
            1000, 32000, 8000, 1000,
            help="Maximum tokens for all context"
        )
        
        context_priority = st.multiselect(
            "Context Priority (ordered)",
            ["Current Query", "Recent Messages", "System Prompt", "Retrieved Documents", "Tool Results"],
            default=["Current Query", "Recent Messages", "System Prompt"]
        )
        
        st.markdown("---")
        
        st.info("📊 **Context Budget**\n\n"
                f"- Max tokens: {max_context_length:,}\n"
                f"- System prompt: ~{len(st.session_state.config['system_prompt'].split())} words\n"
                f"- Memory window: {st.session_state.config['memory_window']} messages\n"
                f"- Available for query: ~{max_context_length - 500:,} tokens")

# Tab 4: Safety & Constraints
with tab4:
    st.header("Safety & Constraint Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Safety Settings")
        safety_mode = st.select_slider(
            "Safety Mode",
            options=["Permissive", "Balanced", "Strict"],
            value=st.session_state.config["safety_mode"]
        )
        st.session_state.config["safety_mode"] = safety_mode
        
        content_filters = st.multiselect(
            "Content Filters",
            ["Profanity", "Violence", "Hate Speech", "Personal Info", "Medical Advice", "Legal Advice"],
            default=["Hate Speech", "Personal Info"]
        )
        
        st.markdown("---")
        
        st.subheader("Behavior Constraints")
        disallow_opinions = st.checkbox("Disallow Personal Opinions", value=False)
        require_citations = st.checkbox("Require Citations for Facts", value=False)
        avoid_speculation = st.checkbox("Avoid Speculation", value=False)
    
    with col2:
        st.subheader("Rate Limits")
        
        max_requests_per_minute = st.number_input(
            "Max Requests/Minute",
            1, 100, 20
        )
        
        max_tokens_per_request = st.number_input(
            "Max Tokens/Request",
            100, 8000, 2000
        )
        
        timeout_seconds = st.number_input(
            "Request Timeout (seconds)",
            5, 300, 60
        )
        
        st.markdown("---")
        
        st.subheader("Error Handling")
        retry_on_error = st.checkbox("Auto-retry on Errors", value=True)
        if retry_on_error:
            max_retries = st.number_input("Max Retries", 1, 5, 3)
        
        fallback_model = st.selectbox(
            "Fallback Model",
            ["None", "gpt-3.5-turbo", "claude-3-haiku"],
            help="Model to use if primary fails"
        )

# Tab 5: Save/Load Configuration
with tab5:
    st.header("Configuration Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Load Configuration")
        
        # Preset configurations
        presets = {
            "Default": st.session_state.config,
            "Creative Writer": {
                "model": "gpt-4",
                "temperature": 0.9,
                "max_tokens": 3000,
                "agent_role": "Creative Writer",
                "system_prompt": "You are a creative writing assistant with a vivid imagination."
            },
            "Code Assistant": {
                "model": "gpt-4-turbo",
                "temperature": 0.3,
                "max_tokens": 2000,
                "agent_role": "Code Assistant",
                "system_prompt": "You are an expert programmer who writes clean, efficient code."
            },
            "Research Assistant": {
                "model": "gpt-4",
                "temperature": 0.5,
                "max_tokens": 2500,
                "agent_role": "Research Assistant",
                "system_prompt": "You are a research assistant who provides accurate, well-cited information."
            }
        }
        
        selected_preset = st.selectbox("Choose Preset", list(presets.keys()))
        
        if st.button("Load Preset", use_container_width=True):
            st.session_state.config.update(presets[selected_preset])
            st.success(f"✅ Loaded preset: {selected_preset}")
            st.rerun()
        
        st.markdown("---")
        
        # Upload configuration file
        uploaded_file = st.file_uploader("Upload Configuration JSON", type=['json'])
        if uploaded_file is not None:
            try:
                loaded_config = json.load(uploaded_file)
                if st.button("Apply Uploaded Config", use_container_width=True):
                    st.session_state.config.update(loaded_config)
                    st.success("✅ Configuration loaded successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading configuration: {str(e)}")
    
    with col2:
        st.subheader("💾 Save Configuration")
        
        config_name = st.text_input("Configuration Name", "my_agent_config")
        
        # Display current configuration
        with st.expander("📄 Current Configuration Preview"):
            st.json(st.session_state.config)
        
        # Download configuration
        config_json = json.dumps(st.session_state.config, indent=2)
        st.download_button(
            "📥 Download Configuration",
            config_json,
            file_name=f"{config_name}.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Quick export options
        st.subheader("Quick Export")
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.code(config_json, language="json")
            st.info("👆 Copy the configuration above")

# Apply configuration button
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("✅ Apply Configuration", use_container_width=True, type="primary"):
        st.success("🎉 Configuration applied successfully!")
        st.balloons()
