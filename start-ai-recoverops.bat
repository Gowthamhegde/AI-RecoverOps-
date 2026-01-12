@echo off
echo Starting AI-RecoverOps Platform...
echo.

REM Start API server
echo Starting API server...
start "AI-RecoverOps API" cmd /k "python api/main.py"

REM Wait for API to start
timeout /t 5 /nobreak > nul

REM Start dashboard
echo Starting dashboard...
cd dashboard
start "AI-RecoverOps Dashboard" cmd /k "npm start"
cd ..

REM Wait for dashboard to start
timeout /t 10 /nobreak > nul

REM Open browser
echo Opening browser...
start http://localhost:3000

echo.
echo AI-RecoverOps is starting up!
echo Dashboard: http://localhost:3000
echo API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause > nul