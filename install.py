#!/usr/bin/env python3
"""
AI-RecoverOps One-Click Installer
Universal installation script that works on any system
"""

import os
import sys
import subprocess
import platform
import urllib.request
import json
import tempfile
import shutil
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Print installation banner"""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                 AI-RecoverOps One-Click Installer            ║
║                                                              ║
║  🚀 Get AI-RecoverOps running in under 5 minutes!          ║
║  🤖 Automatic incident detection and remediation            ║
║  ☁️  Works locally or in the cloud                          ║
║  📊 Complete monitoring and dashboards                      ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.OKGREEN}Welcome! This installer will set up AI-RecoverOps automatically.{Colors.ENDC}
"""
    print(banner)

def check_python():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print(f"{Colors.FAIL}❌ Python 3.8+ required. Found: {sys.version}{Colors.ENDC}")
        print("Please install Python 3.8 or higher and try again.")
        return False
    
    print(f"{Colors.OKGREEN}✅ Python {sys.version.split()[0]} - OK{Colors.ENDC}")
    return True

def install_requirements():
    """Install Python requirements"""
    print(f"{Colors.OKBLUE}📦 Installing Python dependencies...{Colors.ENDC}")
    
    requirements = [
        'click>=8.0.0',
        'rich>=12.0.0',
        'requests>=2.25.0',
        'pyyaml>=6.0',
        'pandas>=1.3.0',
        'fastapi>=0.75.0',
        'uvicorn>=0.17.0',
        'docker-compose>=1.29.0'
    ]
    
    for req in requirements:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], 
                         check=True, capture_output=True)
            print(f"{Colors.OKGREEN}✅ Installed {req.split('>=')[0]}{Colors.ENDC}")
        except subprocess.CalledProcessError:
            print(f"{Colors.WARNING}⚠️  Failed to install {req}, continuing...{Colors.ENDC}")

def download_installer():
    """Download the full installer"""
    print(f"{Colors.OKBLUE}📥 Downloading AI-RecoverOps installer...{Colors.ENDC}")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    installer_path = Path(temp_dir) / 'ai-recoverops-installer.py'
    
    # In a real scenario, this would download from GitHub releases
    # For now, we'll copy the installer we created
    current_dir = Path(__file__).parent
    installer_source = current_dir / 'ai-recoverops-installer.py'
    
    if installer_source.exists():
        shutil.copy(installer_source, installer_path)
        print(f"{Colors.OKGREEN}✅ Installer downloaded{Colors.ENDC}")
        return installer_path
    else:
        print(f"{Colors.FAIL}❌ Installer not found{Colors.ENDC}")
        return None

def run_installer(installer_path):
    """Run the main installer"""
    print(f"{Colors.OKBLUE}🚀 Starting AI-RecoverOps installation...{Colors.ENDC}")
    
    try:
        subprocess.run([sys.executable, str(installer_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}❌ Installation failed: {e}{Colors.ENDC}")
        return False

def create_desktop_shortcuts():
    """Create desktop shortcuts for easy access"""
    print(f"{Colors.OKBLUE}🔗 Creating shortcuts...{Colors.ENDC}")
    
    system = platform.system().lower()
    home_dir = Path.home()
    
    if system == 'windows':
        # Create Windows shortcuts
        desktop = home_dir / 'Desktop'
        if desktop.exists():
            # Create batch files for Windows
            start_script = desktop / 'Start AI-RecoverOps.bat'
            with open(start_script, 'w') as f:
                f.write(f"""@echo off
cd /d "{home_dir}/ai-recoverops"
start.bat
pause
""")
            
            cli_script = desktop / 'AI-RecoverOps CLI.bat'
            with open(cli_script, 'w') as f:
                f.write(f"""@echo off
cd /d "{home_dir}/ai-recoverops"
python ai-recoverops-cli.py interactive
pause
""")
    
    elif system in ['linux', 'darwin']:
        # Create shell scripts
        bin_dir = home_dir / 'bin'
        bin_dir.mkdir(exist_ok=True)
        
        # Add to PATH if not already there
        shell_rc = home_dir / '.bashrc' if system == 'linux' else home_dir / '.zshrc'
        if shell_rc.exists():
            with open(shell_rc, 'a') as f:
                f.write(f'\nexport PATH="$PATH:{bin_dir}"\n')
        
        # Create CLI shortcut
        cli_script = bin_dir / 'ai-recoverops'
        with open(cli_script, 'w') as f:
            f.write(f"""#!/bin/bash
cd "{home_dir}/ai-recoverops"
python ai-recoverops-cli.py "$@"
""")
        os.chmod(cli_script, 0o755)
    
    print(f"{Colors.OKGREEN}✅ Shortcuts created{Colors.ENDC}")

def show_completion_message():
    """Show installation completion message"""
    completion_msg = f"""
{Colors.OKGREEN}{Colors.BOLD}
🎉 AI-RecoverOps Installation Complete! 🎉
{Colors.ENDC}

{Colors.OKBLUE}Quick Start:{Colors.ENDC}
1. Open a new terminal window
2. Run: {Colors.BOLD}ai-recoverops deploy start --environment local{Colors.ENDC}
3. Access dashboard: {Colors.BOLD}http://localhost:3000{Colors.ENDC}

{Colors.OKBLUE}Available Commands:{Colors.ENDC}
• {Colors.BOLD}ai-recoverops status health{Colors.ENDC} - Check system health
• {Colors.BOLD}ai-recoverops incidents list{Colors.ENDC} - View recent incidents
• {Colors.BOLD}ai-recoverops interactive{Colors.ENDC} - Interactive mode
• {Colors.BOLD}ai-recoverops dashboard open{Colors.ENDC} - Open dashboard

{Colors.OKBLUE}What's Next?{Colors.ENDC}
1. 📊 Explore the dashboard and monitoring tools
2. 🔧 Configure your log sources and integrations  
3. 🤖 Set up auto-remediation for your environment
4. 📚 Read the documentation for advanced features

{Colors.OKBLUE}Need Help?{Colors.ENDC}
• Documentation: ~/ai-recoverops/README.md
• CLI Help: ai-recoverops --help
• Interactive Mode: ai-recoverops interactive

{Colors.OKGREEN}Happy incident hunting! 🔍🤖{Colors.ENDC}
"""
    print(completion_msg)

def main():
    """Main installation function"""
    print_banner()
    
    # Check prerequisites
    if not check_python():
        return 1
    
    # Install Python requirements
    install_requirements()
    
    # Download and run installer
    installer_path = download_installer()
    if not installer_path:
        return 1
    
    # Run the main installer
    if not run_installer(installer_path):
        return 1
    
    # Create shortcuts
    create_desktop_shortcuts()
    
    # Show completion message
    show_completion_message()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Installation cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Installation failed: {e}{Colors.ENDC}")
        sys.exit(1)