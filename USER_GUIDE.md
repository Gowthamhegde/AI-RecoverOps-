# AI-RecoverOps User Guide

## 🚀 Getting Started

AI-RecoverOps is designed to be incredibly easy to use. Choose your preferred installation method:

### Option 1: One-Click Installation (Recommended)

**For Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/your-org/ai-recoverops/main/quick-start.sh | bash
```

**For Windows (PowerShell as Administrator):**
```powershell
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/your-org/ai-recoverops/main/quick-start.ps1'))
```

### Option 2: Manual Installation

1. **Download the installer:**
   ```bash
   wget https://github.com/your-org/ai-recoverops/releases/latest/download/install.py
   python3 install.py
   ```

2. **Follow the interactive setup:**
   - Choose deployment type (local/cloud)
   - Configure AWS credentials (if needed)
   - Set up notifications (Slack/email)
   - Configure ML thresholds

### Option 3: Docker (Quick Test)

```bash
docker run -d -p 3000:3000 -p 8000:8000 ai-recoverops/all-in-one:latest
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10+
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM
- **Storage**: 10GB free space
- **Network**: Internet connection for cloud features

### Recommended for Production
- **OS**: Ubuntu 20.04+ or Amazon Linux 2
- **Python**: 3.10+
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ SSD
- **CPU**: 4+ cores
- **Network**: Stable internet with AWS access

## 🎯 Quick Start Guide

### 1. Installation (5 minutes)

Run the one-click installer for your platform:

```bash
# Linux/macOS
curl -sSL https://get.ai-recoverops.com | bash

# Windows PowerShell
iex (iwr https://get.ai-recoverops.com/windows).Content
```

### 2. First Launch (2 minutes)

```bash
# Start services
ai-recoverops start

# Check status
ai-recoverops status

# Open dashboard
ai-recoverops dashboard
```

### 3. Basic Configuration (3 minutes)

1. **Access the dashboard**: http://localhost:3000
2. **Configure log sources**: Add your application log endpoints
3. **Set up notifications**: Connect Slack or email alerts
4. **Test detection**: Generate a test incident

## 🖥️ Using the Dashboard

### Main Dashboard

The dashboard provides a real-time view of your infrastructure health:

- **Incident Overview**: Current incidents and their status
- **System Health**: Overall system health score
- **Auto-Remediation Rate**: Success rate of automated fixes
- **Recent Activity**: Timeline of incidents and remediations

### Incident Management

**Viewing Incidents:**
1. Click on any incident in the list
2. View detailed information including:
   - Root cause analysis
   - Confidence score
   - Recommended actions
   - System metrics at time of incident

**Taking Action:**
- **Acknowledge**: Mark incident as seen
- **Remediate**: Trigger automatic remediation
- **Escalate**: Forward to human operators
- **Resolve**: Mark as manually resolved

### Configuration Panel

**ML Settings:**
- Adjust confidence thresholds
- Enable/disable auto-remediation
- Configure detection sensitivity

**Notification Settings:**
- Set up Slack webhooks
- Configure email alerts
- Define escalation rules

## 💻 Command Line Interface

The CLI provides powerful management capabilities:

### Basic Commands

```bash
# System status
ai-recoverops status health
ai-recoverops status metrics

# Incident management
ai-recoverops incidents list
ai-recoverops incidents show INC-1234
ai-recoverops incidents action INC-1234 remediate

# Model management
ai-recoverops models list
ai-recoverops models train --data-path /path/to/logs

# Deployment
ai-recoverops deploy start --environment production
ai-recoverops deploy stop
ai-recoverops deploy status
```

### Interactive Mode

For easier use, start interactive mode:

```bash
ai-recoverops interactive
```

This provides a guided interface with tab completion and help.

### Configuration Management

```bash
# Set API endpoint
ai-recoverops config set --api-url http://your-api.com

# Show current config
ai-recoverops config show

# Set AWS region
ai-recoverops config set --aws-region us-west-2
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your installation directory:

```bash
# Core Configuration
PROJECT_NAME=ai-recoverops
ENVIRONMENT=production
CONFIDENCE_THRESHOLD=0.8
AUTO_REMEDIATION_ENABLED=true

# AWS Configuration (for cloud deployment)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Notification Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
ALERT_EMAIL=alerts@yourcompany.com

