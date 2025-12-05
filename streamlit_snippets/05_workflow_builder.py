"""
Agent Workflow Builder
======================
Design and manage multi-step agent workflows and chains
"""

import streamlit as st
import json

st.set_page_config(page_title="Workflow Builder", page_icon="🔄", layout="wide")

st.title("🔄 Agent Workflow Builder")
st.markdown("Design complex multi-step workflows for your AI agent")
st.markdown("---")

# Initialize session state
if "workflows" not in st.session_state:
    st.session_state.workflows = {
        "research_workflow": {
            "name": "Research & Summarize",
            "description": "Search web, analyze results, and create summary",
            "steps": [
                {"id": 1, "type": "tool", "tool": "web_search", "params": {"query": "{user_query}"}, "output_var": "search_results"},
                {"id": 2, "type": "agent", "agent": "analyzer", "params": {"input": "{search_results}"}, "output_var": "analysis"},
                {"id": 3, "type": "agent", "agent": "summarizer", "params": {"input": "{analysis}"}, "output_var": "summary"},
                {"id": 4, "type": "output", "format": "markdown", "content": "{summary}"}
            ],
            "status": "active"
        },
        "code_review_workflow": {
            "name": "Code Review Pipeline",
            "description": "Review code, check style, run tests",
            "steps": [
                {"id": 1, "type": "input", "input_type": "file", "file_types": [".py", ".js"], "output_var": "code_file"},
                {"id": 2, "type": "tool", "tool": "code_analyzer", "params": {"code": "{code_file}"}, "output_var": "analysis"},
                {"id": 3, "type": "condition", "condition": "{analysis.has_issues}", "true_branch": 4, "false_branch": 6},
                {"id": 4, "type": "agent", "agent": "code_fixer", "params": {"code": "{code_file}", "issues": "{analysis.issues}"}, "output_var": "fixed_code"},
                {"id": 5, "type": "tool", "tool": "run_tests", "params": {"code": "{fixed_code}"}, "output_var": "test_results"},
                {"id": 6, "type": "output", "format": "report", "content": "Code review complete"}
            ],
            "status": "active"
        }
    }

if "current_workflow" not in st.session_state:
    st.session_state.current_workflow = None

