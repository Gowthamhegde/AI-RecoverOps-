# AI-RecoverOps Deployment Guide

This comprehensive guide will walk you through deploying AI-RecoverOps in production on AWS.

## 📋 Prerequisites

### Required Tools
- AWS CLI v2.x configured with appropriate credentials
- Docker 20.x+ and Docker Compose
- Terraform 1.6+
- Python 3.10+
- Node.js 18+
- Git

### AWS Account Requirements
- AWS Account with administrative access
- Service limits increased for:
  - ECS tasks (minimum 50)
  - Lambda concurrent executions (minimum 100)
  - CloudWatch log groups (minimum 100)

### Estimated Costs
- **Development**: $50-100/month
- **Production**: $200-500/month (depending on log volume)

## 🚀 Step-by-Step Deployment

### Step 1: Repository Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ai-recoverops.git
cd ai-recoverops

# Create environment file
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Application Configuration
ENVIRONMENT=production
PROJECT_NAME=ai-recoverops

# Notification Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
NOTIFICATION_EMAIL=alerts@yourcompany.com

# Security Configuration
DB_PASSWORD=your_secure_password_here
```

### Step 2: Generate Training Data and Train Models

```bash
# Generate synthetic training data
cd data
python generate_synthetic_logs.py

# Train ML models
cd ../ml
pip install -r requirements.txt
python model_training.py

# Verify models are created
ls -la ../models/
```

Expected output:
```
xgboost_model.json
lstm_model.h5
tfidf_vectorizer.pkl
label_encoder.pkl
scaler.pkl
tokenizer.pkl
ensemble_model.pkl
model_metadata.json
```

### Step 3: Deploy AWS Infrastructure

```bash
cd deployment/terraform

# Initialize Terraform
terraform init

# Review the deployment plan
terraform plan -var-file="production.tfvars"

# Deploy infrastructure
terraform apply -var-file="production.tfvars"
```

This will create:
- VPC with public/private subnets
- ECS cluster
- RDS PostgreSQL database
- ElastiCache Redis cluster
- S3 buckets for logs and models
- IAM roles and policies
- Application Load Balancer
- CloudWatch log groups
- SNS topics

### Step 4: Build and Push Docker Images

```bash
# Configure AWS CLI for ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build ML API image
cd api
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-recoverops/ml-api:latest .
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-recoverops/ml-api:latest

# Build Dashboard image
cd ../dashboard
npm install
npm run build
docker build -t $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-recoverops/dashboard:latest .
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-recoverops/dashboard:latest
```

### Step 5: Upload ML Models to S3

```bash
# Upload trained models to S3
aws s3 sync ../models/ s3://ai-recoverops-models-$(terraform output -raw bucket_suffix)/
```

### Step 6: Deploy ECS Services

Create ECS task definitions and services:

```bash
# Create ML API task definition
aws ecs register-task-definition --cli-input-json file://ecs/ml-api-task-definition.json

# Create Dashboard task definition
aws ecs register-task-definition --cli-input-json file://ecs/dashboard-task-definition.json

# Create ML API service
aws ecs create-service --cli-input-json file://ecs/ml-api-service.json

# Create Dashboard service
aws ecs create-service --cli-input-json file://ecs/dashboard-service.json
```

### Step 7: Deploy Lambda Functions

```bash
cd aws/lambda_functions

# Package and deploy log processor
zip -r log_processor.zip log_processor.py
aws lambda create-function \
  --function-name ai-recoverops-log-processor \
  --runtime python3.10 \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/ai-recoverops-lambda-role \
  --handler log_processor.lambda_handler \
  --zip-file fileb://log_processor.zip \
  --timeout 300 \
  --memory-size 512

# Package and deploy remediation executor
zip -r remediation_executor.zip remediation_executor.py ../../remediation/
aws lambda create-function \
  --function-name ai-recoverops-remediation-executor \
  --runtime python3.10 \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/ai-recoverops-lambda-role \
  --handler remediation_executor.lambda_handler \
  --zip-file fileb://remediation_executor.zip \
  --timeout 900 \
  --memory-size 1024
```

### Step 8: Configure CloudWatch Log Subscriptions

```bash
# Create log subscription filters for key log groups
aws logs put-subscription-filter \
  --log-group-name "/aws/ecs/ai-recoverops" \
  --filter-name "ai-recoverops-filter" \
  --filter-pattern "[timestamp, request_id, level=ERROR]" \
  --destination-arn "arn:aws:lambda:us-east-1:$AWS_ACCOUNT_ID:function:ai-recoverops-log-processor"

# Add more subscription filters for other log groups
aws logs put-subscription-filter \
  --log-group-name "/aws/lambda/your-application" \
  --filter-name "lambda-error-filter" \
  --filter-pattern "[timestamp, request_id, level=ERROR]" \
  --destination-arn "arn:aws:lambda:us-east-1:$AWS_ACCOUNT_ID:function:ai-recoverops-log-processor"
```

### Step 9: Deploy SSM Automation Documents

```bash
# Create SSM automation document for remediation
aws ssm create-document \
  --name "AI-RecoverOps-Remediation" \
  --document-type "Automation" \
  --document-format "YAML" \
  --content file://aws/ssm_automation/remediation_runbook.yaml
