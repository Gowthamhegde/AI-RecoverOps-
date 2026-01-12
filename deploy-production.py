#!/usr/bin/env python3
"""
Production Deployment Script for AI-RecoverOps
Deploys a real, production-ready system
"""

import os
import sys
import subprocess
import json
import time
import shutil
from pathlib import Path
import argparse
import yaml

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ProductionDeployer:
    """Production deployment manager for AI-RecoverOps"""
    
    def __init__(self, environment='production'):
        self.environment = environment
        self.project_root = Path(__file__).parent
        self.config = self.load_config()
        
    def load_config(self):
        """Load deployment configuration"""
        config_file = self.project_root / f'config-{self.environment}.yaml'
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        
        # Default production configuration
        return {
            'api': {
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 4,
                'log_level': 'info'
            },
            'dashboard': {
                'port': 3000,
                'build_path': 'dashboard/build'
            },
            'database': {
                'type': 'sqlite',
                'path': 'ai_recoverops_prod.db'
            },
            'monitoring': {
                'enable_metrics': True,
                'prometheus_port': 9090
            },
            'security': {
                'enable_auth': True,
                'cors_origins': ['http://localhost:3000']
            }
        }
    
    def print_banner(self):
        """Print deployment banner"""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║              AI-RecoverOps Production Deployment             ║
║                                                              ║
║  🚀 Deploying enterprise-grade AIOps platform               ║
║  🏭 Production-ready with monitoring & security              ║
║  📊 Real-time incident detection and remediation            ║
║  🔒 Secure, scalable, and maintainable                      ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.OKGREEN}Environment: {self.environment.upper()}{Colors.ENDC}
"""
        print(banner)
    
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        print(f"{Colors.OKBLUE}🔍 Checking prerequisites...{Colors.ENDC}")
        
        requirements = {
            'python': 'Python 3.8+',
            'node': 'Node.js 16+',
            'npm': 'npm package manager'
        }
        
        for cmd, desc in requirements.items():
            if not self.check_command(cmd):
                print(f"{Colors.FAIL}❌ {desc} not found{Colors.ENDC}")
                return False
            print(f"{Colors.OKGREEN}✅ {desc}{Colors.ENDC}")
        
        return True
    
    def check_command(self, command):
        """Check if command exists"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_dependencies(self):
        """Install Python and Node.js dependencies"""
        print(f"{Colors.OKBLUE}📦 Installing dependencies...{Colors.ENDC}")
        
        # Install Python dependencies
        print("Installing Python packages...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'api/requirements.txt'
        ], check=True)
        
        # Install additional production packages
        production_packages = [
            'gunicorn>=20.1.0',
            'prometheus-client>=0.14.0',
            'structlog>=22.1.0',
            'python-multipart>=0.0.5'
        ]
        
        for package in production_packages:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True)
        
        print(f"{Colors.OKGREEN}✅ Python dependencies installed{Colors.ENDC}")
        
        # Install Node.js dependencies and build dashboard
        if Path('dashboard/package.json').exists():
            print("Installing Node.js packages...")
            subprocess.run(['npm', 'install'], cwd='dashboard', check=True)
            
            print("Building production dashboard...")
            subprocess.run(['npm', 'run', 'build'], cwd='dashboard', check=True)
            
            print(f"{Colors.OKGREEN}✅ Dashboard built successfully{Colors.ENDC}")
    
    def setup_database(self):
        """Setup production database"""
        print(f"{Colors.OKBLUE}🗄️ Setting up database...{Colors.ENDC}")
        
        # Initialize database
        db_path = self.config['database']['path']
        
        # Run database initialization
        init_script = f"""
import sqlite3
import json
from datetime import datetime

# Create production database
conn = sqlite3.connect('{db_path}')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        service TEXT NOT NULL,
        instance_id TEXT,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        confidence REAL NOT NULL,
        recommended_action TEXT,
        description TEXT,
        timestamp TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS remediations (
        id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        action TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        success BOOLEAN,
        error_message TEXT,
        FOREIGN KEY (incident_id) REFERENCES incidents (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        cpu_usage REAL,
        memory_usage REAL,
        disk_usage REAL,
        network_io TEXT,
        created_at TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TEXT NOT NULL,
        last_login TEXT
    )
''')

# Create indexes for performance
cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON incidents(timestamp)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity)')

conn.commit()
conn.close()

print("Database initialized successfully")
"""
        
        with open('init_db.py', 'w') as f:
            f.write(init_script)
        
        subprocess.run([sys.executable, 'init_db.py'], check=True)
        os.remove('init_db.py')
        
        print(f"{Colors.OKGREEN}✅ Database setup complete{Colors.ENDC}")
    
    def generate_production_configs(self):
        """Generate production configuration files"""
        print(f"{Colors.OKBLUE}⚙️ Generating production configs...{Colors.ENDC}")
        
        # Generate Gunicorn config
        gunicorn_config = f"""
bind = "{self.config['api']['host']}:{self.config['api']['port']}"
workers = {self.config['api']['workers']}
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "{self.config['api']['log_level']}"
capture_output = True
enable_stdio_inheritance = True
"""
        
        with open('gunicorn.conf.py', 'w') as f:
            f.write(gunicorn_config)
        
        # Generate systemd service file
        service_config = f"""[Unit]
Description=AI-RecoverOps API Server
After=network.target

[Service]
Type=notify
User=ai-recoverops
Group=ai-recoverops
WorkingDirectory={self.project_root.absolute()}
Environment=PATH={self.project_root.absolute()}/venv/bin
ExecStart={sys.executable} -m gunicorn api.main:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        with open('ai-recoverops.service', 'w') as f:
            f.write(service_config)
        
        # Generate nginx config
        nginx_config = f"""
