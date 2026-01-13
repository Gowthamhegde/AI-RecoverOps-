"""
Application-level issue detector for DevOps environments
"""

import asyncio
import aiohttp
import uuid
from datetime import datetime
from typing import List, Dict, Any
from ..core.detector import BaseDetector
from ..core.models import Issue
from ..utils.logger import get_logger

class ApplicationDetector(BaseDetector):
    """Detects application and service issues"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # DevOps-specific thresholds
        self.response_time_threshold = 5000  # ms
        self.error_rate_threshold = 5.0  # %
        self.availability_threshold = 99.0  # %
        
    async def initialize(self):
        """Initialize application detector"""
        self.logger.info("Initializing Application Detector for DevOps")
        
    async def detect(self) -> List[Issue]:
        """Detect application and service issues"""
        issues = []
        
        # Check service health endpoints
        services = self.config.get('services', {})
        for service_name, service_config in services.items():
            health_issues = await self._check_service_health(service_name, service_config)
            issues.extend(health_issues)
            
        # Check container health (Docker/K8s)
        container_issues = await self._check_container_health()
        issues.extend(container_issues)
        
        # Check deployment status
        deployment_issues = await self._check_deployment_status()
        issues.extend(deployment_issues)
        
        return issues
        
    async def _check_service_health(self, service_name: str, config: Dict[str, Any]) -> List[Issue]:
        """Check individual service health"""
        issues = []
        health_url = config.get('health_endpoint')
        
        if not health_url:
            return issues
            
        try:
            async with aiohttp.ClientSession() as session:
                start_time = asyncio.get_event_loop().time()
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    # Check response time
                    if response_time > self.response_time_threshold:
                        issues.append(Issue(
                            id=f"service-latency-{uuid.uuid4().hex[:8]}",
                            type="application",
                            severity="medium",
                            description=f"High response time for {service_name}: {response_time:.0f}ms",
                            metadata={
                                "service_name": service_name,
                                "response_time_ms": response_time,
                                "threshold_ms": self.response_time_threshold,
                                "endpoint": health_url
                            },
                            detected_at=datetime.now(),
                            source="application_detector"
                        ))
                    
                    # Check HTTP status
                    if response.status >= 500:
                        issues.append(Issue(
                            id=f"service-error-{uuid.uuid4().hex[:8]}",
                            type="application",
                            severity="high",
                            description=f"Service {service_name} returning {response.status}",
                            metadata={
                                "service_name": service_name,
                                "status_code": response.status,
                                "endpoint": health_url
                            },
                            detected_at=datetime.now(),
                            source="application_detector"
                        ))
                        
        except asyncio.TimeoutError:
            issues.append(Issue(
                id=f"service-timeout-{uuid.uuid4().hex[:8]}",
                type="application",
                severity="high",
                description=f"Service {service_name} health check timeout",
                metadata={
                    "service_name": service_name,
                    "endpoint": health_url,
                    "timeout_seconds": 10
                },
                detected_at=datetime.now(),
                source="application_detector"
            ))
        except Exception as e:
            issues.append(Issue(
                id=f"service-unreachable-{uuid.uuid4().hex[:8]}",
                type="application",
                severity="critical",
                description=f"Service {service_name} unreachable: {str(e)}",
                metadata={
                    "service_name": service_name,
                    "endpoint": health_url,
                    "error": str(e)
                },
                detected_at=datetime.now(),
                source="application_detector"
            ))
            
        return issues
        
    async def _check_container_health(self) -> List[Issue]:
        """Check Docker container health"""
        issues = []
        
        try:
            # Check if Docker is available
            process = await asyncio.create_subprocess_exec(
                'docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Image}}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                lines = stdout.decode().strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            container_name = parts[0]
                            status = parts[1]
                            
                            if 'Exited' in status or 'Dead' in status:
                                issues.append(Issue(
                                    id=f"container-down-{uuid.uuid4().hex[:8]}",
                                    type="application",
                                    severity="high",
                                    description=f"Container {container_name} is not running: {status}",
                                    metadata={
                                        "container_name": container_name,
                                        "status": status,
                                        "image": parts[2] if len(parts) > 2 else "unknown"
                                    },
                                    detected_at=datetime.now(),
                                    source="application_detector"
                                ))
                                
        except Exception as e:
            self.logger.debug(f"Docker check failed: {e}")
            
        return issues
        
    async def _check_deployment_status(self) -> List[Issue]:
        """Check Kubernetes deployment status"""
        issues = []
        
        try:
            # Check kubectl availability and get deployments
            process = await asyncio.create_subprocess_exec(
                'kubectl', 'get', 'deployments', '-o', 'json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                import json
                deployments = json.loads(stdout.decode())
                
                for deployment in deployments.get('items', []):
                    name = deployment['metadata']['name']
                    status = deployment.get('status', {})
                    
                    replicas = status.get('replicas', 0)
                    ready_replicas = status.get('readyReplicas', 0)
                    
                    if ready_replicas < replicas:
                        issues.append(Issue(
                            id=f"k8s-deployment-{uuid.uuid4().hex[:8]}",
                            type="application",
                            severity="medium",
                            description=f"Deployment {name} has {ready_replicas}/{replicas} replicas ready",
                            metadata={
                                "deployment_name": name,
                                "replicas": replicas,
                                "ready_replicas": ready_replicas,
                                "namespace": deployment['metadata'].get('namespace', 'default')
                            },
                            detected_at=datetime.now(),
                            source="application_detector"
                        ))
                        
        except Exception as e:
            self.logger.debug(f"Kubernetes check failed: {e}")
            
        return issues
        
    def get_detector_type(self) -> str:
        return "application"