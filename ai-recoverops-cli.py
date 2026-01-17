#!/usr/bin/env python3
"""
AI-RecoverOps Command Line Interface
Complete management tool for AI-RecoverOps operations
"""

import os
import sys
import json
import click
import requests
import yaml
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

console = Console()

class AIRecoverOpsCLI:
    """Command line interface for AI-RecoverOps"""
    
    def __init__(self):
        self.config_file = Path.home() / '.ai-recoverops' / 'config.yaml'
        self.config = self.load_config()
        self.api_base_url = self.config.get('api_url', 'http://localhost:8000')
    
    def load_config(self) -> Dict[str, Any]:
        """Load CLI configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return yaml.safe_load(f)
        return {}
    
    def save_config(self):
        """Save CLI configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
    
    def api_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make API request to AI-RecoverOps"""
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=30)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            console.print(f"[red]API Error: {e}[/red]")
            return {}

@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    """AI-RecoverOps Command Line Interface
    
    Manage your AI-RecoverOps deployment with ease.
    """
    ctx.ensure_object(dict)
    ctx.obj['cli'] = AIRecoverOpsCLI()

@cli.group()
def config():
    """Configuration management commands"""
    pass

@config.command()
@click.option('--api-url', help='API base URL')
@click.option('--aws-region', help='AWS region')
@click.option('--environment', help='Environment (dev/staging/prod)')
@click.pass_context
def set(ctx, api_url, aws_region, environment):
    """Set configuration values"""
    cli_obj = ctx.obj['cli']
    
    if api_url:
        cli_obj.config['api_url'] = api_url
        cli_obj.api_base_url = api_url
    
    if aws_region:
        cli_obj.config['aws_region'] = aws_region
    
    if environment:
        cli_obj.config['environment'] = environment
    
    cli_obj.save_config()
    console.print("[green]Configuration updated successfully![/green]")

@config.command()
@click.pass_context
def show(ctx):
    """Show current configuration"""
    cli_obj = ctx.obj['cli']
    
    table = Table(title="AI-RecoverOps Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in cli_obj.config.items():
        table.add_row(key, str(value))
    
    console.print(table)

@cli.group()
def status():
    """System status commands"""
    pass

@status.command()
@click.pass_context
def health(ctx):
    """Check system health"""
    cli_obj = ctx.obj['cli']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking system health...", total=None)
        
        health_data = cli_obj.api_request('/health')
        
        if health_data:
            progress.update(task, description="Health check complete")
            
            # Create health status panel
            status_text = f"""
Status: {health_data.get('status', 'Unknown')}
Timestamp: {health_data.get('timestamp', 'Unknown')}
Version: {health_data.get('version', 'Unknown')}
Models Loaded: {', '.join(health_data.get('models_loaded', []))}
"""
            
            status_color = "green" if health_data.get('status') == 'healthy' else "red"
            panel = Panel(status_text, title="System Health", border_style=status_color)
            console.print(panel)
        else:
            console.print("[red]Failed to get health status[/red]")

@status.command()
@click.pass_context
def metrics(ctx):
    """Show system metrics"""
    cli_obj = ctx.obj['cli']
    
    metrics_data = cli_obj.api_request('/metrics')
    
    if metrics_data:
        table = Table(title="System Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in metrics_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    table.add_row(f"{key}.{sub_key}", str(sub_value))
            else:
                table.add_row(key, str(value))
        
        console.print(table)
    else:
        console.print("[red]Failed to get metrics[/red]")

@cli.group()
def incidents():
    """Incident management commands"""
    pass

@incidents.command()
@click.option('--limit', default=10, help='Number of incidents to show')
@click.option('--severity', help='Filter by severity (critical/high/medium/low)')
@click.option('--status', help='Filter by status (open/investigating/resolved)')
@click.pass_context
def list(ctx, limit, severity, status):
    """List recent incidents"""
    cli_obj = ctx.obj['cli']
    
    # For demo purposes, we'll generate mock data
    # In real implementation, this would call the API
    incidents_data = generate_mock_incidents(limit, severity, status)
    
    if incidents_data:
        table = Table(title=f"Recent Incidents (Last {limit})")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Status", style="green")
        table.add_column("Service", style="blue")
        table.add_column("Timestamp", style="magenta")
        
        for incident in incidents_data:
            severity_style = {
                'critical': '[red]',
                'high': '[orange1]',
                'medium': '[yellow]',
                'low': '[green]'
            }.get(incident['severity'], '')
            
            table.add_row(
                incident['id'],
                incident['type'].replace('_', ' ').title(),
                f"{severity_style}{incident['severity']}[/]",
                incident['status'],
                incident['service'],
                incident['timestamp']
            )
        
        console.print(table)
    else:
        console.print("[yellow]No incidents found[/yellow]")

@incidents.command()
@click.argument('incident_id')
@click.pass_context
def show(ctx, incident_id):
    """Show detailed incident information"""
    cli_obj = ctx.obj['cli']
    
    # Mock incident details
    incident = {
        'id': incident_id,
        'type': 'high_cpu',
        'severity': 'critical',
        'status': 'investigating',
        'service': 'web-server',
        'instance_id': 'i-1234567890abcdef0',
        'timestamp': '2024-01-15T10:30:00Z',
        'description': 'High CPU usage detected on web-server instance',
        'confidence': 0.95,
        'recommended_action': 'restart_service',
        'log_message': 'CPU usage exceeded 95% for 5 minutes on instance i-1234567890abcdef0',
        'metadata': {
            'cpu_usage': 97.5,
            'memory_usage': 78.2,
            'disk_usage': 45.1,
            'response_time': 2500
        }
    }
    
    # Create detailed incident panel
    incident_text = f"""
