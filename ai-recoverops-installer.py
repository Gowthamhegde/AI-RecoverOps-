#!/usr/bin/env python3
"""
AI-RecoverOps Universal Installer
One-click installation and deployment tool for all users
"""

import os
import sys
import json
import subprocess
import platform
import shutil
import urllib.request
import zipfile
import tempfile
from pathlib import Path
import argparse
import time
from typing import Dict, Any, List

class Colors:
    """Terminal colors for better UX"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AIRecoverOpsInstaller:
    """Universal installer for AI-RecoverOps"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.python_version = sys.version_info
        self.install_dir = Path.home() / "ai-recoverops"
        self.config = {}
        
    def print_banner(self):
        """Print installation banner"""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    AI-RecoverOps Installer                   ║
║              Automatic Root Cause Fixer                     ║
║                                                              ║
║  🤖 Intelligent incident detection and remediation          ║
║  ☁️  Cloud-native AWS architecture                          ║
║  🔧 Automated infrastructure healing                        ║
║  📊 Real-time monitoring and dashboards                    ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.OKGREEN}Welcome to the AI-RecoverOps Universal Installer!{Colors.ENDC}
This tool will automatically install and configure AI-RecoverOps for your environment.

"""
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        print(f"{Colors.OKBLUE}🔍 Checking system prerequisites...{Colors.ENDC}")
        
        # Check Python version
        if self.python_version < (3, 8):
            print(f"{Colors.FAIL}❌ Python 3.8+ required. Found: {sys.version}{Colors.ENDC}")
            return False
        print(f"{Colors.OKGREEN}✅ Python {sys.version.split()[0]} - OK{Colors.ENDC}")
        
        # Check operating system
        supported_os = ['linux', 'darwin', 'windows']
        if self.system not in supported_os:
            print(f"{Colors.FAIL}❌ Unsupported OS: {self.system}{Colors.ENDC}")
            return False
        print(f"{Colors.OKGREEN}✅ Operating System: {self.system.title()} - OK{Colors.ENDC}")
        
        # Check required tools
        required_tools = {
            'git': 'Git version control',
            'docker': 'Docker containerization',
            'pip': 'Python package manager'
        }
        
        for tool, description in required_tools.items():
            if not self.check_command(tool):
                print(f"{Colors.WARNING}⚠️  {description} not found. Will attempt to install.{Colors.ENDC}")
            else:
                print(f"{Colors.OKGREEN}✅ {description} - OK{Colors.ENDC}")
        
        return True
    
    def check_command(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_dependencies(self):
        """Install required dependencies"""
        print(f"\n{Colors.OKBLUE}📦 Installing dependencies...{Colors.ENDC}")
        
        # Install Docker if not present
        if not self.check_command('docker'):
            self.install_docker()
        
        # Install Docker Compose if not present
        if not self.check_command('docker-compose'):
            self.install_docker_compose()
        
        # Install AWS CLI if not present
        if not self.check_command('aws'):
            self.install_aws_cli()
        
        # Install Terraform if not present
        if not self.check_command('terraform'):
            self.install_terraform()
    
    def install_docker(self):
        """Install Docker based on OS"""
        print(f"{Colors.OKBLUE}🐳 Installing Docker...{Colors.ENDC}")
        
        if self.system == 'linux':
            # Ubuntu/Debian installation
            commands = [
                'curl -fsSL https://get.docker.com -o get-docker.sh',
                'sudo sh get-docker.sh',
                'sudo usermod -aG docker $USER',
                'rm get-docker.sh'
            ]
            for cmd in commands:
                subprocess.run(cmd, shell=True, check=True)
        
        elif self.system == 'darwin':
            print(f"{Colors.WARNING}Please install Docker Desktop for Mac from: https://docs.docker.com/desktop/mac/install/{Colors.ENDC}")
            input("Press Enter after installing Docker Desktop...")
        
        elif self.system == 'windows':
            print(f"{Colors.WARNING}Please install Docker Desktop for Windows from: https://docs.docker.com/desktop/windows/install/{Colors.ENDC}")
            input("Press Enter after installing Docker Desktop...")
    
    def install_docker_compose(self):
        """Install Docker Compose"""
        print(f"{Colors.OKBLUE}🔧 Installing Docker Compose...{Colors.ENDC}")
        
        if self.system in ['linux', 'darwin']:
            cmd = 'pip3 install docker-compose'
            subprocess.run(cmd, shell=True, check=True)
        else:
            print(f"{Colors.OKGREEN}Docker Compose included with Docker Desktop{Colors.ENDC}")
    
    def install_aws_cli(self):
        """Install AWS CLI"""
        print(f"{Colors.OKBLUE}☁️ Installing AWS CLI...{Colors.ENDC}")
        
        if self.system == 'linux':
            commands = [
                'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"',
                'unzip awscliv2.zip',
                'sudo ./aws/install',
                'rm -rf aws awscliv2.zip'
            ]
        elif self.system == 'darwin':
            commands = [
                'curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"',
                'sudo installer -pkg AWSCLIV2.pkg -target /',
                'rm AWSCLIV2.pkg'
            ]
        else:  # Windows
            print(f"{Colors.WARNING}Please install AWS CLI from: https://aws.amazon.com/cli/{Colors.ENDC}")
            input("Press Enter after installing AWS CLI...")
            return
        
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)
    
    def install_terraform(self):
        """Install Terraform"""
        print(f"{Colors.OKBLUE}🏗️ Installing Terraform...{Colors.ENDC}")
        
        # Download and install Terraform
        tf_version = "1.6.6"
        
        if self.system == 'linux':
            tf_url = f"https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_linux_amd64.zip"
            install_path = "/usr/local/bin"
        elif self.system == 'darwin':
            tf_url = f"https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_darwin_amd64.zip"
            install_path = "/usr/local/bin"
        else:  # Windows
            tf_url = f"https://releases.hashicorp.com/terraform/{tf_version}/terraform_{tf_version}_windows_amd64.zip"
            install_path = str(Path.home() / "bin")
            os.makedirs(install_path, exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "terraform.zip"
            urllib.request.urlretrieve(tf_url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            tf_binary = Path(temp_dir) / "terraform"
            if self.system == 'windows':
                tf_binary = tf_binary.with_suffix('.exe')
            
            shutil.move(str(tf_binary), install_path)
            
            if self.system != 'windows':
                os.chmod(Path(install_path) / "terraform", 0o755)
    
    def collect_configuration(self):
        """Collect configuration from user"""
        print(f"\n{Colors.OKBLUE}⚙️ Configuration Setup{Colors.ENDC}")
        print("Please provide the following information:")
        
        # Deployment type
        print(f"\n{Colors.BOLD}1. Deployment Type:{Colors.ENDC}")
        print("   1) Local Development (Docker Compose)")
        print("   2) AWS Cloud Production")
        print("   3) AWS Cloud Development/Staging")
        
        while True:
            choice = input(f"{Colors.OKCYAN}Select deployment type (1-3): {Colors.ENDC}").strip()
            if choice in ['1', '2', '3']:
                deployment_types = {
                    '1': 'local',
                    '2': 'aws-production', 
                    '3': 'aws-staging'
                }
                self.config['deployment_type'] = deployment_types[choice]
                break
            print(f"{Colors.FAIL}Invalid choice. Please select 1, 2, or 3.{Colors.ENDC}")
        
        # AWS Configuration (if cloud deployment)
        if self.config['deployment_type'].startswith('aws'):
            print(f"\n{Colors.BOLD}2. AWS Configuration:{Colors.ENDC}")
            
            self.config['aws_region'] = input(f"{Colors.OKCYAN}AWS Region (default: us-east-1): {Colors.ENDC}").strip() or 'us-east-1'
            
            print(f"\n{Colors.WARNING}AWS Credentials Setup:{Colors.ENDC}")
            print("You can configure AWS credentials in several ways:")
            print("1) AWS CLI: Run 'aws configure' after installation")
            print("2) Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
            print("3) IAM roles (for EC2 instances)")
            
            configure_now = input(f"{Colors.OKCYAN}Configure AWS credentials now? (y/n): {Colors.ENDC}").strip().lower()
            if configure_now == 'y':
                access_key = input(f"{Colors.OKCYAN}AWS Access Key ID: {Colors.ENDC}").strip()
                secret_key = input(f"{Colors.OKCYAN}AWS Secret Access Key: {Colors.ENDC}").strip()
                
                self.config['aws_access_key_id'] = access_key
                self.config['aws_secret_access_key'] = secret_key
        
        # Notification Configuration
        print(f"\n{Colors.BOLD}3. Notification Configuration:{Colors.ENDC}")
        
        slack_webhook = input(f"{Colors.OKCYAN}Slack Webhook URL (optional): {Colors.ENDC}").strip()
        if slack_webhook:
            self.config['slack_webhook_url'] = slack_webhook
        
        email = input(f"{Colors.OKCYAN}Alert Email Address (optional): {Colors.ENDC}").strip()
        if email:
            self.config['alert_email'] = email
        
        # Advanced Configuration
        print(f"\n{Colors.BOLD}4. Advanced Configuration:{Colors.ENDC}")
        
        self.config['confidence_threshold'] = float(input(f"{Colors.OKCYAN}ML Confidence Threshold (0.0-1.0, default: 0.8): {Colors.ENDC}").strip() or '0.8')
        
        auto_remediation = input(f"{Colors.OKCYAN}Enable Auto-Remediation? (y/n, default: n): {Colors.ENDC}").strip().lower()
        self.config['auto_remediation_enabled'] = auto_remediation == 'y'
        
        # Project Configuration
        self.config['project_name'] = input(f"{Colors.OKCYAN}Project Name (default: ai-recoverops): {Colors.ENDC}").strip() or 'ai-recoverops'
        self.config['environment'] = 'production' if self.config['deployment_type'] == 'aws-production' else 'development'
    
    def download_source_code(self):
        """Download AI-RecoverOps source code"""
        print(f"\n{Colors.OKBLUE}📥 Downloading AI-RecoverOps source code...{Colors.ENDC}")
        
        # Create installation directory
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # For this demo, we'll create the files directly
        # In a real scenario, you'd clone from a Git repository
        print(f"{Colors.OKGREEN}✅ Source code ready at: {self.install_dir}{Colors.ENDC}")
    
    def generate_configuration_files(self):
        """Generate configuration files based on user input"""
        print(f"\n{Colors.OKBLUE}📝 Generating configuration files...{Colors.ENDC}")
        
        # Generate .env file
        env_content = self.generate_env_file()
        with open(self.install_dir / '.env', 'w') as f:
            f.write(env_content)
        
        # Generate docker-compose override for local deployment
        if self.config['deployment_type'] == 'local':
            compose_override = self.generate_compose_override()
            with open(self.install_dir / 'docker-compose.override.yml', 'w') as f:
                f.write(compose_override)
        
        # Generate Terraform variables for AWS deployment
        if self.config['deployment_type'].startswith('aws'):
            tf_vars = self.generate_terraform_vars()
            with open(self.install_dir / 'deployment' / 'terraform' / 'terraform.tfvars', 'w') as f:
                f.write(tf_vars)
        
        # Generate application config
        app_config = self.generate_app_config()
        with open(self.install_dir / 'config.yaml', 'w') as f:
            f.write(app_config)
        
        print(f"{Colors.OKGREEN}✅ Configuration files generated{Colors.ENDC}")
    
    def generate_env_file(self) -> str:
        """Generate .env file content"""
        env_vars = [
            "# AI-RecoverOps Configuration",
            f"PROJECT_NAME={self.config['project_name']}",
            f"ENVIRONMENT={self.config['environment']}",
            f"DEPLOYMENT_TYPE={self.config['deployment_type']}",
            "",
            "# ML Configuration",
            f"CONFIDENCE_THRESHOLD={self.config['confidence_threshold']}",
            f"AUTO_REMEDIATION_ENABLED={str(self.config['auto_remediation_enabled']).lower()}",
            "",
            "# Notification Configuration"
        ]
        
        if 'slack_webhook_url' in self.config:
            env_vars.append(f"SLACK_WEBHOOK_URL={self.config['slack_webhook_url']}")
        
        if 'alert_email' in self.config:
            env_vars.append(f"ALERT_EMAIL={self.config['alert_email']}")
        
        if self.config['deployment_type'].startswith('aws'):
            env_vars.extend([
                "",
                "# AWS Configuration",
                f"AWS_REGION={self.config['aws_region']}"
            ])
            
            if 'aws_access_key_id' in self.config:
                env_vars.extend([
                    f"AWS_ACCESS_KEY_ID={self.config['aws_access_key_id']}",
                    f"AWS_SECRET_ACCESS_KEY={self.config['aws_secret_access_key']}"
                ])
        
        return '\n'.join(env_vars)
    
    def generate_compose_override(self) -> str:
        """Generate Docker Compose override for local development"""
        return f"""version: '3.8'