server {{
    listen 80;
    server_name ai-recoverops.local;
    
    # Dashboard
    location / {{
        root {self.project_root.absolute()}/dashboard/build;
        try_files $uri $uri/ /index.html;
    }}
    
    # API
    location /api/ {{
        proxy_pass http://127.0.0.1:{self.config['api']['port']}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # WebSocket support
    location /ws/ {{
        proxy_pass http://127.0.0.1:{self.config['api']['port']}/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }}
}}
"""
        
        with open('nginx-ai-recoverops.conf', 'w') as f:
            f.write(nginx_config)
        
        # Generate environment file
        env_config = f"""# AI-RecoverOps Production Environment
ENVIRONMENT={self.environment}
API_HOST={self.config['api']['host']}
API_PORT={self.config['api']['port']}
DATABASE_PATH={self.config['database']['path']}
LOG_LEVEL={self.config['api']['log_level']}
ENABLE_AUTH={self.config['security']['enable_auth']}
CORS_ORIGINS={','.join(self.config['security']['cors_origins'])}
PROMETHEUS_PORT={self.config['monitoring']['prometheus_port']}
"""
        
        with open('.env.production', 'w') as f:
            f.write(env_config)
        
        print(f"{Colors.OKGREEN}✅ Production configs generated{Colors.ENDC}")
    
    def setup_logging(self):
        """Setup production logging"""
        print(f"{Colors.OKBLUE}📝 Setting up logging...{Colors.ENDC}")
        
        # Create logs directory
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Generate logging configuration
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
                'json': {
                    'format': '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'detailed',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'json',
                    'filename': 'logs/ai-recoverops.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': 'json',
                    'filename': 'logs/errors.log',
                    'maxBytes': 10485760,
                    'backupCount': 5
                }
            },
            'loggers': {
                'ai_recoverops': {
                    'level': 'INFO',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console', 'file']
            }
        }
        
        with open('logging.json', 'w') as f:
            json.dump(logging_config, f, indent=2)
        
        print(f"{Colors.OKGREEN}✅ Logging configured{Colors.ENDC}")
    
    def setup_monitoring(self):
        """Setup monitoring and metrics"""
        print(f"{Colors.OKBLUE}📊 Setting up monitoring...{Colors.ENDC}")
        
        # Generate Prometheus configuration
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': [
                {
                    'job_name': 'ai-recoverops-api',
                    'static_configs': [
                        {
                            'targets': [f'localhost:{self.config["api"]["port"]}']
                        }
                    ],
                    'metrics_path': '/metrics'
                },
                {
                    'job_name': 'prometheus',
                    'static_configs': [
                        {
                            'targets': [f'localhost:{self.config["monitoring"]["prometheus_port"]}']
                        }
                    ]
                }
            ]
        }
        
        with open('prometheus.yml', 'w') as f:
            yaml.dump(prometheus_config, f)
        
        # Generate health check script
        health_check_script = f"""#!/bin/bash
# AI-RecoverOps Health Check Script

API_URL="http://localhost:{self.config['api']['port']}/health"
DASHBOARD_URL="http://localhost:{self.config['dashboard']['port']}"

echo "Checking AI-RecoverOps health..."

# Check API
if curl -f -s $API_URL > /dev/null; then
    echo "✅ API is healthy"
else
    echo "❌ API is not responding"
    exit 1
fi

# Check dashboard (if running separately)
if [ -d "{self.config['dashboard']['build_path']}" ]; then
    echo "✅ Dashboard build exists"
else
    echo "❌ Dashboard build not found"
    exit 1
fi

echo "🎉 All systems healthy"
"""
        
        with open('health-check.sh', 'w') as f:
            f.write(health_check_script)
        
        os.chmod('health-check.sh', 0o755)
        
        print(f"{Colors.OKGREEN}✅ Monitoring setup complete{Colors.ENDC}")
    
    def create_startup_scripts(self):
        """Create startup and management scripts"""
        print(f"{Colors.OKBLUE}📜 Creating management scripts...{Colors.ENDC}")
        
        # Start script
        start_script = f"""#!/bin/bash
# AI-RecoverOps Start Script

echo "Starting AI-RecoverOps Production Server..."

# Load environment
export $(cat .env.production | xargs)

# Start API server
echo "Starting API server..."
{sys.executable} -m gunicorn api.main:app -c gunicorn.conf.py --daemon

# Wait for startup
sleep 5

# Check health
./health-check.sh

if [ $? -eq 0 ]; then
    echo "🎉 AI-RecoverOps started successfully!"
    echo "📊 Dashboard: http://localhost/dashboard"
    echo "🔌 API: http://localhost:{self.config['api']['port']}"
    echo "📈 Metrics: http://localhost:{self.config['monitoring']['prometheus_port']}"
else
    echo "❌ Startup failed"
    exit 1
fi
"""
        
        with open('start.sh', 'w') as f:
            f.write(start_script)
        os.chmod('start.sh', 0o755)
        
        # Stop script
        stop_script = """#!/bin/bash
# AI-RecoverOps Stop Script

echo "Stopping AI-RecoverOps..."

# Find and kill gunicorn processes
pkill -f "gunicorn.*ai-recoverops"

echo "AI-RecoverOps stopped"
"""
        
        with open('stop.sh', 'w') as f:
            f.write(stop_script)
        os.chmod('stop.sh', 0o755)
        
        # Status script
        status_script = f"""#!/bin/bash
# AI-RecoverOps Status Script

echo "AI-RecoverOps Status:"
echo "===================="

# Check API process
if pgrep -f "gunicorn.*ai-recoverops" > /dev/null; then
    echo "✅ API Server: Running"
else
    echo "❌ API Server: Stopped"
fi

# Check health
./health-check.sh 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Health Check: Passed"
else
    echo "❌ Health Check: Failed"
fi

# Show resource usage
echo ""
echo "Resource Usage:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{{print $2}}' | awk -F'%' '{{print $1}}')%"
echo "Memory: $(free | grep Mem | awk '{{printf("%.1f%%", $3/$2 * 100.0)}}')"
echo "Disk: $(df -h . | awk 'NR==2{{print $5}}')"
"""
        
        with open('status.sh', 'w') as f:
            f.write(status_script)
        os.chmod('status.sh', 0o755)
        
        print(f"{Colors.OKGREEN}✅ Management scripts created{Colors.ENDC}")
    
    def run_tests(self):
        """Run production readiness tests"""
        print(f"{Colors.OKBLUE}🧪 Running production tests...{Colors.ENDC}")
        
        # Test API startup
        print("Testing API startup...")
        try:
            # Start API in background for testing
            process = subprocess.Popen([
                sys.executable, '-m', 'uvicorn', 'api.main:app',
                '--host', '127.0.0.1', '--port', '8001'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for startup
            time.sleep(5)
            
            # Test health endpoint
            import requests
            response = requests.get('http://127.0.0.1:8001/health', timeout=10)
            
            if response.status_code == 200:
                print(f"{Colors.OKGREEN}✅ API health check passed{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}❌ API health check failed{Colors.ENDC}")
            
            # Cleanup
            process.terminate()
            process.wait()
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ API test failed: {e}{Colors.ENDC}")
        
        # Test database
        print("Testing database...")
        try:
            import sqlite3
            conn = sqlite3.connect(self.config['database']['path'])
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            if len(tables) >= 4:  # incidents, remediations, system_metrics, users
                print(f"{Colors.OKGREEN}✅ Database test passed{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}❌ Database test failed{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Database test failed: {e}{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}✅ Production tests completed{Colors.ENDC}")
    
    def deploy(self):
        """Run complete deployment"""
        self.print_banner()
        
        if not self.check_prerequisites():
            print(f"{Colors.FAIL}Prerequisites check failed{Colors.ENDC}")
            return False
        
        try:
            self.install_dependencies()
            self.setup_database()
            self.generate_production_configs()
            self.setup_logging()
            self.setup_monitoring()
            self.create_startup_scripts()
            self.run_tests()
            
            # Final success message
            success_message = f"""
{Colors.OKGREEN}{Colors.BOLD}
🎉 AI-RecoverOps Production Deployment Complete! 🎉
{Colors.ENDC}

{Colors.OKBLUE}🚀 Quick Start:{Colors.ENDC}
  ./start.sh                 # Start all services
  ./status.sh                # Check system status
  ./stop.sh                  # Stop all services

{Colors.OKBLUE}🔗 Access Points:{Colors.ENDC}
  Dashboard: http://localhost/
  API: http://localhost:{self.config['api']['port']}
  Health: http://localhost:{self.config['api']['port']}/health
  Docs: http://localhost:{self.config['api']['port']}/docs

{Colors.OKBLUE}📊 Monitoring:{Colors.ENDC}
  Logs: tail -f logs/ai-recoverops.log
  Metrics: http://localhost:{self.config['monitoring']['prometheus_port']}
  Health Check: ./health-check.sh

{Colors.OKBLUE}🔧 Management:{Colors.ENDC}
  Service File: ai-recoverops.service (for systemd)
  Nginx Config: nginx-ai-recoverops.conf
  Environment: .env.production

{Colors.OKGREEN}Production system is ready for enterprise deployment!{Colors.ENDC}
"""
            
            print(success_message)
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}Deployment failed: {e}{Colors.ENDC}")
            return False

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='AI-RecoverOps Production Deployment')
    parser.add_argument('--environment', default='production', 
                       choices=['production', 'staging', 'development'],
                       help='Deployment environment')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip production readiness tests')
    
    args = parser.parse_args()
    
    deployer = ProductionDeployer(args.environment)
    
    if deployer.deploy():
        print(f"{Colors.OKGREEN}Deployment successful!{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.FAIL}Deployment failed!{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())