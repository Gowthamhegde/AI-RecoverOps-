#!/usr/bin/env python3
"""
AI-RecoverOps Complete Setup Tool
Easy installation and launch for everyone
"""

import os
import sys
import subprocess
import platform
import time
import webbrowser
from pathlib import Path
import json
import shutil

class AIRecoverOpsSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_cmd = self.get_python_command()
        self.npm_cmd = self.get_npm_command()
        self.base_dir = Path.cwd()
        
    def get_python_command(self):
        """Get the correct Python command for the system"""
        for cmd in ['python3', 'python']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue
        return None
    
    def get_npm_command(self):
        """Get the correct npm command for the system"""
        for cmd in ['npm', 'npm.cmd']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue
        return None
    
    def print_banner(self):
        """Print welcome banner"""
        print("=" * 60)
        print("🚀 AI-RecoverOps Complete Setup Tool")
        print("   Enterprise AIOps Platform")
        print("=" * 60)
        print()
    
    def check_requirements(self):
        """Check system requirements"""
        print("📋 Checking system requirements...")
        
        # Check Python
        if not self.python_cmd:
            print("❌ Python not found. Please install Python 3.8+")
            return False
        
        try:
            result = subprocess.run([self.python_cmd, '--version'], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            print(f"✅ {version}")
        except:
            print("❌ Python version check failed")
            return False
        
        # Check Node.js/npm
        if not self.npm_cmd:
            print("❌ npm not found. Please install Node.js")
            return False
        
        try:
            result = subprocess.run([self.npm_cmd, '--version'], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            print(f"✅ npm v{version}")
        except:
            print("❌ npm version check failed")
            return False
        
        print("✅ All requirements met!")
        print()
        return True
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        try:
            # Install API dependencies
            subprocess.run([
                self.python_cmd, '-m', 'pip', 'install', '-r', 
                'api/requirements.txt'
            ], check=True)
            print("✅ Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def install_dashboard_dependencies(self):
        """Install dashboard dependencies"""
        print("📦 Installing dashboard dependencies...")
        
        try:
            # Change to dashboard directory
            os.chdir(self.base_dir / 'dashboard')
            
            # Install npm dependencies
            subprocess.run([self.npm_cmd, 'install'], check=True)
            print("✅ Dashboard dependencies installed")
            
            # Return to base directory
            os.chdir(self.base_dir)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dashboard dependencies: {e}")
            os.chdir(self.base_dir)
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            os.chdir(self.base_dir)
            return False
    
    def create_launcher_scripts(self):
        """Create launcher scripts for different platforms"""
        print("📝 Creating launcher scripts...")
        
        # Windows batch script
        windows_script = """@echo off
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
echo ✅ AI-RecoverOps is starting up!
echo 📊 Dashboard: http://localhost:3000
echo 🔧 API: http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause > nul
"""
        
        # Linux/Mac shell script
        unix_script = """#!/bin/bash
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
echo "✅ AI-RecoverOps is running!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "Stopping services..."; kill $API_PID $DASHBOARD_PID 2>/dev/null; exit' INT
wait
"""
        
        try:
            # Write Windows script
            with open('start-ai-recoverops.bat', 'w') as f:
                f.write(windows_script)
            
            # Write Unix script
            with open('start-ai-recoverops.sh', 'w') as f:
                f.write(unix_script)
            
            # Make Unix script executable
            if self.system != 'windows':
                os.chmod('start-ai-recoverops.sh', 0o755)
            
            print("✅ Launcher scripts created")
            return True
        except Exception as e:
            print(f"❌ Failed to create launcher scripts: {e}")
            return False
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut (Windows only for now)"""
        if self.system != 'windows':
            return True
        
        try:
            desktop = Path.home() / 'Desktop'
            if not desktop.exists():
                return True
            
            shortcut_content = f"""[InternetShortcut]
URL=file:///{self.base_dir}/start-ai-recoverops.bat
IconFile={self.base_dir}/start-ai-recoverops.bat
IconIndex=0
"""
            
            shortcut_path = desktop / 'AI-RecoverOps.url'
            with open(shortcut_path, 'w') as f:
                f.write(shortcut_content)
            
            print("✅ Desktop shortcut created")
            return True
        except Exception as e:
            print(f"⚠️  Could not create desktop shortcut: {e}")
            return True  # Non-critical error
    
    def setup_complete(self):
        """Show setup completion message"""
        print()
        print("🎉 Setup Complete!")
        print("=" * 40)
        print()
        print("🚀 To start AI-RecoverOps:")
        
        if self.system == 'windows':
            print("   • Double-click 'start-ai-recoverops.bat'")
            print("   • Or run: start-ai-recoverops.bat")
        else:
            print("   • Run: ./start-ai-recoverops.sh")
        
        print()
        print("🌐 Access points:")
        print("   📊 Dashboard: http://localhost:3000")
        print("   🔧 API: http://localhost:8000")
        print("   📖 API Docs: http://localhost:8000/docs")
        print()
        print("📚 Documentation:")
        print("   • README.md - Getting started guide")
        print("   • USER_GUIDE.md - User manual")
        print("   • DEPLOYMENT_GUIDE.md - Production deployment")
        print()
    
    def run_setup(self):
        """Run the complete setup process"""
        self.print_banner()
        
        if not self.check_requirements():
            print("❌ Setup failed. Please install missing requirements.")
            return False
        
        print("🔧 Installing dependencies...")
        print()
        
        if not self.install_python_dependencies():
            print("❌ Setup failed during Python dependency installation.")
            return False
        
        if not self.install_dashboard_dependencies():
            print("❌ Setup failed during dashboard dependency installation.")
            return False
        
        if not self.create_launcher_scripts():
            print("❌ Setup failed during launcher script creation.")
            return False
        
        self.create_desktop_shortcut()
        
        self.setup_complete()
        return True

def main():
    """Main setup function"""
    setup = AIRecoverOpsSetup()
    
    try:
        success = setup.run_setup()
        if success:
            # Ask if user wants to start now
            print("Would you like to start AI-RecoverOps now? (y/n): ", end="")
            response = input().lower().strip()
            
            if response in ['y', 'yes']:
                print("\n🚀 Starting AI-RecoverOps...")
                
                if setup.system == 'windows':
                    subprocess.run(['start-ai-recoverops.bat'], shell=True)
                else:
                    subprocess.run(['./start-ai-recoverops.sh'])
        else:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()