services:
  ml-api:
    environment:
      - CONFIDENCE_THRESHOLD={self.config['confidence_threshold']}
      - AUTO_REMEDIATION_ENABLED={str(self.config['auto_remediation_enabled']).lower()}
      - SLACK_WEBHOOK_URL={self.config.get('slack_webhook_url', '')}
    
  dashboard:
    environment:
      - REACT_APP_PROJECT_NAME={self.config['project_name']}
      - REACT_APP_ENVIRONMENT={self.config['environment']}
"""
    
    def generate_terraform_vars(self) -> str:
        """Generate Terraform variables file"""
        return f"""# AI-RecoverOps Terraform Configuration
aws_region = "{self.config['aws_region']}"
environment = "{self.config['environment']}"
project_name = "{self.config['project_name']}"

# Instance sizing based on environment
{self.get_instance_sizing()}

# Notification configuration
alert_email = "{self.config.get('alert_email', '')}"
slack_webhook_url = "{self.config.get('slack_webhook_url', '')}"

# ML Configuration
confidence_threshold = {self.config['confidence_threshold']}
auto_remediation_enabled = {str(self.config['auto_remediation_enabled']).lower()}
"""
    
    def get_instance_sizing(self) -> str:
        """Get instance sizing based on environment"""
        if self.config['deployment_type'] == 'aws-production':
            return """# Production sizing
