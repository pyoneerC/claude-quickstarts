# Demo Video Script (5 minutes)

## Preparation Checklist

- [ ] Docker Desktop running
- [ ] Services started: `docker-compose up`
- [ ] Browser open to http://localhost:8000
- [ ] VNC tab ready at http://localhost:6080/vnc.html
- [ ] API docs tab ready at http://localhost:8000/docs
- [ ] Screen recording software ready
- [ ] Microphone tested

## Video Structure

### Intro (30 seconds)

**Script:**
"Hi! Today I'm demonstrating the Computer Use Demo with a production-ready FastAPI backend. This system transforms Anthropic's experimental Streamlit interface into a scalable, real-time API with database persistence, WebSocket streaming, and VNC access."

**Actions:**
- Show main web interface
- Briefly show the browser tabs ready

---

### Part 1: Architecture Overview (1 minute)

**Script:**
"The architecture consists of three main layers: a FastAPI backend providing RESTful APIs and WebSocket streaming, a PostgreSQL database for persistence, and an embedded VNC-accessible virtual desktop where Claude can interact with applications."

**Actions:**
- Show `docs/ARCHITECTURE.md` diagram
- Briefly show folder structure
- Show `docker-compose.yml` file
- Show running containers: `docker-compose ps`

**Key Points:**
- FastAPI backend with async/await
- PostgreSQL for session persistence
- Real-time streaming (WebSocket + SSE)
- VNC for desktop access

---

### Part 2: Session Management (1 minute)

**Script:**
"Let's create a new session. I'll select Claude Sonnet 4.5, configure the Anthropic provider, and create the session. The API automatically initializes the session, starts a background processing task, and stores it in the database."

**Actions:**
1. Fill in session form:
   - Model: claude-sonnet-4-5-20250929
   - Provider: anthropic
   - System prompt: "You are a helpful assistant"
2. Click "Create New Session"
3. Show session appearing in list
4. Show connection status changing to "Connected"
5. Switch to API docs tab
6. Show `GET /api/sessions` endpoint
7. Execute it to show session in database

**Key Points:**
- Session created and persisted
- Background task started
- WebSocket connected
- Database record created

---

### Part 3: Real-time Chat & Streaming (2 minutes)

**Script:**
"Now let's demonstrate the real-time streaming. I'll ask Claude to take a screenshot and analyze it. Watch how events stream in real-time: thinking events showing Claude's reasoning, tool use events when it executes actions, and tool results with the actual screenshot."

**Actions:**
1. Type message: "Take a screenshot of the desktop and tell me what you see"
2. Click Send
3. **Point out events as they appear:**
   - "Processing..." status
   - Thinking event (if available)
   - Tool use event: `computer` with `screenshot` action
   - Tool result with base64 image
   - Screenshot appears inline
   - Text response from Claude
4. Switch to VNC tab
5. Show the desktop that was captured
6. Return to chat
7. Send another message: "Open the calculator application"
8. Watch tool events again
9. Switch to VNC to show calculator opening

**Key Points:**
- Real-time WebSocket streaming
- Multiple event types
- Screenshots displayed inline
- VNC shows live desktop
- Tool execution visible

---

### Part 4: API & Database (1 minute)

**Script:**
"Behind the scenes, all interactions are persisted to the database and accessible via RESTful APIs. Let me show you the API documentation and the message history."

**Actions:**
1. Switch to API docs tab (http://localhost:8000/docs)
2. Scroll through endpoints
3. Click on `GET /api/sessions/{session_id}/messages`
4. Click "Try it out"
5. Enter session ID from the UI
6. Execute
7. Show message history in JSON format
8. Show both user and assistant messages
9. Show content structure

**Key Points:**
- OpenAPI/Swagger documentation
- All messages persisted
- RESTful API access
- JSON structure

---

### Part 5: Production Features (30 seconds)

**Script:**
"This system is production-ready with comprehensive documentation, Docker deployment, support for PostgreSQL in production, multiple cloud deployment guides, and a complete test suite. Everything you need to deploy this to AWS, GCP, or Azure is included."

**Actions:**
- Show `README_BACKEND.md` in editor
- Scroll through documentation files:
  - `docs/API.md`
  - `docs/DEPLOYMENT.md`
  - `docs/GETTING_STARTED.md`
- Show `tests/test_backend.py`
- Show `examples/client_example.py`
- Show `docker-compose.yml` with PostgreSQL config

**Key Points:**
- Production-ready
- Complete documentation
- Cloud deployment guides
- Testing infrastructure
- Docker orchestration

---

### Conclusion (30 seconds)

**Script:**
"In summary, this implementation provides a scalable FastAPI backend with real-time streaming, database persistence, comprehensive APIs, and production deployment support. The code is well-documented, tested, and ready for deployment. Thank you for watching!"

**Actions:**
- Show final chat interface with conversation history
- Show session list with multiple sessions
- Show health check endpoint
- End with GitHub repo screen (when ready)

---

## Key Talking Points

### Backend Design (40%)
- FastAPI with async/await throughout
- Clean architecture with separation of concerns
- Session manager with background task processing
- Comprehensive error handling

### Real-time Streaming (25%)
- WebSocket for bidirectional communication
- SSE as alternative
- Event-driven architecture
- Support for multiple concurrent clients

### Code Quality (20%)
- Type hints throughout
- Comprehensive documentation
- Test suite included
- Best practices followed

### Documentation (15%)
- Complete API reference
- Architecture documentation
- Deployment guides
- Getting started guide

---

## Recording Tips

1. **Resolution**: 1920x1080 minimum
2. **Audio**: Clear narration, no background noise
3. **Speed**: Not too fast, pause for effect
4. **Highlighting**: Use cursor to highlight important elements
5. **Transitions**: Smooth transitions between tabs
6. **Preparation**: Rehearse 2-3 times before final recording

---

## Post-Recording Checklist

- [ ] Video is 5 minutes or less
- [ ] Audio is clear
- [ ] All features demonstrated
- [ ] No sensitive information visible (API keys)
- [ ] Smooth playback
- [ ] Export in standard format (MP4, 1080p)

---

## Alternative Demo Flow (If Issues)

If live demo has issues, have these backup demonstrations ready:

1. **Pre-recorded session**: Have a successful interaction recorded
2. **API testing**: Use Postman/Insomnia to show API
3. **Code walkthrough**: Show code structure instead
4. **Documentation**: Focus on comprehensive docs

---

## Questions to Address

Be prepared to answer:
- "How does this scale?" → Show session management, async design
- "How is it deployed?" → Show Docker, cloud guides
- "What about security?" → Mention auth recommendations
- "Can I extend it?" → Show tool collection, documentation

---

Good luck with your demo! 🎬
