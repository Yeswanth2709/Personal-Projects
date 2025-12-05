"""
File Upload & Data Input UI
============================
Upload files, input data, and prepare content for agent processing
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Data Input", page_icon="📤", layout="wide")

st.title("📤 Data Input & File Upload")
st.markdown("Upload files and provide data for your AI agent to process")
st.markdown("---")

# Initialize session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "input_data" not in st.session_state:
    st.session_state.input_data = {}

# Sidebar - Upload History
with st.sidebar:
    st.header("📚 Upload History")
    
    st.metric("Total Uploads", len(st.session_state.uploaded_files))
    
    if st.session_state.uploaded_files:
        st.markdown("**Recent Uploads:**")
        for idx, file_info in enumerate(st.session_state.uploaded_files[-5:]):
            with st.container():
                st.caption(f"📄 {file_info['name']}")
                st.caption(f"   {file_info['size']} - {file_info['timestamp']}")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.uploaded_files = []
        st.session_state.input_data = {}
        st.success("✅ History cleared")
        st.rerun()

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📁 File Upload",
    "✏️ Text Input",
    "📊 Structured Data",
    "🌐 URL/API",
    "📋 Preview & Send"
])

# Tab 1: File Upload
with tab1:
    st.header("📁 File Upload")
    
    # File upload section
    st.subheader("Upload Files")
    
    upload_mode = st.radio(
        "Upload Mode",
        ["Single File", "Multiple Files", "Folder"],
        horizontal=True
    )
    
    if upload_mode == "Single File":
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["txt", "pdf", "docx", "csv", "xlsx", "json", "py", "js", "md", "png", "jpg"],
            help="Supported formats: Text, PDF, Word, CSV, Excel, JSON, Code, Images"
        )
        
        if uploaded_file is not None:
            # Display file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Name", uploaded_file.name)
            with col2:
                st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
            with col3:
                st.metric("File Type", uploaded_file.type)
            
            st.markdown("---")
            
            # File processing options
            st.subheader("Processing Options")
            
            col1, col2 = st.columns(2)
            with col1:
                extract_text = st.checkbox("Extract text content", value=True)
                extract_metadata = st.checkbox("Extract metadata", value=True)
            with col2:
                chunk_content = st.checkbox("Chunk content for processing", value=False)
                if chunk_content:
                    chunk_size = st.number_input("Chunk size (characters)", 500, 5000, 1000)
            
            st.markdown("---")
            
            # Preview content
            if st.button("🔍 Preview Content", use_container_width=True):
                with st.expander("File Preview", expanded=True):
                    try:
                        if uploaded_file.type == "text/plain" or uploaded_file.name.endswith((".txt", ".md", ".py", ".js")):
                            content = uploaded_file.read().decode("utf-8")
                            st.code(content[:1000] + ("..." if len(content) > 1000 else ""), language=None)
                        elif uploaded_file.name.endswith(".csv"):
                            df = pd.read_csv(uploaded_file)
                            st.dataframe(df.head(10))
                        elif uploaded_file.name.endswith(".json"):
                            content = json.loads(uploaded_file.read().decode("utf-8"))
                            st.json(content)
                        else:
                            st.info("Preview not available for this file type")
                    except Exception as e:
                        st.error(f"Error previewing file: {str(e)}")
            
            # Save file
            if st.button("💾 Save to Agent Context", type="primary", use_container_width=True):
                file_info = {
                    "name": uploaded_file.name,
                    "size": f"{uploaded_file.size / 1024:.2f} KB",
                    "type": uploaded_file.type,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.uploaded_files.append(file_info)
                st.session_state.input_data["file_upload"] = file_info
                st.success(f"✅ File '{uploaded_file.name}' saved successfully!")
    
    elif upload_mode == "Multiple Files":
        uploaded_files = st.file_uploader(
            "Choose multiple files",
            type=["txt", "pdf", "docx", "csv", "xlsx", "json", "py", "js", "md"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.success(f"📚 {len(uploaded_files)} files uploaded")
            
            # Display files in a table
            files_data = []
            for file in uploaded_files:
                files_data.append({
                    "Name": file.name,
                    "Size (KB)": f"{file.size / 1024:.2f}",
                    "Type": file.type
                })
            
            st.dataframe(pd.DataFrame(files_data), use_container_width=True)
            
            if st.button("💾 Save All Files", type="primary", use_container_width=True):
                for file in uploaded_files:
                    file_info = {
                        "name": file.name,
                        "size": f"{file.size / 1024:.2f} KB",
                        "type": file.type,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.uploaded_files.append(file_info)
                st.success(f"✅ {len(uploaded_files)} files saved successfully!")
    
    else:  # Folder upload
        st.info("📁 Folder upload: Drag and drop a folder or use the file picker to select multiple files from a folder")
        folder_files = st.file_uploader(
            "Select files from folder",
            accept_multiple_files=True
        )
        
        if folder_files:
            st.success(f"📂 {len(folder_files)} files from folder")

# Tab 2: Text Input
with tab2:
    st.header("✏️ Text Input")
    
    input_type = st.selectbox(
        "Input Type",
        ["Free Text", "Formatted Text", "Code", "Prompt Template"]
    )
    
    if input_type == "Free Text":
        st.subheader("Enter Your Text")
        text_input = st.text_area(
            "Text Content",
            height=300,
            placeholder="Enter your text here...\n\nYou can write multiple paragraphs, instructions, or any content you want the agent to process."
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Characters", len(text_input))
        with col2:
            st.metric("Words", len(text_input.split()))
        with col3:
            st.metric("Lines", len(text_input.split("\n")))
        
        if st.button("💾 Save Text", use_container_width=True):
            st.session_state.input_data["text_input"] = text_input
            st.success("✅ Text saved!")
    
    elif input_type == "Formatted Text":
        st.subheader("Markdown Editor")
        markdown_text = st.text_area(
            "Markdown Content",
            height=300,
            placeholder="# Heading\n\n**Bold text**\n\n- List item 1\n- List item 2\n\n```python\ncode here\n```"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Preview:**")
            st.markdown(markdown_text)
        with col2:
            if st.button("💾 Save Markdown", use_container_width=True):
                st.session_state.input_data["markdown_input"] = markdown_text
                st.success("✅ Markdown saved!")
    
    elif input_type == "Code":
        st.subheader("Code Editor")
        
        language = st.selectbox(
            "Programming Language",
            ["python", "javascript", "java", "c", "cpp", "sql", "html", "css", "bash"]
        )
        
        code_input = st.text_area(
            f"{language.upper()} Code",
            height=300,
            placeholder=f"Enter your {language} code here..."
        )
        
        st.code(code_input, language=language)
        
        if st.button("💾 Save Code", use_container_width=True):
            st.session_state.input_data["code_input"] = {
                "language": language,
                "code": code_input
            }
            st.success("✅ Code saved!")
    
    else:  # Prompt Template
        st.subheader("Prompt Template Builder")
        
        st.markdown("**System Prompt:**")
        system_prompt = st.text_area(
            "System instructions",
            "You are a helpful AI assistant.",
            height=100
        )
        
        st.markdown("**User Prompt Template:**")
        user_prompt = st.text_area(
            "User message template (use {variables})",
            "Please analyze the following {data_type}:\n\n{content}",
            height=150
        )
        
        st.markdown("**Variables:**")
        num_vars = st.number_input("Number of variables", 1, 10, 2)
        
        variables = {}
        for i in range(num_vars):
            col1, col2 = st.columns(2)
            with col1:
                var_name = st.text_input(f"Variable {i+1} name", key=f"var_name_{i}")
            with col2:
                var_value = st.text_input(f"Value", key=f"var_value_{i}")
            if var_name:
                variables[var_name] = var_value
        
        st.markdown("---")
        st.markdown("**Rendered Prompt:**")
        try:
            rendered = user_prompt.format(**variables)
            st.info(rendered)
        except KeyError as e:
            st.warning(f"⚠️ Missing variable: {e}")
        
        if st.button("💾 Save Prompt Template", use_container_width=True):
            st.session_state.input_data["prompt_template"] = {
                "system": system_prompt,
                "user": user_prompt,
                "variables": variables
            }
            st.success("✅ Prompt template saved!")

# Tab 3: Structured Data
with tab3:
    st.header("📊 Structured Data Input")
    
    data_format = st.selectbox(
        "Data Format",
        ["JSON", "CSV", "Key-Value Pairs", "Form Builder"]
    )
    
    if data_format == "JSON":
        st.subheader("JSON Data Editor")
        
        json_input = st.text_area(
            "JSON Content",
            '{\n  "key": "value",\n  "items": [1, 2, 3],\n  "nested": {\n    "field": "data"\n  }\n}',
            height=300
        )
        
        # Validate JSON
        try:
            parsed_json = json.loads(json_input)
            st.success("✅ Valid JSON")
            
            with st.expander("Formatted View"):
                st.json(parsed_json)
            
            if st.button("💾 Save JSON", use_container_width=True):
                st.session_state.input_data["json_data"] = parsed_json
                st.success("✅ JSON data saved!")
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {str(e)}")
    
    elif data_format == "CSV":
        st.subheader("CSV Data Editor")
        
        csv_input = st.text_area(
            "CSV Content",
            "Name,Age,City\nJohn,30,New York\nJane,25,Los Angeles\nBob,35,Chicago",
            height=200
        )
        
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(csv_input))
            
            st.success("✅ Valid CSV")
            st.dataframe(df, use_container_width=True)
            
            if st.button("💾 Save CSV Data", use_container_width=True):
                st.session_state.input_data["csv_data"] = df.to_dict()
                st.success("✅ CSV data saved!")
        except Exception as e:
            st.error(f"❌ Invalid CSV: {str(e)}")
    
    elif data_format == "Key-Value Pairs":
        st.subheader("Key-Value Data")
        
        num_pairs = st.number_input("Number of key-value pairs", 1, 20, 5)
        
        kv_data = {}
        for i in range(num_pairs):
            col1, col2 = st.columns(2)
            with col1:
                key = st.text_input(f"Key {i+1}", key=f"kv_key_{i}")
            with col2:
                value = st.text_input(f"Value {i+1}", key=f"kv_value_{i}")
            if key:
                kv_data[key] = value
        
        st.markdown("---")
        st.json(kv_data)
        
        if st.button("💾 Save Key-Value Data", use_container_width=True):
            st.session_state.input_data["kv_data"] = kv_data
            st.success("✅ Key-value data saved!")
    
    else:  # Form Builder
        st.subheader("Dynamic Form")
        
        with st.form("dynamic_form"):
            st.markdown("**User Information**")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                email = st.text_input("Email")
            with col2:
                age = st.number_input("Age", 0, 120, 25)
                country = st.selectbox("Country", ["USA", "UK", "Canada", "Other"])
            
            st.markdown("**Preferences**")
            interests = st.multiselect(
                "Interests",
                ["AI", "Machine Learning", "Web Development", "Data Science", "Mobile Apps"]
            )
            
            experience = st.slider("Years of Experience", 0, 30, 5)
            
            additional_info = st.text_area("Additional Information", height=100)
            
            submitted = st.form_submit_button("💾 Save Form Data", use_container_width=True)
            
            if submitted:
                form_data = {
                    "name": name,
                    "email": email,
                    "age": age,
                    "country": country,
                    "interests": interests,
                    "experience": experience,
                    "additional_info": additional_info
                }
                st.session_state.input_data["form_data"] = form_data
                st.success("✅ Form data saved!")

# Tab 4: URL/API
with tab4:
    st.header("🌐 URL & API Input")
    
    input_mode = st.radio(
        "Input Mode",
        ["Webpage URL", "API Endpoint", "Database Query"],
        horizontal=True
    )
    
    if input_mode == "Webpage URL":
        st.subheader("Fetch Content from URL")
        
        url = st.text_input("Enter URL", placeholder="https://example.com/article")
        
        col1, col2 = st.columns(2)
        with col1:
            extract_main_content = st.checkbox("Extract main content only", value=True)
            extract_links = st.checkbox("Extract links", value=False)
        with col2:
            extract_images = st.checkbox("Extract images", value=False)
            extract_metadata = st.checkbox("Extract metadata", value=True)
        
        if st.button("🔍 Fetch Content", use_container_width=True):
            if url:
                with st.spinner("Fetching content..."):
                    st.success(f"✅ Content fetched from {url}")
                    st.info("📄 Content preview:\n\nThis is a simulated content preview. In a real implementation, this would fetch and display the actual webpage content.")
                    
                    if st.button("💾 Save Fetched Content"):
                        st.session_state.input_data["url_content"] = {
                            "url": url,
                            "timestamp": datetime.now().isoformat()
                        }
                        st.success("✅ Content saved!")
            else:
                st.warning("⚠️ Please enter a URL")
    
    elif input_mode == "API Endpoint":
        st.subheader("API Request Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            api_url = st.text_input("API Endpoint", placeholder="https://api.example.com/data")
            method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE"])
        with col2:
            auth_type = st.selectbox("Authentication", ["None", "API Key", "Bearer Token", "Basic Auth"])
            if auth_type != "None":
                auth_value = st.text_input("Auth Value", type="password")
        
        st.markdown("**Headers:**")
        headers_input = st.text_area(
            "Headers (JSON)",
            '{\n  "Content-Type": "application/json"\n}',
            height=100
        )
        
        if method in ["POST", "PUT"]:
            st.markdown("**Request Body:**")
            body_input = st.text_area(
                "Body (JSON)",
                '{\n  "key": "value"\n}',
                height=150
            )
        
        if st.button("🚀 Send Request", use_container_width=True):
            with st.spinner("Sending request..."):
                st.success("✅ Request sent successfully")
                st.json({"status": 200, "data": "Sample response data"})
                
                if st.button("💾 Save API Response"):
                    st.session_state.input_data["api_response"] = {
                        "endpoint": api_url,
                        "method": method,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.success("✅ API response saved!")
    
    else:  # Database Query
        st.subheader("Database Query")
        
        col1, col2 = st.columns(2)
        with col1:
            db_type = st.selectbox("Database Type", ["PostgreSQL", "MySQL", "MongoDB", "SQLite"])
            connection_string = st.text_input("Connection String", type="password")
        with col2:
            database_name = st.text_input("Database Name")
            table_name = st.text_input("Table/Collection Name")
        
        query = st.text_area(
            "SQL Query",
            "SELECT * FROM table_name LIMIT 10",
            height=150
        )
        
        if st.button("▶️ Execute Query", use_container_width=True):
            with st.spinner("Executing query..."):
                st.success("✅ Query executed successfully")
                
                # Sample result
                sample_df = pd.DataFrame({
                    "id": [1, 2, 3],
                    "name": ["Alice", "Bob", "Charlie"],
                    "value": [100, 200, 300]
                })
                st.dataframe(sample_df, use_container_width=True)
                
                if st.button("💾 Save Query Results"):
                    st.session_state.input_data["db_results"] = sample_df.to_dict()
                    st.success("✅ Query results saved!")

# Tab 5: Preview & Send
with tab5:
    st.header("📋 Preview & Send to Agent")
    
    if not st.session_state.input_data:
        st.info("👈 No data available. Please input some data in the other tabs first.")
    else:
        st.subheader("Collected Data Summary")
        
        # Display all collected data
        for data_type, data_content in st.session_state.input_data.items():
            with st.expander(f"📦 {data_type.replace('_', ' ').title()}", expanded=True):
                if isinstance(data_content, dict) or isinstance(data_content, list):
                    st.json(data_content)
                else:
                    st.text(str(data_content)[:500] + ("..." if len(str(data_content)) > 500 else ""))
        
        st.markdown("---")
        
        # Processing options
        st.subheader("⚙️ Processing Options")
        
        col1, col2 = st.columns(2)
        with col1:
            processing_mode = st.selectbox(
                "Processing Mode",
                ["Immediate", "Batch", "Scheduled"]
            )
            
            if processing_mode == "Scheduled":
                schedule_time = st.time_input("Schedule Time")
        
        with col2:
            output_format = st.selectbox(
                "Output Format",
                ["JSON", "Text", "Markdown", "Report"]
            )
            
            notify_on_complete = st.checkbox("Notify when complete", value=True)
        
        st.markdown("---")
        
        # Send to agent
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Send to Agent", type="primary", use_container_width=True):
                with st.spinner("Sending data to agent..."):
                    st.success("✅ Data sent to agent successfully!")
                    st.balloons()
        
        with col2:
            if st.button("💾 Save as Preset", use_container_width=True):
                st.success("✅ Data saved as preset!")
        
        with col3:
            # Export data
            data_json = json.dumps(st.session_state.input_data, indent=2, default=str)
            st.download_button(
                "📥 Export Data",
                data_json,
                file_name=f"agent_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
