# Quick Reference Guide

## Essential Commands

### Starting the System

```bash
# Quick start
docker-compose up -d

# With logs
docker-compose up

# Rebuild and start
docker-compose up --build -d
```

### Stopping the System

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Viewing Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 app
```

### Service Management

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart app

# View running containers
docker-compose ps

# Check resource usage
docker stats
```

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Web Interface | http://localhost:8000 | Main application |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Redoc | http://localhost:8000/redoc | Alternative docs |
| Health Check | http://localhost:8000/health | System status |
| VNC Desktop | http://localhost:6080/vnc.html | Virtual desktop |
| PostgreSQL | localhost:5432 | Database (internal) |

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database (Production)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Database (Development)
DATABASE_URL=sqlite+aiosqlite:///./computer_use_demo.db

# VNC
VNC_HOST=localhost
VNC_PORT=5900
NOVNC_PORT=6080
```

## API Endpoints Quick Reference

### Sessions
```bash
# Create session
POST /api/sessions
{
  "model": "claude-sonnet-4-5-20250929",
  "provider": "anthropic"
}

# List sessions
GET /api/sessions

# Get session
GET /api/sessions/{id}

# Delete session
DELETE /api/sessions/{id}
```

### Messages
```bash
# Send message
POST /api/sessions/{id}/messages
{
  "content": "Your message"
}

# Get messages
GET /api/sessions/{id}/messages
```

### Streaming
```bash
# WebSocket
WS /ws/{session_id}

# Server-Sent Events
GET /api/sessions/{session_id}/stream
```

### VNC
```bash
# Get VNC info
GET /api/vnc/info
```

## Common Tasks

### Reset Database

```bash
docker-compose down -v
docker-compose up -d
```

### Access Container Shell

```bash
# Backend container
docker-compose exec app bash

# Database container
docker-compose exec db psql -U postgres
```

### View Database

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d computer_use_demo

# List tables
\dt

# View sessions
SELECT * FROM sessions;

# View messages
SELECT * FROM messages;
```

### Check API Health

```bash
curl http://localhost:8000/health
```

### Test API Endpoints

```bash
# Create session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-5-20250929","provider":"anthropic"}'

# List sessions
curl http://localhost:8000/api/sessions
```

## Troubleshooting

### Services won't start
```bash
# Check Docker
docker ps

# Rebuild
docker-compose down
docker-compose up --build
```

### Can't connect to API
```bash
# Check if running
docker-compose ps

# Check logs
docker-compose logs app

# Check port
netstat -an | grep 8000
```

### Database issues
```bash
# Reset database
docker-compose down -v
docker volume ls
docker volume rm computer-use-demo_postgres_data
docker-compose up -d
```

### VNC not working
```bash
# Check X server
docker-compose exec app ps aux | grep X

# Restart app
docker-compose restart app

# Check VNC directly
curl http://localhost:6080
```

## File Locations

### Important Files
```
.env                          # Environment config
docker-compose.yml            # Docker orchestration
backend/main.py              # API entry point
backend/session_manager.py   # Session logic
frontend/index.html          # Web interface
```

### Documentation
```
README_BACKEND.md            # Main README
docs/API.md                  # API reference
docs/ARCHITECTURE.md         # System design
docs/DEPLOYMENT.md           # Deploy guide
docs/GETTING_STARTED.md      # Quick start
```

### Logs
```
docker-compose logs          # All logs
docker-compose logs app      # App logs
docker-compose logs db       # Database logs
```

## Development

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r computer_use_demo/requirements.txt

# Run backend
python -m uvicorn backend.main:app --reload
```

### Run Tests

```bash
pip install pytest pytest-asyncio httpx
pytest tests/
```

### Code Quality

```bash
# Type checking (if mypy installed)
mypy backend/

# Linting (if ruff installed)
ruff check backend/

# Format (if black installed)
black backend/
```

## Monitoring

### Check System Resources

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Network
docker network ls
```

### Database Stats

```bash
# Connect to DB
docker-compose exec db psql -U postgres -d computer_use_demo

# Table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public';

# Row counts
SELECT 'sessions' as table, COUNT(*) FROM sessions
UNION ALL
SELECT 'messages', COUNT(*) FROM messages;
```

## Keyboard Shortcuts (VNC)

| Key | Action |
|-----|--------|
| Ctrl+Alt+Shift | Toggle control bar |
| Ctrl+Alt+F11 | Full screen |
| Ctrl+Alt+R | Refresh screen |

## Python Client Example

```python
from examples.client_example import ComputerUseClient
import asyncio

async def main():
    client = ComputerUseClient()
    session = await client.create_session()
    await client.stream_with_websocket(
        "Take a screenshot",
        on_event=print
    )

asyncio.run(main())
```

## JavaScript Client Example

```javascript
// Create session
const res = await fetch('http://localhost:8000/api/sessions', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    model: 'claude-sonnet-4-5-20250929',
    provider: 'anthropic'
  })
});
const session = await res.json();

// Connect WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/${session.id}`);
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({type: 'message', content: 'Hello!'}));
```

## Support Resources

- 📖 [Full Documentation](docs/)
- 🔧 [API Reference](http://localhost:8000/docs)
- 🐛 [GitHub Issues](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)

---

**Last Updated**: 2024
