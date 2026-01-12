# 🚀 AI-RecoverOps - Your AI DevOps Assistant

**Transform your DevOps with AI-powered incident detection and automated remediation!**

## 🎯 What is AI-RecoverOps?

AI-RecoverOps is an enterprise-grade AIOps platform that:
- 🤖 **Detects incidents automatically** using machine learning
- 🔄 **Fixes problems automatically** with smart remediation
- 📊 **Monitors everything** with real-time dashboards
- 🔧 **Integrates easily** with your existing tools

## ⚡ Quick Start (2 Minutes)

### Step 1: Install Dependencies
Make sure you have:
- **Python 3.8+** ([Download here](https://python.org))
- **Node.js 16+** ([Download here](https://nodejs.org))

### Step 2: One-Click Setup
```bash
python ai-recoverops-setup.py
```

### Step 3: Launch AI-RecoverOps
**Windows:** Double-click `AI-RecoverOps.bat`  
**Mac/Linux:** Run `./start-ai-recoverops.sh`

### Step 4: Open Your Browser
Go to: **http://localhost:3000**

## 🎮 Try It Out!

### Test AI Detection
Send a sample log to see AI in action:

**Windows PowerShell:**
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

**Mac/Linux:**
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

## 🌟 Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| 🤖 **AI Detection** | Machine learning models analyze logs and metrics | Catch issues before they become outages |
| 🔄 **Auto-Remediation** | Automated fixes for common problems | Reduce MTTR from hours to minutes |
| 📊 **Real-time Dashboard** | Live monitoring and analytics | Complete visibility into your systems |
| 🔧 **REST API** | Easy integration with existing tools | Works with your current workflow |
| 📈 **Analytics** | Historical trends and insights | Improve your systems over time |
| 🚨 **Alerting** | Smart notifications and escalation | Get notified when it matters |

## 🎯 Use Cases

### For DevOps Teams
- Monitor production systems 24/7
- Automatically fix common issues
- Reduce on-call burden
- Improve system reliability

### For SRE Teams  
- Implement SLO monitoring
- Automate incident response
- Analyze failure patterns
- Optimize system performance

### For Platform Teams
- Provide self-service monitoring
- Standardize incident response
- Enable proactive maintenance
- Scale operations efficiently

## 🔗 Access Points

Once running, you can access:

| Service | URL | Purpose |
|---------|-----|---------|
| 📊 **Dashboard** | http://localhost:3000 | Main web interface |
| 🔧 **API** | http://localhost:8000 | REST API endpoints |
| 📖 **API Docs** | http://localhost:8000/docs | Interactive API documentation |

## 🛠️ What's Included

### Core Components
- **AI Engine** - Machine learning models for incident detection
- **Remediation Engine** - Automated fix execution
- **Web Dashboard** - React-based monitoring interface
- **REST API** - FastAPI-based backend service
- **Database** - SQLite for incident storage

### Pre-built Detectors
- High CPU usage
- Memory leaks
- Disk space issues
- Service crashes
- Database connection failures
- Network timeouts
- Permission errors
- Container OOM kills

### Auto-Remediation Actions
- Service restarts
- Log cleanup
- Permission fixes
- Process termination
- Database restarts
- Memory limit increases

## 📚 Documentation

- 📖 **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- 📋 **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user manual
- 🚀 **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment
- 🏗️ **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - Technical details

## 🆘 Need Help?

### Common Issues
- **Port already in use**: Stop other services on ports 3000/8000
- **Python not found**: Install Python and add to PATH
- **npm not found**: Install Node.js
- **Permission errors**: Run as administrator (Windows) or use sudo (Mac/Linux)

### Support
- 🐛 **Report bugs**: Create GitHub issues
- 💬 **Ask questions**: Join community discussions
- 📧 **Contact**: Email support team

## 🚀 Next Steps

1. **Explore the Dashboard** - Check out all the features
2. **Integrate with Your Systems** - Use the API to send real logs
3. **Customize Detectors** - Add your own incident types
4. **Deploy to Production** - Follow the deployment guide
5. **Train Your Team** - Share the user guide

---

**Ready to revolutionize your DevOps? Start now! 🚀**

*AI-RecoverOps - Making DevOps teams superhuman with AI*