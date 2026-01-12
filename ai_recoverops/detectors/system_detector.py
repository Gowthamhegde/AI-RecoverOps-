"""
System-level issue detector (CPU, Memory, Disk, etc.)
"""

import psutil
import uuid
from datetime import datetime
from typing import List
from ..core.detector import BaseDetector
from ..core.engine import Issue
from ..utils.logger import get_logger

class SystemDetector(BaseDetector):
    """Detects system resource issues"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Thresholds
        self.cpu_threshold = 85.0
        self.memory_threshold = 90.0
        self.disk_threshold = 95.0
        
    async def initialize(self):
        """Initialize system detector"""
        self.logger.info("Initializing System Detector")
        
    async def detect(self) -> List[Issue]:
        """Detect system resource issues"""
        issues = []
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.cpu_threshold:
            issues.append(Issue(
                id=f"cpu-{uuid.uuid4().hex[:8]}",
                type="system",
                severity="high" if cpu_percent > 95 else "medium",
                description=f"High CPU usage detected: {cpu_percent:.1f}%",
                metadata={
                    "cpu_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                    "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                detected_at=datetime.now(),
                source="system_detector"
            ))
            
        # Memory Usage
        memory = psutil.virtual_memory()
        if memory.percent > self.memory_threshold:
            issues.append(Issue(
                id=f"memory-{uuid.uuid4().hex[:8]}",
                type="system",
                severity="high" if memory.percent > 95 else "medium",
                description=f"High memory usage detected: {memory.percent:.1f}%",
                metadata={
                    "memory_percent": memory.percent,
                    "memory_total": memory.total,
                    "memory_available": memory.available,
                    "memory_used": memory.used
                },
                detected_at=datetime.now(),
                source="system_detector"
            ))
            
        # Disk Usage
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > self.disk_threshold:
                    issues.append(Issue(
                        id=f"disk-{uuid.uuid4().hex[:8]}",
                        type="system",
                        severity="critical" if usage.percent > 98 else "high",
                        description=f"High disk usage on {partition.mountpoint}: {usage.percent:.1f}%",
                        metadata={
                            "disk_percent": usage.percent,
                            "disk_total": usage.total,
                            "disk_free": usage.free,
                            "disk_used": usage.used,
                            "mountpoint": partition.mountpoint
                        },
                        detected_at=datetime.now(),
                        source="system_detector"
                    ))
            except PermissionError:
                continue
                
        return issues
        
    def get_detector_type(self) -> str:
        return "system"