# API Configuration
ML_API_ENDPOINT=http://localhost:8000
DATABASE_URL=postgresql://user:pass@localhost/ai_recoverops
```

### Application Configuration

Edit `config.yaml` for advanced settings:

```yaml
ai_recoverops:
  core:
    log_level: INFO
    max_concurrent_fixes: 3
    rollback_timeout: 300
    
  detection:
    interval: 30  # seconds
    enabled_detectors:
      - system
      - application
      - network
      - database
    
  analysis:
    confidence_threshold: 0.8
    max_analysis_time: 120
    use_historical_data: true
    
  fixes:
    auto_apply: false
    require_approval: true
    backup_before_fix: true
```

## 🔍 Monitoring and Alerting

### Built-in Monitoring

AI-RecoverOps includes comprehensive monitoring:

- **System Health Dashboard**: Real-time system status
- **Incident Timeline**: Historical view of all incidents
- **Performance Metrics**: Response times, success rates
- **ML Model Performance**: Accuracy, confidence trends

### External Integrations

**Grafana Integration:**
```bash
# Access Grafana dashboard
http://localhost:3001
# Login: admin/admin123
```

**Prometheus Metrics:**
```bash
# Metrics endpoint
http://localhost:9090/metrics
```

**CloudWatch Integration:**
- Automatic log forwarding
- Custom metrics publishing
- Alarm integration

### Setting Up Alerts

**Slack Notifications:**
1. Create a Slack webhook URL
2. Add to configuration: `SLACK_WEBHOOK_URL=https://hooks.slack.com/...`
3. Test: `ai-recoverops config test-notifications`

**Email Alerts:**
1. Configure SMTP settings in `config.yaml`
2. Add recipient: `ALERT_EMAIL=team@company.com`
3. Set alert thresholds and conditions

## 🤖 Machine Learning Features

### Incident Detection

AI-RecoverOps uses advanced ML models to detect incidents:

- **XGBoost Classifier**: Analyzes structured log features
- **LSTM Neural Network**: Processes log message sequences
- **Ensemble Model**: Combines multiple models for accuracy

### Supported Incident Types

1. **High CPU Usage**: Detects CPU spikes and sustained high usage
2. **Memory Leaks**: Identifies gradual memory consumption increases
3. **Disk Space Issues**: Monitors disk usage and predicts full disks
4. **Service Crashes**: Detects application failures and crashes
5. **Database Problems**: Identifies connection issues and slow queries
6. **Network Issues**: Monitors connectivity and latency problems
7. **Permission Errors**: Detects access control failures
8. **Container Issues**: Monitors Docker/Kubernetes problems

### Model Training

**Automatic Training:**
- Models retrain automatically on new data
- Continuous learning from incident outcomes
- Performance monitoring and alerting

**Manual Training:**
```bash
# Train with custom data
ai-recoverops models train --data-path /path/to/logs.csv

# Evaluate model performance
ai-recoverops models evaluate

# Deploy new models
ai-recoverops models deploy --version 2.1.0
```

## 🔧 Auto-Remediation

### Safe Remediation

AI-RecoverOps implements safe auto-remediation:

- **Confidence Thresholds**: Only high-confidence predictions trigger actions
- **Rollback Capabilities**: All actions can be automatically reversed
- **Human Approval**: Critical actions require human confirmation
- **Audit Trails**: Complete logging of all remediation activities

### Supported Remediation Actions

1. **Service Management**:
   - Restart failed services
   - Scale services horizontally
   - Kill conflicting processes

2. **Resource Management**:
   - Clean log files
   - Expand disk volumes
   - Optimize memory usage

3. **Database Operations**:
   - Restart database instances
   - Kill long-running queries
   - Optimize database performance

4. **Permission Fixes**:
   - Correct file permissions
   - Update IAM policies
   - Reset access controls

### Configuring Auto-Remediation

**Enable/Disable:**
```bash
# Enable auto-remediation
ai-recoverops config set --auto-remediation true

# Disable for specific incident types
ai-recoverops config set --disable-remediation high_cpu,memory_leak
```

**Safety Settings:**
```yaml
fixes:
  auto_apply: true
  require_approval: false  # Set to true for manual approval
  confidence_threshold: 0.9  # Higher threshold for auto-remediation
  backup_before_fix: true
  rollback_timeout: 300  # Seconds before auto-rollback
```

## 🚀 Deployment Options

### Local Development

Perfect for testing and development:

```bash
# Start local environment
ai-recoverops deploy start --environment local

# Services available at:
# - Dashboard: http://localhost:3000
# - API: http://localhost:8000
# - Grafana: http://localhost:3001
```

### AWS Cloud Production

Full production deployment on AWS:

