"""
Script to initialize and test the backend setup.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from backend.database import init_db


async def check_database():
    """Check database connection and initialize tables."""
    print("🗄️  Checking database...")
    try:
        await init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


async def check_api_key():
    """Check if Anthropic API key is set."""
    print("\n🔑 Checking API key...")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("   Set it in .env file or environment variables")
        return False
    
    if api_key.startswith("sk-ant-"):
        print("✅ API key found and looks valid")
        return True
    else:
        print("⚠️  API key found but format looks unusual")
        return True


async def check_backend():
    """Check if backend is running."""
    print("\n🌐 Checking backend...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend is running")
                print(f"   Status: {data.get('status')}")
                print(f"   Active sessions: {data.get('active_sessions', 0)}")
                return True
            else:
                print(f"⚠️  Backend responded with status {response.status_code}")
                return False
    except httpx.ConnectError:
        print("❌ Backend is not running")
        print("   Start it with: docker-compose up")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False


async def test_session_creation():
    """Test creating a session."""
    print("\n🧪 Testing session creation...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/sessions",
                json={
                    "model": "claude-sonnet-4-5-20250929",
                    "provider": "anthropic",
                    "system_prompt_suffix": "Test session"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get("id")
                print(f"✅ Session created successfully")
                print(f"   ID: {session_id}")
                
                # Clean up
                await client.delete(f"http://localhost:8000/api/sessions/{session_id}")
                print(f"   Cleaned up test session")
                return True
            else:
                print(f"❌ Failed to create session: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing session creation: {e}")
        return False


async def check_vnc():
    """Check VNC configuration."""
    print("\n🖥️  Checking VNC...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/vnc/info", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ VNC configured")
                print(f"   Host: {data.get('vnc_host')}:{data.get('vnc_port')}")
                print(f"   noVNC URL: {data.get('novnc_url')}")
                return True
            else:
                print(f"⚠️  VNC endpoint responded with status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error checking VNC: {e}")
        return False


async def main():
    """Run all checks."""
    print("=" * 60)
    print("Computer Use Demo - Backend Setup Check")
    print("=" * 60)
    
    results = []
    
    # Run checks
    results.append(("Database", await check_database()))
    results.append(("API Key", await check_api_key()))
    results.append(("Backend", await check_backend()))
    
    # Only run these if backend is running
    if results[-1][1]:
        results.append(("Session Creation", await test_session_creation()))
        results.append(("VNC", await check_vnc()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for check, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed!")
        print("You can access the application at:")
        print("  - Web UI: http://localhost:8000")
        print("  - API Docs: http://localhost:8000/docs")
        print("  - VNC: http://localhost:6080/vnc.html")
    else:
        print("⚠️  Some checks failed. Please review the output above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
