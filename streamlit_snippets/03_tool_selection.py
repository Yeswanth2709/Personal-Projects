"""
Tool Selection & Management UI
===============================
Select, configure, and manage tools available to the AI agent
"""

import streamlit as st
import json

st.set_page_config(page_title="Tool Management", page_icon="🔧", layout="wide")

st.title("🔧 Agent Tool Management")
st.markdown("Configure which tools and capabilities your agent can use")
st.markdown("---")

# Initialize session state for tools
if "available_tools" not in st.session_state:
    st.session_state.available_tools = {
        "web_search": {
            "name": "Web Search",
            "description": "Search the internet for current information",
            "category": "Information Retrieval",
            "enabled": True,
            "config": {
                "max_results": 5,
                "search_engine": "Google",
                "safe_search": True
            },
            "icon": "🌐"
        },
        "calculator": {
            "name": "Calculator",
            "description": "Perform mathematical calculations",
            "category": "Computation",
            "enabled": True,
            "config": {
                "precision": 10,
                "scientific_mode": True
            },
            "icon": "🔢"
        },
        "code_executor": {
            "name": "Code Executor",
            "description": "Execute code in a sandboxed environment",
            "category": "Development",
            "enabled": False,
            "config": {
                "languages": ["python", "javascript"],
                "timeout_seconds": 30,
                "max_memory_mb": 512
            },
            "icon": "💻"
        },
        "file_reader": {
            "name": "File Reader",
            "description": "Read and analyze files",
            "category": "File Operations",
            "enabled": True,
            "config": {
                "allowed_extensions": [".txt", ".pdf", ".csv", ".json"],
                "max_file_size_mb": 10
            },
            "icon": "📄"
        },
        "database_query": {
            "name": "Database Query",
            "description": "Query databases for information",
            "category": "Data Access",
            "enabled": False,
            "config": {
                "connection_string": "",
                "read_only": True,
                "timeout_seconds": 60
            },
            "icon": "🗄️"
        },
        "image_generator": {
            "name": "Image Generator",
            "description": "Generate images from text descriptions",
            "category": "Creative",
            "enabled": False,
            "config": {
                "model": "dall-e-3",
                "resolution": "1024x1024",
                "quality": "standard"
            },
            "icon": "🎨"
        },
        "email_sender": {
            "name": "Email Sender",
            "description": "Send emails on behalf of the user",
            "category": "Communication",
            "enabled": False,
            "config": {
                "smtp_server": "",
                "require_confirmation": True
            },
            "icon": "📧"
        },
        "document_analyzer": {
            "name": "Document Analyzer",
            "description": "Extract insights from documents",
            "category": "Analysis",
            "enabled": True,
            "config": {
                "extract_entities": True,
                "summarize": True,
                "extract_tables": True
            },
            "icon": "📊"
        },
        "api_caller": {
            "name": "API Caller",
            "description": "Make HTTP requests to external APIs",
            "category": "Integration",
            "enabled": False,
            "config": {
                "allowed_domains": [],
                "timeout_seconds": 30,
                "max_retries": 3
            },
            "icon": "🔌"
        },
        "memory_store": {
            "name": "Memory Store",
            "description": "Store and retrieve information across sessions",
            "category": "Memory",
            "enabled": True,
            "config": {
                "max_entries": 1000,
                "ttl_days": 30
            },
            "icon": "🧠"
        }
    }

# Sidebar - Tool Categories
with st.sidebar:
    st.header("📁 Tool Categories")
    
    categories = set(tool["category"] for tool in st.session_state.available_tools.values())
    selected_category = st.radio(
        "Filter by Category",
        ["All"] + sorted(list(categories))
    )
    
    st.markdown("---")
    
    # Tool statistics
    st.subheader("📊 Statistics")
    total_tools = len(st.session_state.available_tools)
    enabled_tools = sum(1 for tool in st.session_state.available_tools.values() if tool["enabled"])
    
    st.metric("Total Tools", total_tools)
    st.metric("Enabled Tools", enabled_tools)
    st.metric("Disabled Tools", total_tools - enabled_tools)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Enable All", use_container_width=True):
            for tool in st.session_state.available_tools.values():
                tool["enabled"] = True
            st.rerun()
    with col2:
        if st.button("❌ Disable All", use_container_width=True):
            for tool in st.session_state.available_tools.values():
                tool["enabled"] = False
            st.rerun()

# Main content area
tab1, tab2, tab3 = st.tabs(["🔧 Tool Selection", "➕ Add Custom Tool", "📋 Tool Execution Log"])

