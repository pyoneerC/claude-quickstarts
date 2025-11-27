# Architecture Overview

## System Architecture

The Computer Use Demo backend follows a modern, scalable architecture with clear separation of concerns.

```
┌──────────────────────────────────────────────────────────────────┐
│                         Client Layer                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │  Web Browser │  │ API Clients  │  │  Custom Applications    │ │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬──────────────┘ │
└─────────┼────────────────┼──────────────────────┼────────────────┘
          │                │                      │
          ├────────────────┴──────────────────────┤
          │                                       │
┌─────────▼───────────────────────────────────────▼────────────────┐
│                     API Gateway Layer                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Application                    │   │
│  │  • RESTful APIs    • WebSocket     • SSE                 │   │
│  │  • OpenAPI Docs    • CORS          • Error Handling      │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
          │                │                      │
┌─────────▼────────────────▼──────────────────────▼────────────────┐
│                    Business Logic Layer                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │ Session Manager  │  │   CRUD Ops       │  │   VNC Proxy    │ │
│  │  • Sessions      │  │  • Database      │  │  • WebSocket   │ │
│  │  • Message Queue │  │  • Models        │  │  • Forwarding  │ │
│  │  • Callbacks     │  │  • Persistence   │  │                │ │
│  └──────────────────┘  └──────────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
          │                │                      │
┌─────────▼────────────────▼──────────────────────▼────────────────┐
│                     External Services Layer                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │  Anthropic API   │  │   PostgreSQL     │  │   X11/VNC      │ │
│  │  • Claude Models │  │  • Sessions      │  │  • Desktop     │ │
│  │  • Tool Calling  │  │  • Messages      │  │  • Tools       │ │
│  └──────────────────┘  └──────────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Gateway Layer (FastAPI)

**Responsibilities:**
- HTTP request routing
- WebSocket management
- SSE streaming
- Request validation
- Response formatting
- CORS handling
- Error handling

**Key Files:**
- `backend/main.py` - Application entry point and route definitions

### 2. Session Manager

**Responsibilities:**
- Manage active sessions
- Queue and process messages
- Handle WebSocket/SSE clients
- Execute sampling loop
- Broadcast events to clients

**Key Features:**
- Asynchronous message processing
- Background task management
- Event broadcasting
- Client lifecycle management

**Key Files:**
- `backend/session_manager.py`

### 3. Database Layer

**Responsibilities:**
- Data persistence
- Session management
- Message history
- CRUD operations

**Technologies:**
- SQLAlchemy (ORM)
- Async support (aiosqlite, asyncpg)
- PostgreSQL (production)
- SQLite (development)

**Key Files:**
- `backend/database.py` - Database configuration
- `backend/models.py` - SQLAlchemy models & Pydantic schemas
- `backend/crud.py` - CRUD operations

### 4. Computer Use Integration

**Responsibilities:**
- Execute Anthropic's sampling loop
- Manage tool collection
- Handle tool execution
- Process API responses

**Key Components:**
- `computer_use_demo/loop.py` - Agentic sampling loop
- `computer_use_demo/tools/` - Computer use tools

### 5. VNC Proxy

**Responsibilities:**
- Proxy VNC connections
- WebSocket tunneling
- Connection management

**Key Files:**
- `backend/vnc_proxy.py`

## Data Flow

### Session Creation Flow

```
Client                FastAPI               Database            Session Manager
  │                      │                      │                      │
  ├─POST /api/sessions──>│                      │                      │
  │                      ├─create_session()────>│                      │
  │                      │<─────session─────────┤                      │
  │                      ├─create_session()─────────────────────────>│
  │                      │<─────────────────────────────────────────────┤
  │<─────session─────────┤                      │                      │
  │                      │                      │                      │
```

### Message Processing Flow

```
Client            WebSocket         Session Manager       Anthropic API      Tools
  │                  │                     │                    │              │
  ├─send message────>│                     │                    │              │
  │                  ├─queue_message()────>│                    │              │
  │                  │                     ├─sampling_loop()───>│              │
  │                  │                     │<───tool_use────────┤              │
  │                  │                     ├─execute_tool()────────────────>│
  │                  │                     │<──tool_result──────────────────┤
  │                  │                     ├─broadcast_event()─>│              │
  │<─event───────────┤<────────────────────┤                    │              │
  │                  │                     ├─continue_loop()───>│              │
  │                  │                     │<───response────────┤              │
  │<─event───────────┤<────────────────────┤                    │              │
