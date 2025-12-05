"""
MCP Server - Customer Support System
=====================================
Enterprise customer support server with ticket management, knowledge base,
and automated response suggestions.

Industry Use Case: Customer Service, Help Desk, Technical Support, SaaS Support
"""

import asyncio
import json
from typing import Any, Optional
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Initialize MCP server
server = Server("customer-support-server")

# Ticket database
tickets = {}
ticket_counter = 1000

# Knowledge base
knowledge_base = {
    "kb001": {
        "title": "How to reset your password",
        "category": "Account Management",
        "content": "To reset your password: 1. Go to login page 2. Click 'Forgot Password' 3. Enter your email 4. Follow instructions in email",
        "tags": ["password", "account", "login"],
        "views": 1250,
        "helpful_count": 89
    },
    "kb002": {
        "title": "Setting up two-factor authentication",
        "category": "Security",
        "content": "Enable 2FA: 1. Go to Settings > Security 2. Click 'Enable 2FA' 3. Scan QR code with authenticator app 4. Enter verification code",
        "tags": ["2fa", "security", "authentication"],
        "views": 890,
        "helpful_count": 75
    },
    "kb003": {
        "title": "Billing and subscription management",
        "category": "Billing",
        "content": "Manage billing: 1. Go to Account > Billing 2. View current plan 3. Update payment method 4. Change subscription tier",
        "tags": ["billing", "subscription", "payment"],
        "views": 2100,
        "helpful_count": 156
    }
}

# Automated responses
canned_responses = {
    "greeting": "Hello! Thank you for contacting support. How can I help you today?",
    "password_reset": "I can help you reset your password. I'll send a reset link to your registered email address.",
    "billing_inquiry": "For billing questions, please provide your account email and I'll look up your subscription details.",
    "technical_issue": "I understand you're experiencing a technical issue. Can you provide more details about what's happening?",
    "closing": "Is there anything else I can help you with today?"
}

# Support statistics
support_stats = {
    "total_tickets": 0,
    "open_tickets": 0,
    "resolved_tickets": 0,
    "avg_response_time_minutes": 15,
    "customer_satisfaction": 4.5
}


def create_ticket(customer_email: str, subject: str, description: str, priority: str = "medium") -> dict:
    """Create a new support ticket"""
    global ticket_counter, support_stats
    
    ticket_id = f"TKT-{ticket_counter}"
    ticket_counter += 1
    
    ticket = {
        "id": ticket_id,
        "customer_email": customer_email,
        "subject": subject,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "assigned_to": None,
        "messages": [],
        "tags": []
    }
    
    tickets[ticket_id] = ticket
    support_stats["total_tickets"] += 1
    support_stats["open_tickets"] += 1
    
    return ticket


def search_knowledge_base(query: str, max_results: int = 5) -> list:
    """Search knowledge base articles"""
    results = []
    query_lower = query.lower()
    
    for kb_id, article in knowledge_base.items():
        score = 0
        
        # Check title
        if query_lower in article["title"].lower():
            score += 10
        
        # Check content
        if query_lower in article["content"].lower():
            score += 5
        
        # Check tags
        for tag in article["tags"]:
            if query_lower in tag:
                score += 3
        
        if score > 0:
            results.append({
                "id": kb_id,
                "title": article["title"],
                "category": article["category"],
                "relevance_score": score,
                "snippet": article["content"][:150] + "..."
            })
    
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:max_results]


