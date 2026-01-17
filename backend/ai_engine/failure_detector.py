"""
AI-Powered Failure Detection Engine
Detects and classifies CI/CD and infrastructure failures in real-time
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from database.models import Incident, LogEntry, IncidentSeverity
from database.connection import get_db_session
from database.redis_client import redis_client
from config import settings

logger = logging.getLogger(__name__)

class FailureType(str, Enum):
    BUILD_FAILURE = "build_failure"
    TEST_FAILURE = "test_failure"
    DEPLOYMENT_FAILURE = "deployment_failure"
    DEPENDENCY_ERROR = "dependency_error"
    SYNTAX_ERROR = "syntax_error"
    PERMISSION_ERROR = "permission_error"
    NETWORK_ERROR = "network_error"
    RESOURCE_ERROR = "resource_error"
    TIMEOUT_ERROR = "timeout_error"
    CONFIGURATION_ERROR = "configuration_error"
    SECURITY_ERROR = "security_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class FailurePattern:
    name: str
    pattern: str
    failure_type: FailureType
    severity: IncidentSeverity
    confidence: float
    description: str

class FailureDetector:
    """Advanced failure detection using pattern matching and ML"""
    
    def __init__(self):
        self.running = False
        self.patterns = self._load_failure_patterns()
        self.ml_classifier = None
        self._initialize_ml_classifier()
        
    def _load_failure_patterns(self) -> List[FailurePattern]:
        """Load predefined failure patterns"""
        return [
            # Build Failures
            FailurePattern(
                name="compilation_error",
                pattern=r"(compilation failed|compile error|syntax error|cannot find symbol)",
                failure_type=FailureType.BUILD_FAILURE,
                severity=IncidentSeverity.HIGH,
                confidence=0.9,
                description="Code compilation failure"
            ),
            FailurePattern(
                name="dependency_missing",
                pattern=r"(module not found|package not found|dependency.*not found|could not resolve)",
                failure_type=FailureType.DEPENDENCY_ERROR,
                severity=IncidentSeverity.HIGH,
                confidence=0.85,
                description="Missing dependency or package"
            ),
            
            # Test Failures
            FailurePattern(
                name="test_assertion_failure",
                pattern=r"(assertion.*failed|test.*failed|expected.*but got|AssertionError)",
                failure_type=FailureType.TEST_FAILURE,
                severity=IncidentSeverity.MEDIUM,
                confidence=0.8,
                description="Test assertion failure"
            ),
            FailurePattern(
                name="test_timeout",
                pattern=r"(test.*timeout|test.*timed out|timeout.*test)",
                failure_type=FailureType.TIMEOUT_ERROR,
                severity=IncidentSeverity.MEDIUM,
                confidence=0.85,
                description="Test execution timeout"
            ),
            
            # Deployment Failures
            FailurePattern(
                name="kubernetes_deployment_failed",
                pattern=r"(deployment.*failed|pod.*failed|container.*failed|ImagePullBackOff|CrashLoopBackOff)",
                failure_type=FailureType.DEPLOYMENT_FAILURE,
                severity=IncidentSeverity.CRITICAL,
                confidence=0.9,
                description="Kubernetes deployment failure"
            ),
            FailurePattern(
                name="docker_build_failed",
                pattern=r"(docker build.*failed|dockerfile.*error|image.*build.*failed)",
                failure_type=FailureType.BUILD_FAILURE,
                severity=IncidentSeverity.HIGH,
                confidence=0.85,
                description="Docker image build failure"
            ),
            
            # Configuration Errors
            FailurePattern(
                name="yaml_syntax_error",
                pattern=r"(yaml.*error|yml.*error|invalid.*yaml|malformed.*yaml)",
                failure_type=FailureType.SYNTAX_ERROR,
                severity=IncidentSeverity.MEDIUM,
                confidence=0.9,
                description="YAML configuration syntax error"
            ),
            FailurePattern(
                name="json_syntax_error",
                pattern=r"(json.*error|invalid.*json|malformed.*json|unexpected token)",
                failure_type=FailureType.SYNTAX_ERROR,
                severity=IncidentSeverity.MEDIUM,
                confidence=0.9,
                description="JSON configuration syntax error"
            ),
            
            # Permission Errors
            FailurePattern(
                name="permission_denied",
                pattern=r"(permission denied|access denied|forbidden|unauthorized|403)",
                failure_type=FailureType.PERMISSION_ERROR,
                severity=IncidentSeverity.HIGH,
                confidence=0.85,
                description="Permission or access denied"
            ),
            FailurePattern(
                name="aws_credentials_error",
                pattern=r"(aws.*credentials|access key|secret key|token.*expired|InvalidAccessKeyId)",
                failure_type=FailureType.SECURITY_ERROR,
                severity=IncidentSeverity.CRITICAL,
                confidence=0.9,
                description="AWS credentials or authentication error"
            ),
            
            # Network Errors
            FailurePattern(
                name="connection_timeout",
                pattern=r"(connection.*timeout|network.*timeout|timeout.*connection|timed out)",
                failure_type=FailureType.NETWORK_ERROR,
                severity=IncidentSeverity.MEDIUM,
                confidence=0.8,
                description="Network connection timeout"
            ),
            FailurePattern(
                name="dns_resolution_failed",
                pattern=r"(dns.*resolution.*failed|name.*not.*resolved|host.*not.*found)",
                failure_type=FailureType.NETWORK_ERROR,
                severity=IncidentSeverity.MEDIUM,
                confidence=0.85,
                description="DNS resolution failure"
            ),
            
            # Resource Errors
            FailurePattern(
                name="out_of_memory",
                pattern=r"(out of memory|oom|memory.*exceeded|killed.*memory)",
                failure_type=FailureType.RESOURCE_ERROR,
                severity=IncidentSeverity.HIGH,
                confidence=0.9,
                description="Out of memory error"
            ),
            FailurePattern(
                name="disk_space_full",
                pattern=r"(no space left|disk.*full|storage.*full|quota.*exceeded)",
                failure_type=FailureType.RESOURCE_ERROR,
                severity=IncidentSeverity.HIGH,
                confidence=0.9,
                description="Disk space exhausted"
            ),
        ]
    
    def _initialize_ml_classifier(self):
        """Initialize ML-based failure classifier"""
        try:
            # In production, load a trained model
            # For now, use rule-based classification
            logger.info("ML classifier initialized (rule-based)")
        except Exception as e:
            logger.error(f"Failed to initialize ML classifier: {e}")
    
    async def start(self):
        """Start the failure detection service"""
        self.running = True
        logger.info("🔍 Starting Failure Detection Engine")
        
        while self.running:
            try:
                await self._process_pending_logs()
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in failure detection loop: {e}")
                await asyncio.sleep(10)
    
    async def stop(self):
        """Stop the failure detection service"""
        self.running = False
        logger.info("🛑 Stopping Failure Detection Engine")
    
    def is_healthy(self) -> bool:
        """Check if the failure detector is healthy"""
        return self.running
    
    async def _process_pending_logs(self):
        """Process pending log entries for failure detection"""
        try:
            # Get unprocessed log entries from Redis queue
            log_entries = await self._get_pending_logs()
            
            for log_entry in log_entries:
                await self._analyze_log_entry(log_entry)
                
        except Exception as e:
            logger.error(f"Error processing pending logs: {e}")
    
    async def _get_pending_logs(self) -> List[Dict]:
        """Get pending log entries from Redis queue"""
        try:
            # Pop log entries from Redis queue
            logs = []
            for _ in range(100):  # Process up to 100 logs at once
                log_data = await redis_client.lpop("log_queue")
                if not log_data:
                    break
                
                import json
                logs.append(json.loads(log_data))
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting pending logs: {e}")
            return []
    
    async def _analyze_log_entry(self, log_data: Dict):
        """Analyze a single log entry for failures"""
        try:
            message = log_data.get("message", "")
            level = log_data.get("level", "INFO")
            
            # Skip non-error logs unless they contain failure patterns
            if level not in ["ERROR", "FATAL", "WARN"] and not self._contains_failure_keywords(message):
                return
            
            # Pattern-based detection
            failure_info = await self._detect_failure_patterns(message, log_data)
            
            if failure_info:
                await self._create_incident(log_data, failure_info)
                
        except Exception as e:
            logger.error(f"Error analyzing log entry: {e}")
    
    def _contains_failure_keywords(self, message: str) -> bool:
        """Check if message contains failure-related keywords"""
        failure_keywords = [
            "failed", "error", "exception", "timeout", "denied", "refused",
            "crashed", "killed", "abort", "panic", "fatal", "critical"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in failure_keywords)
    
    async def _detect_failure_patterns(self, message: str, log_data: Dict) -> Optional[Dict]:
        """Detect failure patterns in log message"""
        try:
            best_match = None
            highest_confidence = 0.0
            
            for pattern in self.patterns:
                if re.search(pattern.pattern, message, re.IGNORECASE):
                    if pattern.confidence > highest_confidence:
                        highest_confidence = pattern.confidence
                        best_match = pattern
            
            if best_match:
                return {
                    "failure_type": best_match.failure_type,
                    "severity": best_match.severity,
                    "confidence": best_match.confidence,
                    "description": best_match.description,
                    "pattern_name": best_match.name
                }
            
            # Fallback to ML classification
            return await self._ml_classify_failure(message, log_data)
            
        except Exception as e:
            logger.error(f"Error detecting failure patterns: {e}")
            return None
    
    async def _ml_classify_failure(self, message: str, log_data: Dict) -> Optional[Dict]:
        """Use ML to classify failure type"""
        try:
            # Simplified ML classification based on keywords and context
            message_lower = message.lower()
            
            # Build-related failures
            if any(word in message_lower for word in ["build", "compile", "maven", "gradle", "npm"]):
                return {
                    "failure_type": FailureType.BUILD_FAILURE,
                    "severity": IncidentSeverity.HIGH,
                    "confidence": 0.7,
                    "description": "Build process failure detected",
                    "pattern_name": "ml_build_failure"
                }
            
            # Test-related failures
            if any(word in message_lower for word in ["test", "spec", "junit", "pytest", "mocha"]):
                return {
                    "failure_type": FailureType.TEST_FAILURE,
                    "severity": IncidentSeverity.MEDIUM,
                    "confidence": 0.7,
                    "description": "Test execution failure detected",
                    "pattern_name": "ml_test_failure"
                }
            
            # Deployment-related failures
            if any(word in message_lower for word in ["deploy", "kubernetes", "docker", "container"]):
                return {
                    "failure_type": FailureType.DEPLOYMENT_FAILURE,
                    "severity": IncidentSeverity.HIGH,
                    "confidence": 0.7,
                    "description": "Deployment failure detected",
                    "pattern_name": "ml_deployment_failure"
                }
            
            # Generic error classification
            if log_data.get("level") in ["ERROR", "FATAL"]:
                return {
                    "failure_type": FailureType.UNKNOWN_ERROR,
                    "severity": IncidentSeverity.MEDIUM,
                    "confidence": 0.5,
                    "description": "Unknown error detected",
                    "pattern_name": "ml_unknown_error"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in ML classification: {e}")
            return None
    
    async def _create_incident(self, log_data: Dict, failure_info: Dict):
        """Create a new incident from detected failure"""
        try:
            # Check if similar incident already exists
            existing_incident = await self._find_similar_incident(log_data, failure_info)
            if existing_incident:
                logger.info(f"Similar incident already exists: {existing_incident}")
                return
            
            async with get_db_session() as session:
                incident = Incident(
                    title=f"{failure_info['failure_type'].replace('_', ' ').title()} in {log_data.get('source_id', 'Unknown')}",
                    description=failure_info['description'],
                    status="detected",
                    severity=failure_info['severity'],
                    source_type=log_data.get('source_type'),
                    source_id=log_data.get('source_id'),
                    repository=log_data.get('repository'),
                    branch=log_data.get('branch'),
                    commit_sha=log_data.get('commit_sha'),
                    failure_type=failure_info['failure_type'],
                    error_message=log_data.get('message'),
                    confidence_score=failure_info['confidence'],
                    analysis_data={
                        "pattern_name": failure_info['pattern_name'],
                        "log_data": log_data,
                        "detection_method": "pattern_matching"
                    }
                )
                
                session.add(incident)
                await session.commit()
                
                logger.info(f"✅ Created incident: {incident.id} - {incident.title}")
                
                # Notify other services about new incident
                await self._notify_incident_created(incident)
                
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
    
    async def _find_similar_incident(self, log_data: Dict, failure_info: Dict) -> Optional[str]:
        """Find similar existing incidents to avoid duplicates"""
        try:
            async with get_db_session() as session:
                # Look for incidents in the last hour with same failure type and source
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                
                from sqlalchemy import and_
                similar_incident = await session.execute(
                    session.query(Incident).filter(
                        and_(
                            Incident.failure_type == failure_info['failure_type'],
                            Incident.source_id == log_data.get('source_id'),
                            Incident.detected_at > cutoff_time,
                            Incident.status.in_(["detected", "analyzing", "fixing"])
                        )
                    ).first()
                )
                
                return similar_incident.id if similar_incident else None
                
        except Exception as e:
            logger.error(f"Error finding similar incidents: {e}")
            return None
    
    async def _notify_incident_created(self, incident: Incident):
        """Notify other services about new incident"""
        try:
            # Add to Redis queue for root cause analysis
            incident_data = {
                "incident_id": str(incident.id),
                "failure_type": incident.failure_type,
                "severity": incident.severity,
                "message": incident.error_message,
                "created_at": incident.created_at.isoformat()
            }
            
            import json
            await redis_client.rpush("incident_queue", json.dumps(incident_data))
            
            logger.info(f"📢 Notified services about incident: {incident.id}")
            
        except Exception as e:
            logger.error(f"Error notifying incident created: {e}")
    
    async def detect_failure_from_webhook(self, webhook_data: Dict) -> Optional[str]:
        """Detect failure from webhook payload"""
        try:
            # Extract relevant information from webhook
            if webhook_data.get("action") == "completed" and webhook_data.get("conclusion") == "failure":
                # GitHub Actions failure
                failure_info = {
                    "failure_type": FailureType.BUILD_FAILURE,
                    "severity": IncidentSeverity.HIGH,
                    "confidence": 0.9,
                    "description": "GitHub Actions workflow failed",
                    "pattern_name": "webhook_github_failure"
                }
                
                log_data = {
                    "source_type": "github",
                    "source_id": webhook_data.get("workflow_run", {}).get("id"),
                    "repository": webhook_data.get("repository", {}).get("full_name"),
                    "branch": webhook_data.get("workflow_run", {}).get("head_branch"),
                    "commit_sha": webhook_data.get("workflow_run", {}).get("head_sha"),
                    "message": f"Workflow failed: {webhook_data.get('workflow_run', {}).get('name')}",
                    "level": "ERROR"
                }
                
                await self._create_incident(log_data, failure_info)
                return "incident_created"
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting failure from webhook: {e}")
            return None