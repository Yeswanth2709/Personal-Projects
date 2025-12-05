"""
MCP Server - API Integration Hub
=================================
Enterprise API integration server for connecting with external services.
Provides unified interface for REST APIs, webhooks, and third-party services.

Industry Use Case: E-commerce, SaaS Platforms, Marketing Automation, Fintech
"""

import asyncio
import json
from typing import Any, Optional
from datetime import datetime
import hashlib
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Initialize MCP server
server = Server("api-integration-server")

# Configuration
CONFIG = {
    "rate_limit_per_minute": 60,
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "supported_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"]
}

# API configurations storage
api_configs = {
    "stripe": {
        "name": "Stripe Payment API",
        "base_url": "https://api.stripe.com/v1",
        "auth_type": "bearer",
        "endpoints": ["customers", "payments", "subscriptions"]
    },
    "sendgrid": {
        "name": "SendGrid Email API",
        "base_url": "https://api.sendgrid.com/v3",
        "auth_type": "bearer",
        "endpoints": ["mail/send", "templates", "contacts"]
    },
    "slack": {
        "name": "Slack API",
        "base_url": "https://slack.com/api",
        "auth_type": "bearer",
        "endpoints": ["chat.postMessage", "users.list", "channels.list"]
    },
    "github": {
        "name": "GitHub API",
        "base_url": "https://api.github.com",
        "auth_type": "token",
        "endpoints": ["repos", "issues", "pulls"]
    }
}

# Request history
request_history = []

# Webhook configurations
webhooks = {}


