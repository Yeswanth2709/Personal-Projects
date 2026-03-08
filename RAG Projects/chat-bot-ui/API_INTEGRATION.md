# ChatBot API Integration

## Overview

The chatbot now integrates with your FastAPI backend to answer financial questions based on your company's knowledge base.

## Configuration

### API Endpoint Setup

Update the API configuration in `src/config.js`:

```javascript
export const API_CONFIG = {
  BASE_URL: "http://localhost:8000", // Your FastAPI server URL
  ENDPOINTS: {
    CHAT: "/chat", // Your chat endpoint
  },
};
```

## Backend API Contract

### Request Format

The frontend sends POST requests to your backend with this structure:

```json
{
  "message": "What was our revenue in 2024?"
}
```

### Response Format

Your FastAPI backend should return responses in this format:

```json
{
  "content": "Based on the Q4 2024 Financial Report...",
  "sources": ["Annual_Report_2024.pdf (p.23)", "Q4_Financial_Report.pdf (p.12)"]
}
```

**Alternative Response Fields** (the frontend checks for these):

- `content` (preferred)
- `response`
- `message`

### FastAPI Example

Here's a sample FastAPI endpoint structure:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    content: str
    sources: list[str] = []

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # Your RAG/knowledge base logic here
    user_question = request.message

    # Process the question with your financial knowledge base
    answer = process_financial_query(user_question)

    return ChatResponse(
        content=answer["content"],
        sources=answer.get("sources", [])
    )
```

## Error Handling

The frontend handles these scenarios:

- **Network errors**: Connection issues with the backend
- **API errors**: HTTP error responses (4xx, 5xx)
- **Invalid responses**: Missing or malformed data

Error messages are displayed in the chat interface with troubleshooting hints.

## Features

### What's Included

✅ **Async API calls** - Non-blocking requests to backend  
✅ **Loading states** - Typing indicator while waiting for response  
✅ **Error handling** - Graceful degradation with helpful error messages  
✅ **Source citations** - Displays source documents if provided  
✅ **CORS support** - Configured for cross-origin requests

### Quick Questions

Pre-configured quick question buttons for common queries:

- "What was our revenue in 2024?"
- "Show me expense breakdown"
- "What's our profit margin?"
- "Tell me about cash flow"

## Testing

### 1. Start your FastAPI backend

```bash
cd your-backend-folder
uvicorn main:app --reload
```

### 2. Start the frontend

```bash
npm run dev
```

### 3. Test the integration

- Open the chatbot in your browser
- Send a test message
- Check browser console for API calls
- Verify responses display correctly

## Troubleshooting

### CORS Issues

If you see CORS errors, ensure your FastAPI backend has proper CORS configuration:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Connection Refused

- Check backend is running: `curl http://localhost:8000`
- Verify port matches in `config.js`
- Check firewall settings

### Empty Responses

- Verify backend returns `content`, `response`, or `message` field
- Check backend logs for errors
- Test endpoint directly with curl or Postman

## Customization

### Change API URL

Edit `src/config.js` to match your production URL:

```javascript
BASE_URL: "https://your-api.com";
```

### Modify Request Format

Update the `callBackendAPI` function in `ChatBot.jsx`:

```javascript
body: JSON.stringify({
  message: userMessage,
  session_id: "user-123",  // Add custom fields
  context: additionalContext,
}),
```

### Custom Response Parsing

Adjust response handling in `callBackendAPI`:

```javascript
return {
  content: data.answer || data.content,
  sources: data.references || data.sources,
  confidence: data.confidence_score,
};
```
