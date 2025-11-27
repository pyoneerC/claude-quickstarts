# Computer Use Demo - Production FastAPI Backend

A production-ready implementation of Anthropic's Computer Use Demo with a FastAPI backend, real-time WebSocket streaming, session management, database persistence, and VNC access.

## 🎯 Overview

This project transforms the experimental Streamlit interface into a robust, production-ready system featuring:

- **FastAPI Backend**: RESTful APIs with automatic OpenAPI documentation
- **Real-time Streaming**: WebSocket and Server-Sent Events (SSE) for live agent progress
- **Session Management**: Create, manage, and persist multiple chat sessions
- **Database Persistence**: PostgreSQL support for chat history (SQLite for development)
- **VNC Integration**: Direct access to the virtual desktop where the agent operates
- **Docker Support**: Complete containerization for easy deployment
- **Modern Frontend**: Clean, responsive HTML/JS interface

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Anthropic API key
- 8GB+ RAM recommended

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd anthropic-quickstarts/computer-use-demo
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Start the application**
```bash
docker-compose up --build
```

4. **Access the application**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- VNC Viewer: http://localhost:6080/vnc.html

## 📁 Project Structure

```
computer-use-demo/
├── backend/                    # FastAPI backend
│   ├── main.py                # Application entry point
│   ├── models.py              # Pydantic & SQLAlchemy models
│   ├── database.py            # Database configuration
│   ├── crud.py                # Database operations
│   ├── session_manager.py     # Session & message handling
│   ├── vnc_proxy.py           # VNC WebSocket proxy
│   └── requirements.txt       # Backend dependencies
├── frontend/                   # Simple HTML/JS frontend
│   └── index.html             # Single-page application
├── computer_use_demo/         # Original Anthropic demo code
│   ├── loop.py                # Agentic sampling loop
│   ├── tools/                 # Computer use tools
│   └── ...
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile.backend         # Docker image definition
├── docker-entrypoint.sh       # Container startup script
└── README.md                  # This file
```

## 🔌 API Endpoints

### Session Management

#### Create Session
```http
POST /api/sessions
Content-Type: application/json

{
  "model": "claude-sonnet-4-5-20250929",
  "provider": "anthropic",
  "system_prompt_suffix": "Optional additional instructions"
}
```

#### Get Session
```http
GET /api/sessions/{session_id}
```

#### List Sessions
```http
GET /api/sessions?skip=0&limit=100
```

#### Delete Session
```http
DELETE /api/sessions/{session_id}
```

### Messages

#### Get Messages
```http
GET /api/sessions/{session_id}/messages?skip=0&limit=100
```

#### Send Message
```http
POST /api/sessions/{session_id}/messages
Content-Type: application/json

{
  "content": "Your message here"
}
```

### Real-time Streaming

#### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{session_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

