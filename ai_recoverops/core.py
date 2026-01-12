"""
AI-RecoverOps Core Engine
Universal DevOps Automation Platform
"""

import os
import sys
import json
import yaml
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

class AIOpsCore:
    """Core AI-RecoverOps engine"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.version = "1.0.0"
        self.config_file = config_file or Path.cwd() / "aiops.yml"
        self.state_file = Path.cwd() / ".aiops" / "state.json"
        self.config = self.load_config()
        self.logger = self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_file = Path('.aiops') / 'aiops.log'
        
        # Create logs directory
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger('aiops')
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from aiops.yml"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return self.default_config()
    
    def default_config(self) -> Dict[str, Any]:
        """Default configuration template"""
        return {
            'project': {
                'name': 'ai-recoverops-project',
                'version': '1.0.0',
                'description': 'AI-powered DevOps automation'
            },
            'infrastructure': {
                'provider': 'aws',  # aws, azure, gcp, kubernetes, docker, local
                'region': 'us-east-1',
                'services': []
            },
            'monitoring': {
                'enabled': True,
                'interval': 30,
                'log_sources': [],
                'metrics': [],
                'dashboard': {
                    'enabled': True,
                    'port': 3000
                }
            },
            'remediation': {
                'auto_remediation': True,
                'confidence_threshold': 0.8,
                'max_concurrent': 3,
                'rollback_timeout': 300,
                'dry_run': False
            },
            'notifications': {
                'slack': {'enabled': False, 'webhook': ''},
                'email': {'enabled': False, 'smtp': ''},
                'teams': {'enabled': False, 'webhook': ''},
                'pagerduty': {'enabled': False, 'api_key': ''}
            },
            'logging': {
                'level': 'INFO',
                'retention_days': 30
            }
        }
    
    def save_config(self):
        """Save configuration to aiops.yml"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def init_project(self, project_name: Optional[str] = None, template: str = "web-app") -> bool:
        """Initialize new AI-RecoverOps project"""
        try:
            if project_name:
                self.config['project']['name'] = project_name
            
            self.logger.info(f"Initializing project: {self.config['project']['name']}")
            
            # Create directory structure
            dirs = [
                '.aiops',
                'configs',
                'playbooks',
                'templates',
                'logs',
                'scripts',
                'dashboards'
            ]
            
            for dir_name in dirs:
                Path(dir_name).mkdir(exist_ok=True)
            
            # Create configuration files
            self.save_config()
            
            # Create template-specific files
            if template == "web-app":
                self.create_web_app_template()
            elif template == "microservices":
                self.create_microservices_template()
            elif template == "database":
                self.create_database_template()
            
            # Create example playbooks
            self.create_example_playbooks()
            
            # Create infrastructure templates
            self.create_infrastructure_templates()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize project: {e}")
            return False
    
    def create_web_app_template(self):
        """Create web application template"""
        # Web server configuration
        web_server_config = {
            'name': 'web-server',
            'type': 'web_application',
            'provider': self.config['infrastructure']['provider'],
            'resources': {
                'instances': ['i-1234567890abcdef0'],
                'load_balancer': 'alb-web-server',
                'auto_scaling_group': 'asg-web-server'
            },
            'monitoring': {
                'metrics': ['cpu_usage', 'memory_usage', 'response_time', 'request_count'],
                'logs': ['/var/log/nginx/access.log', '/var/log/nginx/error.log', '/var/log/app.log'],
                'health_check': 'http://localhost:8080/health',
                'endpoints': [
                    {'path': '/', 'method': 'GET', 'expected_status': 200},
                    {'path': '/api/health', 'method': 'GET', 'expected_status': 200}
                ]
            },
            'thresholds': {
                'cpu_usage': {'warning': 70, 'critical': 90},
                'memory_usage': {'warning': 80, 'critical': 95},
                'response_time': {'warning': 1000, 'critical': 5000},
                'error_rate': {'warning': 5, 'critical': 10}
            },
            'scaling': {
                'min_instances': 2,
                'max_instances': 10,
                'target_cpu': 70
            }
        }
        
        # Database configuration
        database_config = {
            'name': 'database',
            'type': 'database',
            'provider': self.config['infrastructure']['provider'],
            'engine': 'postgresql',
            'resources': {
                'instance': 'db.t3.medium',
                'storage': '100GB'
            },
            'monitoring': {
                'metrics': ['cpu_usage', 'memory_usage', 'connections', 'query_time'],
                'logs': ['/var/log/postgresql/postgresql.log'],
                'health_check': 'postgresql://localhost:5432/healthcheck'
            },
            'thresholds': {
                'cpu_usage': {'warning': 80, 'critical': 95},
                'memory_usage': {'warning': 85, 'critical': 95},
                'connections': {'warning': 80, 'critical': 95},
                'query_time': {'warning': 1000, 'critical': 5000}
            }
        }
        
        # Save configurations
        self.save_service_config('web-server', web_server_config)
        self.save_service_config('database', database_config)
    
    def create_microservices_template(self):
        """Create microservices template"""
        services = ['api-gateway', 'user-service', 'order-service', 'payment-service']
        
        for service in services:
            config = {
                'name': service,
                'type': 'microservice',
                'provider': 'kubernetes',
                'resources': {
                    'deployment': f'{service}-deployment',
                    'service': f'{service}-service',
                    'replicas': 3
                },
                'monitoring': {
                    'metrics': ['cpu_usage', 'memory_usage', 'request_latency'],
                    'logs': [f'/var/log/{service}.log'],
                    'health_check': f'http://{service}:8080/health'
                },
                'thresholds': {
                    'cpu_usage': {'warning': 70, 'critical': 90},
                    'memory_usage': {'warning': 80, 'critical': 95},
                    'request_latency': {'warning': 500, 'critical': 2000}
                }
            }
            
            self.save_service_config(service, config)
    
    def create_database_template(self):
        """Create database-focused template"""
        databases = ['primary-db', 'replica-db', 'cache-db']
        
        for db in databases:
            config = {
                'name': db,
                'type': 'database',
                'provider': self.config['infrastructure']['provider'],
                'engine': 'postgresql' if 'db' in db else 'redis',
                'monitoring': {
                    'metrics': ['cpu_usage', 'memory_usage', 'connections', 'replication_lag'],
                    'logs': [f'/var/log/{db}.log'],
                    'health_check': f'tcp://{db}:5432'
                },
                'thresholds': {
                    'cpu_usage': {'warning': 80, 'critical': 95},
                    'memory_usage': {'warning': 85, 'critical': 95},
                    'connections': {'warning': 80, 'critical': 95}
                }
            }
            
            self.save_service_config(db, config)
    
    def save_service_config(self, name: str, config: Dict[str, Any]):
        """Save service configuration"""
        config_file = Path('configs') / f'{name}.yml'
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    
    def create_example_playbooks(self):
        """Create example remediation playbooks"""
        playbooks = {
            'high_cpu_remediation': {
                'name': 'High CPU Remediation',
                'description': 'Automatically handle high CPU usage incidents',
                'triggers': ['high_cpu', 'cpu_spike'],
                'conditions': {
                    'confidence': '> 0.8',
                    'severity': ['critical', 'high']
                },
                'actions': [
                    {
                        'name': 'Check system resources',
                        'type': 'command',
                        'command': 'top -n 1 | head -20',
                        'timeout': 30
                    },
                    {
                        'name': 'Identify high CPU processes',
                        'type': 'command',
                        'command': 'ps aux --sort=-%cpu | head -10',
                        'timeout': 30
                    },
                    {
                        'name': 'Restart service if needed',
                        'type': 'service',
                        'action': 'restart',
                        'service': '{{ incident.service }}',
                        'condition': 'cpu_usage > 90'
                    },
                    {
                        'name': 'Scale horizontally',
                        'type': 'scale',
                        'provider': '{{ infrastructure.provider }}',
                        'resource': '{{ incident.instance_id }}',
                        'action': 'scale_out',
                        'count': 1,
                        'condition': 'cpu_usage > 85 AND duration > 300'
                    }
                ],
                'rollback': [
                    {
                        'name': 'Scale back if issue resolved',
                        'type': 'scale',
                        'action': 'scale_in',
                        'delay': 300,
                        'condition': 'cpu_usage < 60'
                    }
                ]
            },
            
            'memory_leak_remediation': {
                'name': 'Memory Leak Remediation',
                'description': 'Handle memory leak incidents',
                'triggers': ['memory_leak', 'high_memory'],
                'conditions': {
                    'confidence': '> 0.7',
                    'severity': ['critical', 'high']
                },
                'actions': [
                    {
                        'name': 'Check memory usage',
                        'type': 'command',
                        'command': 'free -h && ps aux --sort=-%mem | head -10',
                        'timeout': 30
                    },
                    {
                        'name': 'Generate heap dump',
                        'type': 'command',
                        'command': 'jmap -dump:format=b,file=/tmp/heapdump.hprof {{ process_id }}',
                        'condition': 'service_type == "java"',
                        'timeout': 60
                    },
                    {
                        'name': 'Restart service',
                        'type': 'service',
                        'action': 'restart',
                        'service': '{{ incident.service }}',
                        'condition': 'memory_usage > 95'
                    }
                ]
            },
            
            'service_down_remediation': {
                'name': 'Service Down Remediation',
                'description': 'Handle service outage incidents',
                'triggers': ['service_down', 'health_check_failed'],
                'conditions': {
                    'confidence': '> 0.9'
                },
                'actions': [
                    {
                        'name': 'Check service status',
                        'type': 'command',
                        'command': 'systemctl status {{ incident.service }}',
                        'timeout': 30
                    },
                    {
                        'name': 'Check service logs',
                        'type': 'command',
                        'command': 'journalctl -u {{ incident.service }} --lines=50',
                        'timeout': 30
                    },
                    {
                        'name': 'Restart service',
                        'type': 'service',
                        'action': 'restart',
                        'service': '{{ incident.service }}'
                    },
                    {
                        'name': 'Verify service recovery',
                        'type': 'http',
                        'url': '{{ service.health_check }}',
                        'expected_status': 200,
                        'timeout': 60,
                        'retries': 3
                    }
                ]
            }
        }
        
        for name, playbook in playbooks.items():
            playbook_file = Path('playbooks') / f'{name}.yml'
            with open(playbook_file, 'w') as f:
                yaml.dump(playbook, f, default_flow_style=False, indent=2)
    
    def create_infrastructure_templates(self):
        """Create infrastructure templates"""
        # AWS template
        aws_template = {
            'provider': 'aws',
            'resources': {
                'vpc': {
                    'cidr': '10.0.0.0/16',
                    'subnets': [
                        {'cidr': '10.0.1.0/24', 'az': 'a', 'type': 'public'},
                        {'cidr': '10.0.2.0/24', 'az': 'b', 'type': 'public'},
                        {'cidr': '10.0.3.0/24', 'az': 'a', 'type': 'private'},
                        {'cidr': '10.0.4.0/24', 'az': 'b', 'type': 'private'}
                    ]
                },
                'ec2': {
                    'instance_type': 't3.medium',
                    'ami': 'ami-0abcdef1234567890',
                    'key_pair': 'my-key-pair',
                    'security_groups': ['web-sg', 'ssh-sg']
                },
                'rds': {
                    'engine': 'postgresql',
                    'instance_class': 'db.t3.micro',
                    'allocated_storage': 20,
                    'multi_az': True
                },
                'load_balancer': {
                    'type': 'application',
                    'scheme': 'internet-facing',
                    'target_groups': ['web-tg']
                }
            }
        }
        
        # Kubernetes template
        k8s_template = {
            'provider': 'kubernetes',
            'resources': {
                'namespace': 'ai-recoverops',
                'deployments': [
                    {
                        'name': 'web-app',
                        'replicas': 3,
                        'image': 'nginx:latest',
                        'ports': [80],
                        'resources': {
                            'requests': {'cpu': '100m', 'memory': '128Mi'},
                            'limits': {'cpu': '500m', 'memory': '512Mi'}
                        }
                    }
                ],
                'services': [
                    {
                        'name': 'web-app-service',
                        'type': 'LoadBalancer',
                        'ports': [{'port': 80, 'target_port': 80}]
                    }
                ]
            }
        }
        
        # Save templates
        templates_dir = Path('templates')
        with open(templates_dir / 'aws.yml', 'w') as f:
            yaml.dump(aws_template, f, default_flow_style=False, indent=2)
        
        with open(templates_dir / 'kubernetes.yml', 'w') as f:
            yaml.dump(k8s_template, f, default_flow_style=False, indent=2)
    
    def scan_infrastructure(self) -> List[Dict[str, Any]]:
        """Scan infrastructure for potential issues"""
        self.logger.info("Starting infrastructure scan")
        
        services = self.load_services()
        issues = []
        
        for service in services:
            self.logger.debug(f"Scanning service: {service['name']}")
            service_issues = self.scan_service(service)
            issues.extend(service_issues)
        
        self.logger.info(f"Scan completed. Found {len(issues)} issues")
        return issues
    
    def load_services(self) -> List[Dict[str, Any]]:
        """Load all service configurations"""
        services = []
        config_dir = Path('configs')
        
        if config_dir.exists():
            for config_file in config_dir.glob('*.yml'):
                try:
                    with open(config_file, 'r') as f:
                        service = yaml.safe_load(f)
                        services.append(service)
                except Exception as e:
                    self.logger.error(f"Failed to load service config {config_file}: {e}")
        
        return services
    
    def scan_service(self, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan individual service for issues"""
        issues = []
        
        # Health check
        if 'health_check' in service.get('monitoring', {}):
            health_issue = self.check_service_health(service)
            if health_issue:
                issues.append(health_issue)
        
        # Resource utilization check (mock for demo)
        resource_issues = self.check_resource_utilization(service)
        issues.extend(resource_issues)
        
        return issues
    
    def check_service_health(self, service: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check service health endpoint"""
        health_check = service['monitoring']['health_check']
        
        try:
            if health_check.startswith('http'):
                response = requests.get(health_check, timeout=5)
                if response.status_code != 200:
                    return {
                        'service': service['name'],
                        'severity': 'high',
                        'type': 'health_check_failed',
                        'description': f"Health check failed: HTTP {response.status_code}",
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                # TCP/other protocol checks would go here
                pass
                
        except Exception as e:
            return {
                'service': service['name'],
                'severity': 'critical',
                'type': 'service_unreachable',
                'description': f"Service unreachable: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def check_resource_utilization(self, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check resource utilization (mock implementation)"""
        issues = []
        
        # Mock resource data
        import random
        metrics = {
            'cpu_usage': random.randint(20, 95),
            'memory_usage': random.randint(30, 90),
            'response_time': random.randint(100, 3000),
            'error_rate': random.randint(0, 15)
        }
        
        thresholds = service.get('thresholds', {})
        
        for metric, value in metrics.items():
            threshold_config = thresholds.get(metric, {})
            
            if value > threshold_config.get('critical', 95):
                issues.append({
                    'service': service['name'],
                    'severity': 'critical',
                    'type': f'high_{metric}',
                    'description': f"Critical {metric.replace('_', ' ')}: {value}{'%' if 'usage' in metric else 'ms' if 'time' in metric else ''}",
                    'value': value,
                    'threshold': threshold_config.get('critical'),
                    'timestamp': datetime.now().isoformat()
                })
            elif value > threshold_config.get('warning', 80):
                issues.append({
                    'service': service['name'],
                    'severity': 'warning',
                    'type': f'elevated_{metric}',
                    'description': f"Elevated {metric.replace('_', ' ')}: {value}{'%' if 'usage' in metric else 'ms' if 'time' in metric else ''}",
                    'value': value,
                    'threshold': threshold_config.get('warning'),
                    'timestamp': datetime.now().isoformat()
                })
        
        return issues
    
    def deploy_monitoring(self, environment: str = 'production', dry_run: bool = False, dashboard: bool = True) -> bool:
        """Deploy monitoring and remediation infrastructure"""
        try:
            self.logger.info(f"Deploying to {environment} (dry_run: {dry_run})")
            
            if dry_run:
                self.logger.info("DRY RUN: Would deploy the following components:")
                self.logger.info("- API server on port 8000")
                if dashboard:
                    self.logger.info("- Dashboard on port 3000")
                self.logger.info("- Monitoring agents for configured services")
                return True
            
            # Start API server
            api_success = self.start_api_server()
            if not api_success:
                return False
            
            # Start dashboard if requested
            if dashboard:
                dashboard_success = self.start_dashboard()
                if not dashboard_success:
                    self.logger.warning("Dashboard failed to start, continuing without it")
            
            # Deploy monitoring agents (mock)
            self.deploy_monitoring_agents()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return False
    
    def start_api_server(self) -> bool:
        """Start the API server"""
        try:
            # Check if API is already running
            try:
                response = requests.get('http://localhost:8000/health', timeout=2)
                if response.status_code == 200:
                    self.logger.info("API server already running")
                    return True
            except:
                pass
            
            # Start API server
            api_script = Path(__file__).parent.parent / 'api' / 'main.py'
            if api_script.exists():
                subprocess.Popen([
                    sys.executable, str(api_script)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Wait and verify
                time.sleep(3)
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    self.logger.info("API server started successfully")
                    return True
            
            self.logger.error("Failed to start API server")
            return False
            
        except Exception as e:
            self.logger.error(f"API server startup failed: {e}")
            return False
    
    def start_dashboard(self) -> bool:
        """Start the dashboard"""
        try:
            dashboard_dir = Path(__file__).parent.parent / 'dashboard'
            if dashboard_dir.exists():
                subprocess.Popen([
                    'npm', 'start'
                ], cwd=dashboard_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.logger.info("Dashboard starting...")
                return True
            
            self.logger.warning("Dashboard directory not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Dashboard startup failed: {e}")
            return False
    
    def deploy_monitoring_agents(self):
        """Deploy monitoring agents (mock implementation)"""
        services = self.load_services()
        
        for service in services:
            self.logger.info(f"Deploying monitoring for {service['name']}")
            # In a real implementation, this would deploy actual monitoring agents
    
    def get_system_status(self) -> Dict[str, Dict[str, Any]]:
        """Get system status information"""
        status = {}
        
        # Check API server
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                status['api_server'] = {
                    'status': 'running',
                    'details': f"Uptime: {data.get('uptime', 'Unknown')}"
                }
            else:
                status['api_server'] = {'status': 'error', 'details': f"HTTP {response.status_code}"}
        except:
            status['api_server'] = {'status': 'stopped', 'details': 'Not responding'}
        
        # Check dashboard
        try:
            response = requests.get('http://localhost:3000', timeout=5)
            status['dashboard'] = {'status': 'running', 'details': 'Web interface available'}
        except:
            status['dashboard'] = {'status': 'stopped', 'details': 'Not responding'}
        
        # Check services
        services = self.load_services()
        status['services'] = {
            'status': 'running' if services else 'none',
            'details': f"{len(services)} services configured"
        }
        
        return status
    
    def set_config_value(self, key: str, value: str):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value (try to convert to appropriate type)
        try:
            if value.lower() in ['true', 'false']:
                config[keys[-1]] = value.lower() == 'true'
            elif value.isdigit():
                config[keys[-1]] = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                config[keys[-1]] = float(value)
            else:
                config[keys[-1]] = value
        except:
            config[keys[-1]] = value
        
        self.save_config()
    
    def get_config_value(self, key: str) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        config = self.config
        
        try:
            for k in keys:
                config = config[k]
            return config
        except KeyError:
            return None