```

### Step 10: Configure Monitoring and Alerting

```bash
# Deploy Grafana dashboards
cd deployment/grafana
aws s3 cp dashboards/ s3://ai-recoverops-artifacts-$(terraform output -raw bucket_suffix)/grafana-dashboards/ --recursive

# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "AI-RecoverOps-High-Error-Rate" \
  --alarm-description "High error rate in AI-RecoverOps" \
  --metric-name "ErrorRate" \
  --namespace "AI-RecoverOps" \
  --statistic "Average" \
  --period 300 \
  --threshold 5.0 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 2 \
  --alarm-actions "arn:aws:sns:us-east-1:$AWS_ACCOUNT_ID:ai-recoverops-alerts"
```

## 🔧 Configuration

### Environment-Specific Configuration

Create environment-specific configuration files:

**production.tfvars**:
```hcl
aws_region = "us-east-1"
environment = "production"
project_name = "ai-recoverops"

# Instance sizes for production
ecs_task_cpu = 1024
ecs_task_memory = 2048
rds_instance_class = "db.t3.small"
redis_node_type = "cache.t3.small"

# High availability settings
enable_multi_az = true
backup_retention_period = 30
```

**staging.tfvars**:
```hcl
aws_region = "us-east-1"
environment = "staging"
project_name = "ai-recoverops-staging"

# Smaller instances for staging
ecs_task_cpu = 512
ecs_task_memory = 1024
rds_instance_class = "db.t3.micro"
redis_node_type = "cache.t3.micro"

# Reduced backup retention
backup_retention_period = 7
```

### Application Configuration

Update the ML API configuration:

**api/config/production.yaml**:
```yaml
ml_api:
  confidence_threshold: 0.8
  max_batch_size: 1000
  model_refresh_interval: 3600

database:
  url: "postgresql://ai_recoverops:${DB_PASSWORD}@${RDS_ENDPOINT}/ai_recoverops"
  pool_size: 20
  max_overflow: 30

redis:
  url: "redis://${REDIS_ENDPOINT}:6379"
  ttl: 300

aws:
  region: "${AWS_REGION}"
  s3_models_bucket: "${S3_MODELS_BUCKET}"
  sns_topic_arn: "${SNS_TOPIC_ARN}"
```

## 🔍 Verification and Testing

### Step 1: Health Checks

```bash
# Check ECS services
aws ecs describe-services --cluster ai-recoverops-cluster --services ai-recoverops-ml-api ai-recoverops-dashboard

# Check Lambda functions
aws lambda get-function --function-name ai-recoverops-log-processor
aws lambda get-function --function-name ai-recoverops-remediation-executor

# Check RDS instance
aws rds describe-db-instances --db-instance-identifier ai-recoverops-db
```

### Step 2: API Testing

```bash
# Get ALB DNS name
ALB_DNS=$(terraform output -raw alb_dns_name)

# Test ML API health
curl http://$ALB_DNS/api/health

# Test prediction endpoint
curl -X POST http://$ALB_DNS/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [{
      "timestamp": "2024-01-01T12:00:00Z",
      "log_level": "ERROR",
      "service": "web-server",
      "aws_service": "ec2",
      "instance_id": "i-1234567890abcdef0",
      "message": "High CPU usage detected: 95%",
      "region": "us-east-1",
      "environment": "production"
    }]
  }'
```

### Step 3: End-to-End Testing

```bash
# Generate test incident
python tests/generate_test_incident.py

# Monitor logs
aws logs tail /aws/lambda/ai-recoverops-log-processor --follow

# Check remediation execution
aws ssm describe-automation-executions --filters "Key=DocumentName,Values=AI-RecoverOps-Remediation"
```

## 📊 Monitoring Setup

### CloudWatch Dashboards

Create custom CloudWatch dashboard:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name "AI-RecoverOps-Production" \
  --dashboard-body file://monitoring/cloudwatch-dashboard.json
```

### Grafana Configuration

1. Access Grafana at `http://$ALB_DNS:3001`
2. Login with admin/admin123
3. Import dashboards from `deployment/grafana/dashboards/`
4. Configure data sources:
   - CloudWatch
   - Prometheus
   - PostgreSQL

### Log Aggregation

Configure centralized logging:

```bash
# Create Elasticsearch domain
aws es create-elasticsearch-domain \
  --domain-name ai-recoverops-logs \
  --elasticsearch-version 7.10 \
  --elasticsearch-cluster-config InstanceType=t3.small.elasticsearch,InstanceCount=1 \
  --ebs-options EBSEnabled=true,VolumeType=gp2,VolumeSize=20
```

## 🔒 Security Hardening

### Network Security

```bash
# Update security groups for production
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 443 \
  --source-group sg-yyyyyyyyy

# Enable VPC Flow Logs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxxxxxxxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name VPCFlowLogs
```

### Secrets Management

