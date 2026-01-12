#!/usr/bin/env python3
"""
AI-RecoverOps Quick Start Tool
One-command deployment for immediate use
"""

import os
import sys
import subprocess
import platform
import urllib.request
import json
from pathlib import Path

def quick_start():
    """Ultra-fast deployment for immediate testing"""
    
    print("""
🚀 AI-RecoverOps Quick Start
============================
This will deploy AI-RecoverOps locally in under 5 minutes!

Requirements:
- Docker and Docker Compose
- Python 3.8+
- 4GB RAM available

Press Ctrl+C to cancel, or Enter to continue...
    """)
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(0)
    
    print("🔄 Starting quick deployment...")
    
    # Download and run the full installer with local deployment
    installer_url = "https://raw.githubusercontent.com/your-org/ai-recoverops/main/install.py"
    
    try:
        # Run the installer with local deployment
        subprocess.run([
            sys.executable, "-c",
            f"""
import urllib.request
exec(urllib.request.urlopen('{installer_url}').read())
"""
        ], check=True)
        
    except subprocess.CalledProcessError:
        # Fallback to local installer if available
        if Path("install.py").exists():
            subprocess.run([sys.executable, "install.py", "--deployment-type", "local"], check=True)
        else:
            print("❌ Quick start failed. Please run the full installer.")
            sys.exit(1)
    
    print("""
✅ Quick start completed!

🌐 Access your AI-RecoverOps instance:
   • Dashboard: http://localhost:3000
   • API: http://localhost:8000
   • API Docs: http://localhost:8000/docs

🔧 Management commands:
   • Start: docker-compose up -d
   • Stop: docker-compose down
   • Logs: docker-compose logs -f

📚 Next steps:
   1. Open the dashboard at http://localhost:3000
   2. Review the sample incidents and remediations
   3. Configure your AWS credentials for production use
   4. Customize detectors for your environment

Happy incident recovery! 🎉
    """)

if __name__ == "__main__":
    quick_start()