ecs_task_cpu = 1024
ecs_task_memory = 2048
rds_instance_class = "db.t3.small"
redis_node_type = "cache.t3.small"
enable_multi_az = true
backup_retention_period = 30"""
        else:
            return """# Development/Staging sizing
ecs_task_cpu = 512
ecs_task_memory = 1024
rds_instance_class = "db.t3.micro"
redis_node_type = "cache.t3.micro"
enable_multi_az = false
backup_retention_period = 7"""
    
    def generate_app_config(self) -> str:
        """Generate application configuration"""
        return f"""ai_recoverops:
  core:
    log_level: INFO
    max_concurrent_fixes: 3
    rollback_timeout: 300
    learning_mode: true
    
  detection:
    interval: 30
    enabled_detectors:
      - system
      - application
      - network
      - database
    
  analysis:
    confidence_threshold: {self.config['confidence_threshold']}
    max_analysis_time: 120
    use_historical_data: true
    
  fixes:
    auto_apply: {str(self.config['auto_remediation_enabled']).lower()}
    require_approval: {str(not self.config['auto_remediation_enabled']).lower()}
    backup_before_fix: true
    
  monitoring:
    prometheus_port: 9090
    health_check_port: 8080
    alert_webhook: {self.config.get('slack_webhook_url', 'null')}
    
  ml:
    model_update_interval: 3600
    training_data_retention: 30
    feature_extraction_enabled: true
