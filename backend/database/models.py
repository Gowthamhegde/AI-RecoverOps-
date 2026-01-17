"""
AI-RecoverOps Database Models
SQLAlchemy ORM models for all entities
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class IncidentStatus(str, Enum):
    DETECTED = "detected"
    ANALYZING = "analyzing"
    FIXING = "fixing"
    RESOLVED = "resolved"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PipelineStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class RemediationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class Incident(Base):
    """Core incident tracking model"""
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default=IncidentStatus.DETECTED)
    severity = Column(String(20), default=IncidentSeverity.MEDIUM)
    
    # Source information
    source_type = Column(String(50))  # github, gitlab, jenkins, aws, k8s
    source_id = Column(String(255))   # pipeline_id, job_id, etc.
    repository = Column(String(255))
    branch = Column(String(100))
    commit_sha = Column(String(40))
    
    # Failure details
    failure_type = Column(String(100))
    error_message = Column(Text)
    log_snippet = Column(Text)
    stack_trace = Column(Text)
    
    # AI Analysis
    root_cause = Column(Text)
    confidence_score = Column(Float)
    analysis_data = Column(JSON)
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    remediations = relationship("Remediation", back_populates="incident")
    pipeline_runs = relationship("PipelineRun", back_populates="incident")

class PipelineRun(Base):
    """Pipeline execution tracking"""
    __tablename__ = "pipeline_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(String(255), nullable=False)
    run_number = Column(Integer)
    status = Column(String(20), default=PipelineStatus.PENDING)
    
    # Source details
    source_type = Column(String(50))  # github, gitlab, jenkins
    repository = Column(String(255))
    branch = Column(String(100))
    commit_sha = Column(String(40))
    commit_message = Column(Text)
    author = Column(String(100))
    
    # Execution details
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    duration = Column(Integer)  # seconds
    
    # Results
    success = Column(Boolean)
    error_message = Column(Text)
    logs_url = Column(String(500))
    artifacts_url = Column(String(500))
    
    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    
    # Relationships
    incident = relationship("Incident", back_populates="pipeline_runs")

class Remediation(Base):
    """Remediation action tracking"""
    __tablename__ = "remediations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    
    # Remediation details
    action_type = Column(String(100))  # code_fix, config_fix, resource_restart, etc.
    description = Column(Text)
    status = Column(String(20), default=RemediationStatus.PENDING)
    
    # Fix details
    fix_content = Column(Text)  # patch, yaml, script
    fix_type = Column(String(50))  # patch, yaml, script, api_call
    target_files = Column(JSON)  # list of files to modify
    
    # Execution details
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration = Column(Integer)  # seconds
    
    # Results
    success = Column(Boolean)
    error_message = Column(Text)
    rollback_data = Column(JSON)  # data needed for rollback
    
    # Validation
    validation_passed = Column(Boolean)
    validation_results = Column(JSON)
    
    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", back_populates="remediations")

class AWSResource(Base):
    """AWS resource tracking"""
    __tablename__ = "aws_resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(100))  # ec2, ecs, lambda, s3, etc.
    resource_arn = Column(String(500))
    
    # Resource details
    name = Column(String(255))
    region = Column(String(50))
    account_id = Column(String(20))
    tags = Column(JSON)
    
    # Status
    status = Column(String(50))
    health_status = Column(String(50))
    last_check = Column(DateTime)
    
    # Monitoring
    monitored = Column(Boolean, default=True)
    auto_recovery_enabled = Column(Boolean, default=True)
    
    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KubernetesResource(Base):
    """Kubernetes resource tracking"""
    __tablename__ = "k8s_resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    namespace = Column(String(100))
    kind = Column(String(100))  # Pod, Deployment, Service, etc.
    
    # Resource details
    cluster_name = Column(String(255))
    labels = Column(JSON)
    annotations = Column(JSON)
    
    # Status
    status = Column(String(50))
    ready = Column(Boolean)
    last_check = Column(DateTime)
    
    # Monitoring
    monitored = Column(Boolean, default=True)
    auto_recovery_enabled = Column(Boolean, default=True)
    
    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LogEntry(Base):
    """Log entry storage"""
    __tablename__ = "log_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source information
    source_type = Column(String(50))  # pipeline, aws, k8s
    source_id = Column(String(255))
    
    # Log details
    timestamp = Column(DateTime, nullable=False)
    level = Column(String(20))  # DEBUG, INFO, WARN, ERROR, FATAL
    message = Column(Text, nullable=False)
    
    # Context
    service = Column(String(100))
    component = Column(String(100))
    environment = Column(String(50))
    
    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemHealth(Base):
    """System health metrics"""
    __tablename__ = "system_health"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metrics
    timestamp = Column(DateTime, nullable=False)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    
    # Counters
    active_incidents = Column(Integer, default=0)
    resolved_incidents = Column(Integer, default=0)
    failed_remediations = Column(Integer, default=0)
    
    # Performance
    avg_resolution_time = Column(Float)  # seconds
    success_rate = Column(Float)  # percentage
    
    # Component health
    components_status = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    """User management"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    
    # Authentication
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Permissions
    permissions = Column(JSON)
    
    # Timestamps
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    """Audit logging for all actions"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Action details
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    
    # User context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    username = Column(String(100))
    
    # Details
    description = Column(Text)
    metadata = Column(JSON)
    
    # Results
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

# Indexes for performance
from sqlalchemy import Index

Index('idx_incidents_status', Incident.status)
Index('idx_incidents_severity', Incident.severity)
Index('idx_incidents_detected_at', Incident.detected_at)
Index('idx_pipeline_runs_status', PipelineRun.status)
Index('idx_remediations_status', Remediation.status)
Index('idx_log_entries_timestamp', LogEntry.timestamp)
Index('idx_log_entries_level', LogEntry.level)