def simulate_api_request(method: str, url: str, headers: dict, body: Optional[dict] = None) -> dict:
    """Simulate API request (in production, use requests or httpx)"""
    
    # Simulate successful response
    response = {
        "status_code": 200,
        "headers": {
            "content-type": "application/json",
            "x-request-id": hashlib.md5(url.encode()).hexdigest()[:16]
        },
        "body": {
            "success": True,
            "message": f"Simulated {method} request to {url}",
            "data": {"id": "sim_123", "timestamp": datetime.now().isoformat()}
        },
        "response_time_ms": 145
    }
    
    # Log request
    request_history.append({
        "timestamp": datetime.now().isoformat(),
        "method": method,
        "url": url,
        "status": response["status_code"],
        "response_time_ms": response["response_time_ms"]
    })
    
    return response


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available API integration resources"""
    resources = [
        Resource(
            uri="api://configs",
            name="API Configurations",
            mimeType="application/json",
            description="List of all configured API integrations"
        ),
        Resource(
            uri="api://request-history",
            name="Request History",
            mimeType="application/json",
            description="History of API requests made"
        ),
        Resource(
            uri="api://webhooks",
            name="Webhook Configurations",
            mimeType="application/json",
            description="Configured webhooks and their status"
        ),
        Resource(
            uri="api://rate-limits",
            name="Rate Limit Status",
            mimeType="application/json",
            description="Current rate limit status for all APIs"
        )
    ]
    
    # Add individual API configs
    for api_id, api_config in api_configs.items():
        resources.append(
            Resource(
                uri=f"api://{api_id}",
                name=api_config["name"],
                mimeType="application/json",
                description=f"Configuration for {api_config['name']}"
            )
        )
    
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read API integration resources"""
    
    if uri == "api://configs":
        return json.dumps(api_configs, indent=2)
    
    elif uri == "api://request-history":
        return json.dumps(request_history[-100:], indent=2)  # Last 100 requests
    
    elif uri == "api://webhooks":
        return json.dumps(webhooks, indent=2)
    
    elif uri == "api://rate-limits":
        rate_limits = {
            "per_minute": CONFIG["rate_limit_per_minute"],
            "current_usage": len([r for r in request_history if r["timestamp"] > datetime.now().isoformat()]),
            "apis": {
                api_id: {
                    "name": api_config["name"],
                    "requests_today": len([r for r in request_history if api_id in r.get("url", "")]),
                    "status": "healthy"
                }
                for api_id, api_config in api_configs.items()
            }
        }
        return json.dumps(rate_limits, indent=2)
    
    elif uri.startswith("api://"):
        api_id = uri.replace("api://", "")
        if api_id in api_configs:
            return json.dumps(api_configs[api_id], indent=2)
        else:
            raise ValueError(f"API configuration not found: {api_id}")
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available API integration tools"""
    return [
        Tool(
            name="make_api_request",
            description="Make an HTTP request to any API endpoint with authentication and error handling",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP method"
                    },
                    "url": {
                        "type": "string",
                        "description": "Full API endpoint URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers as key-value pairs"
                    },
                    "body": {
                        "type": "object",
                        "description": "Request body (for POST, PUT, PATCH)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds",
                        "default": 30
                    }
                },
                "required": ["method", "url"]
            }
        ),
        Tool(
            name="call_stripe_api",
            description="Interact with Stripe API for payments, customers, and subscriptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create_customer", "create_payment", "list_subscriptions", "cancel_subscription"],
                        "description": "Stripe action to perform"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Action-specific parameters"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="send_email",
            description="Send email using SendGrid API with templates and attachments",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    },
                    "template_id": {
                        "type": "string",
                        "description": "Optional SendGrid template ID"
                    },
                    "attachments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attachment file paths"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="post_to_slack",
            description="Post message to Slack channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Slack channel ID or name"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message text"
                    },
                    "blocks": {
                        "type": "array",
                        "description": "Optional Slack blocks for rich formatting"
                    },
                    "thread_ts": {
                        "type": "string",
                        "description": "Thread timestamp for replies"
                    }
                },
                "required": ["channel", "message"]
            }
        ),
        Tool(
            name="create_github_issue",
            description="Create an issue in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Issue description"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Issue labels"
                    },
                    "assignees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "GitHub usernames to assign"
                    }
                },
                "required": ["repo", "title", "body"]
            }
        ),
        Tool(
            name="configure_webhook",
            description="Configure a webhook endpoint to receive events from external services",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Webhook name/identifier"
                    },
                    "url": {
                        "type": "string",
                        "description": "Webhook URL endpoint"
                    },
                    "events": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Events to subscribe to"
                    },
                    "secret": {
                        "type": "string",
                        "description": "Webhook secret for verification"
                    }
                },
                "required": ["name", "url", "events"]
            }
        ),
        Tool(
            name="batch_api_requests",
            description="Execute multiple API requests in batch with parallel processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "requests": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string"},
                                "url": {"type": "string"},
                                "headers": {"type": "object"},
                                "body": {"type": "object"}
                            }
                        },
                        "description": "Array of request configurations"
                    },
                    "parallel": {
                        "type": "boolean",
                        "description": "Execute requests in parallel",
                        "default": True
                    }
                },
                "required": ["requests"]
            }
        ),
        Tool(
            name="api_health_check",
            description="Check health status of configured APIs",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of API IDs to check (empty for all)"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute API integration tools"""
    
    if name == "make_api_request":
        method = arguments.get("method", "GET")
        url = arguments.get("url", "")
        headers = arguments.get("headers", {})
        body = arguments.get("body")
        timeout = arguments.get("timeout", 30)
        
        # Simulate API request
        response = simulate_api_request(method, url, headers, body)
        
        result = {
            "request": {
                "method": method,
                "url": url,
                "headers": headers,
                "body": body
            },
            "response": response
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "call_stripe_api":
        action = arguments.get("action", "")
        parameters = arguments.get("parameters", {})
        
        # Simulate Stripe API calls
        if action == "create_customer":
            result = {
                "action": action,
                "customer": {
                    "id": "cus_simulated123",
                    "email": parameters.get("email", "customer@example.com"),
                    "created": int(datetime.now().timestamp()),
                    "name": parameters.get("name", "Customer Name")
                }
            }
        elif action == "create_payment":
            result = {
                "action": action,
                "payment": {
                    "id": "pi_simulated456",
                    "amount": parameters.get("amount", 1000),
                    "currency": parameters.get("currency", "usd"),
                    "status": "succeeded"
                }
            }
        elif action == "list_subscriptions":
            result = {
                "action": action,
                "subscriptions": [
                    {
                        "id": "sub_123",
                        "status": "active",
                        "plan": "pro_monthly",
                        "current_period_end": int(datetime.now().timestamp()) + 2592000
                    }
                ]
            }
        else:
            result = {"error": f"Unknown action: {action}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "send_email":
        to = arguments.get("to", "")
        subject = arguments.get("subject", "")
        body = arguments.get("body", "")
        template_id = arguments.get("template_id")
        
        result = {
            "status": "sent",
            "message_id": f"msg_{hashlib.md5(to.encode()).hexdigest()[:12]}",
            "to": to,
            "subject": subject,
            "template_id": template_id,
            "timestamp": datetime.now().isoformat()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "post_to_slack":
        channel = arguments.get("channel", "")
        message = arguments.get("message", "")
        thread_ts = arguments.get("thread_ts")
        
        result = {
            "ok": True,
            "channel": channel,
            "ts": str(datetime.now().timestamp()),
            "message": {
                "text": message,
                "user": "bot_user",
                "ts": str(datetime.now().timestamp())
            }
        }
        
        if thread_ts:
            result["thread_ts"] = thread_ts
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_github_issue":
        repo = arguments.get("repo", "")
        title = arguments.get("title", "")
        body = arguments.get("body", "")
        labels = arguments.get("labels", [])
        assignees = arguments.get("assignees", [])
        
        result = {
            "number": 42,
            "title": title,
            "body": body,
            "state": "open",
            "labels": labels,
            "assignees": assignees,
            "html_url": f"https://github.com/{repo}/issues/42",
            "created_at": datetime.now().isoformat()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "configure_webhook":
        webhook_name = arguments.get("name", "")
        url = arguments.get("url", "")
        events = arguments.get("events", [])
        secret = arguments.get("secret", "")
        
        webhook_id = f"wh_{hashlib.md5(webhook_name.encode()).hexdigest()[:12]}"
        
        webhooks[webhook_id] = {
            "id": webhook_id,
            "name": webhook_name,
            "url": url,
            "events": events,
            "secret": secret,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "deliveries": 0
        }
        
        result = {
            "status": "created",
            "webhook": webhooks[webhook_id]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "batch_api_requests":
        requests = arguments.get("requests", [])
        parallel = arguments.get("parallel", True)
        
        results = []
        for req in requests:
            response = simulate_api_request(
                req.get("method", "GET"),
                req.get("url", ""),
                req.get("headers", {}),
                req.get("body")
            )
            results.append({
                "request": req,
                "response": response
            })
        
        batch_result = {
            "total_requests": len(requests),
            "parallel": parallel,
            "execution_time_ms": 450,  # Simulated
            "results": results
        }
        
        return [TextContent(type="text", text=json.dumps(batch_result, indent=2))]
    
    elif name == "api_health_check":
        api_ids = arguments.get("api_ids", list(api_configs.keys()))
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "apis": []
        }
        
        for api_id in api_ids:
            if api_id in api_configs:
                # Simulate health check
                health_status["apis"].append({
                    "api_id": api_id,
                    "name": api_configs[api_id]["name"],
                    "status": "healthy",
                    "response_time_ms": 120,
                    "last_check": datetime.now().isoformat()
                })
        
        return [TextContent(type="text", text=json.dumps(health_status, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
