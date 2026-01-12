#!/usr/bin/env python3
"""
AI-RecoverOps CLI Interface
Universal DevOps Automation Platform
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
import yaml
import json
from typing import Optional
from .core import AIOpsCore

app = typer.Typer(
    name="aiops",
    help="AI-RecoverOps - Universal DevOps Automation Platform",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()

@app.command()
def init(
    project_name: Optional[str] = typer.Argument(None, help="Project name"),
    provider: str = typer.Option("aws", help="Infrastructure provider (aws, azure, gcp, kubernetes, docker)"),
    template: str = typer.Option("web-app", help="Project template (web-app, microservices, database)")
):
    """Initialize a new AI-RecoverOps project"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing project...", total=None)
        
        aiops = AIOpsCore()
        aiops.config['infrastructure']['provider'] = provider
        
        success = aiops.init_project(project_name, template)
        
        if success:
            console.print(Panel.fit(
                f"[green]✅ Project '{project_name or 'ai-recoverops-project'}' initialized successfully![/green]\n\n"
                f"[cyan]Next steps:[/cyan]\n"
                f"1. Edit [yellow]aiops.yml[/yellow] to configure your infrastructure\n"
                f"2. Add services in [yellow]configs/[/yellow] directory\n"
                f"3. Run [yellow]aiops scan[/yellow] to start monitoring\n"
                f"4. Run [yellow]aiops deploy[/yellow] to deploy monitoring infrastructure",
                title="🚀 AI-RecoverOps",
                border_style="green"
            ))
        else:
            console.print("[red]❌ Failed to initialize project[/red]")
            raise typer.Exit(1)

