"""
MCP Server - E-commerce Operations
===================================
Enterprise e-commerce server for inventory, orders, and customer management.
Provides comprehensive e-commerce functionality for online retailers.

Industry Use Case: E-commerce, Retail, Online Marketplace, Dropshipping
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
server = Server("ecommerce-operations-server")

# Product catalog
products = {}
product_counter = 1000

# Order management
orders = {}
order_counter = 5000

# Inventory tracking
inventory = {}

# Customer database
customers = {}


def init_sample_data():
    """Initialize sample e-commerce data"""
    global product_counter, order_counter
    
    # Sample products
    sample_products = [
        {"name": "Wireless Headphones", "category": "Electronics", "price": 79.99, "stock": 50},
        {"name": "Running Shoes", "category": "Footwear", "price": 89.99, "stock": 30},
        {"name": "Coffee Maker", "category": "Appliances", "price": 129.99, "stock": 20},
        {"name": "Yoga Mat", "category": "Fitness", "price": 29.99, "stock": 75},
        {"name": "Backpack", "category": "Accessories", "price": 49.99, "stock": 40}
    ]
    
    for product_data in sample_products:
        product_id = f"PRD-{product_counter}"
        product_counter += 1
        
        products[product_id] = {
            "id": product_id,
            "name": product_data["name"],
            "description": f"High-quality {product_data['name'].lower()}",
            "category": product_data["category"],
            "price": product_data["price"],
            "currency": "USD",
            "sku": f"SKU-{product_counter}",
            "images": [f"https://example.com/images/{product_id}.jpg"],
            "created_at": datetime.now().isoformat()
        }
        
        inventory[product_id] = {
            "product_id": product_id,
            "quantity": product_data["stock"],
            "reserved": 0,
            "warehouse": "Main Warehouse"
        }
    
    # Sample customers
    for i in range(5):
        customer_id = f"CUST-{1000 + i}"
        customers[customer_id] = {
            "id": customer_id,
            "email": f"customer{i}@example.com",
            "name": f"Customer {i}",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "address": {
                "street": f"{random.randint(100, 999)} Main St",
                "city": random.choice(["New York", "Los Angeles", "Chicago"]),
                "state": random.choice(["NY", "CA", "IL"]),
                "zip": f"{random.randint(10000, 99999)}",
                "country": "US"
            },
            "total_orders": 0,
            "lifetime_value": 0.0,
            "created_at": datetime.now().isoformat()
        }


def calculate_order_total(items: list) -> dict:
    """Calculate order total with tax and shipping"""
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax_rate = 0.08
    tax = subtotal * tax_rate
    shipping = 10.00 if subtotal < 50 else 0.00
    total = subtotal + tax + shipping
    
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "shipping": round(shipping, 2),
        "total": round(total, 2)
    }


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available e-commerce resources"""
    resources = [
        Resource(
            uri="ecommerce://products",
            name="Product Catalog",
            mimeType="application/json",
            description="Complete product catalog with pricing and details"
        ),
        Resource(
            uri="ecommerce://inventory",
            name="Inventory Levels",
            mimeType="application/json",
            description="Current inventory levels and warehouse locations"
        ),
        Resource(
            uri="ecommerce://orders",
            name="Order History",
            mimeType="application/json",
            description="All customer orders and their status"
        ),
        Resource(
            uri="ecommerce://customers",
            name="Customer Database",
            mimeType="application/json",
            description="Customer information and purchase history"
        ),
        Resource(
            uri="ecommerce://low-stock",
            name="Low Stock Alert",
            mimeType="application/json",
            description="Products with low inventory levels"
        ),
        Resource(
            uri="ecommerce://sales-summary",
            name="Sales Summary",
            mimeType="application/json",
            description="Sales metrics and performance data"
        )
    ]
    
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read e-commerce resources"""
    
    if uri == "ecommerce://products":
        return json.dumps(list(products.values()), indent=2)
    
    elif uri == "ecommerce://inventory":
        return json.dumps(list(inventory.values()), indent=2)
    
    elif uri == "ecommerce://orders":
        return json.dumps(list(orders.values()), indent=2)
    
    elif uri == "ecommerce://customers":
        return json.dumps(list(customers.values()), indent=2)
    
    elif uri == "ecommerce://low-stock":
        low_stock = [
            {**inventory[pid], "product_name": products[pid]["name"]}
            for pid, inv in inventory.items()
            if inv["quantity"] < 10
        ]
        return json.dumps(low_stock, indent=2)
    
    elif uri == "ecommerce://sales-summary":
        summary = {
            "total_orders": len(orders),
            "total_revenue": sum(order.get("total", 0) for order in orders.values()),
            "average_order_value": sum(order.get("total", 0) for order in orders.values()) / len(orders) if orders else 0,
            "total_customers": len(customers),
            "products_in_catalog": len(products)
        }
        return json.dumps(summary, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available e-commerce tools"""
    return [
        Tool(
            name="create_product",
            description="Add a new product to the catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Product name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Product description"
                    },
                    "category": {
                        "type": "string",
                        "description": "Product category"
                    },
                    "price": {
                        "type": "number",
                        "description": "Product price"
                    },
                    "sku": {
                        "type": "string",
                        "description": "Stock keeping unit"
                    },
                    "initial_stock": {
                        "type": "integer",
                        "description": "Initial inventory quantity",
                        "default": 0
                    }
                },
                "required": ["name", "price", "category"]
            }
        ),
        Tool(
            name="update_inventory",
            description="Update product inventory levels",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID"
                    },
                    "quantity_change": {
                        "type": "integer",
                        "description": "Quantity to add (positive) or remove (negative)"
                    },
                    "reason": {
                        "type": "string",
                        "enum": ["restock", "sale", "return", "damage", "adjustment"],
                        "description": "Reason for inventory change"
                    }
                },
                "required": ["product_id", "quantity_change", "reason"]
            }
        ),
        Tool(
            name="create_order",
            description="Create a new customer order",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID"
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "quantity": {"type": "integer"}
                            }
                        },
                        "description": "Order items"
                    },
                    "shipping_address": {
                        "type": "object",
                        "description": "Shipping address (optional, uses customer default if not provided)"
                    }
                },
                "required": ["customer_id", "items"]
            }
        ),
        Tool(
            name="process_order",
            description="Process and fulfill an order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to process"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["confirm", "ship", "deliver", "cancel", "refund"],
                        "description": "Action to perform on the order"
                    },
                    "tracking_number": {
                        "type": "string",
                        "description": "Shipping tracking number (for ship action)"
                    }
                },
                "required": ["order_id", "action"]
            }
        ),
        Tool(
            name="search_products",
            description="Search products by name, category, or filters",
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
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price filter"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter"
                    },
                    "in_stock_only": {
                        "type": "boolean",
                        "description": "Show only in-stock products",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="get_product_analytics",
            description="Get analytics for a specific product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Analysis time period (e.g., '30d')",
                        "default": "30d"
                    }
                },
                "required": ["product_id"]
            }
        ),
        Tool(
            name="apply_discount",
            description="Apply discount code or promotion to an order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID"
                    },
                    "discount_code": {
                        "type": "string",
                        "description": "Discount code"
                    },
                    "discount_type": {
                        "type": "string",
                        "enum": ["percentage", "fixed_amount"],
                        "description": "Type of discount"
                    },
                    "discount_value": {
                        "type": "number",
                        "description": "Discount value (percentage or amount)"
                    }
                },
                "required": ["order_id", "discount_code", "discount_type", "discount_value"]
            }
        ),
        Tool(
            name="generate_invoice",
            description="Generate invoice for an order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "html", "json"],
                        "description": "Invoice format",
                        "default": "pdf"
                    }
                },
                "required": ["order_id"]
            }
        ),
        Tool(
            name="manage_returns",
            description="Process product return or exchange",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Original order ID"
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "reason": {"type": "string"}
                            }
                        },
                        "description": "Items to return"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["refund", "exchange", "store_credit"],
                        "description": "Return action"
                    }
                },
                "required": ["order_id", "items", "action"]
            }
        ),
        Tool(
            name="recommend_products",
            description="Get product recommendations for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID"
                    },
                    "recommendation_type": {
                        "type": "string",
                        "enum": ["similar", "complementary", "popular", "personalized"],
                        "description": "Type of recommendations",
                        "default": "personalized"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of recommendations",
                        "default": 5
                    }
                },
                "required": ["customer_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute e-commerce tools"""
    global product_counter, order_counter
    
    if name == "create_product":
        product_id = f"PRD-{product_counter}"
        product_counter += 1
        
        products[product_id] = {
            "id": product_id,
            "name": arguments.get("name", ""),
            "description": arguments.get("description", ""),
            "category": arguments.get("category", ""),
            "price": arguments.get("price", 0.0),
            "currency": "USD",
            "sku": arguments.get("sku", f"SKU-{product_counter}"),
            "created_at": datetime.now().isoformat()
        }
        
        inventory[product_id] = {
            "product_id": product_id,
            "quantity": arguments.get("initial_stock", 0),
            "reserved": 0,
            "warehouse": "Main Warehouse"
        }
        
        result = {
            "status": "created",
            "product": products[product_id],
            "inventory": inventory[product_id]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "update_inventory":
        product_id = arguments.get("product_id", "")
        quantity_change = arguments.get("quantity_change", 0)
        reason = arguments.get("reason", "adjustment")
        
        if product_id not in inventory:
            return [TextContent(type="text", text=f"Error: Product '{product_id}' not found")]
        
        old_quantity = inventory[product_id]["quantity"]
        inventory[product_id]["quantity"] += quantity_change
        
        result = {
            "status": "updated",
            "product_id": product_id,
            "old_quantity": old_quantity,
            "new_quantity": inventory[product_id]["quantity"],
            "change": quantity_change,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "create_order":
        order_id = f"ORD-{order_counter}"
        order_counter += 1
        
        customer_id = arguments.get("customer_id", "")
        items = arguments.get("items", [])
        
        if customer_id not in customers:
            return [TextContent(type="text", text=f"Error: Customer '{customer_id}' not found")]
        
        # Build order items with prices
        order_items = []
        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            if product_id not in products:
                continue
            
            product = products[product_id]
            order_items.append({
                "product_id": product_id,
                "product_name": product["name"],
                "quantity": quantity,
                "price": product["price"],
                "subtotal": product["price"] * quantity
            })
            
            # Reserve inventory
            if product_id in inventory:
                inventory[product_id]["reserved"] += quantity
        
        # Calculate totals
        totals = calculate_order_total(order_items)
        
        orders[order_id] = {
            "id": order_id,
            "customer_id": customer_id,
            "items": order_items,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            **totals
        }
        
        # Update customer stats
        customers[customer_id]["total_orders"] += 1
        customers[customer_id]["lifetime_value"] += totals["total"]
        
        result = {
            "status": "created",
            "order": orders[order_id]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "process_order":
        order_id = arguments.get("order_id", "")
        action = arguments.get("action", "")
        
        if order_id not in orders:
            return [TextContent(type="text", text=f"Error: Order '{order_id}' not found")]
        
        order = orders[order_id]
        
        if action == "confirm":
            order["status"] = "confirmed"
        elif action == "ship":
            order["status"] = "shipped"
            order["tracking_number"] = arguments.get("tracking_number", f"TRACK-{random.randint(100000, 999999)}")
            order["shipped_at"] = datetime.now().isoformat()
        elif action == "deliver":
            order["status"] = "delivered"
            order["delivered_at"] = datetime.now().isoformat()
        elif action == "cancel":
            order["status"] = "cancelled"
            # Release reserved inventory
            for item in order["items"]:
                product_id = item["product_id"]
                if product_id in inventory:
                    inventory[product_id]["reserved"] -= item["quantity"]
        elif action == "refund":
            order["status"] = "refunded"
            order["refunded_at"] = datetime.now().isoformat()
        
        result = {
            "status": "processed",
            "order_id": order_id,
            "action": action,
            "new_status": order["status"]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "search_products":
        query = arguments.get("query", "").lower()
        category = arguments.get("category")
        min_price = arguments.get("min_price")
        max_price = arguments.get("max_price")
        in_stock_only = arguments.get("in_stock_only", True)
        
        results = []
        for product_id, product in products.items():
            # Apply filters
            if query and query not in product["name"].lower():
                continue
            if category and product["category"] != category:
                continue
            if min_price and product["price"] < min_price:
                continue
            if max_price and product["price"] > max_price:
                continue
            if in_stock_only and inventory[product_id]["quantity"] <= 0:
                continue
            
            results.append({
                **product,
                "stock": inventory[product_id]["quantity"]
            })
        
        search_result = {
            "query": query,
            "filters": {
                "category": category,
                "min_price": min_price,
                "max_price": max_price
            },
            "results_count": len(results),
            "results": results
        }
        
        return [TextContent(type="text", text=json.dumps(search_result, indent=2))]
    
    elif name == "get_product_analytics":
        product_id = arguments.get("product_id", "")
        
        if product_id not in products:
            return [TextContent(type="text", text=f"Error: Product '{product_id}' not found")]
        
        # Simulated analytics
        analytics = {
            "product_id": product_id,
            "product_name": products[product_id]["name"],
            "time_period": arguments.get("time_period", "30d"),
            "metrics": {
                "views": random.randint(500, 2000),
                "conversions": random.randint(20, 100),
                "conversion_rate": random.uniform(2.0, 8.0),
                "revenue": random.uniform(1000, 5000),
                "avg_rating": random.uniform(4.0, 5.0),
                "reviews_count": random.randint(10, 50)
            }
        }
        
        return [TextContent(type="text", text=json.dumps(analytics, indent=2))]
    
    elif name == "recommend_products":
        customer_id = arguments.get("customer_id", "")
        recommendation_type = arguments.get("recommendation_type", "personalized")
        max_results = arguments.get("max_results", 5)
        
        if customer_id not in customers:
            return [TextContent(type="text", text=f"Error: Customer '{customer_id}' not found")]
        
        # Simple recommendation: random products
        available_products = list(products.values())[:max_results]
        
        recommendations = {
            "customer_id": customer_id,
            "recommendation_type": recommendation_type,
            "products": [
                {
                    **product,
                    "relevance_score": random.uniform(0.7, 1.0)
                }
                for product in available_products
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(recommendations, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    init_sample_data()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
