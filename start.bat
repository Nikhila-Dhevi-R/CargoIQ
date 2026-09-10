@echo off
title CargoIQ - Startup

echo.
echo  ██╗  ██╗ █████╗ ██╗   ██╗ █████╗  ██████╗██╗  ██╗     █████╗ ██╗
echo  ██║ ██╔╝██╔══██╗██║   ██║██╔══██╗██╔════╝██║  ██║    ██╔══██╗██║
echo  █████╔╝ ███████║██║   ██║███████║██║     ███████║    ███████║██║
echo  ██╔═██╗ ██╔══██║╚██╗ ██╔╝██╔══██║██║     ██╔══██║    ██╔══██║██║
echo  ██║  ██╗██║  ██║ ╚████╔╝ ██║  ██║╚██████╗██║  ██║    ██║  ██║██║
echo  ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝
echo.
echo  CargoIQ — See the Risk. Stop the Damage.
echo  ------------------------------------------------------------------
echo.

REM --- Start Backend (FastAPI + Uvicorn) ---
echo [1/2] Starting CargoIQ Backend (FastAPI on port 8000)...
start "CargoIQ Backend" cmd /k "cd /d %~dp0backend && .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload"

REM Wait for backend to initialize
timeout /t 3 /nobreak >nul

REM --- Start Frontend (Vite Dev Server) ---
echo [2/2] Starting CargoIQ Frontend (Vite on port 5173)...
start "CargoIQ Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

REM Wait for frontend to start
timeout /t 4 /nobreak >nul

echo.
echo  ✓ Backend API:   http://localhost:8000
echo  ✓ Frontend UI:   http://localhost:5173
echo  ✓ API Swagger:   http://localhost:8000/docs
echo.
echo  Opening CargoIQ in your browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173

echo.
echo  Both services are running in separate windows.
echo  Close those windows to stop the servers.
echo.
pause
