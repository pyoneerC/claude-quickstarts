"""
FastAPI backend for Computer Use Demo.
Provides session management, real-time streaming, and VNC connection APIs.
"""

import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import SessionCreate, SessionResponse, MessageCreate, MessageResponse
from backend.database import init_db, get_db
from backend.session_manager import SessionManager
from backend.vnc_proxy import VNCProxy
from backend import crud

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="Computer Use Demo API",
    description="FastAPI backend for Anthropic Computer Use Demo with session management, real-time streaming, and VNC access",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
session_manager = SessionManager()
vnc_proxy = VNCProxy()


# ===== Session Management APIs =====

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(
    session: SessionCreate,
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """Create a new chat session."""
    try:
        db_session = await crud.create_session(
            db,
            model=session.model,
            provider=session.provider,
            system_prompt_suffix=session.system_prompt_suffix
        )
        
        # Initialize session in manager
        session_manager.create_session(
            session_id=db_session.id,
            model=db_session.model,
            provider=db_session.provider,
            system_prompt_suffix=db_session.system_prompt_suffix or ""
        )
        
        logger.info(f"Created session: {db_session.id}")
        return SessionResponse(
            id=db_session.id,
            model=db_session.model,
            provider=db_session.provider,
            system_prompt_suffix=db_session.system_prompt_suffix,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """Get session details."""
    db_session = await crud.get_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        id=db_session.id,
        model=db_session.model,
        provider=db_session.provider,
        system_prompt_suffix=db_session.system_prompt_suffix,
        created_at=db_session.created_at,
        updated_at=db_session.updated_at
    )


@app.get("/api/sessions")
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all sessions."""
    sessions = await crud.get_sessions(db, skip=skip, limit=limit)
    return [
        SessionResponse(
            id=s.id,
            model=s.model,
            provider=s.provider,
            system_prompt_suffix=s.system_prompt_suffix,
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        for s in sessions
    ]


@app.delete("/api/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a session."""
    success = await crud.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clean up from session manager
    session_manager.remove_session(session_id)
    
    return {"message": "Session deleted successfully"}


# ===== Message APIs =====

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a session."""
    messages = await crud.get_messages(db, session_id, skip=skip, limit=limit)
    return [
        MessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            timestamp=m.timestamp
        )
        for m in messages
    ]


@app.post("/api/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message and process it.
    Returns immediately with message ID. Use WebSocket or SSE for real-time updates.
    """
    # Verify session exists
    db_session = await crud.get_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Store user message
    user_message = await crud.create_message(
        db,
        session_id=session_id,
        role="user",
        content=[{"type": "text", "text": message.content}]
    )
    
    # Queue the message for processing
    session_manager.queue_message(session_id, message.content)
    
    return {
        "message_id": user_message.id,
        "session_id": session_id,
        "status": "queued"
    }


# ===== Real-time Streaming APIs =====

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time streaming of agent progress.
    Sends updates as the agent processes messages.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for session: {session_id}")
    
    try:
        # Add client to session
        session_manager.add_websocket_client(session_id, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if message_data.get("type") == "message":
                    # Queue message for processing
                    content = message_data.get("content", "")
                    session_manager.queue_message(session_id, content)
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session: {session_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })
                
    finally:
        session_manager.remove_websocket_client(session_id, websocket)


@app.get("/api/sessions/{session_id}/stream")
async def sse_endpoint(session_id: str):
    """
    Server-Sent Events endpoint for real-time streaming.
    Alternative to WebSocket for one-way communication.
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        queue = asyncio.Queue()
        session_manager.add_sse_client(session_id, queue)
        
        try:
            while True:
                # Wait for events
                event = await queue.get()
                
                if event.get("type") == "close":
                    break
                
                # Format as SSE
                yield f"data: {json.dumps(event)}\n\n"
                
        except asyncio.CancelledError:
            logger.info(f"SSE connection cancelled for session: {session_id}")
        finally:
            session_manager.remove_sse_client(session_id, queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ===== VNC Connection APIs =====

@app.get("/api/vnc/info")
async def get_vnc_info():
    """Get VNC connection information."""
    return vnc_proxy.get_connection_info()


@app.websocket("/ws/vnc")
async def vnc_websocket(websocket: WebSocket):
    """WebSocket proxy for VNC connection (for web-based VNC clients)."""
    await vnc_proxy.handle_websocket(websocket)


# ===== Health Check =====

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(session_manager.sessions)
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Computer Use Demo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Mount static files for frontend
try:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
except Exception as e:
    logger.warning(f"Frontend directory not found: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
