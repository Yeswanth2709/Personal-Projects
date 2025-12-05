# MCP Server Code Snippets

This directory contains production-ready MCP (Model Context Protocol) server implementations for various enterprise use cases. Each server demonstrates best practices for building scalable, industry-specific AI integrations.

## 🚀 Quick Start

### Installation

```bash
# Install MCP SDK
pip install mcp

# Each server can run independently
python 01_database_query_server.py
```

### Running an MCP Server

```bash
# Run any server using Python
python <server_filename>.py
```

## 📁 Available MCP Servers

### 1. **Database Query Server** (`01_database_query_server.py`)

**Industry:** Data Analytics, Business Intelligence, Enterprise Applications

**Features:**

- Execute SQL/NoSQL queries with validation
- Database schema introspection
- Query performance analysis
- Data export in multiple formats
- Audit logging for compliance

**Tools:** 4 tools including `execute_query`, `get_table_info`, `analyze_query_performance`, `export_data`

**Resources:** Sample customer/order tables, schema information, audit logs

---

### 2. **Document Processing Server** (`02_document_processing_server.py`)

**Industry:** Legal Tech, Healthcare, Insurance, Document Management

**Features:**

- Multi-format document handling (PDF, Word, Excel, text)
- Text extraction and entity recognition
- Document summarization
- OCR for scanned documents
- Document comparison and search

**Tools:** 7 tools including `upload_document`, `extract_entities`, `summarize_document`, `ocr_document`

**Resources:** Dynamic resources per uploaded document

---

### 3. **API Integration Server** (`03_api_integration_server.py`)

**Industry:** E-commerce, SaaS Platforms, Marketing Automation, Fintech

**Features:**

- Unified API integration hub
- Pre-configured integrations (Stripe, SendGrid, Slack, GitHub)
- Batch API requests
- Webhook management
- API health monitoring

**Tools:** 8 tools including `make_api_request`, `call_stripe_api`, `send_email`, `post_to_slack`

**Resources:** API configurations, request history, webhook settings

---

### 4. **Customer Support Server** (`04_customer_support_server.py`)

**Industry:** Customer Service, Help Desk, Technical Support, SaaS Support

**Features:**

- Ticket lifecycle management
- Knowledge base search
- Automated response suggestions
- Ticket categorization and prioritization
- Escalation workflows
- Customer satisfaction tracking

**Tools:** 9 tools including `create_ticket`, `search_knowledge_base`, `suggest_response`, `escalate_ticket`

**Resources:** Knowledge base articles, canned responses, ticket templates

---

### 5. **Analytics & Business Intelligence Server** (`05_analytics_bi_server.py`)

**Industry:** Business Intelligence, Data Analytics, SaaS Metrics, E-commerce

**Features:**

- KPI tracking and calculations
- Funnel and cohort analysis
- A/B test evaluation
- Churn prediction
- User segmentation
- Custom analytics queries
- Data visualization support

**Tools:** 10 tools including `track_event`, `calculate_kpi`, `create_funnel_analysis`, `cohort_analysis`

**Resources:** KPI definitions, user/event/revenue data, saved reports

---

### 6. **E-commerce Operations Server** (`06_ecommerce_operations_server.py`)

**Industry:** E-commerce, Retail, Online Marketplace, Dropshipping

**Features:**

- Product catalog management
- Inventory tracking and alerts
- Order lifecycle management
- Customer database
- Product recommendations
- Discount/promotion management
- Invoice generation

**Tools:** 10 tools including `create_product`, `update_inventory`, `create_order`, `process_order`

**Resources:** Product catalog, inventory levels, order history, customer data

---

### 7. **Healthcare Patient Management Server** (`07_healthcare_patient_management_server.py`)

**Industry:** Healthcare, Hospitals, Clinics, Telemedicine, EHR Systems

**Features:**

- HIPAA-compliant patient registration
- Appointment scheduling
- Electronic medical records (EMR)
- Prescription management
- Drug interaction checking
- Clinical risk scoring
- Patient history tracking

**Tools:** 10 tools including `register_patient`, `schedule_appointment`, `create_prescription`, `check_drug_interactions`

**Resources:** Patient database, appointments, medical records, prescriptions

