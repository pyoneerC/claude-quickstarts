"""
Example client for interacting with the FastAPI backend.
"""

import asyncio
import json
import os
from typing import Optional
import httpx
import websockets


class ComputerUseClient:
    """Client for interacting with the Computer Use Demo API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
        self.session_id: Optional[str] = None
        
    async def create_session(
        self,
        model: str = "claude-sonnet-4-5-20250929",
        provider: str = "anthropic",
        system_prompt_suffix: Optional[str] = None
    ) -> dict:
        """Create a new session."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/sessions",
                json={
                    "model": model,
                    "provider": provider,
                    "system_prompt_suffix": system_prompt_suffix
                }
            )
            response.raise_for_status()
            session = response.json()
            self.session_id = session["id"]
            print(f"Created session: {self.session_id}")
            return session
    
    async def list_sessions(self) -> list:
        """List all sessions."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/sessions")
            response.raise_for_status()
            return response.json()
    
    async def get_session(self, session_id: str) -> dict:
        """Get session details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/sessions/{session_id}")
            response.raise_for_status()
            return response.json()
    
    async def delete_session(self, session_id: str):
        """Delete a session."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/api/sessions/{session_id}")
            response.raise_for_status()
            print(f"Deleted session: {session_id}")
    
    async def send_message(self, content: str, session_id: Optional[str] = None):
        """Send a message via HTTP."""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID available")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/sessions/{sid}/messages",
                json={"content": content}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_messages(self, session_id: Optional[str] = None) -> list:
        """Get messages for a session."""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID available")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/sessions/{sid}/messages")
            response.raise_for_status()
            return response.json()
    
    async def stream_with_websocket(
        self,
        message: str,
        session_id: Optional[str] = None,
        on_event: Optional[callable] = None
    ):
        """Send a message and stream responses via WebSocket."""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID available")
        
        async with websockets.connect(f"{self.ws_url}/ws/{sid}") as websocket:
            # Send message
            await websocket.send(json.dumps({
                "type": "message",
                "content": message
            }))
            
            # Receive responses
            async for message in websocket:
                event = json.loads(message)
                
                if on_event:
                    on_event(event)
                else:
                    print(f"Event: {event}")
                
                # Stop on completion or error
                if event.get("type") == "status" and event.get("status") == "completed":
                    break
                if event.get("type") == "error":
                    break
    
    async def get_vnc_info(self) -> dict:
        """Get VNC connection information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/vnc/info")
            response.raise_for_status()
            return response.json()


async def main():
    """Example usage."""
    client = ComputerUseClient()
    
    # Create a session
    session = await client.create_session(
        model="claude-sonnet-4-5-20250929",
        provider="anthropic",
        system_prompt_suffix="You are a helpful assistant."
    )
    print(f"Session created: {session['id']}")
    
    # Event handler
    def handle_event(event):
        event_type = event.get("type")
        
        if event_type == "text":
            print(f"Assistant: {event['text']}")
        elif event_type == "thinking":
            print(f"Thinking: {event['thinking']}")
        elif event_type == "tool_use":
            print(f"Using tool: {event['tool_name']}")
            print(f"Input: {json.dumps(event['tool_input'], indent=2)}")
        elif event_type == "tool_result":
            if event.get('output'):
                print(f"Tool output: {event['output'][:200]}...")
            if event.get('base64_image'):
                print("Tool returned an image")
        elif event_type == "status":
            print(f"Status: {event['status']} - {event.get('message', '')}")
        elif event_type == "error":
            print(f"Error: {event['error']}")
    
    # Send a message with streaming
    print("\nSending message...")
    await client.stream_with_websocket(
        "Take a screenshot and tell me what you see",
        on_event=handle_event
    )
    
    # Get VNC info
    vnc_info = await client.get_vnc_info()
    print(f"\nVNC URL: {vnc_info['novnc_url']}")
    
    # Get messages
    messages = await client.get_messages()
    print(f"\nTotal messages: {len(messages)}")


if __name__ == "__main__":
    asyncio.run(main())