# Tab 1: Tool Selection
with tab1:
    st.header("Available Tools")
    
    # Filter tools by category
    filtered_tools = {
        k: v for k, v in st.session_state.available_tools.items()
        if selected_category == "All" or v["category"] == selected_category
    }
    
    # Display tools in a grid
    for tool_id, tool in filtered_tools.items():
        with st.expander(f"{tool['icon']} {tool['name']}", expanded=tool["enabled"]):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {tool['description']}")
                st.markdown(f"**Category:** {tool['category']}")
            
            with col2:
                enabled = st.checkbox(
                    "Enabled",
                    value=tool["enabled"],
                    key=f"enable_{tool_id}"
                )
                st.session_state.available_tools[tool_id]["enabled"] = enabled
            
            # Tool configuration
            if enabled:
                st.markdown("---")
                st.subheader("⚙️ Configuration")
                
                # Dynamically create configuration UI based on tool config
                for config_key, config_value in tool["config"].items():
                    config_label = config_key.replace("_", " ").title()
                    
                    if isinstance(config_value, bool):
                        new_value = st.checkbox(
                            config_label,
                            value=config_value,
                            key=f"{tool_id}_{config_key}"
                        )
                    elif isinstance(config_value, int):
                        new_value = st.number_input(
                            config_label,
                            value=config_value,
                            key=f"{tool_id}_{config_key}"
                        )
                    elif isinstance(config_value, list):
                        if len(config_value) > 0 and isinstance(config_value[0], str):
                            new_value = st.multiselect(
                                config_label,
                                options=config_value,
                                default=config_value,
                                key=f"{tool_id}_{config_key}"
                            )
                        else:
                            new_value = st.text_area(
                                config_label,
                                value=", ".join(map(str, config_value)),
                                key=f"{tool_id}_{config_key}",
                                height=100
                            )
                    else:
                        new_value = st.text_input(
                            config_label,
                            value=str(config_value),
                            key=f"{tool_id}_{config_key}"
                        )
                    
                    st.session_state.available_tools[tool_id]["config"][config_key] = new_value
                
                # Tool permissions
                st.markdown("---")
                st.subheader("🔒 Permissions")
                
                col1, col2 = st.columns(2)
                with col1:
                    require_confirmation = st.checkbox(
                        "Require user confirmation",
                        value=False,
                        key=f"{tool_id}_confirm"
                    )
                with col2:
                    auto_retry = st.checkbox(
                        "Auto-retry on failure",
                        value=True,
                        key=f"{tool_id}_retry"
                    )
                
                # Usage limits
                st.markdown("---")
                st.subheader("📊 Usage Limits")
                
                col1, col2 = st.columns(2)
                with col1:
                    max_calls_per_session = st.number_input(
                        "Max calls per session",
                        min_value=1,
                        value=100,
                        key=f"{tool_id}_max_calls"
                    )
                with col2:
                    cooldown_seconds = st.number_input(
                        "Cooldown (seconds)",
                        min_value=0,
                        value=0,
                        key=f"{tool_id}_cooldown"
                    )

