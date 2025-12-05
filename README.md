# Agentic AI Streamlit Components

A comprehensive collection of Streamlit UI components for building agentic AI applications. This repository contains ready-to-use, production-quality interfaces for chat, configuration, tools, memory management, workflows, monitoring, and data input.

## 📋 Overview

This collection provides **7 complete Streamlit applications** covering all essential aspects of building and managing AI agents:

1. **Chat Interface** - Professional conversational UI
2. **Agent Configuration** - Comprehensive parameter settings
3. **Tool Management** - Tool selection and configuration
4. **Memory & Context Viewer** - Conversation and long-term memory management
5. **Workflow Builder** - Multi-step agent workflow designer
6. **Performance Dashboard** - Real-time monitoring and analytics
7. **Data Input** - File upload and data ingestion interfaces

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Create a virtual environment:**

```bash
python -m venv venv
```

2. **Activate the virtual environment:**

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install Streamlit:**

```bash
pip install streamlit
```

### Running the Applications

#### Run Individual Components

Each component can be run independently:

```bash
# Chat Interface
streamlit run streamlit_snippets/01_chat_interface.py

# Agent Configuration
streamlit run streamlit_snippets/02_agent_configuration.py

# Tool Selection
streamlit run streamlit_snippets/03_tool_selection.py

# Memory & Context Viewer
streamlit run streamlit_snippets/04_memory_context_viewer.py

# Workflow Builder
streamlit run streamlit_snippets/05_workflow_builder.py

# Performance Dashboard
streamlit run streamlit_snippets/06_monitoring_dashboard.py

# Data Input
streamlit run streamlit_snippets/07_file_upload_input.py
```

#### Run the Demo Application

To see all components showcased in a single application:

```bash
streamlit run streamlit_snippets/demo_app.py
```

## 📦 Components

### 1. 💬 Chat Interface (`01_chat_interface.py`)

A professional chat UI for AI agent conversations featuring:

- Message history with timestamps
- Streaming responses simulation
- Agent thinking process display
- Tool usage tracking
- Export conversation functionality
- Configurable chat parameters
- Clear chat history option

**Use Case:** Customer support bots, conversational assistants, interactive AI tutors

### 2. ⚙️ Agent Configuration (`02_agent_configuration.py`)

Comprehensive configuration interface for AI agents:

- Model selection (GPT-4, Claude, etc.)
- Generation parameters (temperature, top_p, etc.)
- Agent behavior and personality settings
- Memory and context management
- Safety and constraint configuration
- Save/load configuration presets
- Export/import configurations

**Use Case:** Setting up different agent personas, fine-tuning agent behavior, managing agent fleets

### 3. 🔧 Tool Management (`03_tool_selection.py`)

Select and configure tools available to your agent:

- 10+ pre-configured tools (web search, calculator, code executor, etc.)
- Custom tool creation
- Tool-specific configuration
- Permission and usage limits
- Tool execution logging
- Import/export tool configurations

**Use Case:** Enabling specific capabilities, restricting tool access, monitoring tool usage

### 4. 🧠 Memory & Context Viewer (`04_memory_context_viewer.py`)

Manage agent memory and conversation context:

- Conversation history viewer
- Long-term memory storage (facts, preferences, entities)
- Semantic memory search
- Context window management
- Memory analytics and statistics
- Export memory data

**Use Case:** Understanding agent knowledge, debugging context issues, managing persistent data

### 5. 🔄 Workflow Builder (`05_workflow_builder.py`)

Design complex multi-step agent workflows:

- Visual workflow editor
- Multiple step types (tool, agent, condition, input, output)
- Conditional branching
- Workflow visualization
- Test and debug modes
- Import/export workflows

**Use Case:** Research pipelines, content generation workflows, code review processes

### 6. 📊 Performance Dashboard (`06_monitoring_dashboard.py`)

Monitor and analyze agent performance:

- Real-time KPIs (response time, success rate, costs)
- Performance trends and charts
- Cost analysis and optimization
- Detailed request logs
- System status monitoring
- Export analytics data

**Use Case:** Production monitoring, cost optimization, performance troubleshooting

