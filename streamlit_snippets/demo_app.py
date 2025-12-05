"""
Agentic AI Demo - Complete Application
======================================
Comprehensive demo showcasing all agent UI components
"""

import streamlit as st
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Agentic AI Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "demo_page" not in st.session_state:
    st.session_state.demo_page = "Home"

if "agent_status" not in st.session_state:
    st.session_state.agent_status = "online"

# Sidebar Navigation
with st.sidebar:
    st.markdown("# 🤖 Navigation")
    st.markdown("---")
    
    pages = {
        "🏠 Home": "Home",
        "💬 Chat Interface": "Chat",
        "⚙️ Configuration": "Config",
        "🔧 Tools": "Tools",
        "🧠 Memory": "Memory",
        "🔄 Workflows": "Workflows",
        "📊 Dashboard": "Dashboard",
        "📤 Data Input": "Input"
    }
    
    for page_name, page_key in pages.items():
        if st.button(page_name, use_container_width=True):
            st.session_state.demo_page = page_key
            st.rerun()
    
    st.markdown("---")
    
    # Agent status
    st.markdown("### 🤖 Agent Status")
    status_color = "🟢" if st.session_state.agent_status == "online" else "🔴"
    st.markdown(f"{status_color} **{st.session_state.agent_status.upper()}**")
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### 📊 Quick Stats")
    st.metric("Sessions Today", "24", delta="5")
    st.metric("Avg Response", "1.2s", delta="-0.3s")
    st.metric("Success Rate", "98.5%", delta="2.1%")

