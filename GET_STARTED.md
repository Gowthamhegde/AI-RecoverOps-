# 🚀 Get Started with AI-RecoverOps

## Quick Launch (Easiest Way)

### Option 1: One-Click Python Launcher
```bash
python launch-ai-recoverops.py
```
This will automatically:
- Start the API server
- Start the dashboard
- Open your browser
- Show you all access points

### Option 2: Platform-Specific Launchers

**Windows:**
```cmd
# Double-click this file or run:
AI-RecoverOps.bat
```

**Mac/Linux:**
```bash
./start-ai-recoverops.sh
```

## What You'll See

Once started, you'll have access to:

| Service | URL | What it does |
|---------|-----|--------------|
| 📊 **Dashboard** | http://localhost:3000 | Main web interface for monitoring |
| 🔧 **API** | http://localhost:8000 | Backend service for integrations |
| 📖 **API Docs** | http://localhost:8000/docs | Interactive API documentation |

## First Steps

### 1. Explore the Dashboard
- **Dashboard Tab**: Overview of system health and incidents
- **Incidents Tab**: Detailed incident management
- **Analytics Tab**: Historical data and trends
- **Models Tab**: AI model status and performance
- **Settings Tab**: Configuration and integrations

### 2. Test AI Detection
Send a sample log to see AI in action:

**Using PowerShell (Windows):**
```powershell
$body = @{
    logs = @(
        @{
            timestamp = "2026-01-13T00:00:00Z"
            log_level = "ERROR"
            service = "web-server"
            aws_service = "ec2"
            instance_id = "i-1234567890abcdef0"
            message = "High CPU usage detected: 95%"
            region = "us-east-1"
            environment = "production"
            metadata = @{}
        }
    )
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
```

**Using curl (Mac/Linux):**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [{
      "timestamp": "2026-01-13T00:00:00Z",
      "log_level": "ERROR",
      "service": "web-server",
      "aws_service": "ec2",
      "instance_id": "i-1234567890abcdef0",
      "message": "High CPU usage detected: 95%",
      "region": "us-east-1",
      "environment": "production",
      "metadata": {}
    }]
  }'
```

### 3. Check the Results
After sending the test log:
1. Go to the **Incidents** tab in the dashboard
2. You should see a new incident detected
3. Check the **Dashboard** tab for updated statistics
4. The AI should have automatically triggered remediation

## Common Use Cases

### For DevOps Teams
```bash
# Monitor production logs
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"logs": [your_log_data]}'

# Check incident status
curl "http://localhost:8000/api/incidents"

# Get system metrics
curl "http://localhost:8000/api/metrics"
```

### For Monitoring Integration
```python
import requests

# Send logs to AI-RecoverOps
response = requests.post('http://localhost:8000/predict', json={
    'logs': [log_entry]
})

incidents = response.json()['predictions']
```

### For Dashboard Integration
The dashboard provides real-time monitoring with:
- Live incident feeds
- System health metrics
- Auto-remediation status
- Historical analytics

## Troubleshooting

### Services Won't Start
```bash
# Check if ports are in use
netstat -an | findstr "3000 8000"  # Windows
netstat -an | grep "3000\|8000"   # Mac/Linux

# Kill processes using the ports if needed
# Then restart with the launcher
```

### Dashboard Shows Errors
1. Make sure the API is running on port 8000
2. Check browser console for errors
3. Try refreshing the page
4. Restart both services

### API Not Responding
1. Check if Python dependencies are installed
2. Verify the API process is running
3. Check for error messages in the terminal
4. Try restarting the API service

## Next Steps

### 1. Integrate with Your Systems
- Use the REST API to send real logs
- Set up webhooks for notifications
- Configure monitoring dashboards

### 2. Customize Detection
- Add your own incident types
- Adjust confidence thresholds
- Configure auto-remediation rules

### 3. Production Deployment
- Follow the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Set up proper authentication
- Configure production databases

## Need Help?

- 📖 **Full Documentation**: [USER_GUIDE.md](USER_GUIDE.md)
- 🚀 **Production Setup**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- 🏗️ **Architecture**: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- 🐛 **Issues**: Report on GitHub

---

**Ready to revolutionize your DevOps? Start exploring! 🚀**