@app.command()
def scan(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    output: str = typer.Option("table", "--output", "-o", help="Output format (table, json, yaml)"),
    severity: Optional[str] = typer.Option(None, "--severity", "-s", help="Filter by severity (critical, high, medium, low)")
):
    """Scan infrastructure for potential issues"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning infrastructure...", total=None)
        
        aiops = AIOpsCore()
        issues = aiops.scan_infrastructure()
        
        if severity:
            issues = [issue for issue in issues if issue['severity'] == severity]
        
        if not issues:
            console.print("[green]✅ No issues detected[/green]")
            return
        
        if output == "table":
            table = Table(title="Infrastructure Issues")
            table.add_column("Service", style="cyan")
            table.add_column("Severity", style="red")
            table.add_column("Description", style="white")
            
            for issue in issues:
                severity_color = {
                    'critical': 'red',
                    'high': 'orange3',
                    'medium': 'yellow',
                    'low': 'green'
                }.get(issue['severity'], 'white')
                
                table.add_row(
                    issue['service'],
                    f"[{severity_color}]{issue['severity'].upper()}[/{severity_color}]",
                    issue['description']
                )
            
            console.print(table)
        
        elif output == "json":
            console.print(json.dumps(issues, indent=2))
        
        elif output == "yaml":
            console.print(yaml.dump(issues, default_flow_style=False))

@app.command()
def deploy(
    env: str = typer.Option("production", "--env", "-e", help="Environment (production, staging, development)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deployed without actually deploying"),
    dashboard: bool = typer.Option(True, "--dashboard/--no-dashboard", help="Deploy dashboard")
):
    """Deploy monitoring and remediation infrastructure"""
    
    if dry_run:
        console.print("[yellow]🔍 Dry run mode - showing what would be deployed[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Deploying to {env}...", total=None)
        
        aiops = AIOpsCore()
        success = aiops.deploy_monitoring(env, dry_run, dashboard)
        
        if success:
            console.print(Panel.fit(
                f"[green]✅ Successfully deployed to {env}![/green]\n\n"
                f"[cyan]Access Points:[/cyan]\n"
                f"📊 Dashboard: [link]http://localhost:3000[/link]\n"
                f"🔧 API: [link]http://localhost:8000[/link]\n"
                f"📖 API Docs: [link]http://localhost:8000/docs[/link]",
                title="🚀 Deployment Complete",
                border_style="green"
            ))
        else:
            console.print("[red]❌ Deployment failed[/red]")
            raise typer.Exit(1)

@app.command()
def monitor(
    watch: bool = typer.Option(False, "--watch", "-w", help="Continuous monitoring mode"),
    interval: int = typer.Option(30, "--interval", "-i", help="Monitoring interval in seconds"),
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Monitor specific service")
):
    """Start monitoring infrastructure"""
    
    aiops = AIOpsCore()
    
    if watch:
        console.print(f"[cyan]👁️  Starting continuous monitoring (interval: {interval}s)[/cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        
        try:
            aiops.start_monitoring(watch=True, interval=interval, service=service)
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped[/yellow]")
    else:
        console.print("[cyan]🔍 Running single scan...[/cyan]")
        aiops.start_monitoring(watch=False, service=service)

@app.command()
def remediate(
    incident_id: str = typer.Argument(..., help="Incident ID to remediate"),
    force: bool = typer.Option(False, "--force", "-f", help="Force remediation without confirmation"),
    playbook: Optional[str] = typer.Option(None, "--playbook", "-p", help="Specific playbook to use")
):
    """Execute remediation for a specific incident"""
    
    if not force:
        confirm = typer.confirm(f"Execute remediation for incident {incident_id}?")
        if not confirm:
            console.print("[yellow]Remediation cancelled[/yellow]")
            return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Executing remediation...", total=None)
        
        aiops = AIOpsCore()
        success = aiops.execute_remediation_by_id(incident_id, playbook)
        
        if success:
            console.print(f"[green]✅ Remediation completed for incident {incident_id}[/green]")
        else:
            console.print(f"[red]❌ Remediation failed for incident {incident_id}[/red]")
            raise typer.Exit(1)

@app.command()
def status():
    """Show system status and health"""
    
    aiops = AIOpsCore()
    status_info = aiops.get_system_status()
    
    # Create status table
    table = Table(title="AI-RecoverOps System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")
    
    for component, info in status_info.items():
        status_icon = "✅" if info['status'] == 'running' else "❌"
        status_text = f"{status_icon} {info['status'].title()}"
        
        table.add_row(
            component.replace('_', ' ').title(),
            status_text,
            info.get('details', '')
        )
    
    console.print(table)
    
    # Show configuration summary
    config_panel = Panel.fit(
        f"[cyan]Project:[/cyan] {aiops.config['project']['name']}\n"
        f"[cyan]Provider:[/cyan] {aiops.config['infrastructure']['provider']}\n"
        f"[cyan]Auto-remediation:[/cyan] {'✅' if aiops.config['remediation']['auto_remediation'] else '❌'}\n"
        f"[cyan]Services monitored:[/cyan] {len(aiops.load_services())}",
        title="📊 Configuration",
        border_style="blue"
    )
    console.print(config_panel)

@app.command()
def config(
    list_config: bool = typer.Option(False, "--list", "-l", help="List current configuration"),
    set_value: Optional[str] = typer.Option(None, "--set", "-s", help="Set configuration value (key=value)"),
    get_value: Optional[str] = typer.Option(None, "--get", "-g", help="Get configuration value"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Edit configuration file")
):
    """Manage AI-RecoverOps configuration"""
    
    aiops = AIOpsCore()
    
    if list_config:
        console.print(yaml.dump(aiops.config, default_flow_style=False))
    
    elif set_value:
        try:
            key, value = set_value.split('=', 1)
            aiops.set_config_value(key, value)
            console.print(f"[green]✅ Set {key} = {value}[/green]")
        except ValueError:
            console.print("[red]❌ Invalid format. Use key=value[/red]")
            raise typer.Exit(1)
    
    elif get_value:
        value = aiops.get_config_value(get_value)
        if value is not None:
            console.print(f"{get_value}: {value}")
        else:
            console.print(f"[red]❌ Configuration key '{get_value}' not found[/red]")
            raise typer.Exit(1)
    
    elif edit:
        import subprocess
        editor = os.environ.get('EDITOR', 'vim')
        subprocess.run([editor, str(aiops.config_file)])
    
    else:
        # Show configuration summary
        status()

@app.command()
def playbook(
    action: str = typer.Argument(..., help="Action: list, run, create, edit"),
    name: Optional[str] = typer.Argument(None, help="Playbook name"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Playbook template")
):
    """Manage remediation playbooks"""
    
    aiops = AIOpsCore()
    
    if action == "list":
        playbooks = aiops.load_playbooks()
        
        if not playbooks:
            console.print("[yellow]No playbooks found[/yellow]")
            return
        
        table = Table(title="Available Playbooks")
        table.add_column("Name", style="cyan")
        table.add_column("Triggers", style="yellow")
        table.add_column("Actions", style="green")
        table.add_column("Description", style="dim")
        
        for playbook in playbooks:
            triggers = ", ".join(playbook.get('triggers', []))
            actions = str(len(playbook.get('actions', [])))
            description = playbook.get('description', '')
            
            table.add_row(playbook['name'], triggers, actions, description)
        
        console.print(table)
    
    elif action == "run" and name:
        console.print(f"[cyan]🎭 Running playbook: {name}[/cyan]")
        success = aiops.run_playbook_by_name(name)
        
        if success:
            console.print(f"[green]✅ Playbook '{name}' completed successfully[/green]")
        else:
            console.print(f"[red]❌ Playbook '{name}' failed[/red]")
            raise typer.Exit(1)
    
    elif action == "create" and name:
        success = aiops.create_playbook(name, template)
        
        if success:
            console.print(f"[green]✅ Created playbook: {name}[/green]")
        else:
            console.print(f"[red]❌ Failed to create playbook: {name}[/red]")
            raise typer.Exit(1)
    
    else:
        console.print("[red]❌ Invalid action or missing playbook name[/red]")
        raise typer.Exit(1)

@app.command()
def logs(
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Filter by service"),
    level: Optional[str] = typer.Option(None, "--level", "-l", help="Filter by log level"),
    tail: int = typer.Option(100, "--tail", "-n", help="Number of lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output")
):
    """View system and service logs"""
    
    aiops = AIOpsCore()
    
    if follow:
        console.print("[cyan]📜 Following logs... (Press Ctrl+C to stop)[/cyan]")
        try:
            aiops.follow_logs(service=service, level=level)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped following logs[/yellow]")
    else:
        logs = aiops.get_logs(service=service, level=level, tail=tail)
        
        for log_entry in logs:
            timestamp = log_entry.get('timestamp', '')
            level_color = {
                'ERROR': 'red',
                'WARN': 'yellow',
                'INFO': 'blue',
                'DEBUG': 'dim'
            }.get(log_entry.get('level', ''), 'white')
            
            console.print(
                f"[dim]{timestamp}[/dim] "
                f"[{level_color}]{log_entry.get('level', '')}[/{level_color}] "
                f"[cyan]{log_entry.get('service', '')}[/cyan] "
                f"{log_entry.get('message', '')}"
            )

@app.command()
def version():
    """Show version information"""
    
    from . import __version__, __author__, __description__
    
    console.print(Panel.fit(
        f"[bold cyan]AI-RecoverOps[/bold cyan] v{__version__}\n"
        f"{__description__}\n\n"
        f"[dim]Created by {__author__}[/dim]",
        title="🚀 Version Info",
        border_style="cyan"
    ))

def main():
    """Main CLI entry point"""
    app()

if __name__ == "__main__":
    main()