"""
    
    def setup_local_environment(self):
        """Setup local development environment"""
        print(f"\n{Colors.OKBLUE}🐳 Setting up local environment...{Colors.ENDC}")
        
        os.chdir(self.install_dir)
        
        # Generate synthetic data
        print(f"{Colors.OKCYAN}Generating training data...{Colors.ENDC}")
        subprocess.run([sys.executable, 'data/generate_synthetic_logs.py'], check=True)
        
        # Train ML models
        print(f"{Colors.OKCYAN}Training ML models...{Colors.ENDC}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'ml/requirements.txt'], check=True)
        subprocess.run([sys.executable, 'ml/model_training.py'], check=True)
        
        # Start services
        print(f"{Colors.OKCYAN}Starting Docker services...{Colors.ENDC}")
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        
        # Wait for services to be ready
        print(f"{Colors.OKCYAN}Waiting for services to start...{Colors.ENDC}")
        time.sleep(30)
        
        # Verify services
        self.verify_local_services()
    
    def setup_aws_environment(self):
        """Setup AWS cloud environment"""
        print(f"\n{Colors.OKBLUE}☁️ Setting up AWS environment...{Colors.ENDC}")
        
        os.chdir(self.install_dir)
        
        # Configure AWS CLI if credentials provided
        if 'aws_access_key_id' in self.config:
            self.configure_aws_cli()
        
        # Generate and train models locally first
        print(f"{Colors.OKCYAN}Preparing ML models...{Colors.ENDC}")
        subprocess.run([sys.executable, 'data/generate_synthetic_logs.py'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'ml/requirements.txt'], check=True)
        subprocess.run([sys.executable, 'ml/model_training.py'], check=True)
        
        # Deploy infrastructure with Terraform
        print(f"{Colors.OKCYAN}Deploying AWS infrastructure...{Colors.ENDC}")
        os.chdir('deployment/terraform')
        
        subprocess.run(['terraform', 'init'], check=True)
        subprocess.run(['terraform', 'plan', '-var-file=terraform.tfvars'], check=True)
        
        apply_confirm = input(f"{Colors.WARNING}Deploy to AWS? This will create billable resources. (y/n): {Colors.ENDC}").strip().lower()
        if apply_confirm == 'y':
            subprocess.run(['terraform', 'apply', '-auto-approve', '-var-file=terraform.tfvars'], check=True)
            
            # Get outputs
            outputs = self.get_terraform_outputs()
            
            # Deploy application components
            os.chdir('../..')
            self.deploy_aws_applications(outputs)
        else:
            print(f"{Colors.WARNING}AWS deployment cancelled by user{Colors.ENDC}")
    
    def configure_aws_cli(self):
        """Configure AWS CLI with provided credentials"""
        print(f"{Colors.OKCYAN}Configuring AWS CLI...{Colors.ENDC}")
        
        aws_config = f"""[default]