ID: {incident['id']}
Type: {incident['type'].replace('_', ' ').title()}
Severity: {incident['severity'].upper()}
Status: {incident['status'].title()}
Service: {incident['service']}
Instance: {incident['instance_id']}
Timestamp: {incident['timestamp']}
Confidence: {incident['confidence']:.1%}

Description:
{incident['description']}

Log Message:
{incident['log_message']}

Recommended Action:
{incident['recommended_action'].replace('_', ' ').title()}

System Metrics:
• CPU Usage: {incident['metadata']['cpu_usage']}%
• Memory Usage: {incident['metadata']['memory_usage']}%
• Disk Usage: {incident['metadata']['disk_usage']}%
• Response Time: {incident['metadata']['response_time']}ms
"""
    
    severity_color = {
        'critical': 'red',
        'high': 'orange1',
        'medium': 'yellow',
        'low': 'green'
    }.get(incident['severity'], 'white')
    
    panel = Panel(incident_text, title=f"Incident Details - {incident_id}", border_style=severity_color)
    console.print(panel)

@incidents.command()
@click.argument('incident_id')
@click.argument('action', type=click.Choice(['acknowledge', 'resolve', 'escalate', 'remediate']))
@click.pass_context
def action(ctx, incident_id, action):
    """Perform action on incident"""
    cli_obj = ctx.obj['cli']
    
    if action == 'remediate':
        if not Confirm.ask(f"Are you sure you want to trigger auto-remediation for incident {incident_id}?"):
            console.print("[yellow]Remediation cancelled[/yellow]")
            return
    
    # Mock action execution
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Executing {action} on incident {incident_id}...", total=None)
        time.sleep(2)  # Simulate processing
        
        progress.update(task, description=f"{action.title()} completed successfully")
    
    console.print(f"[green]Successfully executed {action} on incident {incident_id}[/green]")

@cli.group()
def models():
    """ML model management commands"""
    pass

@models.command()
@click.pass_context
def list(ctx):
    """List available ML models"""
    cli_obj = ctx.obj['cli']
    
    models_data = cli_obj.api_request('/models')
    
    if models_data:
        table = Table(title="ML Models")
        table.add_column("Model", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Accuracy", style="yellow")
        
        # Mock model data
        models = [
            {'name': 'XGBoost Classifier', 'status': 'Loaded', 'accuracy': '85.2%'},
            {'name': 'LSTM Sequence Model', 'status': 'Loaded', 'accuracy': '82.7%'},
            {'name': 'Ensemble Predictor', 'status': 'Loaded', 'accuracy': '87.1%'}
        ]
        
        for model in models:
            table.add_row(model['name'], model['status'], model['accuracy'])
        
        console.print(table)
    else:
        console.print("[red]Failed to get model information[/red]")

@models.command()
@click.option('--data-path', help='Path to training data')
@click.pass_context
def train(ctx, data_path):
    """Train ML models"""
    cli_obj = ctx.obj['cli']
    
    if not data_path:
        data_path = Prompt.ask("Enter path to training data", default="data/training_logs.csv")
    
    if not Path(data_path).exists():
        console.print(f"[red]Training data not found: {data_path}[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Training ML models...", total=None)
        
        # Simulate training process
        steps = [
            "Loading training data...",
            "Preprocessing features...",
            "Training XGBoost model...",
            "Training LSTM model...",
            "Creating ensemble model...",
            "Evaluating models...",
            "Saving models..."
        ]
        
        for step in steps:
            progress.update(task, description=step)
            time.sleep(1)
    
    console.print("[green]Model training completed successfully![/green]")
    console.print("New models are ready for deployment.")

@cli.group()
def logs():
    """Log analysis commands"""
    pass

@logs.command()
@click.option('--file', help='Log file to analyze')
@click.option('--lines', default=100, help='Number of lines to analyze')
@click.pass_context
def analyze(ctx, file, lines):
    """Analyze log file for incidents"""
    cli_obj = ctx.obj['cli']
    
    if not file:
        file = Prompt.ask("Enter log file path")
    
    if not Path(file).exists():
        console.print(f"[red]Log file not found: {file}[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Analyzing {lines} lines from {file}...", total=None)
        
        # Mock analysis
        time.sleep(3)
        
        # Mock results
        results = [
            {'line': 45, 'type': 'high_cpu', 'confidence': 0.92, 'message': 'CPU usage exceeded threshold'},
            {'line': 78, 'type': 'memory_leak', 'confidence': 0.87, 'message': 'Memory usage increasing rapidly'},
            {'line': 156, 'type': 'disk_full', 'confidence': 0.95, 'message': 'Disk space critically low'}
        ]
        
        progress.update(task, description="Analysis complete")
    
    if results:
        table = Table(title=f"Log Analysis Results - {file}")
        table.add_column("Line", style="cyan")
        table.add_column("Incident Type", style="yellow")
        table.add_column("Confidence", style="green")
        table.add_column("Message", style="white")
        
        for result in results:
            table.add_row(
                str(result['line']),
                result['type'].replace('_', ' ').title(),
                f"{result['confidence']:.1%}",
                result['message']
            )
        
        console.print(table)
    else:
        console.print("[green]No incidents detected in log file[/green]")

@cli.group()
def deploy():
    """Deployment management commands"""
    pass

@deploy.command()
@click.option('--environment', type=click.Choice(['local', 'staging', 'production']), help='Deployment environment')
@click.pass_context
def start(ctx, environment):
    """Start AI-RecoverOps services"""
    cli_obj = ctx.obj['cli']
    
    if not environment:
        environment = Prompt.ask("Select environment", choices=['local', 'staging', 'production'], default='local')
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if environment == 'local':
            task = progress.add_task("Starting local services...", total=None)
            
            # Start Docker Compose services
            try:
                subprocess.run(['docker-compose', 'up', '-d'], check=True, capture_output=True)
                progress.update(task, description="Services started successfully")
                
                console.print("[green]Local services started successfully![/green]")
                console.print("Access points:")
                console.print("• Dashboard: http://localhost:3000")
                console.print("• ML API: http://localhost:8000")
                console.print("• Grafana: http://localhost:3001")
                
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Failed to start services: {e}[/red]")
        
        else:
            task = progress.add_task(f"Deploying to {environment}...", total=None)
            
            # Mock cloud deployment
            steps = [
                "Validating configuration...",
                "Building Docker images...",
                "Pushing to registry...",
                "Updating ECS services...",
                "Waiting for deployment..."
            ]
            
            for step in steps:
                progress.update(task, description=step)
                time.sleep(2)
            
            console.print(f"[green]Successfully deployed to {environment}![/green]")

@deploy.command()
@click.pass_context
def stop(ctx):
    """Stop AI-RecoverOps services"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Stopping services...", total=None)
        
        try:
            subprocess.run(['docker-compose', 'down'], check=True, capture_output=True)
            progress.update(task, description="Services stopped successfully")
            console.print("[green]Services stopped successfully![/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to stop services: {e}[/red]")

