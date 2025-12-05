"""
MCP Server - Database Query System
===================================
Enterprise-level database query server for SQL and NoSQL databases.
Provides secure, monitored access to databases with query validation.

Industry Use Case: Data Analytics, Business Intelligence, Enterprise Applications
"""

import asyncio
import json
from typing import Any, Optional
from datetime import datetime
import sqlite3
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

# Initialize MCP server
server = Server("database-query-server")

# Database configuration (in production, use environment variables)
DB_CONFIG = {
    "sqlite": {
        "path": "enterprise.db"
    },
    "max_query_time": 30,  # seconds
    "allowed_operations": ["SELECT", "INSERT", "UPDATE", "DELETE"]
}

# Query audit log
query_log = []


def init_sample_database():
    """Initialize a sample database for demonstration"""
    conn = sqlite3.connect(DB_CONFIG["sqlite"]["path"])
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product TEXT,
            amount DECIMAL(10,2),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO customers (id, name, email) VALUES (1, 'John Doe', 'john@example.com')")
    cursor.execute("INSERT OR IGNORE INTO customers (id, name, email) VALUES (2, 'Jane Smith', 'jane@example.com')")
    cursor.execute("INSERT OR IGNORE INTO orders (customer_id, product, amount) VALUES (1, 'Laptop', 1299.99)")
    cursor.execute("INSERT OR IGNORE INTO orders (customer_id, product, amount) VALUES (1, 'Mouse', 29.99)")
    cursor.execute("INSERT OR IGNORE INTO orders (customer_id, product, amount) VALUES (2, 'Keyboard', 89.99)")
    
    conn.commit()
    conn.close()


def validate_query(query: str) -> tuple[bool, str]:
    """Validate SQL query for security"""
    query_upper = query.upper().strip()
    
    # Check for dangerous operations
    dangerous_keywords = ["DROP", "TRUNCATE", "ALTER", "CREATE", "GRANT", "REVOKE"]
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f"Dangerous operation '{keyword}' not allowed"
    
    # Check if operation is allowed
    operation = query_upper.split()[0]
    if operation not in DB_CONFIG["allowed_operations"]:
        return False, f"Operation '{operation}' not allowed"
    
    return True, "Valid query"


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available database resources"""
    return [
        Resource(
            uri="db://customers",
            name="Customers Table",
            mimeType="application/json",
            description="Customer information including name, email, and registration date"
        ),
        Resource(
            uri="db://orders",
            name="Orders Table",
            mimeType="application/json",
            description="Order information including customer, product, and amount"
        ),
        Resource(
            uri="db://schema",
            name="Database Schema",
            mimeType="text/plain",
            description="Complete database schema information"
        ),
        Resource(
            uri="db://audit-log",
            name="Query Audit Log",
            mimeType="application/json",
            description="Historical record of all executed queries"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read database resources"""
    conn = sqlite3.connect(DB_CONFIG["sqlite"]["path"])
    cursor = conn.cursor()
    
    try:
        if uri == "db://customers":
            cursor.execute("SELECT * FROM customers")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return json.dumps(data, indent=2)
        
        elif uri == "db://orders":
            cursor.execute("SELECT * FROM orders")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return json.dumps(data, indent=2)
        
        elif uri == "db://schema":
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            schemas = cursor.fetchall()
            return "\n\n".join([schema[0] for schema in schemas if schema[0]])
        
        elif uri == "db://audit-log":
            return json.dumps(query_log[-100:], indent=2)  # Last 100 queries
        
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    finally:
        conn.close()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available database tools"""
    return [
        Tool(
            name="execute_query",
            description="Execute SQL query with validation and monitoring. Returns results as JSON.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute (SELECT, INSERT, UPDATE, DELETE)"
                    },
                    "parameters": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Query parameters for parameterized queries"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_table_info",
            description="Get detailed information about a specific table including schema and row count",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to inspect"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="analyze_query_performance",
            description="Analyze query performance and get optimization suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to analyze"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="export_data",
            description="Export query results to CSV or JSON format",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to export"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["csv", "json"],
                        "description": "Export format"
                    }
                },
                "required": ["query", "format"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute database tools"""
    
    if name == "execute_query":
        query = arguments.get("query", "")
        parameters = arguments.get("parameters", [])
        
        # Validate query
        is_valid, message = validate_query(query)
        if not is_valid:
            return [TextContent(type="text", text=f"Error: {message}")]
        
        # Execute query
        conn = sqlite3.connect(DB_CONFIG["sqlite"]["path"])
        cursor = conn.cursor()
        
        try:
            start_time = datetime.now()
            
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Handle SELECT queries
            if query.upper().strip().startswith("SELECT"):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]
                
                result = {
                    "status": "success",
                    "rows_returned": len(data),
                    "execution_time_seconds": execution_time,
                    "data": data
                }
            else:
                # Handle INSERT/UPDATE/DELETE
                conn.commit()
                result = {
                    "status": "success",
                    "rows_affected": cursor.rowcount,
                    "execution_time_seconds": execution_time
                }
            
            # Log query
            query_log.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "execution_time": execution_time,
                "status": "success"
            })
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except Exception as e:
            query_log.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "status": "error",
                "error": str(e)
            })
            return [TextContent(type="text", text=f"Error executing query: {str(e)}")]
        
        finally:
            conn.close()
    
    elif name == "get_table_info":
        table_name = arguments.get("table_name", "")
        conn = sqlite3.connect(DB_CONFIG["sqlite"]["path"])
        cursor = conn.cursor()
        
        try:
            # Get schema
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            schema = cursor.fetchone()
            
            if not schema:
                return [TextContent(type="text", text=f"Table '{table_name}' not found")]
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            result = {
                "table_name": table_name,
                "row_count": row_count,
                "schema": schema[0],
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ]
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        finally:
            conn.close()
    
    elif name == "analyze_query_performance":
        query = arguments.get("query", "")
        conn = sqlite3.connect(DB_CONFIG["sqlite"]["path"])
        cursor = conn.cursor()
        
        try:
            # Get query plan
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = cursor.fetchall()
            
            analysis = {
                "query": query,
                "query_plan": [str(row) for row in plan],
                "recommendations": []
            }
            
            # Simple optimization suggestions
            if "WHERE" not in query.upper():
                analysis["recommendations"].append("Consider adding WHERE clause to filter results")
            
            if "*" in query:
                analysis["recommendations"].append("Specify column names instead of using *")
            
            return [TextContent(type="text", text=json.dumps(analysis, indent=2))]
        
        finally:
            conn.close()
    
    elif name == "export_data":
        query = arguments.get("query", "")
        export_format = arguments.get("format", "json")
        
        # Validate and execute query
        is_valid, message = validate_query(query)
        if not is_valid:
            return [TextContent(type="text", text=f"Error: {message}")]
        
        conn = sqlite3.connect(DB_CONFIG["sqlite"]["path"])
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if export_format == "csv":
                # Generate CSV
                csv_data = ",".join(columns) + "\n"
                for row in rows:
                    csv_data += ",".join([str(val) for val in row]) + "\n"
                
                result = {
                    "format": "csv",
                    "rows": len(rows),
                    "data": csv_data
                }
            else:
                # Generate JSON
                data = [dict(zip(columns, row)) for row in rows]
                result = {
                    "format": "json",
                    "rows": len(data),
                    "data": data
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        finally:
            conn.close()
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    # Initialize database
    init_sample_database()
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
