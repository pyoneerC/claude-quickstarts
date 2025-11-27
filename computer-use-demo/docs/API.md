# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

Currently, the API uses the `ANTHROPIC_API_KEY` environment variable for authentication with the Anthropic API. For production, implement proper user authentication.

## Endpoints

### Health Check

#### GET /health

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "active_sessions": 3
}
```

---

### Sessions

#### POST /api/sessions

Create a new chat session.

**Request Body:**
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "provider": "anthropic",
  "system_prompt_suffix": "Optional additional instructions"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "model": "claude-sonnet-4-5-20250929",
  "provider": "anthropic",
  "system_prompt_suffix": "Optional additional instructions",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Status Codes:**
- `200 OK` - Session created successfully
- `500 Internal Server Error` - Failed to create session

---

#### GET /api/sessions/{session_id}

Get details of a specific session.

**Parameters:**
- `session_id` (path) - UUID of the session

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "model": "claude-sonnet-4-5-20250929",
  "provider": "anthropic",
  "system_prompt_suffix": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Status Codes:**
- `200 OK` - Session found
- `404 Not Found` - Session not found

---

#### GET /api/sessions

List all sessions.

**Query Parameters:**
- `skip` (optional, default: 0) - Number of sessions to skip
- `limit` (optional, default: 100) - Maximum number of sessions to return

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "model": "claude-sonnet-4-5-20250929",
    "provider": "anthropic",
    "system_prompt_suffix": null,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

---

#### DELETE /api/sessions/{session_id}

Delete a session and all its messages.

**Parameters:**
- `session_id` (path) - UUID of the session

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

**Status Codes:**
- `200 OK` - Session deleted
- `404 Not Found` - Session not found

---

### Messages

#### GET /api/sessions/{session_id}/messages

Get all messages for a session.

**Parameters:**
- `session_id` (path) - UUID of the session

**Query Parameters:**
- `skip` (optional, default: 0) - Number of messages to skip
- `limit` (optional, default: 100) - Maximum number of messages to return

**Response:**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Hello, can you help me?"
      }
    ],
    "timestamp": "2024-01-15T10:31:00"
  },
  {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "assistant",
    "content": [
      {
        "type": "text",
        "text": "Of course! How can I assist you today?"
      }
    ],
    "timestamp": "2024-01-15T10:31:05"
  }
]
```

---

#### POST /api/sessions/{session_id}/messages

Send a message to the session.

**Parameters:**
- `session_id` (path) - UUID of the session

**Request Body:**
```json
{
  "content": "Your message here"
}
```

**Response:**
```json
{
  "message_id": "880e8400-e29b-41d4-a716-446655440000",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

**Note:** This endpoint queues the message for processing. Use WebSocket or SSE for real-time updates.

---

### Real-time Streaming

#### WebSocket /ws/{session_id}

Real-time bidirectional communication for a session.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/550e8400-e29b-41d4-a716-446655440000');
```

**Send Message:**
```javascript
ws.send(JSON.stringify({
  type: 'message',
  content: 'Your message here'
}));
```

**Receive Events:**

Events are sent as JSON objects with different types:

**Text Event:**
```json
{
  "type": "text",
  "text": "Assistant response text"
}
```

**Thinking Event:**
```json
{
  "type": "thinking",
  "thinking": "Internal reasoning process"
}
```

**Tool Use Event:**
```json
{
  "type": "tool_use",
  "tool_name": "computer",
  "tool_input": {
    "action": "screenshot"
  },
  "tool_use_id": "toolu_123"
}
```

**Tool Result Event:**
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_123",
  "output": "Screenshot taken successfully",
  "error": null,
  "base64_image": "iVBORw0KGgoAAAANS..."
}
```

**Status Event:**
```json
{
  "type": "status",
  "status": "processing",
  "message": "Processing your request..."
}
```

**Error Event:**
```json
{
  "type": "error",
  "error": "Error message",
  "details": "ErrorType"
}
```

---

#### GET /api/sessions/{session_id}/stream

Server-Sent Events (SSE) endpoint for one-way streaming.

**Connection:**
```javascript
const eventSource = new EventSource('http://localhost:8000/api/sessions/550e8400-e29b-41d4-a716-446655440000/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Events:** Same format as WebSocket events.

---

### VNC

#### GET /api/vnc/info

Get VNC connection information.

**Response:**
```json
{
  "vnc_host": "localhost",
  "vnc_port": 5900,
  "novnc_port": 6080,
  "novnc_url": "http://localhost:6080/vnc.html",
  "websocket_url": "ws://localhost:6080/websockify"
}
```

---

#### WebSocket /ws/vnc

WebSocket proxy for VNC connections.

**Note:** This is primarily for web-based VNC clients. For direct VNC access, use the noVNC URL from `/api/vnc/info`.

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Rate Limiting

Currently, no rate limiting is implemented. For production, implement rate limiting based on your requirements.

---

## CORS

CORS is configured to allow all origins in development. For production, configure `allow_origins` in `backend/main.py` to only allow trusted domains.

---

## Examples

### Create Session and Send Message (JavaScript)

```javascript
// Create session
const createSession = async () => {
  const response = await fetch('http://localhost:8000/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'claude-sonnet-4-5-20250929',
      provider: 'anthropic'
    })
  });
  return response.json();
};

// Connect WebSocket
const connectWebSocket = (sessionId) => {
  const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
  
  ws.onopen = () => {
    console.log('Connected');
    
    // Send message
    ws.send(JSON.stringify({
      type: 'message',
      content: 'Hello!'
    }));
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Event:', data);
  };
};

// Usage
const session = await createSession();
connectWebSocket(session.id);
```

### Create Session and Send Message (Python)

```python
import asyncio
import httpx
import websockets
import json

async def main():
    # Create session
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:8000/api/sessions',
            json={
                'model': 'claude-sonnet-4-5-20250929',
                'provider': 'anthropic'
            }
        )
        session = response.json()
        session_id = session['id']
    
    # Connect WebSocket
    async with websockets.connect(f'ws://localhost:8000/ws/{session_id}') as ws:
        # Send message
        await ws.send(json.dumps({
            'type': 'message',
            'content': 'Hello!'
        }))
        
        # Receive messages
        async for message in ws:
            event = json.loads(message)
            print('Event:', event)
            
            if event.get('type') == 'status' and event.get('status') == 'completed':
                break

asyncio.run(main())
```

---

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
