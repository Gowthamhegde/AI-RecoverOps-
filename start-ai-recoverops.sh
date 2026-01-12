#!/bin/bash
echo "Starting AI-RecoverOps Platform..."
echo

# Start API server in background
echo "Starting API server..."
python3 api/main.py &
API_PID=$!

# Wait for API to start
sleep 5

# Start dashboard in background
echo "Starting dashboard..."
cd dashboard
npm start &
DASHBOARD_PID=$!
cd ..

# Wait for dashboard to start
sleep 10

# Open browser
echo "Opening browser..."
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    open http://localhost:3000
fi

echo
echo "AI-RecoverOps is running!"
echo "Dashboard: http://localhost:3000"
echo "API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "Stopping services..."; kill $API_PID $DASHBOARD_PID 2>/dev/null; exit' INT
wait