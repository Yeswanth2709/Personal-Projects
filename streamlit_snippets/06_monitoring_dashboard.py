"""
Agent Performance Monitoring Dashboard
=======================================
Monitor agent performance, track metrics, and analyze behavior
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Performance Dashboard", page_icon="📊", layout="wide")

st.title("📊 Agent Performance Dashboard")
st.markdown("Monitor and analyze your AI agent's performance in real-time")
st.markdown("---")

# Initialize session state with sample data
if "metrics_data" not in st.session_state:
    # Generate sample metrics data
    dates = pd.date_range(start="2025-12-01", end="2025-12-04", freq="1H")
    st.session_state.metrics_data = pd.DataFrame({
        "timestamp": dates,
        "response_time": [random.uniform(0.5, 3.0) for _ in range(len(dates))],
        "tokens_used": [random.randint(100, 2000) for _ in range(len(dates))],
        "success_rate": [random.uniform(0.85, 1.0) for _ in range(len(dates))],
        "cost": [random.uniform(0.001, 0.05) for _ in range(len(dates))]
    })

if "recent_requests" not in st.session_state:
    st.session_state.recent_requests = [
        {"timestamp": "2025-12-04 10:30:45", "type": "chat", "status": "success", "duration": "1.2s", "tokens": 450, "cost": "$0.012"},
        {"timestamp": "2025-12-04 10:31:12", "type": "tool_call", "status": "success", "duration": "0.8s", "tokens": 120, "cost": "$0.003"},
        {"timestamp": "2025-12-04 10:31:45", "type": "chat", "status": "success", "duration": "1.5s", "tokens": 680, "cost": "$0.018"},
        {"timestamp": "2025-12-04 10:32:30", "type": "workflow", "status": "error", "duration": "3.2s", "tokens": 0, "cost": "$0.000"},
        {"timestamp": "2025-12-04 10:33:15", "type": "chat", "status": "success", "duration": "1.1s", "tokens": 520, "cost": "$0.014"},
    ]

# Sidebar - Time Range & Filters
with st.sidebar:
    st.header("⏱️ Time Range")
    
    time_range = st.selectbox(
        "Select Period",
        ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom"]
    )
    
    if time_range == "Custom":
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
    
    st.markdown("---")
    
    st.header("🔍 Filters")
    
    request_types = st.multiselect(
        "Request Types",
        ["chat", "tool_call", "workflow", "embedding"],
        default=["chat", "tool_call", "workflow"]
    )
    
    status_filter = st.multiselect(
        "Status",
        ["success", "error", "timeout", "rate_limited"],
        default=["success", "error"]
    )
    
    st.markdown("---")
    
    st.header("🎯 Alerts")
    st.metric("Active Alerts", "2", delta="1")
    
    with st.expander("⚠️ View Alerts"):
        st.warning("High latency detected: avg 2.8s")
        st.error("Error rate above threshold: 5.2%")
    
    st.markdown("---")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    auto_refresh = st.checkbox("Auto-refresh (30s)")

# Main Dashboard
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "⚡ Performance", "💰 Costs", "🔍 Detailed Logs"])

# Tab 1: Overview
with tab1:
    st.header("Key Performance Indicators")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = len(st.session_state.recent_requests)
        st.metric(
            "Total Requests",
            f"{total_requests:,}",
            delta="+12 from last hour",
            delta_color="normal"
        )
    
    with col2:
        avg_response_time = st.session_state.metrics_data["response_time"].mean()
        st.metric(
            "Avg Response Time",
            f"{avg_response_time:.2f}s",
            delta="-0.3s",
            delta_color="inverse"
        )
    
    with col3:
        success_rate = st.session_state.metrics_data["success_rate"].mean() * 100
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            delta="+2.1%",
            delta_color="normal"
        )
    
    with col4:
        total_cost = st.session_state.metrics_data["cost"].sum()
        st.metric(
            "Total Cost",
            f"${total_cost:.2f}",
            delta="+$0.45",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Time Series Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Response Time Trend")
        chart_data = st.session_state.metrics_data.set_index("timestamp")["response_time"]
        st.line_chart(chart_data)
    
    with col2:
        st.subheader("📊 Success Rate Trend")
        chart_data = st.session_state.metrics_data.set_index("timestamp")["success_rate"]
        st.line_chart(chart_data)
    
    st.markdown("---")
    
    # Request Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Requests by Type")
        request_counts = {
            "Chat": 45,
            "Tool Call": 23,
            "Workflow": 12,
            "Embedding": 8
        }
        st.bar_chart(request_counts)
    
    with col2:
        st.subheader("✅ Status Distribution")
        status_counts = {
            "Success": 85,
            "Error": 3,
            "Timeout": 1,
            "Rate Limited": 0
        }
        st.bar_chart(status_counts)
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("🕐 Recent Activity")
    
    for req in st.session_state.recent_requests[:10]:
        status_icon = "✅" if req["status"] == "success" else "❌"
        status_color = "green" if req["status"] == "success" else "red"
        
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
        with col1:
            st.markdown(f"{req['timestamp']}")
        with col2:
            st.markdown(f"🔧 {req['type']}")
        with col3:
            st.markdown(f":{status_color}[{status_icon} {req['status']}]")
        with col4:
            st.markdown(f"⏱️ {req['duration']}")
        with col5:
            st.markdown(f"💰 {req['cost']}")
        
        st.markdown("---")

# Tab 2: Performance Analysis
with tab2:
    st.header("⚡ Performance Analysis")
    
    # Performance Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("⏱️ Latency")
        st.metric("P50 (Median)", "1.2s")
        st.metric("P95", "2.5s")
        st.metric("P99", "3.8s")
    
    with col2:
        st.subheader("🎯 Throughput")
        st.metric("Requests/min", "15.3")
        st.metric("Requests/hour", "918")
        st.metric("Peak Load", "25 req/min")
    
    with col3:
        st.subheader("🔧 Resource Usage")
        st.metric("Avg Tokens/Request", "450")
        st.metric("Token Usage Rate", "6.9K/min")
        st.metric("Context Utilization", "67%")
    
    st.markdown("---")
    
    # Performance Over Time
    st.subheader("📈 Performance Metrics Over Time")
    
    metric_to_plot = st.selectbox(
        "Select Metric",
        ["Response Time", "Tokens Used", "Success Rate", "Cost"]
    )
    
    metric_map = {
        "Response Time": "response_time",
        "Tokens Used": "tokens_used",
        "Success Rate": "success_rate",
        "Cost": "cost"
    }
    
    chart_data = st.session_state.metrics_data.set_index("timestamp")[metric_map[metric_to_plot]]
    st.line_chart(chart_data, height=300)
    
    st.markdown("---")
    
    # Detailed Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Response Time Distribution")
        
        # Create histogram data
        hist_data = st.session_state.metrics_data["response_time"]
        st.bar_chart(hist_data.value_counts().sort_index())
    
    with col2:
        st.subheader("🔍 Performance Breakdown")
        
        breakdown_data = {
            "Agent Processing": 45,
            "Tool Execution": 30,
            "Network I/O": 15,
            "Context Loading": 10
        }
        
        for component, percentage in breakdown_data.items():
            st.progress(percentage / 100, text=f"{component}: {percentage}%")
    
    st.markdown("---")
    
    # Performance Recommendations
    st.subheader("💡 Performance Recommendations")
    
    recommendations = [
        {"priority": "High", "recommendation": "Reduce context window size to improve response time", "impact": "20% faster"},
        {"priority": "Medium", "recommendation": "Cache frequent tool results", "impact": "15% cost reduction"},
        {"priority": "Low", "recommendation": "Optimize prompt templates", "impact": "5% token savings"}
    ]
    
    for rec in recommendations:
        priority_color = {"High": "red", "Medium": "orange", "Low": "blue"}[rec["priority"]]
        col1, col2, col3 = st.columns([1, 5, 2])
        with col1:
            st.markdown(f":{priority_color}[**{rec['priority']}**]")
        with col2:
            st.markdown(rec["recommendation"])
        with col3:
            st.success(rec["impact"])

# Tab 3: Cost Analysis
with tab3:
    st.header("💰 Cost Analysis")
    
    # Cost Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Today's Cost", "$2.45", delta="+$0.35")
    with col2:
        st.metric("This Week", "$14.20", delta="+$2.10")
    with col3:
        st.metric("This Month", "$48.90", delta="+$8.50")
    with col4:
        st.metric("Projected Monthly", "$65.00")
    
    st.markdown("---")
    
    # Cost Trend
    st.subheader("📈 Cost Trend")
    cost_data = st.session_state.metrics_data.set_index("timestamp")["cost"]
    st.area_chart(cost_data)
    
    st.markdown("---")
    
    # Cost Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Cost by Component")
        
        cost_breakdown = {
            "Model API Calls": 35.20,
            "Tool Executions": 8.50,
            "Embeddings": 3.20,
            "Storage": 2.00
        }
        
        st.bar_chart(cost_breakdown)
    
    with col2:
        st.subheader("🔧 Cost by Request Type")
        
        type_costs = {
            "Chat Requests": 28.50,
            "Workflow Executions": 12.30,
            "Tool Calls": 5.80,
            "Other": 2.30
        }
        
        st.bar_chart(type_costs)
    
    st.markdown("---")
    
    # Cost Optimization
    st.subheader("💡 Cost Optimization Opportunities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎯 Potential Savings**")
        st.metric("Monthly", "$12.50")
        st.caption("19% reduction")
    
    with col2:
        st.markdown("**📊 Current Efficiency**")
        st.metric("Cost per Request", "$0.027")
        st.caption("Industry avg: $0.035")
    
    with col3:
        st.markdown("**⚡ Optimization Score**")
        st.metric("Score", "82/100")
        st.caption("Good performance")
    
    st.markdown("---")
    
    # Detailed Cost Table
    st.subheader("📋 Detailed Cost Breakdown")
    
    cost_table = pd.DataFrame({
        "Date": ["2025-12-04", "2025-12-03", "2025-12-02", "2025-12-01"],
        "Requests": [458, 392, 425, 410],
        "Tokens": ["206K", "178K", "192K", "185K"],
        "Cost": ["$2.45", "$2.10", "$2.28", "$2.20"],
        "Avg per Request": ["$0.0053", "$0.0054", "$0.0054", "$0.0054"]
    })
    
    st.dataframe(cost_table, use_container_width=True)

# Tab 4: Detailed Logs
with tab4:
    st.header("🔍 Detailed Request Logs")
    
    # Search and filters
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search logs", placeholder="Enter keywords...")
    with col2:
        log_level = st.selectbox("Log Level", ["All", "Info", "Warning", "Error"])
    with col3:
        max_logs = st.number_input("Max Entries", 10, 100, 50)
    
    st.markdown("---")
    
    # Detailed log entries
    sample_logs = [
        {
            "timestamp": "2025-12-04 10:30:45.123",
            "level": "Info",
            "type": "chat",
            "message": "User query processed successfully",
            "details": {
                "user_id": "user_123",
                "tokens_input": 45,
                "tokens_output": 405,
                "model": "gpt-4",
                "temperature": 0.7
            }
        },
        {
            "timestamp": "2025-12-04 10:31:12.456",
            "level": "Info",
            "type": "tool_call",
            "message": "Web search executed",
            "details": {
                "tool": "web_search",
                "query": "latest AI news",
                "results": 5,
                "duration": "0.8s"
            }
        },
        {
            "timestamp": "2025-12-04 10:32:30.789",
            "level": "Error",
            "type": "workflow",
            "message": "Workflow execution failed: timeout",
            "details": {
                "workflow_id": "research_workflow",
                "failed_step": 3,
                "error": "Request timeout after 30s"
            }
        }
    ]
    
    for log in sample_logs[:max_logs]:
        level_icon = {"Info": "ℹ️", "Warning": "⚠️", "Error": "❌"}[log["level"]]
        level_color = {"Info": "blue", "Warning": "orange", "Error": "red"}[log["level"]]
        
        with st.expander(f"{level_icon} [{log['timestamp']}] {log['message']}"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**Level:** :{level_color}[{log['level']}]")
                st.markdown(f"**Type:** {log['type']}")
            
            with col2:
                st.markdown("**Details:**")
                st.json(log["details"])
    
    st.markdown("---")
    
    # Export logs
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Logs (JSON)", use_container_width=True):
            logs_json = json.dumps(sample_logs, indent=2)
            st.download_button(
                "Download JSON",
                logs_json,
                file_name=f"agent_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        if st.button("📥 Export Logs (CSV)", use_container_width=True):
            logs_df = pd.DataFrame(sample_logs)
            st.download_button(
                "Download CSV",
                logs_df.to_csv(index=False),
                file_name=f"agent_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# Footer - System Status
st.markdown("---")
st.subheader("🖥️ System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Agent Status", "🟢 Online")
with col2:
    st.metric("API Health", "🟢 Healthy")
with col3:
    st.metric("Database", "🟢 Connected")
with col4:
    st.metric("Last Update", "5s ago")