# Main Content Area
if st.session_state.demo_page == "Home":
    # Home Page
    st.markdown('<h1 class="main-header">🤖 Agentic AI Platform</h1>', unsafe_allow_html=True)
    st.markdown("### Build, Deploy, and Monitor Intelligent AI Agents")
    st.markdown("---")
    
    # Hero section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. **Configure** your agent
        2. **Select** tools and capabilities
        3. **Chat** with your agent
        4. **Monitor** performance
        """)
        if st.button("Get Started →", use_container_width=True, type="primary"):
            st.session_state.demo_page = "Config"
            st.rerun()
    
    with col2:
        st.markdown("### 💡 Features")
        st.markdown("""
        - 💬 Conversational interface
        - 🔧 Customizable tools
        - 🧠 Persistent memory
        - 🔄 Complex workflows
        - 📊 Real-time monitoring
        """)
    
    with col3:
        st.markdown("### 📚 Resources")
        st.markdown("""
        - [📖 Documentation](#)
        - [🎓 Tutorials](#)
        - [💻 API Reference](#)
        - [🤝 Community](#)
        - [🐛 Report Issues](#)
        """)
    
    st.markdown("---")
    
    # Component showcase
    st.markdown("## 🎯 Platform Components")
    
    components = [
        {
            "title": "💬 Chat Interface",
            "description": "Professional chat UI with streaming responses, message history, and conversation export.",
            "file": "01_chat_interface.py",
            "icon": "💬"
        },
        {
            "title": "⚙️ Agent Configuration",
            "description": "Comprehensive settings for model parameters, behavior, memory, and safety controls.",
            "file": "02_agent_configuration.py",
            "icon": "⚙️"
        },
        {
            "title": "🔧 Tool Management",
            "description": "Select, configure, and manage tools available to your AI agent.",
            "file": "03_tool_selection.py",
            "icon": "🔧"
        },
        {
            "title": "🧠 Memory & Context",
            "description": "View and manage conversation history, long-term memory, and semantic search.",
            "file": "04_memory_context_viewer.py",
            "icon": "🧠"
        },
        {
            "title": "🔄 Workflow Builder",
            "description": "Design complex multi-step workflows with conditional logic and branching.",
            "file": "05_workflow_builder.py",
            "icon": "🔄"
        },
        {
            "title": "📊 Performance Dashboard",
            "description": "Monitor metrics, track costs, analyze performance, and view detailed logs.",
            "file": "06_monitoring_dashboard.py",
            "icon": "📊"
        },
        {
            "title": "📤 Data Input",
            "description": "Upload files, input text, structured data, and fetch content from URLs.",
            "file": "07_file_upload_input.py",
            "icon": "📤"
        }
    ]
    
    # Display components in grid
    col1, col2 = st.columns(2)
    
    for idx, component in enumerate(components):
        with col1 if idx % 2 == 0 else col2:
            with st.container():
                st.markdown(f"### {component['icon']} {component['title']}")
                st.markdown(component['description'])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.code(component['file'], language=None)
                with col_b:
                    if st.button(f"View Demo →", key=f"demo_{idx}", use_container_width=True):
                        page_map = {
                            "01_chat_interface.py": "Chat",
                            "02_agent_configuration.py": "Config",
                            "03_tool_selection.py": "Tools",
                            "04_memory_context_viewer.py": "Memory",
                            "05_workflow_builder.py": "Workflows",
                            "06_monitoring_dashboard.py": "Dashboard",
                            "07_file_upload_input.py": "Input"
                        }
                        st.session_state.demo_page = page_map.get(component['file'], "Home")
                        st.rerun()
                
                st.markdown("---")
    
    # Getting started guide
    st.markdown("## 🚀 Getting Started")
    
    with st.expander("📦 Installation", expanded=True):
        st.markdown("### 1. Create a virtual environment")
        st.code("python -m venv venv", language="bash")
        
        st.markdown("### 2. Activate the environment")
        st.code("venv\\Scripts\\activate  # Windows\nsource venv/bin/activate  # Linux/Mac", language="bash")
        
        st.markdown("### 3. Install dependencies")
        st.code("pip install streamlit", language="bash")
    
    with st.expander("▶️ Running the Applications"):
        st.markdown("Run any component individually:")
        st.code("streamlit run streamlit_snippets/01_chat_interface.py", language="bash")
        
        st.markdown("Or run this demo app:")
        st.code("streamlit run streamlit_snippets/demo_app.py", language="bash")
    
    with st.expander("🔧 Customization"):
        st.markdown("""
        Each component is fully customizable:
        
        - **Modify UI elements** - All components use Streamlit widgets
        - **Add new features** - Extend functionality with new tools and capabilities
        - **Integrate APIs** - Connect to your LLM providers (OpenAI, Anthropic, etc.)
        - **Style customization** - Use custom CSS and themes
        - **Data persistence** - Add database integration for real data storage
        """)

elif st.session_state.demo_page == "Chat":
    st.info("💬 **Chat Interface Demo** - In a full implementation, this would load the chat interface component. Run `streamlit run streamlit_snippets/01_chat_interface.py` to see it standalone.")
    
    if st.button("← Back to Home"):
        st.session_state.demo_page = "Home"
        st.rerun()

elif st.session_state.demo_page == "Config":
    st.info("⚙️ **Configuration Demo** - Run `streamlit run streamlit_snippets/02_agent_configuration.py` to see the full configuration interface.")
    
    if st.button("← Back to Home"):
        st.session_state.demo_page = "Home"
        st.rerun()

elif st.session_state.demo_page == "Tools":
    st.info("🔧 **Tool Management Demo** - Run `streamlit run streamlit_snippets/03_tool_selection.py` to see the full tool management interface.")
    
    if st.button("← Back to Home"):
        st.session_state.demo_page = "Home"
        st.rerun()

elif st.session_state.demo_page == "Memory":
    st.info("🧠 **Memory Viewer Demo** - Run `streamlit run streamlit_snippets/04_memory_context_viewer.py` to see the full memory management interface.")
    
    if st.button("← Back to Home"):
        st.session_state.demo_page = "Home"
        st.rerun()

elif st.session_state.demo_page == "Workflows":
    st.info("🔄 **Workflow Builder Demo** - Run `streamlit run streamlit_snippets/05_workflow_builder.py` to see the full workflow builder.")
    
    if st.button("← Back to Home"):
        st.session_state.demo_page = "Home"
        st.rerun()

elif st.session_state.demo_page == "Dashboard":
    st.info("📊 **Monitoring Dashboard Demo** - Run `streamlit run streamlit_snippets/06_monitoring_dashboard.py` to see the full performance dashboard.")
    
    if st.button("← Back to Home"):
        st.session_state.demo_page = "Home"
        st.rerun()

elif st.session_state.demo_page == "Input":
    st.info("📤 **Data Input Demo** - Run `streamlit run streamlit_snippets/07_file_upload_input.py` to see the full data input interface.")
    
    if st.button("← Back to Home"):
        st.session_state.demo_page = "Home"
        st.rerun()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📚 Documentation")
    st.markdown("View the README for detailed information")

with col2:
    st.markdown("### 🤝 Community")
    st.markdown("Join our community forums")

with col3:
    st.markdown("### 💻 Source Code")
    st.markdown("All components are open source")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Built with ❤️ using Streamlit | "
    f"© {datetime.now().year} Agentic AI Platform</p>",
    unsafe_allow_html=True
)
