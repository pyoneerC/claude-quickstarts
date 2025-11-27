"""
Tests for the FastAPI backend.
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from backend.main import app
from backend.database import get_db, Base
from backend.models import SessionCreate

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
async def setup_database():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(setup_database):
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestSessionAPI:
    """Test session management APIs."""
    
    @pytest.mark.asyncio
    async def test_create_session(self, client):
        """Test creating a new session."""
        response = await client.post(
            "/api/sessions",
            json={
                "model": "claude-sonnet-4-5-20250929",
                "provider": "anthropic",
                "system_prompt_suffix": "Test prompt"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["model"] == "claude-sonnet-4-5-20250929"
        assert data["provider"] == "anthropic"
    
    @pytest.mark.asyncio
    async def test_get_session(self, client):
        """Test getting a session."""
        # Create session first
        create_response = await client.post(
            "/api/sessions",
            json={
                "model": "claude-sonnet-4-5-20250929",
                "provider": "anthropic"
            }
        )
        session_id = create_response.json()["id"]
        
        # Get session
        response = await client.get(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, client):
        """Test listing sessions."""
        # Create multiple sessions
        for i in range(3):
            await client.post(
                "/api/sessions",
                json={
                    "model": "claude-sonnet-4-5-20250929",
                    "provider": "anthropic"
                }
            )
        
        # List sessions
        response = await client.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    @pytest.mark.asyncio
    async def test_delete_session(self, client):
        """Test deleting a session."""
        # Create session
        create_response = await client.post(
            "/api/sessions",
            json={
                "model": "claude-sonnet-4-5-20250929",
                "provider": "anthropic"
            }
        )
        session_id = create_response.json()["id"]
        
        # Delete session
        response = await client.delete(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 404


class TestMessageAPI:
    """Test message APIs."""
    
    @pytest.mark.asyncio
    async def test_send_message(self, client):
        """Test sending a message."""
        # Create session
        create_response = await client.post(
            "/api/sessions",
            json={
                "model": "claude-sonnet-4-5-20250929",
                "provider": "anthropic"
            }
        )
        session_id = create_response.json()["id"]
        
        # Send message
        response = await client.post(
            f"/api/sessions/{session_id}/messages",
            json={"content": "Test message"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message_id" in data
        assert data["session_id"] == session_id
    
    @pytest.mark.asyncio
    async def test_get_messages(self, client):
        """Test getting messages."""
        # Create session
        create_response = await client.post(
            "/api/sessions",
            json={
                "model": "claude-sonnet-4-5-20250929",
                "provider": "anthropic"
            }
        )
        session_id = create_response.json()["id"]
        
        # Send messages
        await client.post(
            f"/api/sessions/{session_id}/messages",
            json={"content": "Message 1"}
        )
        await client.post(
            f"/api/sessions/{session_id}/messages",
            json={"content": "Message 2"}
        )
        
        # Get messages
        response = await client.get(f"/api/sessions/{session_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2


class TestHealthCheck:
    """Test health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
