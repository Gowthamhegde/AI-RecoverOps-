# 🔧 Browser Access Troubleshooting

## ✅ Services Status
- **API Server**: ✅ Running on port 8000
- **Dashboard**: ✅ Running on port 3000
- **Network**: ✅ Ports are listening and responding

## 🌐 Try These URLs

### Method 1: Direct URLs
Copy and paste these exact URLs into your browser:

```
http://localhost:3000
http://127.0.0.1:3000
http://localhost:8000
http://127.0.0.1:8000
```

### Method 2: Alternative Ports
If localhost doesn't work, try the network IP:
```
http://192.168.56.1:3000
http://192.168.56.1:8000
```

## 🔍 Common Issues & Solutions

### Issue 1: Browser Security/Firewall
**Solution**: Try different browsers
- Chrome: `chrome.exe http://localhost:3000`
- Edge: `msedge.exe http://localhost:3000`
- Firefox: `firefox.exe http://localhost:3000`

### Issue 2: Windows Firewall
**Solution**: Allow through firewall
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Node.js and Python if not listed

### Issue 3: Antivirus Blocking
**Solution**: Temporarily disable antivirus or add exceptions for:
- Node.js
- Python
- The project folder

### Issue 4: Proxy Settings
**Solution**: Disable proxy in browser settings
- Chrome: Settings → Advanced → System → Open proxy settings
- Disable "Use a proxy server"

## 🚀 Quick Fixes

### Fix 1: Restart Services
```cmd
# Stop current processes
taskkill /f /im node.exe
taskkill /f /im python.exe

# Restart using the launcher
python launch-ai-recoverops.py
```

### Fix 2: Use Different Ports
If ports 3000/8000 are blocked, we can change them:

**For Dashboard (port 3001):**
```cmd
cd dashboard
set PORT=3001
npm start
```

**For API (port 8001):**
Edit `api/main.py` and change the last line to:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Fix 3: Open Browser Programmatically
```cmd
# Windows
start http://localhost:3000

# Or use PowerShell
Start-Process "http://localhost:3000"
```

## 🧪 Test Commands

### Test 1: Check if services respond
```powershell
# Test API
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Test Dashboard
Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
```

### Test 2: Check what's blocking access
```cmd
# Check if anything else is using the ports
netstat -ano | findstr "3000 8000"

# Check Windows Firewall logs
# Go to Windows Logs → Security in Event Viewer
```

## 🔧 Manual Browser Opening

### Method 1: Command Line
```cmd
# Chrome
"C:\Program Files\Google\Chrome\Application\chrome.exe" http://localhost:3000

# Edge
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" http://localhost:3000

# Firefox
"C:\Program Files\Mozilla Firefox\firefox.exe" http://localhost:3000
```

### Method 2: Run Dialog
1. Press `Win + R`
2. Type: `http://localhost:3000`
3. Press Enter

### Method 3: File Explorer
1. Open File Explorer
2. Type in address bar: `http://localhost:3000`
3. Press Enter

## 📱 Alternative Access Methods

### Method 1: Use curl to verify
```cmd
curl http://localhost:3000
curl http://localhost:8000/health
```

### Method 2: Use PowerShell
```powershell
# Get dashboard HTML
$response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
$response.Content | Out-File dashboard.html
# Then open dashboard.html in browser
```

## 🆘 If Nothing Works

### Last Resort: Use Python's Built-in Server
```python
# Create a simple proxy
import webbrowser
import http.server
import socketserver
from urllib.request import urlopen

# Open browser automatically
webbrowser.open('http://localhost:3000')
```

### Contact Support
If none of these solutions work:
1. Check Windows Event Viewer for errors
2. Try running as Administrator
3. Check if corporate firewall is blocking
4. Try on a different network

## ✅ Success Indicators

You'll know it's working when you see:
- **Dashboard**: AI-RecoverOps interface with navigation menu
- **API**: JSON response with health status
- **No errors**: Browser loads without timeout or connection errors

## 🎯 Quick Test

Run this command to open browser automatically:
```cmd
start http://localhost:3000 && start http://localhost:8000/docs
```

If this doesn't work, the issue is likely browser/firewall related.