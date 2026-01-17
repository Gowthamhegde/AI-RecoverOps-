# AI-RecoverOps: Production-Grade DevOps Recovery System

<div align="center">

![AI-RecoverOps Logo](https://via.placeholder.com/200x100/1890ff/ffffff?text=AI-RecoverOps)

**Autonomous DevOps Recovery System - Your AI SRE Engineer**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/ai-recoverops/ai-recoverops)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io)

</div>

## 🎯 Overview

AI-RecoverOps is a production-grade autonomous DevOps recovery system that acts as an AI-powered Site Reliability Engineer (SRE). It automatically detects CI/CD failures, analyzes root causes using advanced AI, generates precise fixes, and applies them in real-time to restore your development pipeline.

### ✨ Key Features

- 🤖 **AI-Powered Analysis**: Uses GPT-4 and ML models for intelligent root cause analysis
- 🔧 **Autonomous Remediation**: Automatically generates and applies fixes via GitHub/GitLab PRs
- 📊 **Real-time Monitoring**: Live dashboard with WebSocket updates and system metrics
- 🚀 **Multi-Platform Support**: GitHub Actions, GitLab CI, Jenkins integration
- ☁️ **Cloud Recovery**: AWS EC2, ECS, Lambda, S3 resource recovery
- 🎛️ **Kubernetes Native**: Pod, deployment, and service auto-healing
- 📈 **Production Ready**: High availability, horizontal scaling, comprehensive monitoring

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "External Systems"
        GH[GitHub Actions]
        GL[GitLab CI]
        JK[Jenkins]
        AWS[AWS Resources]
        K8S[Kubernetes]
    end
    
    subgraph "AI-RecoverOps Core"
        subgraph "Ingestion Layer"
            WH[Webhook Listeners]
            LS[Log Streamers]
            MQ[Message Queue]
        end
        
        subgraph "AI Processing"
            FD[Failure Detector]
            AI[AI Analyzer]
            FG[Fix Generator]
            RE[Remediation Engine]
        end
        
        subgraph "Storage"
            PG[(PostgreSQL)]
            RD[(Redis)]
            S3[(S3 Logs)]
        end
        
        subgraph "Interface"
            API[FastAPI Backend]
            UI[React Dashboard]
        end
    end
    
    GH --> WH
    GL --> WH
    JK --> WH
    AWS --> LS
    K8S --> LS
    
    WH --> MQ
    LS --> MQ
    MQ --> FD
    FD --> AI
    AI --> FG
    FG --> RE
    
    API --> UI
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. Clone Repository

```bash
git clone https://github.com/ai-recoverops/ai-recoverops.git
cd ai-recoverops
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Required environment variables:
```env
# Core Configuration
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=sk-your-openai-api-key
DATABASE_URL=postgresql://airecoverops:password@localhost:5432/airecoverops
REDIS_URL=redis://localhost:6379/0

# Platform Integrations
GITHUB_TOKEN=ghp_your-github-token
GITLAB_TOKEN=glpat-your-gitlab-token
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# Feature Flags
AUTO_REMEDIATION_ENABLED=true
AI_CONFIDENCE_THRESHOLD=0.8
MAX_CONCURRENT_REMEDIATIONS=5
```

### 3. Docker Deployment (Recommended)

```bash
# Start all services
docker-compose -f deployment/docker/docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ai-recoverops-api
```

### 4. Manual Installation

```bash
# Backend setup
cd backend
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 8000

# Dashboard setup (new terminal)
cd dashboard-v2
npm install
npm start
```

### 5. Verify Installation

- **API Health**: http://localhost:8000/health
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 📋 Integration Guide

### GitHub Actions Integration

Add to your repository's `.github/workflows/`:

```yaml
name: AI-RecoverOps Integration
on:
  workflow_run:
    workflows: ["*"]
    types: [completed]

jobs:
  notify-ai-recoverops:
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Send status to AI-RecoverOps
        uses: actions/github-script@v7
        with:
          script: |
            const axios = require('axios');
            await axios.post('${{ secrets.AI_RECOVEROPS_URL }}/webhooks/github', {
              action: 'completed',
              workflow_run: {
                id: context.runId,
                status: '${{ job.status }}',
                conclusion: '${{ job.status }}',
                repository: context.repo.owner + '/' + context.repo.repo
              }
            });
```

### GitLab CI Integration

Add to your `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - test
  - notify

notify_ai_recoverops:
  stage: notify
  script:
    - |
      curl -X POST "$AI_RECOVEROPS_URL/webhooks/gitlab" \
        -H "Content-Type: application/json" \
        -H "X-Gitlab-Token: $GITLAB_WEBHOOK_SECRET" \
        -d '{
          "object_attributes": {
            "id": "'$CI_PIPELINE_ID'",
            "status": "'$CI_JOB_STATUS'",
            "ref": "'$CI_COMMIT_REF_NAME'",
            "sha": "'$CI_COMMIT_SHA'"
          },
          "project": {
            "path_with_namespace": "'$CI_PROJECT_PATH'"
          }
        }'
  when: always
```

### Webhook Configuration

Configure webhooks in your platforms:

**GitHub:**
- URL: `https://your-domain.com/webhooks/github`
- Events: Workflow runs, Check runs, Push, Pull requests
- Secret: Set `GITHUB_WEBHOOK_SECRET`