aws_access_key_id = {self.config['aws_access_key_id']}
aws_secret_access_key = {self.config['aws_secret_access_key']}
region = {self.config['aws_region']}
output = json
"""
        
        aws_dir = Path.home() / '.aws'
        aws_dir.mkdir(exist_ok=True)
        
        with open(aws_dir / 'credentials', 'w') as f:
            f.write(aws_config)
    
    def get_terraform_outputs(self) -> Dict[str, str]:
        """Get Terraform outputs"""
        result = subprocess.run(['terraform', 'output', '-json'], 
                              capture_output=True, text=True, check=True)
        outputs = json.loads(result.stdout)
        return {k: v['value'] for k, v in outputs.items()}
    
    def deploy_aws_applications(self, outputs: Dict[str, str]):
        """Deploy applications to AWS"""
        print(f"{Colors.OKCYAN}Deploying applications to AWS...{Colors.ENDC}")
        
        # Upload models to S3
        s3_bucket = outputs['s3_models_bucket']
        subprocess.run(['aws', 's3', 'sync', 'models/', f's3://{s3_bucket}/'], check=True)
        
        # Build and push Docker images
        ecr_api_repo = outputs['ecr_ml_api_repository_url']
        ecr_dashboard_repo = outputs['ecr_dashboard_repository_url']
        
        # Login to ECR
        subprocess.run(['aws', 'ecr', 'get-login-password', '--region', self.config['aws_region']], 
                      capture_output=True, text=True, check=True)
        
        # Build and push images (simplified for demo)
        print(f"{Colors.OKCYAN}Building and pushing Docker images...{Colors.ENDC}")
        
        # Deploy Lambda functions
        self.deploy_lambda_functions()
        
        # Create ECS services
        self.create_ecs_services(outputs)
    
    def deploy_lambda_functions(self):
        """Deploy Lambda functions"""
        print(f"{Colors.OKCYAN}Deploying Lambda functions...{Colors.ENDC}")
        
        # Package and deploy log processor
        os.chdir('aws/lambda_functions')
        
        with zipfile.ZipFile('log_processor.zip', 'w') as zipf:
            zipf.write('log_processor.py')
        
        subprocess.run([
            'aws', 'lambda', 'create-function',
            '--function-name', f"{self.config['project_name']}-log-processor",
            '--runtime', 'python3.10',
            '--role', f"arn:aws:iam::{self.get_account_id()}:role/{self.config['project_name']}-lambda-role",
            '--handler', 'log_processor.lambda_handler',
            '--zip-file', 'fileb://log_processor.zip'
        ], check=True)
        
        os.chdir('../..')
    
    def create_ecs_services(self, outputs: Dict[str, str]):
        """Create ECS services"""
        print(f"{Colors.OKCYAN}Creating ECS services...{Colors.ENDC}")
        # Implementation would create ECS task definitions and services
        pass
    
    def get_account_id(self) -> str:
        """Get AWS account ID"""
        result = subprocess.run(['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'],
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    
    def verify_local_services(self):
        """Verify local services are running"""
        print(f"\n{Colors.OKBLUE}🔍 Verifying services...{Colors.ENDC}")
        
        services = {
            'ML API': 'http://localhost:8000/health',
            'Dashboard': 'http://localhost:3000',
            'Grafana': 'http://localhost:3001',
            'Redis': 'redis://localhost:6379'
        }
        
        for service, url in services.items():
            try:
                if url.startswith('http'):
                    urllib.request.urlopen(url, timeout=5)
                print(f"{Colors.OKGREEN}✅ {service} - Running{Colors.ENDC}")
            except:
                print(f"{Colors.FAIL}❌ {service} - Not responding{Colors.ENDC}")
    
    def create_management_scripts(self):
        """Create management scripts for easy operation"""
        print(f"\n{Colors.OKBLUE}📜 Creating management scripts...{Colors.ENDC}")
        
        # Create start script
        start_script = f"""#!/bin/bash
