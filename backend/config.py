"""
AI-RecoverOps Configuration Management
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "AI-RecoverOps"
    VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://dashboard.ai-recoverops.com"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://airecoverops:password@localhost:5432/airecoverops",
        env="DATABASE_URL"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI/ML Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    AI_CONFIDENCE_THRESHOLD: float = Field(default=0.8, env="AI_CONFIDENCE_THRESHOLD")
    
    # GitHub Integration
    GITHUB_TOKEN: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    GITHUB_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="GITHUB_WEBHOOK_SECRET")
    
    # GitLab Integration
    GITLAB_TOKEN: Optional[str] = Field(default=None, env="GITLAB_TOKEN")
    GITLAB_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="GITLAB_WEBHOOK_SECRET")
    
    # Jenkins Integration
    JENKINS_URL: Optional[str] = Field(default=None, env="JENKINS_URL")
    JENKINS_USERNAME: Optional[str] = Field(default=None, env="JENKINS_USERNAME")
    JENKINS_TOKEN: Optional[str] = Field(default=None, env="JENKINS_TOKEN")
    
    # AWS Configuration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # Kubernetes
    KUBECONFIG_PATH: Optional[str] = Field(default=None, env="KUBECONFIG_PATH")
    K8S_NAMESPACE: str = Field(default="default", env="K8S_NAMESPACE")
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    GRAFANA_URL: Optional[str] = Field(default=None, env="GRAFANA_URL")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Remediation Settings
    AUTO_REMEDIATION_ENABLED: bool = Field(default=True, env="AUTO_REMEDIATION_ENABLED")
    MAX_CONCURRENT_REMEDIATIONS: int = Field(default=5, env="MAX_CONCURRENT_REMEDIATIONS")
    REMEDIATION_TIMEOUT: int = Field(default=300, env="REMEDIATION_TIMEOUT")  # seconds
    
    # Rollback Settings
    AUTO_ROLLBACK_ENABLED: bool = Field(default=True, env="AUTO_ROLLBACK_ENABLED")
    ROLLBACK_TIMEOUT: int = Field(default=600, env="ROLLBACK_TIMEOUT")  # seconds
    
    # Notification Settings
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    EMAIL_SMTP_HOST: Optional[str] = Field(default=None, env="EMAIL_SMTP_HOST")
    EMAIL_SMTP_PORT: int = Field(default=587, env="EMAIL_SMTP_PORT")
    EMAIL_USERNAME: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    
    # Storage
    S3_BUCKET_LOGS: Optional[str] = Field(default=None, env="S3_BUCKET_LOGS")
    S3_BUCKET_ARTIFACTS: Optional[str] = Field(default=None, env="S3_BUCKET_ARTIFACTS")
    
    # Feature Flags
    ENABLE_GITHUB_INTEGRATION: bool = Field(default=True, env="ENABLE_GITHUB_INTEGRATION")
    ENABLE_GITLAB_INTEGRATION: bool = Field(default=True, env="ENABLE_GITLAB_INTEGRATION")
    ENABLE_JENKINS_INTEGRATION: bool = Field(default=True, env="ENABLE_JENKINS_INTEGRATION")
    ENABLE_AWS_RECOVERY: bool = Field(default=True, env="ENABLE_AWS_RECOVERY")
    ENABLE_K8S_RECOVERY: bool = Field(default=True, env="ENABLE_K8S_RECOVERY")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Validation
def validate_settings():
    """Validate critical settings"""
    errors = []
    
    if settings.AUTO_REMEDIATION_ENABLED and not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required when auto-remediation is enabled")
    
    if settings.ENABLE_GITHUB_INTEGRATION and not settings.GITHUB_TOKEN:
        errors.append("GITHUB_TOKEN is required for GitHub integration")
    
    if settings.ENABLE_GITLAB_INTEGRATION and not settings.GITLAB_TOKEN:
        errors.append("GITLAB_TOKEN is required for GitLab integration")
    
    if settings.ENABLE_AWS_RECOVERY and not (settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY):
        errors.append("AWS credentials are required for AWS recovery")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")

# Validate on import
validate_settings()