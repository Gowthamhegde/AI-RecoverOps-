"""
Network connectivity and infrastructure detector for DevOps
"""

import asyncio
import socket
import uuid
from datetime import datetime
from typing import List, Dict, Any
from ..core.detector import BaseDetector
from ..core.models import Issue
from ..utils.logger import get_logger

class NetworkDetector(BaseDetector):
    """Detects network and connectivity issues"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Network thresholds
        self.ping_timeout = 5.0
        self.port_timeout = 3.0
        
    async def initialize(self):
        """Initialize network detector"""
        self.logger.info("Initializing Network Detector for DevOps")
        
    async def detect(self) -> List[Issue]:
        """Detect network connectivity issues"""
        issues = []
        
        # Check critical endpoints
        endpoints = self.config.get('network', {}).get('critical_endpoints', [])
        for endpoint in endpoints:
            connectivity_issues = await self._check_endpoint_connectivity(endpoint)
            issues.extend(connectivity_issues)
            
        # Check load balancer health
        lb_issues = await self._check_load_balancer_health()
        issues.extend(lb_issues)
        
        # Check DNS resolution
        dns_issues = await self._check_dns_resolution()
        issues.extend(dns_issues)
        
        return issues
        
    async def _check_endpoint_connectivity(self, endpoint: Dict[str, Any]) -> List[Issue]:
        """Check connectivity to critical endpoints"""
        issues = []
        host = endpoint.get('host')
        port = endpoint.get('port')
        name = endpoint.get('name', f"{host}:{port}")
        
        if not host or not port:
            return issues
            
        try:
            # Test TCP connectivity
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=self.port_timeout)
            writer.close()
            await writer.wait_closed()
            
        except asyncio.TimeoutError:
            issues.append(Issue(
                id=f"network-timeout-{uuid.uuid4().hex[:8]}",
                type="network",
                severity="high",
                description=f"Connection timeout to {name}",
                metadata={
                    "endpoint_name": name,
                    "host": host,
                    "port": port,
                    "timeout_seconds": self.port_timeout
                },
                detected_at=datetime.now(),
                source="network_detector"
            ))
        except ConnectionRefusedError:
            issues.append(Issue(
                id=f"network-refused-{uuid.uuid4().hex[:8]}",
                type="network",
                severity="critical",
                description=f"Connection refused to {name}",
                metadata={
                    "endpoint_name": name,
                    "host": host,
                    "port": port
                },
                detected_at=datetime.now(),
                source="network_detector"
            ))
        except Exception as e:
            issues.append(Issue(
                id=f"network-error-{uuid.uuid4().hex[:8]}",
                type="network",
                severity="high",
                description=f"Network error connecting to {name}: {str(e)}",
                metadata={
                    "endpoint_name": name,
                    "host": host,
                    "port": port,
                    "error": str(e)
                },
                detected_at=datetime.now(),
                source="network_detector"
            ))
            
        return issues
        
    async def _check_load_balancer_health(self) -> List[Issue]:
        """Check load balancer and ingress health"""
        issues = []
        
        # Check HAProxy stats (if configured)
        haproxy_stats = self.config.get('network', {}).get('haproxy_stats_url')
        if haproxy_stats:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(haproxy_stats, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status != 200:
                            issues.append(Issue(
                                id=f"lb-stats-{uuid.uuid4().hex[:8]}",
                                type="network",
                                severity="medium",
                                description=f"Load balancer stats unavailable: HTTP {response.status}",
                                metadata={
                                    "stats_url": haproxy_stats,
                                    "status_code": response.status
                                },
                                detected_at=datetime.now(),
                                source="network_detector"
                            ))
            except Exception as e:
                issues.append(Issue(
                    id=f"lb-unreachable-{uuid.uuid4().hex[:8]}",
                    type="network",
                    severity="high",
                    description=f"Load balancer stats unreachable: {str(e)}",
                    metadata={
                        "stats_url": haproxy_stats,
                        "error": str(e)
                    },
                    detected_at=datetime.now(),
                    source="network_detector"
                ))
                
        return issues
        
    async def _check_dns_resolution(self) -> List[Issue]:
        """Check DNS resolution for critical domains"""
        issues = []
        
        critical_domains = self.config.get('network', {}).get('critical_domains', [])
        for domain in critical_domains:
            try:
                # Test DNS resolution
                loop = asyncio.get_event_loop()
                await loop.getaddrinfo(domain, None)
                
            except socket.gaierror as e:
                issues.append(Issue(
                    id=f"dns-resolution-{uuid.uuid4().hex[:8]}",
                    type="network",
                    severity="high",
                    description=f"DNS resolution failed for {domain}",
                    metadata={
                        "domain": domain,
                        "error": str(e)
                    },
                    detected_at=datetime.now(),
                    source="network_detector"
                ))
            except Exception as e:
                issues.append(Issue(
                    id=f"dns-error-{uuid.uuid4().hex[:8]}",
                    type="network",
                    severity="medium",
                    description=f"DNS check error for {domain}: {str(e)}",
                    metadata={
                        "domain": domain,
                        "error": str(e)
                    },
                    detected_at=datetime.now(),
                    source="network_detector"
                ))
                
        return issues
        
    def get_detector_type(self) -> str:
        return "network"