@deploy.command()
@click.pass_context
def status(ctx):
    """Show deployment status"""
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, check=True)
        
        if result.stdout:
            console.print("[cyan]Docker Compose Services:[/cyan]")
            console.print(result.stdout)
        else:
            console.print("[yellow]No services running[/yellow]")
    except subprocess.CalledProcessError:
        console.print("[red]Failed to get service status[/red]")

@cli.group()
def dashboard():
    """Dashboard management commands"""
    pass

@dashboard.command()
@click.pass_context
def open(ctx):
    """Open dashboard in browser"""
    import webbrowser
    
    dashboard_url = "http://localhost:3000"
    console.print(f"Opening dashboard: {dashboard_url}")
    webbrowser.open(dashboard_url)

@dashboard.command()
@click.pass_context
def summary(ctx):
    """Show dashboard summary"""
    cli_obj = ctx.obj['cli']
    
    # Mock dashboard data
    summary_data = {
        'total_incidents': 156,
        'open_incidents': 12,
        'resolved_today': 23,
        'auto_remediation_rate': 78.5,
        'avg_resolution_time': '4m 32s',
        'system_health': 94.2
    }
    
    # Create summary panel
    summary_text = f"""
Total Incidents: {summary_data['total_incidents']}
Open Incidents: {summary_data['open_incidents']}
Resolved Today: {summary_data['resolved_today']}
Auto-Remediation Rate: {summary_data['auto_remediation_rate']}%
Avg Resolution Time: {summary_data['avg_resolution_time']}
System Health Score: {summary_data['system_health']}%
"""
    
    panel = Panel(summary_text, title="Dashboard Summary", border_style="blue")
    console.print(panel)