```bash
# Configure AWS credentials
aws configure

# Deploy to AWS
ai-recoverops deploy start --environment production

# Monitor deployment
ai-recoverops deploy status
```

### Hybrid Deployment

Run locally with AWS integrations:

```bash
# Local services with AWS log sources
ai-recoverops deploy start --environment hybrid --aws-integration
```

## 🔒 Security Best Practices

### Access Control

- **IAM Roles**: Use least-privilege IAM roles for AWS access
- **API Authentication**: Enable API key authentication for production
- **Network Security**: Deploy in private subnets with proper security groups

### Data Protection

- **Encryption**: All data encrypted at rest and in transit
- **Log Sanitization**: Sensitive data automatically redacted
- **Audit Logging**: Complete audit trail of all activities

### Safe Remediation

- **Approval Workflows**: Require human approval for critical actions
- **Rollback Plans**: Every remediation has an automatic rollback
- **Testing**: Test all remediation actions in staging first

## 🆘 Troubleshooting

### Common Issues

**Services Won't Start:**
```bash
# Check Docker status
docker ps

# Check logs
ai-recoverops logs --service ml-api

# Restart services
ai-recoverops deploy restart
```

**API Connection Issues:**
```bash
# Test API connectivity
curl http://localhost:8000/health

# Check configuration
ai-recoverops config show

# Reset configuration
ai-recoverops config reset
```

**ML Models Not Loading:**
```bash
# Check model files
ls -la models/

# Retrain models
ai-recoverops models train

# Verify model health
ai-recoverops models status
```

### Getting Help

**Built-in Help:**
```bash
# General help
ai-recoverops --help

# Command-specific help
ai-recoverops incidents --help

# Interactive help
ai-recoverops interactive
```

**Log Analysis:**
```bash
# View system logs
ai-recoverops logs --tail 100

# Debug mode
ai-recoverops --debug status health
```

**Community Support:**
- GitHub Issues: Report bugs and request features
- Documentation: Comprehensive guides and API reference
- Slack Community: Join for real-time help and discussions

## 📚 Advanced Usage

### Custom Detectors

Create custom incident detectors:

```python
from ai_recoverops.core.detector import BaseDetector

class CustomDetector(BaseDetector):
    def detect(self):
        # Your custom detection logic
        pass
```

### Custom Remediators

Implement custom remediation actions:

```python
from ai_recoverops.core.fixer import BaseFixer

class CustomFixer(BaseFixer):
    def apply_fix(self, issue):
        # Your custom remediation logic
        pass
```

### API Integration

Integrate with external systems:

```python
import requests

# Get incidents via API
response = requests.get('http://localhost:8000/incidents')
incidents = response.json()

# Trigger remediation
requests.post('http://localhost:8000/incidents/123/remediate')
```

### Webhook Integration

Set up webhooks for external notifications:

```bash
# Configure webhook endpoint
ai-recoverops config set --webhook-url https://your-system.com/webhook

# Test webhook
ai-recoverops config test-webhook
```

## 🎯 Best Practices

### Deployment

1. **Start Small**: Begin with local deployment and expand to cloud
2. **Test Thoroughly**: Test all remediation actions in staging
3. **Monitor Closely**: Watch system performance and ML accuracy
4. **Iterate Quickly**: Continuously improve based on real incidents

### Configuration

1. **Conservative Thresholds**: Start with high confidence thresholds
2. **Gradual Automation**: Enable auto-remediation incrementally
3. **Regular Updates**: Keep models and rules updated
4. **Document Changes**: Maintain configuration change logs

### Operations

1. **Regular Backups**: Backup configuration and model data
2. **Performance Monitoring**: Track system and ML performance
3. **Security Reviews**: Regular security audits and updates
4. **Team Training**: Ensure team understands the system

---

## 🎉 You're Ready!

Congratulations! You now have a complete understanding of AI-RecoverOps. Start with a local deployment, explore the features, and gradually expand to full production use.

**Next Steps:**
1. 🚀 Install AI-RecoverOps using the one-click installer
2. 📊 Explore the dashboard and familiarize yourself with the interface
3. 🔧 Configure your first log sources and notification channels
4. 🤖 Test incident detection with sample data
5. 🛡️ Set up auto-remediation for non-critical incidents
6. 📈 Monitor performance and iterate on your configuration

**Need Help?**
- 📖 Check the comprehensive documentation
- 💬 Join our community Slack workspace
- 🐛 Report issues on GitHub
- 📧 Contact support for enterprise assistance

Happy incident hunting! 🔍🤖