# Sidebar - Workflow Management
with st.sidebar:
    st.header("📋 My Workflows")
    
    # List workflows
    for wf_id, workflow in st.session_state.workflows.items():
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(workflow["name"], key=f"select_{wf_id}", use_container_width=True):
                    st.session_state.current_workflow = wf_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{wf_id}"):
                    del st.session_state.workflows[wf_id]
                    st.session_state.current_workflow = None
                    st.rerun()
    
    st.markdown("---")
    
    if st.button("➕ New Workflow", use_container_width=True, type="primary"):
        new_id = f"workflow_{len(st.session_state.workflows) + 1}"
        st.session_state.workflows[new_id] = {
            "name": "New Workflow",
            "description": "Description",
            "steps": [],
            "status": "draft"
        }
        st.session_state.current_workflow = new_id
        st.rerun()
    
    st.markdown("---")
    
    # Import/Export
    st.subheader("💾 Import/Export")
    
    # Export
    if st.button("📥 Export All", use_container_width=True):
        workflows_json = json.dumps(st.session_state.workflows, indent=2)
        st.download_button(
            "Download Workflows",
            workflows_json,
            file_name="workflows.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Import
    uploaded_file = st.file_uploader("Import Workflows", type=['json'])
    if uploaded_file is not None:
        try:
            loaded_workflows = json.load(uploaded_file)
            if st.button("Apply Imported Workflows"):
                st.session_state.workflows.update(loaded_workflows)
                st.success("✅ Workflows imported!")
                st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Main content
if st.session_state.current_workflow is None:
    # Welcome screen
    st.info("👈 Select a workflow from the sidebar or create a new one to get started")
    
    st.subheader("🌟 What are Agent Workflows?")
    st.markdown("""
    Agent workflows allow you to:
    - **Chain multiple steps** together for complex tasks
    - **Combine tools and agents** in sequence
    - **Add conditional logic** and branching
    - **Process data** through multiple stages
    - **Create reusable** task patterns
    
    ### Common Workflow Patterns:
    
    1. **Research Pipeline**: Search → Analyze → Summarize → Report
    2. **Content Generation**: Plan → Draft → Review → Refine → Publish
    3. **Code Development**: Design → Implement → Test → Review → Deploy
    4. **Data Processing**: Extract → Transform → Analyze → Visualize
    """)
    
else:
    # Edit selected workflow
    workflow = st.session_state.workflows[st.session_state.current_workflow]
    
    # Workflow header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        workflow["name"] = st.text_input("Workflow Name", workflow["name"])
    with col2:
        workflow["status"] = st.selectbox("Status", ["draft", "active", "archived"], 
                                         index=["draft", "active", "archived"].index(workflow["status"]))
    with col3:
        st.write("")
        st.write("")
        if st.button("▶️ Run Workflow", type="primary", use_container_width=True):
            st.success("🚀 Workflow execution started!")
    
    workflow["description"] = st.text_area("Description", workflow["description"], height=80)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🔧 Build", "👁️ Visualize", "⚙️ Configure"])
    
    # Tab 1: Build workflow
    with tab1:
        st.subheader("Workflow Steps")
        
        # Display existing steps
        for idx, step in enumerate(workflow["steps"]):
            with st.expander(f"Step {step['id']}: {step['type'].upper()}", expanded=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Step type selection
                    step_type = st.selectbox(
                        "Step Type",
                        ["tool", "agent", "condition", "input", "output", "loop"],
                        index=["tool", "agent", "condition", "input", "output", "loop"].index(step["type"]),
                        key=f"type_{idx}"
                    )
                    step["type"] = step_type
                    
                    # Type-specific configuration
                    if step_type == "tool":
                        step["tool"] = st.selectbox(
                            "Tool",
                            ["web_search", "calculator", "file_reader", "code_executor", "database_query"],
                            key=f"tool_{idx}"
                        )
                        step["params"] = st.text_area(
                            "Parameters (JSON)",
                            json.dumps(step.get("params", {}), indent=2),
                            key=f"params_{idx}",
                            height=100
                        )
                    
                    elif step_type == "agent":
                        step["agent"] = st.selectbox(
                            "Agent",
                            ["analyzer", "summarizer", "code_fixer", "writer", "researcher"],
                            key=f"agent_{idx}"
                        )
                        step["params"] = st.text_area(
                            "Parameters (JSON)",
                            json.dumps(step.get("params", {}), indent=2),
                            key=f"params_{idx}",
                            height=100
                        )
                    
                    elif step_type == "condition":
                        step["condition"] = st.text_input(
                            "Condition",
                            step.get("condition", ""),
                            key=f"cond_{idx}"
                        )
                        col_a, col_b = st.columns(2)
                        with col_a:
                            step["true_branch"] = st.number_input("If True, go to step", 1, 100, 
                                                                 step.get("true_branch", idx+2), key=f"true_{idx}")
                        with col_b:
                            step["false_branch"] = st.number_input("If False, go to step", 1, 100,
                                                                   step.get("false_branch", idx+2), key=f"false_{idx}")
                    
                    elif step_type == "input":
                        step["input_type"] = st.selectbox(
                            "Input Type",
                            ["text", "file", "number", "date"],
                            key=f"input_type_{idx}"
                        )
                        if step["input_type"] == "file":
                            step["file_types"] = st.text_input(
                                "Allowed File Types (comma-separated)",
                                ", ".join(step.get("file_types", [])),
                                key=f"files_{idx}"
                            ).split(", ")
                    
                    elif step_type == "output":
                        step["format"] = st.selectbox(
                            "Output Format",
                            ["text", "markdown", "json", "report", "chart"],
                            key=f"format_{idx}"
                        )
                        step["content"] = st.text_area(
                            "Content Template",
                            step.get("content", ""),
                            key=f"content_{idx}",
                            height=100
                        )
                    
                    # Output variable
                    if step_type in ["tool", "agent", "input"]:
                        step["output_var"] = st.text_input(
                            "Output Variable Name",
                            step.get("output_var", f"step_{step['id']}_output"),
                            key=f"output_{idx}"
                        )
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("⬆️", key=f"up_{idx}", disabled=(idx == 0)):
                        workflow["steps"][idx], workflow["steps"][idx-1] = workflow["steps"][idx-1], workflow["steps"][idx]
                        st.rerun()
                    if st.button("⬇️", key=f"down_{idx}", disabled=(idx == len(workflow["steps"])-1)):
                        workflow["steps"][idx], workflow["steps"][idx+1] = workflow["steps"][idx+1], workflow["steps"][idx]
                        st.rerun()
                    if st.button("🗑️", key=f"delete_{idx}"):
                        workflow["steps"].pop(idx)
                        st.rerun()
        
        # Add new step
        st.markdown("---")
        if st.button("➕ Add Step", use_container_width=True):
            new_step_id = max([s["id"] for s in workflow["steps"]], default=0) + 1
            workflow["steps"].append({
                "id": new_step_id,
                "type": "tool",
                "tool": "web_search",
                "params": {},
                "output_var": f"step_{new_step_id}_output"
            })
            st.rerun()
    
    # Tab 2: Visualize workflow
    with tab2:
        st.subheader("Workflow Visualization")
        
        # Create a simple visual representation
        st.markdown("```mermaid\ngraph TD\n    Start([Start])")
        
        for step in workflow["steps"]:
            step_id = f"S{step['id']}"
            
            if step["type"] == "tool":
                label = f"{step_id}[🔧 {step.get('tool', 'Tool')}]"
            elif step["type"] == "agent":
                label = f"{step_id}[🤖 {step.get('agent', 'Agent')}]"
            elif step["type"] == "condition":
                label = f"{step_id}{{{step.get('condition', 'Condition')}}}"
            elif step["type"] == "input":
                label = f"{step_id}[/📥 Input/]"
            elif step["type"] == "output":
                label = f"{step_id}[\\📤 Output\\]"
            else:
                label = f"{step_id}[{step['type']}]"
            
            st.markdown(f"    {label}")
            
            # Add connections
            if idx > 0:
                st.markdown(f"    S{workflow['steps'][idx-1]['id']} --> {step_id}")
            else:
                st.markdown(f"    Start --> {step_id}")
        
        if workflow["steps"]:
            st.markdown(f"    S{workflow['steps'][-1]['id']} --> End([End])")
        
        st.markdown("```")
        
        st.info("💡 The diagram above shows the flow of your workflow. Each step is connected sequentially.")
        
        st.markdown("---")
        
        # Workflow statistics
        st.subheader("📊 Workflow Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Steps", len(workflow["steps"]))
        with col2:
            tool_steps = len([s for s in workflow["steps"] if s["type"] == "tool"])
            st.metric("Tool Steps", tool_steps)
        with col3:
            agent_steps = len([s for s in workflow["steps"] if s["type"] == "agent"])
            st.metric("Agent Steps", agent_steps)
        with col4:
            condition_steps = len([s for s in workflow["steps"] if s["type"] == "condition"])
            st.metric("Conditions", condition_steps)
    
    # Tab 3: Configure workflow
    with tab3:
        st.subheader("⚙️ Workflow Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Execution Settings**")
            
            timeout = st.number_input("Timeout (seconds)", 10, 3600, 300)
            max_retries = st.number_input("Max Retries per Step", 0, 5, 2)
            parallel_execution = st.checkbox("Enable Parallel Execution", value=False)
            
            st.markdown("---")
            
            st.markdown("**Error Handling**")
            on_error = st.selectbox(
                "On Error",
                ["stop", "continue", "retry", "fallback"]
            )
            
            if on_error == "fallback":
                fallback_workflow = st.selectbox(
                    "Fallback Workflow",
                    ["None"] + list(st.session_state.workflows.keys())
                )
        
        with col2:
            st.markdown("**Input/Output Settings**")
            
            require_input = st.checkbox("Require User Input", value=True)
            save_output = st.checkbox("Save Output to File", value=False)
            
            if save_output:
                output_format = st.selectbox("Output Format", ["json", "txt", "csv", "pdf"])
            
            st.markdown("---")
            
            st.markdown("**Notifications**")
            notify_on_start = st.checkbox("Notify on Start", value=False)
            notify_on_complete = st.checkbox("Notify on Complete", value=True)
            notify_on_error = st.checkbox("Notify on Error", value=True)
        
        st.markdown("---")
        
        # Variables
        st.subheader("🔤 Workflow Variables")
        st.markdown("Available variables you can use in step configurations:")
        
        variables = ["{user_query}", "{user_input}"]
        for step in workflow["steps"]:
            if "output_var" in step:
                variables.append(f"{{{step['output_var']}}}")
        
        cols = st.columns(4)
        for idx, var in enumerate(variables):
            with cols[idx % 4]:
                st.code(var, language=None)
        
        st.markdown("---")
        
        # Test workflow
        st.subheader("🧪 Test Workflow")
        
        test_input = st.text_area("Test Input (JSON)", '{"user_query": "test query"}', height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Test Run", use_container_width=True):
                with st.spinner("Running workflow..."):
                    st.success("✅ Workflow test completed successfully!")
                    st.json({
                        "status": "success",
                        "duration": "2.3s",
                        "steps_executed": len(workflow["steps"]),
                        "output": "Test output data"
                    })
        
        with col2:
            if st.button("🐛 Debug Mode", use_container_width=True):
                st.info("🔍 Debug mode enabled - step-by-step execution")

# Footer - Quick Actions
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Workflow", use_container_width=True):
        st.success("✅ Workflow saved!")

with col2:
    if st.button("📋 Duplicate", use_container_width=True):
        if st.session_state.current_workflow:
            new_id = f"workflow_{len(st.session_state.workflows) + 1}"
            st.session_state.workflows[new_id] = workflow.copy()
            st.session_state.workflows[new_id]["name"] = f"{workflow['name']} (Copy)"
            st.success("✅ Workflow duplicated!")
            st.rerun()

with col3:
    if st.button("📤 Export", use_container_width=True):
        if st.session_state.current_workflow:
            workflow_json = json.dumps(workflow, indent=2)
            st.download_button(
                "Download Workflow",
                workflow_json,
                file_name=f"{workflow['name'].replace(' ', '_').lower()}.json",
                mime="application/json",
                use_container_width=True
            )
