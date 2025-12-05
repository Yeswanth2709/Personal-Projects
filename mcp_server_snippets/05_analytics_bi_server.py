"""
MCP Server - Analytics & Business Intelligence
===============================================
Enterprise analytics server for data analysis, reporting, and insights.
Provides KPI tracking, data visualization, and predictive analytics.

Industry Use Case: Business Intelligence, Data Analytics, SaaS Metrics, E-commerce
"""

import asyncio
import json
from typing import Any, Optional
from datetime import datetime, timedelta
import random
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Initialize MCP server
server = Server("analytics-bi-server")

# Analytics data storage
analytics_data = {
    "users": [],
    "events": [],
    "revenue": [],
    "conversions": []
}

# KPI definitions
kpis = {
    "daily_active_users": {
        "name": "Daily Active Users (DAU)",
        "description": "Number of unique users active each day",
        "target": 10000,
        "current": 8500
    },
    "monthly_recurring_revenue": {
        "name": "Monthly Recurring Revenue (MRR)",
        "description": "Predictable monthly revenue from subscriptions",
        "target": 100000,
        "current": 85000
    },
    "customer_acquisition_cost": {
        "name": "Customer Acquisition Cost (CAC)",
        "description": "Cost to acquire a new customer",
        "target": 50,
        "current": 65
    },
    "customer_lifetime_value": {
        "name": "Customer Lifetime Value (CLV)",
        "description": "Predicted revenue from a customer over their lifetime",
        "target": 500,
        "current": 450
    },
    "churn_rate": {
        "name": "Churn Rate",
        "description": "Percentage of customers who cancel subscriptions",
        "target": 3.0,
        "current": 4.2
    },
    "net_promoter_score": {
        "name": "Net Promoter Score (NPS)",
        "description": "Customer satisfaction and loyalty metric",
        "target": 50,
        "current": 42
    }
}

# Reports storage
saved_reports = {}


def generate_sample_data():
    """Generate sample analytics data"""
    # User data
    for i in range(100):
        analytics_data["users"].append({
            "user_id": f"user_{i}",
            "signup_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "plan": random.choice(["free", "basic", "pro", "enterprise"]),
            "country": random.choice(["US", "UK", "CA", "DE", "FR"]),
            "status": random.choice(["active", "active", "active", "churned"])
        })
    
    # Event data
    event_types = ["page_view", "button_click", "form_submit", "purchase", "signup"]
    for i in range(500):
        analytics_data["events"].append({
            "event_id": f"evt_{i}",
            "user_id": f"user_{random.randint(0, 99)}",
            "event_type": random.choice(event_types),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
            "properties": {
                "page": random.choice(["/home", "/pricing", "/features", "/blog"]),
                "device": random.choice(["desktop", "mobile", "tablet"])
            }
        })
    
    # Revenue data
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        analytics_data["revenue"].append({
            "date": date.date().isoformat(),
            "revenue": random.randint(2000, 5000),
            "transactions": random.randint(50, 150),
            "avg_order_value": random.uniform(30, 80)
        })


def calculate_metric(metric_name: str, time_period: str = "30d") -> dict:
    """Calculate analytics metrics"""
    
    if metric_name == "user_growth":
        # Simulate user growth calculation
        return {
            "metric": "user_growth",
            "time_period": time_period,
            "value": 15.5,
            "unit": "percent",
            "trend": "up",
            "previous_period": 12.3
        }
    
    elif metric_name == "engagement_rate":
        return {
            "metric": "engagement_rate",
            "time_period": time_period,
            "value": 68.5,
            "unit": "percent",
            "trend": "up",
            "breakdown": {
                "daily_sessions": 2.3,
                "avg_session_duration_minutes": 8.5,
                "pages_per_session": 4.2
            }
        }
    
    elif metric_name == "conversion_rate":
        return {
            "metric": "conversion_rate",
            "time_period": time_period,
            "value": 3.8,
            "unit": "percent",
            "trend": "down",
            "funnel": {
                "visitors": 10000,
                "signups": 800,
                "trials": 500,
                "paid": 380
            }
        }
    
    elif metric_name == "retention_rate":
        return {
            "metric": "retention_rate",
            "time_period": time_period,
            "value": 85.0,
            "unit": "percent",
            "cohort_analysis": {
                "week_1": 92.0,
                "week_2": 88.0,
                "week_4": 85.0,
                "week_8": 82.0
            }
        }
    
    else:
        return {
            "metric": metric_name,
            "error": "Metric not found"
        }


