# 🚀 AI-RecoverOps Quick Start

## Get Started in 3 Steps

### 1. Run the Setup (One Time Only)
```bash
python ai-recoverops-setup.py
```

### 2. Start AI-RecoverOps
**Windows:**
```cmd
start-ai-recoverops.bat
```

**Mac/Linux:**
```bash
./start-ai-recoverops.sh
```

### 3. Access the Platform
- 📊 **Dashboard**: http://localhost:3000
- 🔧 **API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs

## What You Can Do

### 🤖 Test AI Incident Detection
Send a log to see AI in action:
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

### 📊 View Dashboard
- Real-time incident monitoring
- System health metrics
- Auto-remediation status
- Historical analytics

### 🔧 API Integration
Use the REST API to integrate with your existing tools:
- `/api/incidents` - Manage incidents
- `/api/dashboard` - Get dashboard data
- `/api/metrics` - System metrics
- `/predict` - AI predictions

## Features

✅ **AI-Powered Detection** - Machine learning models detect incidents automatically  
✅ **Auto-Remediation** - Automated fixes for common issues  
✅ **Real-time Dashboard** - Live monitoring and analytics  
✅ **REST API** - Easy integration with existing tools  
✅ **Multi-Cloud Support** - AWS, Azure, GCP ready  
✅ **Incident Management** - Full lifecycle tracking  

## Need Help?

- 📖 Read the full [USER_GUIDE.md](USER_GUIDE.md)
- 🚀 Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production setup
- 🐛 Report issues on GitHub

---

**Ready to revolutionize your DevOps? Start now! 🚀**