```

### Real-time Streaming Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ├──WebSocket Connection──────┐
       │                            │
       ├──SSE Connection───────┐    │
       │                       │    │
       ▼                       ▼    ▼
┌──────────────────────────────────────┐
│      Session Manager                 │
│  ┌────────────────────────────────┐  │
│  │   Event Broadcasting System    │  │
│  │  • WebSocket clients set       │  │
│  │  • SSE clients queue           │  │
│  │  • Event serialization         │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
       │
       ▼
  [JSON Events]
  • text
  • thinking
  • tool_use
  • tool_result
  • status
  • error
```

## Concurrency Model

### Async/Await Pattern

All I/O operations use Python's async/await:

```python
# Database operations
async def create_session(db: AsyncSession, ...):
    # Async database operation
    ...

# API endpoints
@app.post("/api/sessions")
async def create_session(...):
    # Async processing
    ...

# WebSocket handling
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(...):
    # Async communication
    ...
```

### Background Task Management

Each session runs a background task for message processing:

```
Session 1 ──> Background Task 1 ──> Message Queue 1 ──> Processing Loop
Session 2 ──> Background Task 2 ──> Message Queue 2 ──> Processing Loop
Session 3 ──> Background Task 3 ──> Message Queue 3 ──> Processing Loop
```

## Scalability Considerations

### Horizontal Scaling

**Challenges:**
- Session state management
- WebSocket connection persistence
- Database connection pooling

**Solutions:**
- External session storage (Redis)
- Sticky sessions on load balancer
- Database read replicas

### Vertical Scaling

**Resource Requirements:**
- CPU: 2-4 cores (for concurrent sessions)
- Memory: 4-8GB (for X11 desktop + Python processes)
- Storage: 20GB+ (for database and desktop environment)

## Security Architecture

### Authentication & Authorization

Currently implemented:
- API key for Anthropic API
- No user authentication (add for production)

Production recommendations:
- JWT tokens
- OAuth2 integration
- API key management
- Role-based access control

### Network Security

```
Internet
   │
   ▼
┌──────────────┐
│  Load Balancer │ ← SSL/TLS Termination
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Firewall    │ ← Port filtering
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Application  │ ← CORS, Rate limiting
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Database    │ ← VPC, Private subnet
└──────────────┘
```

## Monitoring & Observability

### Logging Levels

- **INFO**: Normal operations (session creation, message processing)
- **WARNING**: Degraded operations (slow responses, retries)
- **ERROR**: Failures (API errors, database errors)

### Metrics to Track

- Active sessions count
- Message processing time
- API response times
- Database query times
- WebSocket connection count
- Error rates

### Health Checks

```
GET /health
├─ Database connectivity
├─ Active sessions count
└─ System resources
```

## Error Handling Strategy

### Graceful Degradation

```
API Error ──> Log error ──> Broadcast error event ──> Client handles
                                                        └─> Retry
                                                        └─> User notification
```

### Retry Logic

- Anthropic API: 4 retries (built-in)
- Database: Connection retry on failure
- WebSocket: Automatic reconnection on client

## Future Enhancements

### Planned Features

1. **Authentication System**
   - User accounts
   - API keys
   - Usage quotas

2. **Multi-tenancy**
   - Isolated sessions per user
   - Resource limits
   - Billing integration

3. **Enhanced Monitoring**
   - Metrics dashboard
   - Performance analytics
   - Cost tracking

4. **Advanced Features**
   - Session sharing
   - Collaborative sessions
   - Recording & replay
   - Custom tool integration

### Performance Optimizations

1. **Caching**
   - Response caching
   - Static asset CDN
   - Database query caching

2. **Database**
   - Connection pooling
   - Read replicas
   - Query optimization

3. **API**
   - Request batching
   - Response compression
   - Rate limiting
