# AI-RecoverOps Installation Guide

This comprehensive guide covers all installation methods for AI-RecoverOps, from development setup to production deployment.

## 📋 Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- OS: Linux, macOS, or Windows with WSL2

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 100GB+ SSD
- OS: Ubuntu 20.04+ or CentOS 8+

### Software Dependencies

**Required:**
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Git

**Optional (for advanced features):**
- Docker & Docker Compose
- Kubernetes cluster
- AWS CLI
- Terraform

## 🚀 Installation Methods

### Method 1: Docker Compose (Recommended)

This is the fastest way to get AI-RecoverOps running with all dependencies.

#### Step 1: Clone Repository

```bash
git clone https://github.com/ai-recoverops/ai-recoverops.git
cd ai-recoverops
```

#### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables:**

```env
# Core Configuration
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_URL=postgresql://airecoverops:airecoverops123@postgres:5432/airecoverops
REDIS_URL=redis://redis:6379/0

# Platform Integrations
GITHUB_TOKEN=ghp_your-github-personal-access-token
GITLAB_TOKEN=glpat-your-gitlab-access-token
JENKINS_URL=http://your-jenkins-server:8080
JENKINS_USERNAME=your-jenkins-username
JENKINS_TOKEN=your-jenkins-api-token

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

# Feature Configuration
AUTO_REMEDIATION_ENABLED=true
AI_CONFIDENCE_THRESHOLD=0.8
MAX_CONCURRENT_REMEDIATIONS=5
ENVIRONMENT=production
```

#### Step 3: Start Services

```bash
# Start all services in background
docker-compose -f deployment/docker/docker-compose.yml up -d

# Check service status
docker-compose -f deployment/docker/docker-compose.yml ps

# View logs
docker-compose -f deployment/docker/docker-compose.yml logs -f
```

#### Step 4: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Access dashboard
open http://localhost:3000

# View API documentation
open http://localhost:8000/docs
```

### Method 2: Manual Installation

For development or custom deployments.

#### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm postgresql-15 redis-server git curl
```

**CentOS/RHEL:**
```bash
sudo dnf install -y python3.11 python3-pip nodejs npm postgresql15-server redis git curl
sudo systemctl enable --now postgresql redis
```

**macOS:**
```bash
brew install python@3.11 node postgresql@15 redis git
brew services start postgresql@15
brew services start redis
```

#### Step 2: Setup Database

**PostgreSQL Setup:**
```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE airecoverops;
CREATE USER airecoverops WITH PASSWORD 'airecoverops123';
GRANT ALL PRIVILEGES ON DATABASE airecoverops TO airecoverops;
ALTER USER airecoverops CREATEDB;
\q
EOF
```

**Redis Setup:**
```bash
# Configure Redis (optional password)
sudo nano /etc/redis/redis.conf
# Uncomment and set: requirepass redis123

# Restart Redis
sudo systemctl restart redis
```

#### Step 3: Backend Setup

```bash
# Clone repository
git clone https://github.com/ai-recoverops/ai-recoverops.git
cd ai-recoverops

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://airecoverops:airecoverops123@localhost:5432/airecoverops"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key-change-in-production"
export OPENAI_API_KEY="sk-your-openai-api-key"

# Initialize database
python -c "
import asyncio
from database.connection import init_database
asyncio.run(init_database())
"

# Start backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 4: Frontend Setup

```bash
# Open new terminal
cd ai-recoverops/dashboard-v2

# Install dependencies
npm install

# Set environment variables
export REACT_APP_API_URL=http://localhost:8000
export REACT_APP_WEBSOCKET_URL=ws://localhost:8000

# Start development server
npm start
```

### Method 3: Kubernetes Deployment

For production environments with high availability.

#### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.x (optional)
- Ingress controller (nginx recommended)
- Cert-manager (for TLS)

#### Step 1: Prepare Secrets

```bash
# Create namespace
kubectl create namespace ai-recoverops

# Create secrets
kubectl create secret generic ai-recoverops-secrets \
  --from-literal=SECRET_KEY="your-secret-key" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-key" \
  --from-literal=GITHUB_TOKEN="ghp-your-github-token" \
  --from-literal=AWS_ACCESS_KEY_ID="your-aws-key" \
  --from-literal=AWS_SECRET_ACCESS_KEY="your-aws-secret" \
  --from-literal=POSTGRES_PASSWORD="airecoverops123" \
  --from-literal=REDIS_PASSWORD="redis123" \
  -n ai-recoverops
```

#### Step 2: Deploy Application

```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/ai-recoverops-deployment.yaml

# Check deployment status
kubectl get pods -n ai-recoverops
kubectl get services -n ai-recoverops
kubectl get ingress -n ai-recoverops
```

#### Step 3: Configure Ingress

Update the ingress configuration with your domain:

```bash
# Edit ingress
kubectl edit ingress ai-recoverops-ingress -n ai-recoverops

# Update host to your domain
# spec:
#   rules:
#   - host: ai-recoverops.yourdomain.com
```

#### Step 4: Verify Deployment

```bash
# Check pod status
kubectl get pods -n ai-recoverops