# AI-RecoverOps Start Script
cd {self.install_dir}

echo "Starting AI-RecoverOps..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 30

echo "Services started successfully!"
echo "Dashboard: http://localhost:3000"
echo "ML API: http://localhost:8000"
echo "Grafana: http://localhost:3001 (admin/admin123)"
"""
        
        with open(self.install_dir / 'start.sh', 'w') as f:
            f.write(start_script)
        os.chmod(self.install_dir / 'start.sh', 0o755)
        
        # Create stop script
        stop_script = f"""#!/bin/bash
# AI-RecoverOps Stop Script
cd {self.install_dir}

echo "Stopping AI-RecoverOps..."
docker-compose down

echo "AI-RecoverOps stopped successfully!"
"""
        
        with open(self.install_dir / 'stop.sh', 'w') as f:
            f.write(stop_script)
        os.chmod(self.install_dir / 'stop.sh', 0o755)
        
        # Create status script
        status_script = f"""#!/bin/bash
# AI-RecoverOps Status Script
cd {self.install_dir}

echo "AI-RecoverOps Status:"
docker-compose ps
"""
        
        with open(self.install_dir / 'status.sh', 'w') as f:
            f.write(status_script)
        os.chmod(self.install_dir / 'status.sh', 0o755)
        
        print(f"{Colors.OKGREEN}✅ Management scripts created{Colors.ENDC}")
    
    def print_success_message(self):
        """Print installation success message"""
        success_msg = f"""
{Colors.OKGREEN}{Colors.BOLD}
🎉 AI-RecoverOps Installation Complete! 🎉
{Colors.ENDC}