### 7. 📤 Data Input (`07_file_upload_input.py`)

Upload and prepare data for agent processing:

- File upload (multiple formats: PDF, CSV, JSON, code, images)
- Text input with formatting options
- Structured data (JSON, CSV, key-value)
- URL/API content fetching
- Database query interface
- Preview and validation

**Use Case:** Document analysis, data processing workflows, API integration

## 🎯 Features

### Universal Features Across All Components

- **Session State Management** - Persistent data across interactions
- **Export/Import** - Save and load configurations
- **Responsive Design** - Works on desktop and mobile
- **Professional UI** - Clean, modern interface design
- **Comprehensive Controls** - Detailed configuration options
- **Error Handling** - Graceful error messages and validation
- **Documentation** - Inline help and tooltips

## 🔧 Customization

All components are designed to be easily customizable:

### Styling

Modify colors, fonts, and layout by editing the custom CSS in each file or using Streamlit themes.

### Functionality

Each component uses modular code that can be easily extended:

- Add new tool types in `03_tool_selection.py`
- Implement custom workflow steps in `05_workflow_builder.py`
- Add new metrics in `06_monitoring_dashboard.py`

### Integration

Connect to real AI services:

```python
# Example: Integrate with OpenAI
import openai

def get_ai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

## 📚 Architecture

### State Management

All components use Streamlit's `session_state` for data persistence:

```python
if "variable_name" not in st.session_state:
    st.session_state.variable_name = initial_value
```

### Component Structure

Each component follows this structure:

1. **Configuration** - Page setup and styling
2. **State Initialization** - Session state management
3. **Sidebar** - Navigation and quick actions
4. **Main Content** - Tabs and primary interface
5. **Footer** - Export/import and additional actions

## 🛠️ Dependencies

- **streamlit** - Web application framework
- **pandas** - Data manipulation (optional, for data components)
- **json** - Configuration management

Install additional dependencies as needed:

```bash
pip install pandas numpy plotly  # Optional enhancements
```

## 💡 Usage Examples

### Example 1: Build a Research Assistant

1. Configure agent in `02_agent_configuration.py` with research-focused settings
2. Enable web search and document analyzer tools in `03_tool_selection.py`
3. Create a research workflow in `05_workflow_builder.py`
4. Upload documents in `07_file_upload_input.py`
5. Chat with the agent in `01_chat_interface.py`
6. Monitor performance in `06_monitoring_dashboard.py`

### Example 2: Create a Code Review Bot

1. Configure agent for code analysis
2. Enable code executor and file reader tools
3. Build code review workflow
4. Upload code files
5. Review results and monitor execution

## 🤝 Contributing

These components are designed to be educational and extensible. Feel free to:

- Modify for your specific use cases
- Add new features and capabilities
- Integrate with your preferred LLM providers
- Share improvements and extensions

## 📄 License

This code is provided as-is for educational and development purposes.

## 🐛 Troubleshooting

### Common Issues

**Issue:** Import errors

```bash
# Solution: Ensure Streamlit is installed
pip install streamlit --upgrade
```

**Issue:** Port already in use

```bash
# Solution: Specify a different port
streamlit run app.py --server.port 8502
```

**Issue:** Session state not persisting

```bash
# Solution: Don't use st.rerun() unnecessarily, check state initialization
```

## 📞 Support

For issues, questions, or suggestions:

- Check the inline documentation in each file
- Review Streamlit documentation: https://docs.streamlit.io
- Experiment with the demo app to understand component interactions

## 🎓 Learning Resources

- **Streamlit Documentation**: https://docs.streamlit.io
- **Building AI Agents**: Research agent frameworks like LangChain, AutoGPT
- **UI/UX Best Practices**: Follow modern web design principles

## 🚀 Next Steps

1. **Explore Each Component** - Run each file individually to understand its functionality
2. **Customize** - Modify components to match your specific requirements
3. **Integrate** - Connect to real AI services (OpenAI, Anthropic, local models)
4. **Extend** - Add new features, tools, and capabilities
5. **Deploy** - Use Streamlit Cloud or your own hosting for production deployment

---

**Built with ❤️ using Streamlit**

Happy building! 🤖✨