def suggest_response(ticket_description: str) -> dict:
    """Suggest automated response based on ticket content"""
    description_lower = ticket_description.lower()
    
    suggestions = []
    
    if "password" in description_lower or "login" in description_lower:
        suggestions.append({
            "type": "canned_response",
            "text": canned_responses["password_reset"],
            "confidence": 0.85
        })
        # Also suggest KB article
        kb_results = search_knowledge_base("password reset", 1)
        if kb_results:
            suggestions.append({
                "type": "knowledge_base",
                "article_id": kb_results[0]["id"],
                "title": kb_results[0]["title"],
                "confidence": 0.90
            })
    
    elif "billing" in description_lower or "payment" in description_lower or "subscription" in description_lower:
        suggestions.append({
            "type": "canned_response",
            "text": canned_responses["billing_inquiry"],
            "confidence": 0.82
        })
    
    elif "error" in description_lower or "not working" in description_lower or "broken" in description_lower:
        suggestions.append({
            "type": "canned_response",
            "text": canned_responses["technical_issue"],
            "confidence": 0.78
        })
    
    if not suggestions:
        suggestions.append({
            "type": "canned_response",
            "text": canned_responses["greeting"],
            "confidence": 0.50
        })
    
    return {
        "suggestions": suggestions,
        "recommended_action": "review_and_send"
    }


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available customer support resources"""
    resources = [
        Resource(
            uri="support://tickets",
            name="All Support Tickets",
            mimeType="application/json",
            description="Complete list of support tickets"
        ),
        Resource(
            uri="support://open-tickets",
            name="Open Tickets",
            mimeType="application/json",
            description="Currently open support tickets"
        ),
        Resource(
            uri="support://knowledge-base",
            name="Knowledge Base",
            mimeType="application/json",
            description="Support knowledge base articles"
        ),
        Resource(
            uri="support://canned-responses",
            name="Canned Responses",
            mimeType="application/json",
            description="Pre-written response templates"
        ),
        Resource(
            uri="support://statistics",
            name="Support Statistics",
            mimeType="application/json",
            description="Support metrics and KPIs"
        )
    ]
    
    # Add individual tickets
    for ticket_id, ticket in tickets.items():
        resources.append(
            Resource(
                uri=f"support://ticket/{ticket_id}",
                name=f"Ticket {ticket_id}",
                mimeType="application/json",
                description=f"{ticket['subject']} - {ticket['status']}"
            )
        )
    
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read customer support resources"""
    
    if uri == "support://tickets":
        return json.dumps(list(tickets.values()), indent=2)
    
    elif uri == "support://open-tickets":
        open_tickets = [t for t in tickets.values() if t["status"] == "open"]
        return json.dumps(open_tickets, indent=2)
    
    elif uri == "support://knowledge-base":
        return json.dumps(knowledge_base, indent=2)
    
    elif uri == "support://canned-responses":
        return json.dumps(canned_responses, indent=2)
    
    elif uri == "support://statistics":
        return json.dumps(support_stats, indent=2)
    
    elif uri.startswith("support://ticket/"):
        ticket_id = uri.replace("support://ticket/", "")
        if ticket_id in tickets:
            return json.dumps(tickets[ticket_id], indent=2)
        else:
            raise ValueError(f"Ticket not found: {ticket_id}")
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available customer support tools"""
    return [
        Tool(
            name="create_ticket",
            description="Create a new support ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_email": {
                        "type": "string",
                        "description": "Customer's email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Ticket subject/title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Ticket priority level",
                        "default": "medium"
                    }
                },
                "required": ["customer_email", "subject", "description"]
            }
        ),
        Tool(
            name="update_ticket",
            description="Update an existing ticket status or details",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID to update"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["open", "in_progress", "waiting_customer", "resolved", "closed"],
                        "description": "New ticket status"
                    },
                    "assigned_to": {
                        "type": "string",
                        "description": "Support agent to assign ticket to"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Internal notes"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="add_ticket_message",
            description="Add a message/response to a ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message content"
                    },
                    "sender": {
                        "type": "string",
                        "enum": ["customer", "agent", "system"],
                        "description": "Who is sending the message"
                    },
                    "internal": {
                        "type": "boolean",
                        "description": "Is this an internal note?",
                        "default": False
                    }
                },
                "required": ["ticket_id", "message", "sender"]
            }
        ),
        Tool(
            name="search_knowledge_base",
            description="Search knowledge base for relevant articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="suggest_response",
            description="Get AI-powered response suggestions for a ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID to analyze"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="categorize_ticket",
            description="Automatically categorize and tag a ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID to categorize"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="escalate_ticket",
            description="Escalate ticket to higher priority or management",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID to escalate"
                    },
                    "escalation_reason": {
                        "type": "string",
                        "description": "Reason for escalation"
                    },
                    "escalate_to": {
                        "type": "string",
                        "description": "Team or person to escalate to"
                    }
                },
                "required": ["ticket_id", "escalation_reason"]
            }
        ),
        Tool(
            name="generate_report",
            description="Generate support metrics report",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly", "custom"],
                        "description": "Type of report to generate"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for custom reports (ISO format)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for custom reports (ISO format)"
                    }
                },
                "required": ["report_type"]
            }
        ),
        Tool(
            name="customer_satisfaction_survey",
            description="Send satisfaction survey to customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID to send survey for"
                    },
                    "survey_type": {
                        "type": "string",
                        "enum": ["nps", "csat", "ces"],
                        "description": "Type of satisfaction survey",
                        "default": "csat"
                    }
                },
                "required": ["ticket_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute customer support tools"""
    
    if name == "create_ticket":
        customer_email = arguments.get("customer_email", "")
        subject = arguments.get("subject", "")
        description = arguments.get("description", "")
        priority = arguments.get("priority", "medium")
        
        ticket = create_ticket(customer_email, subject, description, priority)
        
        # Auto-suggest knowledge base articles
        kb_suggestions = search_knowledge_base(description, 3)
        
        result = {
            "status": "created",
            "ticket": ticket,
            "suggested_articles": kb_suggestions
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_ticket":
        ticket_id = arguments.get("ticket_id", "")
        status = arguments.get("status")
        assigned_to = arguments.get("assigned_to")
        notes = arguments.get("notes")
        
        if ticket_id not in tickets:
            return [TextContent(type="text", text=f"Error: Ticket '{ticket_id}' not found")]
        
        ticket = tickets[ticket_id]
        
        if status:
            old_status = ticket["status"]
            ticket["status"] = status
            
            # Update statistics
            if old_status == "open" and status != "open":
                support_stats["open_tickets"] -= 1
            if status == "resolved" or status == "closed":
                support_stats["resolved_tickets"] += 1
        
        if assigned_to:
            ticket["assigned_to"] = assigned_to
        
        ticket["updated_at"] = datetime.now().isoformat()
        
        if notes:
            ticket["messages"].append({
                "timestamp": datetime.now().isoformat(),
                "sender": "system",
                "message": notes,
                "internal": True
            })
        
        result = {
            "status": "updated",
            "ticket": ticket
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "add_ticket_message":
        ticket_id = arguments.get("ticket_id", "")
        message = arguments.get("message", "")
        sender = arguments.get("sender", "agent")
        internal = arguments.get("internal", False)
        
        if ticket_id not in tickets:
            return [TextContent(type="text", text=f"Error: Ticket '{ticket_id}' not found")]
        
        ticket = tickets[ticket_id]
        
        message_obj = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "message": message,
            "internal": internal
        }
        
        ticket["messages"].append(message_obj)
        ticket["updated_at"] = datetime.now().isoformat()
        
        result = {
            "status": "message_added",
            "ticket_id": ticket_id,
            "message": message_obj
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "search_knowledge_base":
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 5)
        
        results = search_knowledge_base(query, max_results)
        
        search_result = {
            "query": query,
            "results_found": len(results),
            "articles": results
        }
        
        return [TextContent(type="text", text=json.dumps(search_result, indent=2))]
    
    elif name == "suggest_response":
        ticket_id = arguments.get("ticket_id", "")
        
        if ticket_id not in tickets:
            return [TextContent(type="text", text=f"Error: Ticket '{ticket_id}' not found")]
        
        ticket = tickets[ticket_id]
        suggestions = suggest_response(ticket["description"])
        
        result = {
            "ticket_id": ticket_id,
            "suggestions": suggestions
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "categorize_ticket":
        ticket_id = arguments.get("ticket_id", "")
        
        if ticket_id not in tickets:
            return [TextContent(type="text", text=f"Error: Ticket '{ticket_id}' not found")]
        
        ticket = tickets[ticket_id]
        description_lower = ticket["description"].lower()
        
        # Auto-categorization
        tags = []
        if "password" in description_lower or "login" in description_lower:
            tags.extend(["account", "authentication"])
        if "billing" in description_lower or "payment" in description_lower:
            tags.extend(["billing", "finance"])
        if "error" in description_lower or "bug" in description_lower:
            tags.extend(["technical", "bug"])
        
        ticket["tags"] = tags
        
        result = {
            "ticket_id": ticket_id,
            "assigned_tags": tags,
            "confidence": 0.85
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "escalate_ticket":
        ticket_id = arguments.get("ticket_id", "")
        escalation_reason = arguments.get("escalation_reason", "")
        escalate_to = arguments.get("escalate_to", "senior_support")
        
        if ticket_id not in tickets:
            return [TextContent(type="text", text=f"Error: Ticket '{ticket_id}' not found")]
        
        ticket = tickets[ticket_id]
        ticket["priority"] = "urgent"
        ticket["assigned_to"] = escalate_to
        ticket["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "sender": "system",
            "message": f"Ticket escalated: {escalation_reason}",
            "internal": True
        })
        
        result = {
            "status": "escalated",
            "ticket_id": ticket_id,
            "escalated_to": escalate_to,
            "reason": escalation_reason
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "generate_report":
        report_type = arguments.get("report_type", "daily")
        
        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "total_tickets": support_stats["total_tickets"],
                "open_tickets": support_stats["open_tickets"],
                "resolved_tickets": support_stats["resolved_tickets"],
                "avg_response_time_minutes": support_stats["avg_response_time_minutes"],
                "customer_satisfaction": support_stats["customer_satisfaction"]
            },
            "ticket_breakdown": {
                "by_priority": {
                    "urgent": len([t for t in tickets.values() if t["priority"] == "urgent"]),
                    "high": len([t for t in tickets.values() if t["priority"] == "high"]),
                    "medium": len([t for t in tickets.values() if t["priority"] == "medium"]),
                    "low": len([t for t in tickets.values() if t["priority"] == "low"])
                },
                "by_status": {
                    "open": len([t for t in tickets.values() if t["status"] == "open"]),
                    "in_progress": len([t for t in tickets.values() if t["status"] == "in_progress"]),
                    "resolved": len([t for t in tickets.values() if t["status"] == "resolved"])
                }
            }
        }
        
        return [TextContent(type="text", text=json.dumps(report, indent=2))]
    
    elif name == "customer_satisfaction_survey":
        ticket_id = arguments.get("ticket_id", "")
        survey_type = arguments.get("survey_type", "csat")
        
        if ticket_id not in tickets:
            return [TextContent(type="text", text=f"Error: Ticket '{ticket_id}' not found")]
        
        ticket = tickets[ticket_id]
        
        result = {
            "status": "survey_sent",
            "ticket_id": ticket_id,
            "customer_email": ticket["customer_email"],
            "survey_type": survey_type,
            "survey_link": f"https://survey.example.com/{ticket_id}/{survey_type}",
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    # Create some sample tickets
    create_ticket("john@example.com", "Cannot reset password", "I'm unable to reset my password. The link in the email doesn't work.", "high")
    create_ticket("jane@example.com", "Billing question", "I was charged twice this month. Can you help?", "medium")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