# Tab 2: Add Custom Tool
with tab2:
    st.header("➕ Create Custom Tool")
    st.markdown("Define a custom tool for your agent")
    
    col1, col2 = st.columns(2)
    
    with col1:
        custom_tool_id = st.text_input("Tool ID", placeholder="my_custom_tool")
        custom_tool_name = st.text_input("Tool Name", placeholder="My Custom Tool")
        custom_tool_icon = st.text_input("Icon (emoji)", value="⚡")
        custom_tool_category = st.selectbox(
            "Category",
            ["Information Retrieval", "Computation", "Development", "File Operations", 
             "Data Access", "Creative", "Communication", "Analysis", "Integration", "Memory", "Custom"]
        )
    
    with col2:
        custom_tool_description = st.text_area(
            "Description",
            placeholder="Describe what this tool does...",
            height=100
        )
        
        custom_tool_enabled = st.checkbox("Enable by default", value=True)
    
    st.markdown("---")
    st.subheader("🔧 Tool Configuration")
    
    # Allow user to define config parameters
    num_params = st.number_input("Number of configuration parameters", min_value=0, max_value=10, value=2)
    
    custom_config = {}
    for i in range(num_params):
        st.markdown(f"**Parameter {i+1}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            param_name = st.text_input(f"Name", key=f"param_name_{i}", placeholder="parameter_name")
        with col2:
            param_type = st.selectbox(f"Type", ["string", "number", "boolean", "list"], key=f"param_type_{i}")
        with col3:
            param_default = st.text_input(f"Default", key=f"param_default_{i}", placeholder="default_value")
        
        if param_name:
            if param_type == "number":
                custom_config[param_name] = int(param_default) if param_default.isdigit() else 0
            elif param_type == "boolean":
                custom_config[param_name] = param_default.lower() == "true"
            elif param_type == "list":
                custom_config[param_name] = [x.strip() for x in param_default.split(",")] if param_default else []
            else:
                custom_config[param_name] = param_default
    
    st.markdown("---")
    
    if st.button("➕ Add Custom Tool", type="primary", use_container_width=True):
        if custom_tool_id and custom_tool_name:
            if custom_tool_id not in st.session_state.available_tools:
                st.session_state.available_tools[custom_tool_id] = {
                    "name": custom_tool_name,
                    "description": custom_tool_description,
                    "category": custom_tool_category,
                    "enabled": custom_tool_enabled,
                    "config": custom_config,
                    "icon": custom_tool_icon
                }
                st.success(f"✅ Tool '{custom_tool_name}' added successfully!")
                st.rerun()
            else:
                st.error(f"❌ Tool ID '{custom_tool_id}' already exists!")
        else:
            st.warning("⚠️ Please provide Tool ID and Name")

# Tab 3: Tool Execution Log
with tab3:
    st.header("📋 Tool Execution Log")
    st.markdown("Monitor tool usage and performance")
    
    # Simulated execution log
    if "tool_log" not in st.session_state:
        st.session_state.tool_log = [
            {"timestamp": "2025-12-04 10:23:45", "tool": "Web Search", "status": "Success", "duration": "1.2s", "details": "Query: 'latest AI news'"},
            {"timestamp": "2025-12-04 10:24:12", "tool": "Calculator", "status": "Success", "duration": "0.1s", "details": "Expression: 'sqrt(144)'"},
            {"timestamp": "2025-12-04 10:25:33", "tool": "File Reader", "status": "Success", "duration": "0.5s", "details": "File: data.csv"},
            {"timestamp": "2025-12-04 10:26:45", "tool": "Code Executor", "status": "Error", "duration": "2.1s", "details": "Error: Timeout exceeded"},
            {"timestamp": "2025-12-04 10:27:18", "tool": "Web Search", "status": "Success", "duration": "1.5s", "details": "Query: 'Python best practices'"},
        ]
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_tool = st.selectbox("Filter by Tool", ["All"] + [tool["name"] for tool in st.session_state.available_tools.values()])
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All", "Success", "Error", "Pending"])
    with col3:
        max_entries = st.number_input("Max Entries", 5, 100, 20)
    
    st.markdown("---")
    
    # Display log entries
    for log_entry in st.session_state.tool_log[:max_entries]:
        if (filter_tool == "All" or log_entry["tool"] == filter_tool) and \
           (filter_status == "All" or log_entry["status"] == filter_status):
            
            status_icon = "✅" if log_entry["status"] == "Success" else "❌"
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    st.markdown(f"**{log_entry['timestamp']}**")
                with col2:
                    st.markdown(f"🔧 {log_entry['tool']}")
                with col3:
                    st.markdown(f"{status_icon} {log_entry['status']}")
                with col4:
                    st.markdown(f"⏱️ {log_entry['duration']}")
                
                st.caption(log_entry['details'])
                st.markdown("---")
    
    # Export log
    if st.button("📥 Export Log", use_container_width=True):
        log_json = json.dumps(st.session_state.tool_log, indent=2)
        st.download_button(
            "Download Log",
            log_json,
            file_name="tool_execution_log.json",
            mime="application/json",
            use_container_width=True
        )

# Footer - Export/Import Tools Configuration
st.markdown("---")
st.subheader("💾 Configuration Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Export Tools Configuration**")
    tools_config_json = json.dumps(st.session_state.available_tools, indent=2)
    st.download_button(
        "📥 Download Tools Config",
        tools_config_json,
        file_name="tools_config.json",
        mime="application/json",
        use_container_width=True
    )

with col2:
    st.markdown("**Import Tools Configuration**")
    uploaded_config = st.file_uploader("Upload Tools Config JSON", type=['json'])
    if uploaded_config is not None:
        try:
            loaded_tools = json.load(uploaded_config)
            if st.button("Apply Imported Config", use_container_width=True):
                st.session_state.available_tools = loaded_tools
                st.success("✅ Tools configuration imported successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"❌ Error loading configuration: {str(e)}")
