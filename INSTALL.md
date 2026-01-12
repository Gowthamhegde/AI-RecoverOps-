# 🚀 AI-RecoverOps Quick Install Guide

## One-Click Installation

### For Everyone (Easiest Way)

1. **Download or clone this repository**
2. **Run the setup tool:**

   **Windows:**
   ```cmd
   python ai-recoverops-setup.py
   ```

   **Mac/Linux:**
   ```bash
   python3 ai-recoverops-setup.py
   ```

3. **Follow the prompts** - the tool will:
   - Check system requirements
   - Install all dependencies
   - Create launcher scripts
   - Set up desktop shortcuts

4. **Start using AI-RecoverOps:**
   - **Windows:** Double-click `start-ai-recoverops.bat`
   - **Mac/Linux:** Run `./start-ai-recoverops.sh`

## What You Get

- 📊 **Web Dashboard** at http://localhost:3000
- 🔧 **API Server** at http://localhost:8000  
- 📖 **API Documentation** at http://localhost:8000/docs
- 🤖 **AI-powered incident detection**
- 🔄 **Automated remediation**
- 📈 **Real-time monitoring**

## Requirements

- **Python 3.8+** (Download from [python.org](https://python.org))
- **Node.js 16+** (Download from [nodejs.org](https://nodejs.org))

## Troubleshooting

### Python not found
- Install Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### npm not found  
- Install Node.js from [nodejs.org](https://nodejs.org)
- Restart your terminal after installation

### Permission errors (Mac/Linux)
```bash
chmod +x start-ai-recoverops.sh
```

### Port already in use
- Stop other services using ports 3000 or 8000
- Or modify the ports in the configuration files

## Manual Installation (Advanced)

If you prefer manual setup:

1. **Install API dependencies:**
   ```bash
   pip install -r api/requirements.txt
   ```

2. **Install dashboard dependencies:**
   ```bash
   cd dashboard
   npm install
   cd ..
   ```

3. **Start API server:**
   ```bash
   python api/main.py
   ```

4. **Start dashboard (in new terminal):**
   ```bash
   cd dashboard
   npm start
   ```

## Support

- 📖 Check `USER_GUIDE.md` for detailed usage instructions
- 🐛 Report issues on GitHub
- 💬 Join our community discussions

---

**Ready to revolutionize your DevOps with AI? Let's get started! 🚀**