```bash
# Store sensitive configuration in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "ai-recoverops/database" \
  --description "Database credentials for AI-RecoverOps" \
  --secret-string '{"username":"ai_recoverops","password":"your_secure_password"}'

aws secretsmanager create-secret \
  --name "ai-recoverops/slack" \
  --description "Slack webhook URL" \
  --secret-string '{"webhook_url":"https://hooks.slack.com/services/..."}'
```

### SSL/TLS Configuration

```bash
# Request SSL certificate
aws acm request-certificate \
  --domain-name ai-recoverops.yourcompany.com \
  --validation-method DNS \
  --subject-alternative-names "*.ai-recoverops.yourcompany.com"

# Update ALB listener for HTTPS
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/ai-recoverops-alb/1234567890123456 \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/ai-recoverops-dashboard-tg/1234567890123456
```

## 🚀 Production Optimization

### Auto Scaling Configuration

```bash
# Configure ECS auto scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/ai-recoverops-cluster/ai-recoverops-ml-api \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --policy-name ai-recoverops-ml-api-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/ai-recoverops-cluster/ai-recoverops-ml-api \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

### Performance Tuning

1. **Database Optimization**:
   ```sql
   -- Connect to RDS and run optimization queries
   CREATE INDEX CONCURRENTLY idx_incidents_timestamp ON incidents(timestamp);
   CREATE INDEX CONCURRENTLY idx_incidents_severity ON incidents(severity);
   ANALYZE;
   ```

2. **Redis Configuration**:
   ```bash
   # Update Redis parameters
   aws elasticache modify-cache-parameter-group \
     --cache-parameter-group-name ai-recoverops-redis-params \
     --parameter-name-values ParameterName=maxmemory-policy,ParameterValue=allkeys-lru
   ```

3. **Lambda Optimization**:
   ```bash
   # Increase Lambda memory for better performance
   aws lambda update-function-configuration \
     --function-name ai-recoverops-log-processor \
     --memory-size 1024 \
     --timeout 300
   ```

## 🔄 Backup and Disaster Recovery

### Automated Backups

```bash
# Enable automated RDS backups
aws rds modify-db-instance \
  --db-instance-identifier ai-recoverops-db \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00"

# Create S3 backup lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket ai-recoverops-models-xxxx \
  --lifecycle-configuration file://s3-lifecycle-policy.json
```

### Cross-Region Replication

```bash
# Set up cross-region RDS read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier ai-recoverops-db-replica \
  --source-db-instance-identifier ai-recoverops-db \
  --db-instance-class db.t3.small \
  --availability-zone us-west-2a
```

## 📈 Scaling Considerations

### Horizontal Scaling
- ECS services can scale from 2 to 50 tasks
- Lambda functions support up to 1000 concurrent executions
- RDS read replicas for read-heavy workloads

### Vertical Scaling
- Upgrade ECS task definitions for more CPU/memory
- Increase RDS instance class for better database performance
- Use larger Lambda memory allocations for faster processing

### Cost Optimization
- Use Spot instances for non-critical ECS tasks
- Implement S3 Intelligent Tiering for log storage
- Schedule non-production environments to run only during business hours

## 🆘 Troubleshooting

### Common Issues

1. **ECS Tasks Failing to Start**:
   ```bash
   # Check ECS service events
   aws ecs describe-services --cluster ai-recoverops-cluster --services ai-recoverops-ml-api
   
   # Check CloudWatch logs
   aws logs tail /ecs/ai-recoverops --follow
   ```

2. **Lambda Function Timeouts**:
   ```bash
   # Increase timeout and memory
   aws lambda update-function-configuration \
     --function-name ai-recoverops-log-processor \
     --timeout 900 \
     --memory-size 1024
   ```

3. **Database Connection Issues**:
   ```bash
   # Check security groups
   aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
   
   # Test database connectivity
   psql -h your-rds-endpoint.amazonaws.com -U ai_recoverops -d ai_recoverops
   ```

### Monitoring and Alerting

Set up comprehensive monitoring:

```bash
# Create CloudWatch alarms for key metrics
aws cloudwatch put-metric-alarm \
  --alarm-name "AI-RecoverOps-API-Errors" \
  --alarm-description "High error rate in ML API" \
  --metric-name "4XXError" \
  --namespace "AWS/ApplicationELB" \
  --statistic "Sum" \
  --period 300 \
  --threshold 10 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 2
```

## ✅ Post-Deployment Checklist

- [ ] All ECS services are running and healthy
- [ ] Lambda functions are deployed and configured
- [ ] RDS database is accessible and optimized
- [ ] S3 buckets have proper permissions and lifecycle policies
- [ ] CloudWatch alarms are configured and tested
- [ ] SSL certificates are installed and valid
- [ ] Backup and disaster recovery procedures are tested
- [ ] Security groups and IAM policies follow least privilege
- [ ] Monitoring dashboards are configured and accessible
- [ ] Documentation is updated with production URLs and credentials

## 📞 Support

For deployment issues or questions:
- Create an issue in the GitHub repository
- Contact the DevOps team at devops@yourcompany.com
- Check the troubleshooting guide in the documentation

---

**Congratulations! You have successfully deployed AI-RecoverOps to production. The system is now ready to automatically detect, analyze, and remediate infrastructure incidents in your AWS environment.**