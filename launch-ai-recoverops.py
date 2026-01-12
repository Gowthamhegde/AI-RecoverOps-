#!/usr/bin/env python3
"""
AI-RecoverOps Simple Launcher
One-click start for both API and Dashboard
"""

import subprocess
import time
import webbrowser
import sys
import os
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚀 AI-RecoverOps Platform Launcher")
    print("   Starting API and Dashboard...")
    print("=" * 60)
    print()

def check_ports():
    """Check if ports are already in use"""
    import socket
    
    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    api_running = is_port_open(8000)
    dashboard_running = is_port_open(3000)
    
    return api_running, dashboard_running

def start_api():
    """Start the API server"""
    print("🔧 Starting API server...")
    try:
        # Start API in background
        if sys.platform == "win32":
            api_process = subprocess.Popen(
                [sys.executable, "api/main.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            api_process = subprocess.Popen([sys.executable, "api/main.py"])
        
        print("✅ API server started (PID: {})".format(api_process.pid))
        return api_process
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_dashboard():
    """Start the dashboard"""
    print("📊 Starting dashboard...")
    try:
        # Change to dashboard directory and start
        dashboard_dir = Path("dashboard")
        if not dashboard_dir.exists():
            print("❌ Dashboard directory not found")
            return None
        
        if sys.platform == "win32":
            dashboard_process = subprocess.Popen(
                ["npm", "start"],
                cwd=dashboard_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            dashboard_process = subprocess.Popen(
                ["npm", "start"],
                cwd=dashboard_dir
            )
        
        print("✅ Dashboard started (PID: {})".format(dashboard_process.pid))
        return dashboard_process
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return None

def wait_for_services():
    """Wait for services to be ready"""
    print("\n⏳ Waiting for services to start...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        api_ready, dashboard_ready = check_ports()
        
        if api_ready and dashboard_ready:
            print("✅ All services are ready!")
            return True
        
        print(f"   Attempt {attempt + 1}/{max_attempts} - API: {'✅' if api_ready else '⏳'} Dashboard: {'✅' if dashboard_ready else '⏳'}")
        time.sleep(2)
    
    print("⚠️  Services may still be starting...")
    return False

def open_browser():
    """Open the dashboard in browser"""
    print("\n🌐 Opening dashboard in browser...")
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ Browser opened")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")

def main():
    print_banner()
    
    # Check if services are already running
    api_running, dashboard_running = check_ports()
    
    if api_running and dashboard_running:
        print("✅ Services are already running!")
        print("📊 Dashboard: http://localhost:3000")
        print("🔧 API: http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
        
        response = input("\nOpen dashboard in browser? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            open_browser()
        return
    
    processes = []
    
    # Start API if not running
    if not api_running:
        api_process = start_api()
        if api_process:
            processes.append(api_process)
        time.sleep(3)  # Give API time to start
    else:
        print("✅ API server already running")
    
    # Start dashboard if not running
    if not dashboard_running:
        dashboard_process = start_dashboard()
        if dashboard_process:
            processes.append(dashboard_process)
    else:
        print("✅ Dashboard already running")
    
    # Wait for services to be ready
    if processes:
        wait_for_services()
    
    # Show access information
    print("\n" + "=" * 60)
    print("🎉 AI-RecoverOps is now running!")
    print("=" * 60)
    print("📊 Dashboard:  http://localhost:3000")
    print("🔧 API:        http://localhost:8000")
    print("📖 API Docs:   http://localhost:8000/docs")
    print("=" * 60)
    
    # Open browser
    open_browser()
    
    print("\n💡 Tips:")
    print("   • Use the dashboard to monitor incidents")
    print("   • Test AI detection with the API")
    print("   • Check API docs for integration")
    print("\n🛑 To stop: Close the terminal windows or press Ctrl+C")
    
    try:
        input("\nPress Enter to exit launcher (services will continue running)...")
    except KeyboardInterrupt:
        print("\n👋 Launcher exited. Services are still running.")

if __name__ == "__main__":
    main()