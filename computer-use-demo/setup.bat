@echo off
REM Computer Use Demo - Quick Setup Script for Windows

echo =========================================
echo Computer Use Demo - FastAPI Backend Setup
echo =========================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed
    echo Please install Docker Desktop first: https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose is not installed
    echo Please install Docker Compose: https://docs.docker.com/compose/install/
    exit /b 1
)

echo [OK] Docker is installed
echo.

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [WARNING] Please edit .env and add your ANTHROPIC_API_KEY
    echo.
    pause
)

echo [OK] Environment configured
echo.

REM Build and start containers
echo Building Docker containers...
docker-compose build

echo.
echo Starting services...
docker-compose up -d

REM Wait for services to be ready
echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check health
echo.
echo Checking service health...
for /L %%i in (1,1,30) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo [OK] Backend is running
        goto :success
    )
    timeout /t 2 /nobreak >nul
)

echo [ERROR] Backend failed to start. Check logs with: docker-compose logs
exit /b 1

:success
echo.
echo =========================================
echo Setup complete!
echo =========================================
echo.
echo Access the application:
echo   - Web Interface: http://localhost:8000
echo   - API Documentation: http://localhost:8000/docs
echo   - VNC Desktop: http://localhost:6080/vnc.html
echo.
echo Useful commands:
echo   - View logs: docker-compose logs -f
echo   - Stop services: docker-compose down
echo   - Restart services: docker-compose restart
echo.
pause
