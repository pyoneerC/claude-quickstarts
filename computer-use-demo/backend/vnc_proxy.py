"""
VNC proxy for connecting to the virtual desktop.
"""

import asyncio
import logging
import os
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class VNCProxy:
    """Proxy for VNC connections to the virtual desktop."""
    
    def __init__(self):
        self.vnc_host = os.getenv("VNC_HOST", "localhost")
        self.vnc_port = int(os.getenv("VNC_PORT", "5900"))
        self.novnc_port = int(os.getenv("NOVNC_PORT", "6080"))
        
    def get_connection_info(self) -> dict:
        """Get VNC connection information."""
        return {
            "vnc_host": self.vnc_host,
            "vnc_port": self.vnc_port,
            "novnc_port": self.novnc_port,
            "novnc_url": f"http://{self.vnc_host}:{self.novnc_port}/vnc.html",
            "websocket_url": f"ws://{self.vnc_host}:{self.novnc_port}/websockify"
        }
    
    async def handle_websocket(self, websocket: WebSocket):
        """
        Handle WebSocket connection for VNC.
        This proxies data between the client WebSocket and the VNC server.
        """
        await websocket.accept()
        logger.info("VNC WebSocket connection established")
        
        try:
            # Connect to VNC server
            reader, writer = await asyncio.open_connection(
                self.vnc_host,
                self.vnc_port
            )
            
            # Create tasks for bidirectional data transfer
            client_to_vnc = asyncio.create_task(
                self._forward_client_to_vnc(websocket, writer)
            )
            vnc_to_client = asyncio.create_task(
                self._forward_vnc_to_client(reader, websocket)
            )
            
            # Wait for either task to complete (connection closed)
            done, pending = await asyncio.wait(
                [client_to_vnc, vnc_to_client],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            
            # Close connections
            writer.close()
            await writer.wait_closed()
            
        except WebSocketDisconnect:
            logger.info("VNC WebSocket disconnected")
        except Exception as e:
            logger.error(f"VNC WebSocket error: {e}")
        finally:
            logger.info("VNC WebSocket connection closed")
    
    async def _forward_client_to_vnc(self, websocket: WebSocket, writer: asyncio.StreamWriter):
        """Forward data from WebSocket client to VNC server."""
        try:
            while True:
                data = await websocket.receive_bytes()
                writer.write(data)
                await writer.drain()
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"Error forwarding client to VNC: {e}")
    
    async def _forward_vnc_to_client(self, reader: asyncio.StreamReader, websocket: WebSocket):
        """Forward data from VNC server to WebSocket client."""
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception as e:
            logger.error(f"Error forwarding VNC to client: {e}")