def generate_chart_data(chart_type: str, data_source: str, time_range: str) -> dict:
    """Generate chart data for visualization"""
    
    if chart_type == "line":
        # Generate time series data
        dates = [(datetime.now() - timedelta(days=i)).date().isoformat() for i in range(30, 0, -1)]
        values = [random.randint(100, 500) for _ in range(30)]
        
        return {
            "chart_type": "line",
            "data": {
                "labels": dates,
                "datasets": [{
                    "label": data_source,
                    "data": values
                }]
            }
        }
    
    elif chart_type == "bar":
        categories = ["Product A", "Product B", "Product C", "Product D", "Product E"]
        values = [random.randint(50, 200) for _ in range(5)]
        
        return {
            "chart_type": "bar",
            "data": {
                "labels": categories,
                "datasets": [{
                    "label": data_source,
                    "data": values
                }]
            }
        }
    
    elif chart_type == "pie":
        return {
            "chart_type": "pie",
            "data": {
                "labels": ["Free", "Basic", "Pro", "Enterprise"],
                "datasets": [{
                    "data": [45, 30, 20, 5]
                }]
            }
        }
    
    else:
        return {"error": "Unsupported chart type"}


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available analytics resources"""
    resources = [
        Resource(
            uri="analytics://kpis",
            name="Key Performance Indicators",
            mimeType="application/json",
            description="All tracked KPIs and their current values"
        ),
        Resource(
            uri="analytics://users",
            name="User Data",
            mimeType="application/json",
            description="User analytics and demographics"
        ),
        Resource(
            uri="analytics://events",
            name="Event Stream",
            mimeType="application/json",
            description="User events and interactions"
        ),
        Resource(
            uri="analytics://revenue",
            name="Revenue Data",
            mimeType="application/json",
            description="Revenue and transaction data"
        ),
        Resource(
            uri="analytics://dashboards",
            name="Dashboards",
            mimeType="application/json",
            description="Saved analytics dashboards"
        ),
        Resource(
            uri="analytics://reports",
            name="Saved Reports",
            mimeType="application/json",
            description="Collection of saved reports"
        )
    ]
    
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read analytics resources"""
    
    if uri == "analytics://kpis":
        return json.dumps(kpis, indent=2)
    
    elif uri == "analytics://users":
        return json.dumps(analytics_data["users"][:50], indent=2)  # Return first 50
    
    elif uri == "analytics://events":
        return json.dumps(analytics_data["events"][:100], indent=2)  # Return first 100
    
    elif uri == "analytics://revenue":
        return json.dumps(analytics_data["revenue"], indent=2)
    
    elif uri == "analytics://dashboards":
        dashboards = {
            "executive_dashboard": {
                "name": "Executive Dashboard",
                "widgets": ["MRR", "DAU", "Churn Rate", "NPS"]
            },
            "product_dashboard": {
                "name": "Product Analytics",
                "widgets": ["Feature Usage", "User Flows", "Engagement", "Retention"]
            },
            "marketing_dashboard": {
                "name": "Marketing Dashboard",
                "widgets": ["CAC", "Conversion Rate", "Traffic Sources", "Campaign Performance"]
            }
        }
        return json.dumps(dashboards, indent=2)
    
    elif uri == "analytics://reports":
        return json.dumps(saved_reports, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available analytics tools"""
    return [
        Tool(
            name="track_event",
            description="Track a user event or interaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "event_type": {
                        "type": "string",
                        "description": "Type of event (e.g., 'button_click', 'purchase')"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Additional event properties"
                    }
                },
                "required": ["event_type"]
            }
        ),
        Tool(
            name="calculate_kpi",
            description="Calculate a specific KPI value",
            inputSchema={
                "type": "object",
                "properties": {
                    "kpi_name": {
                        "type": "string",
                        "description": "Name of the KPI to calculate"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period (e.g., '7d', '30d', '90d')",
                        "default": "30d"
                    }
                },
                "required": ["kpi_name"]
            }
        ),
        Tool(
            name="run_query",
            description="Run a custom analytics query using filters and aggregations",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_source": {
                        "type": "string",
                        "enum": ["users", "events", "revenue", "conversions"],
                        "description": "Data source to query"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Query filters"
                    },
                    "aggregations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Aggregation functions (e.g., 'count', 'sum', 'avg')"
                    },
                    "group_by": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to group by"
                    }
                },
                "required": ["data_source"]
            }
        ),
        Tool(
            name="generate_report",
            description="Generate a comprehensive analytics report",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["executive_summary", "user_analytics", "revenue_analysis", "marketing_performance", "product_metrics"],
                        "description": "Type of report to generate"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for the report",
                        "default": "30d"
                    },
                    "include_charts": {
                        "type": "boolean",
                        "description": "Include visualization charts",
                        "default": True
                    }
                },
                "required": ["report_type"]
            }
        ),
        Tool(
            name="create_funnel_analysis",
            description="Analyze conversion funnel with step-by-step metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "funnel_name": {
                        "type": "string",
                        "description": "Name of the funnel"
                    },
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Funnel steps in order"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Analysis time period",
                        "default": "30d"
                    }
                },
                "required": ["funnel_name", "steps"]
            }
        ),
        Tool(
            name="cohort_analysis",
            description="Perform cohort analysis to track user behavior over time",
            inputSchema={
                "type": "object",
                "properties": {
                    "cohort_type": {
                        "type": "string",
                        "enum": ["signup_date", "first_purchase", "plan_upgrade"],
                        "description": "Type of cohort to analyze"
                    },
                    "metric": {
                        "type": "string",
                        "enum": ["retention", "revenue", "engagement"],
                        "description": "Metric to track"
                    },
                    "time_buckets": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"],
                        "description": "Time bucket size",
                        "default": "weekly"
                    }
                },
                "required": ["cohort_type", "metric"]
            }
        ),
        Tool(
            name="ab_test_analysis",
            description="Analyze A/B test results with statistical significance",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {
                        "type": "string",
                        "description": "Name of the A/B test"
                    },
                    "variant_a": {
                        "type": "object",
                        "description": "Variant A data (control)"
                    },
                    "variant_b": {
                        "type": "object",
                        "description": "Variant B data (treatment)"
                    },
                    "metric": {
                        "type": "string",
                        "description": "Primary metric to evaluate"
                    }
                },
                "required": ["test_name", "metric"]
            }
        ),
        Tool(
            name="predict_churn",
            description="Predict user churn risk using historical data",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to analyze (optional, analyzes all if not provided)"
                    },
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Features to use for prediction"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="segment_users",
            description="Segment users based on behavior and characteristics",
            inputSchema={
                "type": "object",
                "properties": {
                    "segmentation_method": {
                        "type": "string",
                        "enum": ["rfm", "behavioral", "demographic", "value_based"],
                        "description": "Segmentation method to use"
                    },
                    "num_segments": {
                        "type": "integer",
                        "description": "Number of segments to create",
                        "default": 4
                    }
                },
                "required": ["segmentation_method"]
            }
        ),
        Tool(
            name="export_data",
            description="Export analytics data in various formats",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "enum": ["users", "events", "revenue", "custom_query"],
                        "description": "Type of data to export"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["csv", "json", "excel", "parquet"],
                        "description": "Export format",
                        "default": "csv"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply"
                    }
                },
                "required": ["data_type", "format"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute analytics tools"""
    
    if name == "track_event":
        user_id = arguments.get("user_id", "anonymous")
        event_type = arguments.get("event_type", "")
        properties = arguments.get("properties", {})
        
        event = {
            "event_id": f"evt_{len(analytics_data['events'])}",
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "properties": properties
        }
        
        analytics_data["events"].append(event)
        
        result = {
            "status": "tracked",
            "event": event
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "calculate_kpi":
        kpi_name = arguments.get("kpi_name", "")
        time_period = arguments.get("time_period", "30d")
        
        if kpi_name in kpis:
            kpi = kpis[kpi_name].copy()
            kpi["time_period"] = time_period
            kpi["last_updated"] = datetime.now().isoformat()
            
            # Add trend data
            kpi["trend"] = {
                "direction": "up" if kpi["current"] > kpi["target"] * 0.9 else "down",
                "change_percent": ((kpi["current"] - kpi["target"]) / kpi["target"] * 100)
            }
            
            return [TextContent(type="text", text=json.dumps(kpi, indent=2))]
        else:
            # Calculate custom metric
            metric_data = calculate_metric(kpi_name, time_period)
            return [TextContent(type="text", text=json.dumps(metric_data, indent=2))]
    
    elif name == "run_query":
        data_source = arguments.get("data_source", "events")
        filters = arguments.get("filters", {})
        aggregations = arguments.get("aggregations", ["count"])
        group_by = arguments.get("group_by", [])
        
        # Simulate query execution
        result = {
            "data_source": data_source,
            "filters_applied": filters,
            "results": {
                "total_rows": len(analytics_data.get(data_source, [])),
                "aggregations": {agg: random.randint(100, 1000) for agg in aggregations}
            },
            "execution_time_ms": 125
        }
        
        if group_by:
            result["results"]["groups"] = [
                {"key": f"group_{i}", "value": random.randint(10, 100)}
                for i in range(5)
            ]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "generate_report":
        report_type = arguments.get("report_type", "executive_summary")
        time_period = arguments.get("time_period", "30d")
        include_charts = arguments.get("include_charts", True)
        
        report = {
            "report_type": report_type,
            "time_period": time_period,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_users": len(analytics_data["users"]),
                "active_users": len([u for u in analytics_data["users"] if u["status"] == "active"]),
                "total_revenue": sum([r["revenue"] for r in analytics_data["revenue"]]),
                "avg_revenue_per_user": 125.50
            },
            "key_metrics": {
                "user_growth": "+15.5%",
                "revenue_growth": "+22.3%",
                "retention_rate": "85%",
                "churn_rate": "4.2%"
            }
        }
        
        if include_charts:
            report["charts"] = [
                generate_chart_data("line", "Daily Revenue", time_period),
                generate_chart_data("bar", "Users by Plan", time_period)
            ]
        
        # Save report
        report_id = f"report_{len(saved_reports)}"
        saved_reports[report_id] = report
        
        return [TextContent(type="text", text=json.dumps(report, indent=2))]
    
    elif name == "create_funnel_analysis":
        funnel_name = arguments.get("funnel_name", "")
        steps = arguments.get("steps", [])
        time_period = arguments.get("time_period", "30d")
        
        # Simulate funnel analysis
        funnel_data = {
            "funnel_name": funnel_name,
            "time_period": time_period,
            "total_users": 10000,
            "steps": []
        }
        
        remaining = 10000
        for i, step in enumerate(steps):
            conversion_rate = random.uniform(0.5, 0.9)
            remaining = int(remaining * conversion_rate)
            
            funnel_data["steps"].append({
                "step_number": i + 1,
                "step_name": step,
                "users": remaining,
                "conversion_rate": conversion_rate * 100,
                "drop_off": int((1 - conversion_rate) * 10000)
            })
        
        funnel_data["overall_conversion_rate"] = (remaining / 10000) * 100
        
        return [TextContent(type="text", text=json.dumps(funnel_data, indent=2))]
    
    elif name == "cohort_analysis":
        cohort_type = arguments.get("cohort_type", "signup_date")
        metric = arguments.get("metric", "retention")
        time_buckets = arguments.get("time_buckets", "weekly")
        
        # Simulate cohort analysis
        cohorts = []
        for i in range(8):
            cohort_date = (datetime.now() - timedelta(weeks=i)).date().isoformat()
            retention_values = [100]
            
            for week in range(1, 9):
                retention = max(20, 100 - (week * random.uniform(8, 15)))
                retention_values.append(round(retention, 1))
            
            cohorts.append({
                "cohort": cohort_date,
                "cohort_size": random.randint(200, 500),
                f"{metric}_by_week": retention_values[:min(9 - i, 9)]
            })
        
        result = {
            "cohort_type": cohort_type,
            "metric": metric,
            "time_buckets": time_buckets,
            "cohorts": cohorts
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "ab_test_analysis":
        test_name = arguments.get("test_name", "")
        metric = arguments.get("metric", "")
        
        # Simulate A/B test results
        result = {
            "test_name": test_name,
            "metric": metric,
            "variant_a": {
                "name": "Control",
                "sample_size": 5000,
                "conversions": 250,
                "conversion_rate": 5.0
            },
            "variant_b": {
                "name": "Treatment",
                "sample_size": 5000,
                "conversions": 300,
                "conversion_rate": 6.0
            },
            "results": {
                "improvement": 20.0,
                "statistical_significance": 95.5,
                "confidence_interval": [0.5, 1.5],
                "recommendation": "Deploy variant B"
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "predict_churn":
        user_id = arguments.get("user_id")
        
        if user_id:
            # Predict for single user
            prediction = {
                "user_id": user_id,
                "churn_risk": random.choice(["low", "medium", "high"]),
                "churn_probability": random.uniform(0.1, 0.9),
                "risk_factors": [
                    "Low engagement last 7 days",
                    "No feature usage this month"
                ],
                "recommended_actions": [
                    "Send re-engagement email",
                    "Offer personalized discount"
                ]
            }
            return [TextContent(type="text", text=json.dumps(prediction, indent=2))]
        else:
            # Predict for all users
            result = {
                "total_users_analyzed": len(analytics_data["users"]),
                "churn_predictions": {
                    "high_risk": random.randint(50, 150),
                    "medium_risk": random.randint(200, 400),
                    "low_risk": random.randint(500, 800)
                },
                "top_risk_factors": [
                    "Decreased login frequency",
                    "Feature abandonment",
                    "Support ticket count increase"
                ]
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "segment_users":
        segmentation_method = arguments.get("segmentation_method", "behavioral")
        num_segments = arguments.get("num_segments", 4)
        
        segments = []
        for i in range(num_segments):
            segments.append({
                "segment_id": f"seg_{i+1}",
                "segment_name": f"Segment {i+1}",
                "user_count": random.randint(100, 500),
                "characteristics": {
                    "avg_revenue": random.randint(50, 200),
                    "avg_engagement_score": random.uniform(0.3, 0.9),
                    "churn_risk": random.choice(["low", "medium", "high"])
                }
            })
        
        result = {
            "segmentation_method": segmentation_method,
            "num_segments": num_segments,
            "segments": segments,
            "total_users_segmented": sum(s["user_count"] for s in segments)
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "export_data":
        data_type = arguments.get("data_type", "users")
        export_format = arguments.get("format", "csv")
        filters = arguments.get("filters", {})
        
        result = {
            "status": "exported",
            "data_type": data_type,
            "format": export_format,
            "rows_exported": len(analytics_data.get(data_type, [])),
            "file_size_mb": random.uniform(0.5, 10.0),
            "download_url": f"https://exports.example.com/{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}",
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    # Generate sample data
    generate_sample_data()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