# View logs
kubectl logs -f deployment/ai-recoverops-api -n ai-recoverops

# Port forward for testing
kubectl port-forward svc/ai-recoverops-dashboard-service 3000:3000 -n ai-recoverops
```

## 🔧 Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | JWT signing key (min 32 chars) |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for AI analysis |
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | Yes | - | Redis connection string |
| `GITHUB_TOKEN` | No | - | GitHub personal access token |
| `GITLAB_TOKEN` | No | - | GitLab access token |
| `AWS_ACCESS_KEY_ID` | No | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | No | - | AWS secret key |
| `AUTO_REMEDIATION_ENABLED` | No | `true` | Enable automatic fixes |
| `AI_CONFIDENCE_THRESHOLD` | No | `0.8` | Minimum confidence for auto-fix |
| `MAX_CONCURRENT_REMEDIATIONS` | No | `5` | Max parallel remediations |

### Platform Integration Setup

#### GitHub Integration

1. **Create Personal Access Token:**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate new token with scopes: `repo`, `workflow`, `admin:repo_hook`
   - Set as `GITHUB_TOKEN` environment variable

2. **Configure Webhook:**
   - Repository Settings → Webhooks → Add webhook
   - Payload URL: `https://your-domain.com/webhooks/github`
   - Content type: `application/json`
   - Events: Select "Workflow runs", "Check runs", "Pushes", "Pull requests"
   - Secret: Set `GITHUB_WEBHOOK_SECRET` environment variable

#### GitLab Integration

1. **Create Access Token:**
   - GitLab Settings → Access Tokens
   - Create token with scopes: `api`, `read_repository`, `write_repository`
   - Set as `GITLAB_TOKEN` environment variable

2. **Configure Webhook:**
   - Project Settings → Webhooks
   - URL: `https://your-domain.com/webhooks/gitlab`
   - Trigger: Pipeline events, Job events, Push events
   - Secret token: Set `GITLAB_WEBHOOK_SECRET` environment variable

#### AWS Integration

1. **Create IAM User:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ec2:*",
           "ecs:*",
           "lambda:*",
           "s3:*",
           "iam:ListRoles",
           "iam:PassRole"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

2. **Set Credentials:**
   ```bash
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_REGION="us-east-1"
   ```

## 🔍 Verification & Testing

### Health Checks

```bash
# API health check
curl -f http://localhost:8000/health

# Database connectivity
curl -f http://localhost:8000/api/system-status

# Redis connectivity
redis-cli ping

# PostgreSQL connectivity
psql -h localhost -U airecoverops -d airecoverops -c "SELECT 1;"
```

### Functional Testing

```bash
# Test webhook endpoint
curl -X POST http://localhost:8000/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: workflow_run" \
  -d '{"action": "completed", "workflow_run": {"id": "test", "conclusion": "failure"}}'

# Test incident creation
curl -X POST http://localhost:8000/api/test/simulate-incident \
  -H "Content-Type: application/json" \
  -d '{"type": "build_failure", "repository": "test/repo"}'
```

### Performance Testing

```bash
# Install testing tools
pip install locust

# Run load tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U airecoverops -d airecoverops

# Reset password
sudo -u postgres psql -c "ALTER USER airecoverops PASSWORD 'newpassword';"
```

#### Redis Connection Failed
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping

# Check configuration
sudo nano /etc/redis/redis.conf
```

#### OpenAI API Errors
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Check quota
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/usage
```

#### Docker Issues
```bash
# Check container logs
docker-compose logs ai-recoverops-api

# Restart services
docker-compose restart

# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Log Analysis

```bash
# Backend logs
tail -f backend/logs/ai-recoverops.log

# Docker logs
docker-compose logs -f --tail=100

# Kubernetes logs
kubectl logs -f deployment/ai-recoverops-api -n ai-recoverops
```

### Performance Issues

```bash
# Check system resources
htop
df -h
free -h

# Database performance
psql -U airecoverops -d airecoverops -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;"

# Redis performance
redis-cli info stats
```

## 🔄 Updates & Maintenance

### Updating AI-RecoverOps

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade
npm install

# Run database migrations
python -c "
import asyncio
from database.connection import init_database
asyncio.run(init_database())
"

# Restart services
docker-compose restart
```

### Backup & Recovery

```bash
# Database backup
pg_dump -h localhost -U airecoverops airecoverops > backup.sql

# Redis backup
redis-cli BGSAVE

# Restore database
psql -h localhost -U airecoverops airecoverops < backup.sql
```

## 📞 Support

If you encounter issues during installation:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [GitHub Issues](https://github.com/ai-recoverops/ai-recoverops/issues)
3. Join our [Discord Community](https://discord.gg/ai-recoverops)
4. Contact support: support@ai-recoverops.com

## ✅ Next Steps

After successful installation:

1. [Configure Platform Integrations](CONFIGURATION.md)
2. [Set up Monitoring](MONITORING.md)
3. [Deploy to Production](DEPLOYMENT.md)
4. [Review Security Settings](SECURITY.md)