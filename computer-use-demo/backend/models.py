"""
Database models and schemas.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ===== SQLAlchemy Models =====

class SessionDB(Base):
    """Database model for chat sessions."""
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    model = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    system_prompt_suffix = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    messages = relationship("MessageDB", back_populates="session", cascade="all, delete-orphan")


class MessageDB(Base):
    """Database model for chat messages."""
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(JSON, nullable=False)  # Store as JSON array
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("SessionDB", back_populates="messages")


# ===== Pydantic Models (API Schemas) =====

class SessionCreate(BaseModel):
    """Schema for creating a new session."""
    model: str = Field(..., description="Model name (e.g., claude-sonnet-4-5-20250929)")
    provider: str = Field(default="anthropic", description="API provider (anthropic, bedrock, vertex)")
    system_prompt_suffix: Optional[str] = Field(None, description="Additional system prompt")


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: str
    model: str
    provider: str
    system_prompt_suffix: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str = Field(..., description="Message content")


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: str
    session_id: str
    role: str
    content: List[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True


class ToolUseEvent(BaseModel):
    """Schema for tool use events."""
    type: str = "tool_use"
    tool_name: str
    tool_input: Dict[str, Any]
    tool_use_id: str


class ToolResultEvent(BaseModel):
    """Schema for tool result events."""
    type: str = "tool_result"
    tool_use_id: str
    output: Optional[str] = None
    error: Optional[str] = None
    base64_image: Optional[str] = None


class TextEvent(BaseModel):
    """Schema for text content events."""
    type: str = "text"
    text: str


class ThinkingEvent(BaseModel):
    """Schema for thinking events."""
    type: str = "thinking"
    thinking: str


class ErrorEvent(BaseModel):
    """Schema for error events."""
    type: str = "error"
    error: str
    details: Optional[str] = None


class StatusEvent(BaseModel):
    """Schema for status events."""
    type: str = "status"
    status: str
    message: Optional[str] = None