@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive mode"""
    cli_obj = ctx.obj['cli']
    
    console.print("[cyan]Welcome to AI-RecoverOps Interactive Mode![/cyan]")
    console.print("Type 'help' for available commands or 'exit' to quit.")
    
    while True:
        try:
            command = Prompt.ask("\n[bold blue]ai-recoverops>[/bold blue]")
            
            if command.lower() in ['exit', 'quit']:
                console.print("[green]Goodbye![/green]")
                break
            elif command.lower() == 'help':
                show_interactive_help()
            elif command.lower() == 'status':
                ctx.invoke(health)
            elif command.lower() == 'incidents':
                ctx.invoke(list)
            elif command.lower() == 'models':
                ctx.invoke(models.commands['list'])
            else:
                console.print(f"[red]Unknown command: {command}[/red]")
                console.print("Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            console.print("\n[green]Goodbye![/green]")
            break

def show_interactive_help():
    """Show interactive mode help"""
    help_text = """
Available Commands:
• status      - Show system health
• incidents   - List recent incidents  
• models      - Show ML model status
• help        - Show this help message
• exit/quit   - Exit interactive mode

For full CLI functionality, exit interactive mode and use:
ai-recoverops-cli <command> --help
"""
    
    panel = Panel(help_text, title="Interactive Mode Help", border_style="green")
    console.print(panel)

def generate_mock_incidents(limit: int, severity: str = None, status: str = None) -> List[Dict]:
    """Generate mock incident data for demo"""
    import random
    from datetime import datetime, timedelta
    
    incident_types = ['high_cpu', 'memory_leak', 'disk_full', 'service_crash', 'db_connection_failure']
    severities = ['critical', 'high', 'medium', 'low']
    statuses = ['open', 'investigating', 'resolved']
    services = ['web-server', 'api-service', 'database', 'cache-service', 'worker']
    
    incidents = []
    
    for i in range(limit):
        incident_severity = severity if severity else random.choice(severities)
        incident_status = status if status else random.choice(statuses)
        
        timestamp = datetime.now() - timedelta(hours=random.randint(0, 72))
        
        incidents.append({
            'id': f"INC-{random.randint(1000, 9999)}",
            'type': random.choice(incident_types),
            'severity': incident_severity,
            'status': incident_status,
            'service': random.choice(services),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return incidents

if __name__ == '__main__':
    cli()