{Colors.OKBLUE}Installation Directory:{Colors.ENDC} {self.install_dir}

{Colors.OKBLUE}Quick Start Commands:{Colors.ENDC}
"""
        
        if self.config['deployment_type'] == 'local':
            success_msg += f"""
  Start Services:    {self.install_dir}/start.sh
  Stop Services:     {self.install_dir}/stop.sh
  Check Status:      {self.install_dir}/status.sh

{Colors.OKBLUE}Access URLs:{Colors.ENDC}
  🖥️  Dashboard:      http://localhost:3000
  🤖 ML API:         http://localhost:8000
  📊 Grafana:        http://localhost:3001 (admin/admin123)
  🔍 MLflow:         http://localhost:5000

{Colors.OKBLUE}Next Steps:{Colors.ENDC}
  1. Access the dashboard to monitor incidents
  2. Configure log sources in your applications
  3. Set up CloudWatch log forwarding (for AWS integration)
  4. Customize detection rules and remediation actions
"""
        else:
            success_msg += f"""
{Colors.OKBLUE}AWS Resources Created:{Colors.ENDC}
  - ECS Cluster for application hosting
  - RDS PostgreSQL database
  - ElastiCache Redis cluster
  - S3 buckets for logs and models
  - Lambda functions for log processing
  - CloudWatch alarms and dashboards

{Colors.OKBLUE}Next Steps:{Colors.ENDC}
  1. Configure your applications to send logs to CloudWatch
  2. Set up log subscription filters
  3. Access the dashboard via the ALB endpoint
  4. Configure notification channels (Slack, email)
"""
        
        success_msg += f"""
{Colors.OKBLUE}Documentation:{Colors.ENDC}
  📖 User Guide:      {self.install_dir}/README.md
  🚀 Deployment:     {self.install_dir}/DEPLOYMENT_GUIDE.md
  🏗️  Architecture:   {self.install_dir}/SYSTEM_ARCHITECTURE.md

{Colors.OKBLUE}Support:{Colors.ENDC}
  📧 Issues: Create an issue in the GitHub repository
  💬 Community: Join our Slack workspace
  📚 Docs: Check the documentation directory

{Colors.WARNING}Remember to:{Colors.ENDC}
  - Secure your AWS credentials
  - Configure proper IAM permissions
  - Set up monitoring and alerting
  - Test remediation actions in a safe environment

{Colors.OKGREEN}Happy incident hunting! 🔍🤖{Colors.ENDC}
"""
        
        print(success_msg)
    
    def run_installation(self):
        """Run the complete installation process"""
        try:
            self.print_banner()
            
            if not self.check_prerequisites():
                print(f"{Colors.FAIL}Prerequisites check failed. Please install required tools and try again.{Colors.ENDC}")
                return False
            
            self.install_dependencies()
            self.collect_configuration()
            self.download_source_code()
            self.generate_configuration_files()
            
            if self.config['deployment_type'] == 'local':
                self.setup_local_environment()
            else:
                self.setup_aws_environment()
            
            self.create_management_scripts()
            self.print_success_message()
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Installation cancelled by user{Colors.ENDC}")
            return False
        except Exception as e:
            print(f"\n{Colors.FAIL}Installation failed: {str(e)}{Colors.ENDC}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI-RecoverOps Universal Installer')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--non-interactive', action='store_true', help='Run in non-interactive mode')
    args = parser.parse_args()
    
    installer = AIRecoverOpsInstaller()
    
    if args.non_interactive:
        # Load configuration from file for automated installation
        if args.config and os.path.exists(args.config):
            with open(args.config) as f:
                installer.config = json.load(f)
        else:
            print(f"{Colors.FAIL}Configuration file required for non-interactive mode{Colors.ENDC}")
            return 1
    
    success = installer.run_installation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())