---

## 🏗️ Architecture

### MCP Server Structure

Each server follows this standard pattern:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# 1. Initialize Server
server = Server("server-name")

# 2. Define Resources (data sources)
@server.list_resources()
async def list_resources() -> list[Resource]:
    # Return available data resources
    pass

@server.read_resource()
async def read_resource(uri: str) -> str:
    # Read specific resource
    pass

# 3. Define Tools (actions/operations)
@server.list_tools()
async def list_tools() -> list[Tool]:
    # Return available tools
    pass

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    # Execute tool logic
    pass

# 4. Run Server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream,
                        server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Components

- **Resources:** Read-only data sources (databases, files, APIs)
- **Tools:** Executable actions that modify state or perform operations
- **URI Scheme:** Custom URI patterns for resource identification (e.g., `database://`, `healthcare://`)

## 🔧 Customization

### Adding Production Database

Replace simulated data with real database connections:

```python
import sqlite3  # or psycopg2, pymongo, etc.

# Example: PostgreSQL connection
import psycopg2
conn = psycopg2.connect(
    host="your-host",
    database="your-db",
    user="your-user",
    password="your-password"
)
```

### Adding Authentication

Add authentication to your MCP server:

```python
from mcp.server import Server

server = Server("secure-server")

# Add authentication middleware
async def authenticate(request):
    # Verify API keys, tokens, etc.
    pass
```

### Error Handling

Implement robust error handling:

```python
@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    try:
        # Tool logic
        pass
    except ValueError as e:
        return [TextContent(type="text", text=f"Validation error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Server error: {str(e)}")]
```

## 🔒 Security Considerations

### Production Checklist

- [ ] **Authentication:** Implement API key or OAuth authentication
- [ ] **Authorization:** Role-based access control (RBAC)
- [ ] **Input Validation:** Validate all user inputs
- [ ] **Data Encryption:** Encrypt sensitive data at rest and in transit
- [ ] **Rate Limiting:** Prevent abuse with rate limits
- [ ] **Audit Logging:** Log all operations for compliance
- [ ] **HIPAA Compliance:** For healthcare servers, ensure HIPAA compliance
- [ ] **PCI DSS:** For payment processing, follow PCI DSS standards

### Example Security Implementation

```python
import hashlib
import hmac

def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify HMAC signature for webhook/API requests"""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## 📊 Monitoring & Logging

Add monitoring to track server performance:

```python
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    start_time = time.time()
    logger.info(f"Executing tool: {name}")

    try:
        result = # ... tool execution
        duration = time.time() - start_time
        logger.info(f"Tool {name} completed in {duration:.2f}s")
        return result
    except Exception as e:
        logger.error(f"Tool {name} failed: {str(e)}")
        raise
```

## 🧪 Testing

### Unit Testing Example

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_execute_query():
    # Test database query execution
    result = await call_tool("execute_query", {
        "query": "SELECT * FROM customers LIMIT 1"
    })
    assert len(result) > 0
    assert "error" not in result[0].text
```

### Integration Testing

```bash
# Run MCP server in test mode
python -m pytest tests/

# Test with MCP client
mcp connect stdio python 01_database_query_server.py
```

## 📦 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY mcp_server_snippets/ .

CMD ["python", "01_database_query_server.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
        - name: mcp-server
          image: your-registry/mcp-server:latest
          ports:
            - containerPort: 8080
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code follows PEP 8 style guide
5. Submit a pull request

## 📝 License

These code snippets are provided as examples for educational purposes. Adapt them according to your project's license requirements.

## 🆘 Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'mcp'`

```bash
# Solution: Install MCP SDK
pip install mcp
```

**Issue:** Server not responding

```bash
# Solution: Check if server is running
ps aux | grep python
# Kill and restart if needed
```

**Issue:** Port already in use

```bash
# Solution: Change port or kill existing process
lsof -i :8080
kill -9 <PID>
```

## 📚 Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Best Practices for MCP Servers](https://modelcontextprotocol.io/docs/best-practices)

## 🔄 Version History

- **v1.0.0** (2024) - Initial release with 7 industry-specific MCP servers

---

**Need Help?** Open an issue or contact the development team.