// Send message
ws.send(JSON.stringify({
  type: 'message',
  content: 'Your message'
}));
```

#### Server-Sent Events
```javascript
const eventSource = new EventSource('/api/sessions/{session_id}/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### VNC Access

#### Get VNC Info
```http
GET /api/vnc/info
```

#### VNC WebSocket Proxy
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/vnc');
```

## 🎨 Frontend Features

The included frontend demonstrates all API capabilities:

- **Session Management**: Create and switch between sessions
- **Live Chat**: Real-time conversation with the AI agent
- **Tool Visualization**: See what tools the agent uses
- **VNC Viewer**: Embedded virtual desktop view
- **Status Indicators**: Connection and processing status
- **Screenshot Display**: View agent-captured screenshots

## 🗄️ Database Schema

### Sessions Table
```sql
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    model VARCHAR NOT NULL,
    provider VARCHAR NOT NULL,
    system_prompt_suffix TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id VARCHAR PRIMARY KEY,
    session_id VARCHAR REFERENCES sessions(id),
    role VARCHAR NOT NULL,
    content JSON NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Real-time Event Types

### Text Event
```json
{
  "type": "text",
  "text": "Agent response text"
}
```

### Thinking Event
```json
{
  "type": "thinking",
  "thinking": "Agent's thought process"
}
```

### Tool Use Event
```json
{
  "type": "tool_use",
  "tool_name": "computer",
  "tool_input": {"action": "screenshot"},
  "tool_use_id": "unique_id"
}
```

### Tool Result Event
```json
{
  "type": "tool_result",
  "tool_use_id": "unique_id",
  "output": "Tool output",
  "error": null,
  "base64_image": "base64_encoded_image"
}
```

### Status Event
```json
{
  "type": "status",
  "status": "processing|completed",
  "message": "Status message"
}
```

### Error Event
```json
{
  "type": "error",
  "error": "Error message",
  "details": "Error type"
}
```

## 🐳 Docker Configuration

### Development Mode

```bash
# Build and start with hot reload
docker-compose up --build

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

### Production Mode

```bash
# Use production database
# Update DATABASE_URL in .env to point to production PostgreSQL

# Build
docker-compose build

# Run detached
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key (required) | - |
| `DATABASE_URL` | Database connection string | SQLite |
| `VNC_HOST` | VNC server host | localhost |
| `VNC_PORT` | VNC server port | 5900 |
| `NOVNC_PORT` | noVNC web port | 6080 |
| `DISPLAY_NUM` | X display number | 1 |
| `WIDTH` | Desktop width | 1024 |
| `HEIGHT` | Desktop height | 768 |

## 🔧 Development

### Local Development (without Docker)

1. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r backend/requirements.txt
pip install -r computer_use_demo/requirements.txt
```

3. **Set environment variables**
```bash
export ANTHROPIC_API_KEY=your_key
export DATABASE_URL=sqlite+aiosqlite:///./computer_use_demo.db
```

4. **Run the backend**
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

5. **Open browser**
```
http://localhost:8000
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 📊 Architecture

### Backend Architecture

```
┌─────────────┐
│   Client    │
│ (Browser)   │
└──────┬──────┘
       │
       ├── HTTP/REST ──────────┐
       │                       │
       ├── WebSocket ──────────┤
       │                       │
       └── SSE ────────────────┤
                               │
                        ┌──────▼──────┐
                        │   FastAPI   │
                        │   Backend   │
                        └──────┬──────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼─────┐
         │  Session   │ │  Database  │ │   VNC    │
         │  Manager   │ │ (Postgres) │ │  Proxy   │
         └──────┬─────┘ └────────────┘ └────┬─────┘
                │                            │
         ┌──────▼─────┐                ┌────▼─────┐
         │ Anthropic  │                │   X11    │
         │    API     │                │  Desktop │
         └────────────┘                └──────────┘
```

### Message Flow

1. Client sends message via WebSocket
2. Session Manager queues message
3. Background task processes message through sampling loop
4. Anthropic API called with tools
5. Tool results executed and captured
6. Events streamed back to client in real-time
7. All messages persisted to database

## 🎥 Demo Video

A 5-minute demo video showing:
- Session creation
- Real-time chat interaction
- Tool usage visualization
- VNC desktop viewing
- Multiple session management
- Database persistence

[Link to demo video]

## 📝 Code Quality

### Features

- **Type Hints**: Full Python type annotations
- **Async/Await**: Proper async patterns throughout
- **Error Handling**: Comprehensive error handling
- **Logging**: Structured logging for debugging
- **Documentation**: Inline comments and docstrings
- **API Docs**: Auto-generated OpenAPI/Swagger docs

### Best Practices

- Dependency injection with FastAPI Depends
- Database session management with context managers
- WebSocket connection lifecycle handling
- Graceful shutdown and cleanup
- Environment-based configuration

## 🔒 Security Considerations

For production deployment:

1. **API Key Management**: Use secrets management (AWS Secrets Manager, etc.)
2. **CORS**: Configure allowed origins properly
3. **Authentication**: Add user authentication
4. **Rate Limiting**: Implement rate limiting
5. **HTTPS**: Use SSL/TLS certificates
6. **Database**: Use connection pooling and prepared statements
7. **VNC**: Restrict VNC access with authentication

## 🚀 Deployment

### Cloud Deployment

#### AWS ECS/Fargate

1. Build and push Docker image to ECR
2. Create ECS task definition
3. Configure RDS PostgreSQL
4. Set up Application Load Balancer
5. Configure environment variables

#### Google Cloud Run

1. Build container image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Configure Cloud SQL PostgreSQL
5. Set environment variables

#### Azure Container Instances

1. Build and push to Azure Container Registry
2. Create container instance
3. Configure Azure Database for PostgreSQL
4. Set environment variables

### Environment Variables for Production

```bash
# Production environment
ANTHROPIC_API_KEY=<secret>
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
VNC_HOST=0.0.0.0
CORS_ORIGINS=https://yourdomain.com
```

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Review the API documentation at `/docs`
- Check the container logs: `docker-compose logs -f`

## 📄 License

This project builds upon Anthropic's Computer Use Demo. Please refer to the LICENSE file for details.

## 🙏 Acknowledgments

- Anthropic for the Computer Use Demo
- FastAPI for the excellent web framework
- The Python async/await ecosystem

---

**Built with ❤️ for production deployment**
