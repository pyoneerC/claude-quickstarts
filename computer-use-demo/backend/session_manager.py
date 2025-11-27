"""
Session manager for handling active sessions and message processing.
"""

import asyncio
import logging
import os
from typing import Dict, Optional, Any, Callable
from collections import defaultdict

from fastapi import WebSocket
from anthropic.types.beta import BetaContentBlockParam

from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import ToolResult

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages active chat sessions and their message queues."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.websocket_clients: Dict[str, set[WebSocket]] = defaultdict(set)
        self.sse_clients: Dict[str, set[asyncio.Queue]] = defaultdict(set)
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        
    def create_session(
        self,
        session_id: str,
        model: str,
        provider: str,
        system_prompt_suffix: str = ""
    ):
        """Create a new session."""
        self.sessions[session_id] = {
            "model": model,
            "provider": provider,
            "system_prompt_suffix": system_prompt_suffix,
            "messages": [],
            "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        }
        self.message_queues[session_id] = asyncio.Queue()
        
        # Start processing task for this session
        task = asyncio.create_task(self._process_session(session_id))
        self.processing_tasks[session_id] = task
        
        logger.info(f"Session created: {session_id}")
    
    def remove_session(self, session_id: str):
        """Remove a session and clean up resources."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        if session_id in self.message_queues:
            del self.message_queues[session_id]
        
        if session_id in self.websocket_clients:
            del self.websocket_clients[session_id]
        
        if session_id in self.sse_clients:
            del self.sse_clients[session_id]
        
        if session_id in self.processing_tasks:
            task = self.processing_tasks[session_id]
            task.cancel()
            del self.processing_tasks[session_id]
        
        logger.info(f"Session removed: {session_id}")
    
    def queue_message(self, session_id: str, content: str):
        """Queue a message for processing."""
        if session_id not in self.message_queues:
            logger.error(f"Session not found: {session_id}")
            return
        
        self.message_queues[session_id].put_nowait(content)
        logger.info(f"Message queued for session: {session_id}")
    
    def add_websocket_client(self, session_id: str, websocket: WebSocket):
        """Add a WebSocket client to a session."""
        self.websocket_clients[session_id].add(websocket)
        logger.info(f"WebSocket client added to session: {session_id}")
    
    def remove_websocket_client(self, session_id: str, websocket: WebSocket):
        """Remove a WebSocket client from a session."""
        if session_id in self.websocket_clients:
            self.websocket_clients[session_id].discard(websocket)
            logger.info(f"WebSocket client removed from session: {session_id}")
    
    def add_sse_client(self, session_id: str, queue: asyncio.Queue):
        """Add an SSE client to a session."""
        self.sse_clients[session_id].add(queue)
        logger.info(f"SSE client added to session: {session_id}")
    
    def remove_sse_client(self, session_id: str, queue: asyncio.Queue):
        """Remove an SSE client from a session."""
        if session_id in self.sse_clients:
            self.sse_clients[session_id].discard(queue)
            logger.info(f"SSE client removed from session: {session_id}")
    
    async def broadcast_to_session(self, session_id: str, event: dict):
        """Broadcast an event to all clients of a session."""
        # Broadcast to WebSocket clients
        if session_id in self.websocket_clients:
            dead_clients = set()
            for ws in self.websocket_clients[session_id]:
                try:
                    await ws.send_json(event)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    dead_clients.add(ws)
            
            # Remove dead clients
            for ws in dead_clients:
                self.websocket_clients[session_id].discard(ws)
        
        # Broadcast to SSE clients
        if session_id in self.sse_clients:
            dead_clients = set()
            for queue in self.sse_clients[session_id]:
                try:
                    await queue.put(event)
                except Exception as e:
                    logger.error(f"Error sending to SSE: {e}")
                    dead_clients.add(queue)
            
            # Remove dead clients
            for queue in dead_clients:
                self.sse_clients[session_id].discard(queue)
    
    async def _process_session(self, session_id: str):
        """Background task to process messages for a session."""
        logger.info(f"Starting message processor for session: {session_id}")
        
        try:
            while True:
                # Wait for a message
                content = await self.message_queues[session_id].get()
                
                # Process the message
                await self._process_message(session_id, content)
                
        except asyncio.CancelledError:
            logger.info(f"Message processor cancelled for session: {session_id}")
        except Exception as e:
            logger.error(f"Error in message processor for session {session_id}: {e}")
    
    async def _process_message(self, session_id: str, content: str):
        """Process a single message through the sampling loop."""
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return
        
        # Add user message
        user_message = {
            "role": "user",
            "content": [{"type": "text", "text": content}]
        }
        session["messages"].append(user_message)
        
        # Broadcast user message
        await self.broadcast_to_session(session_id, {
            "type": "user_message",
            "content": content
        })
        
        # Broadcast processing status
        await self.broadcast_to_session(session_id, {
            "type": "status",
            "status": "processing",
            "message": "Processing your request..."
        })
        
        # Define callbacks
        def output_callback(content_block: BetaContentBlockParam):
            """Callback for content blocks."""
            asyncio.create_task(self._handle_output(session_id, content_block))
        
        def tool_output_callback(result: ToolResult, tool_use_id: str):
            """Callback for tool results."""
            asyncio.create_task(self._handle_tool_result(session_id, result, tool_use_id))
        
        def api_response_callback(request, response, error):
            """Callback for API responses."""
            if error:
                asyncio.create_task(self._handle_error(session_id, error))
        
        try:
            # Run the sampling loop
            updated_messages = await sampling_loop(
                model=session["model"],
                provider=APIProvider(session["provider"]),
                system_prompt_suffix=session["system_prompt_suffix"],
                messages=session["messages"],
                output_callback=output_callback,
                tool_output_callback=tool_output_callback,
                api_response_callback=api_response_callback,
                api_key=session["api_key"],
                max_tokens=4096,
                tool_version="computer_use_20250124",
            )
            
            # Update session messages
            session["messages"] = updated_messages
            
            # Broadcast completion
            await self.broadcast_to_session(session_id, {
                "type": "status",
                "status": "completed",
                "message": "Request completed"
            })
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self._handle_error(session_id, e)
    
    async def _handle_output(self, session_id: str, content_block: BetaContentBlockParam):
        """Handle output content blocks."""
        if isinstance(content_block, dict):
            block_type = content_block.get("type")
            
            if block_type == "text":
                await self.broadcast_to_session(session_id, {
                    "type": "text",
                    "text": content_block.get("text", "")
                })
            
            elif block_type == "thinking":
                await self.broadcast_to_session(session_id, {
                    "type": "thinking",
                    "thinking": content_block.get("thinking", "")
                })
            
            elif block_type == "tool_use":
                await self.broadcast_to_session(session_id, {
                    "type": "tool_use",
                    "tool_name": content_block.get("name", ""),
                    "tool_input": content_block.get("input", {}),
                    "tool_use_id": content_block.get("id", "")
                })
    
    async def _handle_tool_result(self, session_id: str, result: ToolResult, tool_use_id: str):
        """Handle tool execution results."""
        event = {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "output": result.output,
            "error": result.error,
        }
        
        if result.base64_image:
            event["base64_image"] = result.base64_image
        
        await self.broadcast_to_session(session_id, event)
    
    async def _handle_error(self, session_id: str, error: Exception):
        """Handle errors."""
        await self.broadcast_to_session(session_id, {
            "type": "error",
            "error": str(error),
            "details": str(type(error).__name__)
        })
