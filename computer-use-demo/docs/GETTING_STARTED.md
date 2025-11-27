# Getting Started Guide

Welcome to the Computer Use Demo with FastAPI Backend! This guide will help you get up and running quickly.

## Quick Start (5 minutes)

### Prerequisites

- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Anthropic API key ([Get one](https://console.anthropic.com/))
- 8GB+ RAM recommended

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd computer-use-demo
   ```

2. **Configure environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env and add your API key
   # ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

3. **Run setup script**
   
   **On Linux/Mac:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   **On Windows:**
   ```cmd
   setup.bat
   ```

4. **Access the application**
   - Web Interface: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - VNC Desktop: http://localhost:6080/vnc.html

## What You Can Do

### 1. Create a Session

Open http://localhost:8000 and click "Create New Session". This initializes a new chat session with the AI agent.

### 2. Chat with the Agent

Type a message like:
- "Take a screenshot and tell me what you see"
- "Open Firefox and search for Python tutorials"
- "Create a text file with today's date"

### 3. Watch in Real-time

- Chat messages appear in the chat panel
- Tool usage is shown with details
- Screenshots appear automatically
- The VNC viewer shows the desktop in real-time

### 4. Explore the API

Visit http://localhost:8000/docs to see interactive API documentation with:
- All available endpoints
- Request/response schemas
- Try-it-out functionality

## Understanding the Interface

### Web Interface Components

1. **Session Management Panel**
   - Create new sessions
   - Select model and provider
   - View session list
   - Current session info

2. **Chat Panel**
   - Message history
   - Send messages
   - See agent responses
   - View tool usage

3. **VNC Desktop**
   - Live view of virtual desktop
   - See agent interactions
   - Full desktop environment

### Event Types

As you chat, you'll see different event types:

- 💬 **User Messages**: Your messages
- 🤖 **Assistant Responses**: AI responses
- 💭 **Thinking**: Agent's reasoning
- 🔧 **Tool Use**: Tools being used
- ✅ **Tool Results**: Results from tools
- 📷 **Screenshots**: Captured images
- ⚠️ **Errors**: Any issues

## Example Interactions

### Example 1: Web Research

**You:** "Search for the latest news about AI"

**Agent will:**
1. Think about the task
2. Use computer tool to click Firefox
3. Type in search query
4. Take screenshot
5. Read and summarize results

### Example 2: File Operations

**You:** "Create a file called notes.txt with a list of programming languages"

**Agent will:**
1. Use bash tool to create file
2. Write content to file
3. Verify creation
4. Report success

### Example 3: Complex Task

**You:** "Download a sample CSV file and open it in LibreOffice Calc"

**Agent will:**
1. Use bash to download file
2. Navigate to file location
3. Open file in Calc
4. Take screenshot to show result

## Common Tasks

### Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View only app logs
docker-compose logs -f app

# View database logs
docker-compose logs -f db
```

### Restarting Services

```bash
# Restart everything
docker-compose restart

# Restart only app
docker-compose restart app
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Updating Code

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up --build -d
```

## Troubleshooting

### Services Won't Start

**Check Docker is running:**
```bash
docker ps
```

**Check logs:**
```bash
docker-compose logs
```

**Rebuild containers:**
```bash
docker-compose down
docker-compose up --build
```

### Can't Connect to Backend

**Verify services are running:**
```bash
docker-compose ps
```

**Check health:**
```bash
curl http://localhost:8000/health
```

**Check ports:**
```bash
# Linux/Mac
netstat -an | grep 8000

# Windows
netstat -an | findstr 8000
```

### API Key Issues

**Verify API key is set:**
```bash
cat .env | grep ANTHROPIC_API_KEY
```

**Test API key:**
```bash
# Inside container
docker-compose exec app env | grep ANTHROPIC
```

### VNC Not Working

**Check VNC is running:**
```bash
curl http://localhost:6080
```

**Access VNC directly:**
- Open http://localhost:6080/vnc.html
- Click "Connect"

**Check X server:**
```bash
docker-compose exec app ps aux | grep X
```

### Database Issues

**Reset database:**
```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm computer-use-demo_postgres_data

# Start fresh
docker-compose up -d
```

**Check database connection:**
```bash
docker-compose exec app python -c "import asyncio; from backend.database import init_db; asyncio.run(init_db())"
```

## Development Mode

### Running Locally (without Docker)

1. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
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

4. **Run backend**
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```

### Hot Reload

The backend supports hot reload in development:
- Changes to Python files are automatically detected
- Server restarts automatically
- No need to rebuild Docker container

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_backend.py

# Run with coverage
pytest --cov=backend tests/
```

## Using the API Programmatically

### Python Example

```python
from examples.client_example import ComputerUseClient
import asyncio

async def main():
    client = ComputerUseClient()
    
    # Create session
    session = await client.create_session()
    
    # Send message with streaming
    await client.stream_with_websocket(
        "Take a screenshot",
        on_event=lambda e: print(e)
    )

asyncio.run(main())
```

### JavaScript Example

```javascript
// Create session
const response = await fetch('http://localhost:8000/api/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'claude-sonnet-4-5-20250929',
    provider: 'anthropic'
  })
});

const session = await response.json();

// Connect WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/${session.id}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

// Send message
ws.send(JSON.stringify({
  type: 'message',
  content: 'Hello!'
}));
```

### cURL Examples

```bash
# Create session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-5-20250929","provider":"anthropic"}'

# List sessions
curl http://localhost:8000/api/sessions

# Get session
curl http://localhost:8000/api/sessions/{session_id}

# Send message
curl -X POST http://localhost:8000/api/sessions/{session_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello!"}'
```

## Next Steps

### Learn More

- 📖 [API Documentation](docs/API.md) - Detailed API reference
- 🏗️ [Architecture](docs/ARCHITECTURE.md) - System design and components
- 🚀 [Deployment Guide](docs/DEPLOYMENT.md) - Deploy to production
- 📚 [FastAPI Docs](https://fastapi.tiangolo.com/) - Framework documentation

### Customize

- Modify system prompts in session creation
- Add custom tools to `computer_use_demo/tools/`
- Customize frontend in `frontend/index.html`
- Add authentication and authorization
- Integrate with other services

### Deploy

Ready for production? See the [Deployment Guide](docs/DEPLOYMENT.md) for:
- AWS ECS deployment
- Google Cloud Run
- Azure Container Instances
- Custom VPS setup

## Getting Help

- 📖 Check the [documentation](docs/)
- 🐛 [Open an issue](https://github.com/your-repo/issues)
- 💬 Review API docs at http://localhost:8000/docs
- 🔍 Search existing issues

## Resources

- [Anthropic Documentation](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Happy building! 🚀**
