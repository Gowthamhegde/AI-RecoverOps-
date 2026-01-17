#!/usr/bin/env python3
"""
AI-RecoverOps Demo: Failure Simulation
Simulates various DevOps failures to demonstrate AI-RecoverOps capabilities
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

import httpx
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()

class FailureSimulator:
    """Simulates various DevOps failures for demonstration"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.client = httpx.AsyncClient(base_url=api_url, timeout=30.0)
        
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def simulate_github_workflow_failure(self) -> Dict[str, Any]:
        """Simulate GitHub Actions workflow failure"""
        
        failure_scenarios = [
            {
                "name": "Build Failure - Missing Dependency",
                "error": "ModuleNotFoundError: No module named 'requests'",
                "workflow": "CI/CD Pipeline",
                "step": "Install Dependencies",
                "fix_type": "dependency_update"
            },
            {
                "name": "Test Failure - Assertion Error",
                "error": "AssertionError: Expected status 200, got 404",
                "workflow": "Test Suite",
                "step": "Run Tests",
                "fix_type": "code_fix"
            },
            {
                "name": "Docker Build Failure",
                "error": "Error building image: COPY failed: no source files were specified",
                "workflow": "Build and Deploy",
                "step": "Build Docker Image",
                "fix_type": "dockerfile_fix"
            },
            {
                "name": "Deployment Failure - Resource Limits",
                "error": "OOMKilled: Container exceeded memory limit (128Mi)",
                "workflow": "Deploy to Production",
                "step": "Deploy Application",
                "fix_type": "kubernetes_fix"
            },
            {
                "name": "Linting Failure",
                "error": "flake8: E302 expected 2 blank lines, found 1",
                "workflow": "Code Quality Check",
                "step": "Run Linter",
                "fix_type": "code_fix"
            }
        ]
        
        scenario = random.choice(failure_scenarios)
        
        # Create GitHub webhook payload
        payload = {
            "action": "completed",
            "workflow_run": {
                "id": f"demo_{int(time.time())}",
                "name": scenario["workflow"],
                "status": "completed",
                "conclusion": "failure",
                "head_branch": "main",
                "head_sha": f"abc{random.randint(100, 999)}def{random.randint(100, 999)}",
                "html_url": f"https://github.com/demo/repo/actions/runs/{random.randint(1000, 9999)}",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "jobs_url": "https://api.github.com/repos/demo/repo/actions/runs/123/jobs"
            },
            "repository": {
                "full_name": "demo/ai-recoverops-test",
                "html_url": "https://github.com/demo/ai-recoverops-test"
            }
        }
        
        # Send webhook
        response = await self.client.post(
            "/webhooks/github",
            json=payload,
            headers={"X-GitHub-Event": "workflow_run"}
        )
        
        # Also simulate log entry with detailed error
        log_payload = {
            "source_type": "github",
            "source_id": payload["workflow_run"]["id"],
            "repository": "demo/ai-recoverops-test",
            "branch": "main",
            "commit_sha": payload["workflow_run"]["head_sha"],
            "message": f"{scenario['step']}: {scenario['error']}",
            "level": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "workflow_name": scenario["workflow"],
                "step_name": scenario["step"],
                "failure_type": scenario["fix_type"],
                "scenario": scenario["name"]
            }
        }
        
        # Send to log processing queue
        await self.client.post("/api/test/process-log", json=log_payload)
        
        return {
            "scenario": scenario,
            "workflow_id": payload["workflow_run"]["id"],
            "status": "simulated"
        }
    
    async def simulate_kubernetes_pod_failure(self) -> Dict[str, Any]:
        """Simulate Kubernetes pod failure"""
        
        k8s_scenarios = [
            {
                "name": "Pod OOMKilled",
                "error": "Pod myapp-deployment-abc123 killed due to OOMKilled",
                "reason": "OOMKilled",
                "exit_code": 137,
                "fix_type": "increase_memory_limit"
            },
            {
                "name": "Image Pull Failure",
                "error": "Failed to pull image 'myapp:v1.2.3': ImagePullBackOff",
                "reason": "ImagePullBackOff",
                "exit_code": 125,
                "fix_type": "fix_image_config"
            },
            {
                "name": "CrashLoopBackOff",
                "error": "Pod myapp-deployment-xyz789 in CrashLoopBackOff state",
                "reason": "CrashLoopBackOff",
                "exit_code": 1,
                "fix_type": "fix_application_config"
            },
            {
                "name": "Persistent Volume Mount Failure",
                "error": "Unable to mount volume: permission denied",
                "reason": "FailedMount",
                "exit_code": 32,
                "fix_type": "fix_volume_permissions"
            }
        ]
        
        scenario = random.choice(k8s_scenarios)
        pod_name = f"myapp-deployment-{random.randint(100000, 999999)}"
        
        log_payload = {
            "source_type": "kubernetes",
            "source_id": f"k8s_failure_{int(time.time())}",
            "message": scenario["error"],
            "level": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "namespace": "production",
                "pod_name": pod_name,
                "container": "myapp",
                "reason": scenario["reason"],
                "exit_code": scenario["exit_code"],
                "node": f"node-{random.randint(1, 5)}",
                "scenario": scenario["name"]
            }
        }
        
        await self.client.post("/api/test/process-log", json=log_payload)
        
        return {
            "scenario": scenario,
            "pod_name": pod_name,
            "status": "simulated"
        }
    
    async def simulate_aws_resource_failure(self) -> Dict[str, Any]:
        """Simulate AWS resource failure"""
        
        aws_scenarios = [
            {
                "name": "EC2 Instance Stopped",
                "error": "EC2 instance i-1234567890abcdef0 is in stopped state",
                "resource_type": "ec2",
                "resource_id": f"i-{random.randint(1000000000, 9999999999):010x}",
                "fix_type": "restart_instance"
            },
            {
                "name": "ECS Service Failure",
                "error": "ECS service 'myapp-service' has 0 running tasks",
                "resource_type": "ecs",
                "resource_id": f"myapp-service-{random.randint(100, 999)}",
                "fix_type": "restart_ecs_service"
            },
            {
                "name": "Lambda Function Error",
                "error": "Lambda function 'data-processor' failed with timeout",
                "resource_type": "lambda",
                "resource_id": f"data-processor-{random.randint(100, 999)}",
                "fix_type": "increase_lambda_timeout"
            },
            {
                "name": "RDS Connection Failure",
                "error": "Unable to connect to RDS instance: connection timeout",
                "resource_type": "rds",
                "resource_id": f"myapp-db-{random.randint(100, 999)}",
                "fix_type": "restart_rds_instance"
            }
        ]
        
        scenario = random.choice(aws_scenarios)
        
        log_payload = {
            "source_type": "aws",
            "source_id": f"aws_failure_{int(time.time())}",
            "message": scenario["error"],
            "level": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "resource_type": scenario["resource_type"],
                "resource_id": scenario["resource_id"],
                "region": "us-east-1",
                "account_id": "123456789012",
                "scenario": scenario["name"]
            }
        }
        
        await self.client.post("/api/test/process-log", json=log_payload)
        
        return {
            "scenario": scenario,
            "resource_id": scenario["resource_id"],
            "status": "simulated"
        }
    
    async def simulate_database_failure(self) -> Dict[str, Any]:
        """Simulate database failure"""
        
        db_scenarios = [
            {
                "name": "Connection Pool Exhausted",
                "error": "FATAL: remaining connection slots are reserved for non-replication superuser connections",
                "fix_type": "increase_max_connections"
            },
            {
                "name": "Slow Query Performance",
                "error": "Query execution time exceeded 30 seconds",
                "fix_type": "optimize_query_performance"
            },
            {
                "name": "Disk Space Full",
                "error": "ERROR: could not extend file: No space left on device",
                "fix_type": "increase_storage_space"
            },
            {
                "name": "Deadlock Detected",
                "error": "ERROR: deadlock detected - process terminated",
                "fix_type": "optimize_transaction_handling"
            }
        ]
        
        scenario = random.choice(db_scenarios)
        
        log_payload = {
            "source_type": "database",
            "source_id": f"db_failure_{int(time.time())}",
            "message": scenario["error"],
            "level": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "database_name": "myapp_production",
                "host": "db.example.com",
                "port": 5432,
                "scenario": scenario["name"]
            }
        }
        
        await self.client.post("/api/test/process-log", json=log_payload)
        
        return {
            "scenario": scenario,
            "status": "simulated"
        }
    
    async def monitor_incident_resolution(self, incident_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Monitor incident resolution progress"""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = await self.client.get(f"/api/incidents/{incident_id}")
                if response.status_code == 200:
                    incident = response.json()
                    
                    if incident["status"] in ["resolved", "failed", "rolled_back"]:
                        # Get remediation details
                        remediations_response = await self.client.get(f"/api/incidents/{incident_id}/remediations")
                        remediations = remediations_response.json() if remediations_response.status_code == 200 else []
                        
                        return {
                            "incident": incident,
                            "remediations": remediations,
                            "resolution_time": time.time() - start_time,
                            "status": "completed"
                        }
                
                await asyncio.sleep(5)
                
            except Exception as e:
                console.print(f"[red]Error monitoring incident: {e}[/red]")
                await asyncio.sleep(5)
        
        return {"status": "timeout", "resolution_time": timeout}

@click.group()
def cli():
    """AI-RecoverOps Demo: Failure Simulation"""
    pass

@cli.command()
@click.option('--api-url', default='http://localhost:8000', help='AI-RecoverOps API URL')
@click.option('--count', default=1, help='Number of failures to simulate')
@click.option('--type', 'failure_type', 
              type=click.Choice(['github', 'kubernetes', 'aws', 'database', 'all']),
              default='all', help='Type of failure to simulate')
@click.option('--monitor', is_flag=True, help='Monitor incident resolution')
async def simulate(api_url: str, count: int, failure_type: str, monitor: bool):
    """Simulate DevOps failures"""
    
    console.print(Panel.fit(
        "[bold blue]AI-RecoverOps Failure Simulation Demo[/bold blue]\n"
        f"API URL: {api_url}\n"
        f"Simulating {count} failure(s) of type: {failure_type}",
        title="🚀 Demo Starting"
    ))
    
    simulator = FailureSimulator(api_url)
    
    try:
        # Check API health
        health_response = await simulator.client.get("/health")
        if health_response.status_code != 200:
            console.print("[red]❌ AI-RecoverOps API is not healthy![/red]")
            return
        
        console.print("[green]✅ AI-RecoverOps API is healthy[/green]")
        
        simulated_failures = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            for i in range(count):
                task = progress.add_task(f"Simulating failure {i+1}/{count}...", total=None)
                
                # Choose failure type
                if failure_type == 'all':
                    chosen_type = random.choice(['github', 'kubernetes', 'aws', 'database'])
                else:
                    chosen_type = failure_type
                
                # Simulate failure
                if chosen_type == 'github':
                    result = await simulator.simulate_github_workflow_failure()
                elif chosen_type == 'kubernetes':
                    result = await simulator.simulate_kubernetes_pod_failure()
                elif chosen_type == 'aws':
                    result = await simulator.simulate_aws_resource_failure()
                elif chosen_type == 'database':
                    result = await simulator.simulate_database_failure()
                
                result['type'] = chosen_type
                simulated_failures.append(result)
                
                progress.update(task, description=f"✅ Simulated {result['scenario']['name']}")
                
                # Wait between simulations
                if i < count - 1:
                    await asyncio.sleep(2)
        
        # Display results
        table = Table(title="Simulated Failures")
        table.add_column("Type", style="cyan")
        table.add_column("Scenario", style="yellow")
        table.add_column("Status", style="green")
        
        for failure in simulated_failures:
            table.add_row(
                failure['type'].title(),
                failure['scenario']['name'],
                failure['status'].title()
            )
        
        console.print(table)
        
        if monitor:
            console.print("\n[blue]🔍 Monitoring incident resolution...[/blue]")
            
            # Wait for incidents to be created
            await asyncio.sleep(10)
            
            # Get recent incidents
            incidents_response = await simulator.client.get("/api/incidents?limit=10")
            if incidents_response.status_code == 200:
                incidents = incidents_response.json()
                
                # Monitor each incident
                for incident in incidents[:count]:
                    console.print(f"\n📋 Monitoring incident: {incident['title']}")
                    
                    result = await simulator.monitor_incident_resolution(incident['id'])
                    
                    if result['status'] == 'completed':
                        console.print(f"✅ Resolved in {result['resolution_time']:.1f} seconds")
                        console.print(f"   Status: {result['incident']['status']}")
                        console.print(f"   Root Cause: {result['incident']['root_cause']}")
                        
                        if result['remediations']:
                            console.print(f"   Remediations Applied: {len(result['remediations'])}")
                    else:
                        console.print(f"⏰ Monitoring timeout after {result['resolution_time']} seconds")
        
        console.print("\n[green]🎉 Demo completed successfully![/green]")
        console.print("\n💡 Check the AI-RecoverOps dashboard at http://localhost:3000 to see the incidents and their resolution!")
        
    except Exception as e:
        console.print(f"[red]❌ Demo failed: {e}[/red]")
    finally:
        await simulator.close()

@cli.command()
@click.option('--api-url', default='http://localhost:8000', help='AI-RecoverOps API URL')
async def status(api_url: str):
    """Check AI-RecoverOps system status"""
    
    simulator = FailureSimulator(api_url)
    
    try:
        # Get system status
        health_response = await simulator.client.get("/health")
        status_response = await simulator.client.get("/api/system-status")
        incidents_response = await simulator.client.get("/api/incidents?limit=5")
        
        # Display health
        if health_response.status_code == 200:
            health_data = health_response.json()
            console.print(f"[green]✅ System Health: {health_data['status']}[/green]")
        else:
            console.print("[red]❌ System Health: Unhealthy[/red]")
        
        # Display status
        if status_response.status_code == 200:
            status_data = status_response.json()
            
            table = Table(title="System Status")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="yellow")
            
            table.add_row("Active Incidents", str(status_data.get('active_incidents', 0)))
            table.add_row("Resolved Today", str(status_data.get('resolved_today', 0)))
            table.add_row("Success Rate", f"{status_data.get('success_rate', 0):.1f}%")
            table.add_row("Avg Resolution Time", f"{status_data.get('avg_resolution_time', 0)} min")
            
            console.print(table)
        
        # Display recent incidents
        if incidents_response.status_code == 200:
            incidents = incidents_response.json()
            
            if incidents:
                incident_table = Table(title="Recent Incidents")
                incident_table.add_column("Title", style="cyan")
                incident_table.add_column("Status", style="yellow")
                incident_table.add_column("Severity", style="red")
                incident_table.add_column("Detected", style="green")
                
                for incident in incidents:
                    incident_table.add_row(
                        incident['title'][:50] + "..." if len(incident['title']) > 50 else incident['title'],
                        incident['status'],
                        incident['severity'],
                        incident['detected_at'][:19]  # Remove microseconds
                    )
                
                console.print(incident_table)
            else:
                console.print("[green]No recent incidents[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to get status: {e}[/red]")
    finally:
        await simulator.close()

@cli.command()
@click.option('--api-url', default='http://localhost:8000', help='AI-RecoverOps API URL')
@click.option('--duration', default=300, help='Demo duration in seconds')
async def continuous(api_url: str, duration: int):
    """Run continuous failure simulation"""
    
    console.print(Panel.fit(
        f"[bold blue]Continuous Failure Simulation[/bold blue]\n"
        f"Duration: {duration} seconds\n"
        f"Simulating realistic DevOps failures...",
        title="🔄 Continuous Demo"
    ))
    
    simulator = FailureSimulator(api_url)
    start_time = time.time()
    failure_count = 0
    
    try:
        while time.time() - start_time < duration:
            # Random delay between failures (30-120 seconds)
            delay = random.randint(30, 120)
            
            console.print(f"[blue]⏳ Waiting {delay} seconds before next failure...[/blue]")
            await asyncio.sleep(delay)
            
            # Simulate random failure
            failure_types = ['github', 'kubernetes', 'aws', 'database']
            chosen_type = random.choice(failure_types)
            
            console.print(f"[yellow]🚨 Simulating {chosen_type} failure...[/yellow]")
            
            if chosen_type == 'github':
                result = await simulator.simulate_github_workflow_failure()
            elif chosen_type == 'kubernetes':
                result = await simulator.simulate_kubernetes_pod_failure()
            elif chosen_type == 'aws':
                result = await simulator.simulate_aws_resource_failure()
            elif chosen_type == 'database':
                result = await simulator.simulate_database_failure()
            
            failure_count += 1
            console.print(f"[green]✅ Simulated failure #{failure_count}: {result['scenario']['name']}[/green]")
            
            # Check if we should continue
            if time.time() - start_time >= duration:
                break
        
        console.print(f"\n[green]🎉 Continuous demo completed![/green]")
        console.print(f"Total failures simulated: {failure_count}")
        console.print(f"Duration: {duration} seconds")
        
    except KeyboardInterrupt:
        console.print(f"\n[yellow]⏹️  Demo stopped by user[/yellow]")
        console.print(f"Failures simulated: {failure_count}")
    except Exception as e:
        console.print(f"[red]❌ Demo failed: {e}[/red]")
    finally:
        await simulator.close()

if __name__ == "__main__":
    # Run async CLI
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Convert sync click commands to async
    def async_command(f):
        def wrapper(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))
        return wrapper
    
    # Apply async wrapper to commands
    simulate.callback = async_command(simulate.callback)
    status.callback = async_command(status.callback)
    continuous.callback = async_command(continuous.callback)
    
    cli()