**GitLab:**
- URL: `https://your-domain.com/webhooks/gitlab`
- Events: Pipeline events, Job events, Push events
- Token: Set `GITLAB_WEBHOOK_SECRET`

## 🎛️ Configuration

### Core Settings

```yaml
# config/settings.yaml
ai_recoverops:
  core:
    auto_remediation: true
    confidence_threshold: 0.8
    max_concurrent_fixes: 5
    rollback_timeout: 600
    
  detection:
    enabled_platforms:
      - github
      - gitlab
      - jenkins
    failure_patterns:
      - build_failure
      - test_failure
      - deployment_failure
      - dependency_error
      
  ai:
    openai_model: "gpt-4"
    max_tokens: 2000
    temperature: 0.2
    
  notifications:
    slack:
      enabled: true
      webhook_url: "https://hooks.slack.com/..."
    email:
      enabled: true
      smtp_host: "smtp.gmail.com"
```

### Platform-Specific Configuration

**AWS Integration:**
```yaml
aws:
  region: us-east-1
  services:
    - ec2
    - ecs
    - lambda
    - s3
  auto_recovery: true
  resource_tags:
    - "ai-recoverops:managed"
```

**Kubernetes Integration:**
```yaml
kubernetes:
  namespaces:
    - default
    - production
  resources:
    - pods
    - deployments
    - services
  auto_healing: true
```

## 📊 Dashboard Features

### Real-time Monitoring
- Live incident detection and resolution
- System health metrics
- Pipeline status tracking
- WebSocket-powered updates

### Analytics & Insights
- Failure pattern analysis
- Resolution time trends
- Success rate metrics
- Top failure categories

### Incident Management
- Detailed incident timeline
- Root cause analysis results
- Applied fixes and outcomes
- Manual remediation controls

### Recovery Actions
- AWS resource management
- Kubernetes pod healing
- CI/CD pipeline recovery
- Custom remediation scripts

## 🔧 API Reference

### Core Endpoints

```http
GET    /health                    # System health check
GET    /api/incidents             # List incidents
POST   /api/incidents/{id}/remediate  # Trigger remediation
GET    /api/pipelines             # List pipeline runs
POST   /api/recovery/aws/restart  # Restart AWS resources
GET    /api/analytics             # Get analytics data
```

### Webhook Endpoints

```http
POST   /webhooks/github           # GitHub webhook receiver
POST   /webhooks/gitlab           # GitLab webhook receiver
POST   /webhooks/jenkins          # Jenkins webhook receiver
```

### Authentication

```http
POST   /api/auth/login            # User authentication
GET    /api/auth/me               # Current user info
```

Full API documentation: http://localhost:8000/docs

## 🚀 Production Deployment

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/

# Check deployment status
kubectl get pods -n ai-recoverops

# Access dashboard
kubectl port-forward svc/ai-recoverops-dashboard-service 3000:3000 -n ai-recoverops
```

### AWS ECS Deployment

```bash
# Build and push images
docker build -t ai-recoverops/api:2.0.0 -f deployment/docker/Dockerfile .
docker push ai-recoverops/api:2.0.0

# Deploy with Terraform
cd deployment/terraform
terraform init
terraform plan
terraform apply
```

### Monitoring Setup

**Prometheus Metrics:**
- System performance metrics
- Incident resolution rates
- API response times
- Queue lengths

**Grafana Dashboards:**
- Real-time system overview
- Incident trends and patterns
- Performance monitoring
- Alert management

## 🧪 Testing

### Unit Tests

```bash
cd backend
pytest tests/ -v --cov=.
```

### Integration Tests

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/ -v
```

### End-to-End Tests

```bash
# Simulate failure scenarios
python tests/e2e/simulate_failures.py

# Test auto-remediation
python tests/e2e/test_remediation.py
```

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key management
- OAuth2 integration

### Data Protection
- Encryption at rest and in transit
- Secure credential storage
- Audit logging
- GDPR compliance

### Network Security
- TLS/SSL encryption
- Network policies
- Firewall rules
- VPN integration

## 📈 Performance

### Scalability
- Horizontal pod autoscaling
- Database connection pooling
- Redis clustering
- Load balancing

### Optimization
- Async processing
- Message queuing
- Caching strategies
- Database indexing

### Monitoring
- Real-time metrics
- Performance alerts
- Resource utilization
- SLA tracking

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/ai-recoverops.git

# Create development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Start development servers
make dev-start
```

### Code Standards
- Python: Black formatting, flake8 linting, mypy type checking
- JavaScript: ESLint, Prettier formatting
- Git: Conventional commits
- Testing: 90%+ code coverage

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Configuration Reference](docs/CONFIGURATION.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Architecture Deep Dive](docs/ARCHITECTURE.md)

## 🆘 Support

### Community Support
- [GitHub Discussions](https://github.com/ai-recoverops/ai-recoverops/discussions)
- [Discord Server](https://discord.gg/ai-recoverops)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/ai-recoverops)

### Enterprise Support
- 24/7 technical support
- Custom integrations
- Training and consulting
- SLA guarantees

Contact: enterprise@ai-recoverops.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- FastAPI framework
- React ecosystem
- Kubernetes community
- All our contributors

---

<div align="center">

**Made with ❤️ by the AI-RecoverOps Team**

[Website](https://ai-recoverops.com) • [Documentation](https://docs.ai-recoverops.com) • [Blog](https://blog.ai-recoverops.com)

</div>