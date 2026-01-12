@echo off
title AI-RecoverOps Platform
color 0A

echo.
echo  ========================================
echo   AI-RecoverOps Enterprise Platform
echo  ========================================
echo.
echo  Starting services...
echo.

REM Check if API is already running
netstat -an | find "8000" > nul
if %errorlevel% == 0 (
    echo  API server already running on port 8000
) else (
    echo  Starting API server...
    start "AI-RecoverOps API" /min cmd /c "python api/main.py"
    timeout /t 3 /nobreak > nul
)

REM Check if Dashboard is already running  
netstat -an | find "3000" > nul
if %errorlevel% == 0 (
    echo  Dashboard already running on port 3000
) else (
    echo  Starting dashboard...
    cd dashboard
    start "AI-RecoverOps Dashboard" /min cmd /c "npm start"
    cd ..
    timeout /t 8 /nobreak > nul
)

echo.
echo  Opening AI-RecoverOps Dashboard...
timeout /t 2 /nobreak > nul
start http://localhost:3000

echo.
echo  ========================================
echo   AI-RecoverOps is now running!
echo  ========================================
echo.
echo   Dashboard:  http://localhost:3000
echo   API:        http://localhost:8000  
echo   API Docs:   http://localhost:8000/docs
echo.
echo  Press any key to exit...
pause > nul