# System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD INFRASTRUCTURE                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   LOG SOURCES   │  │   LOG SOURCES   │  │   LOG SOURCES   │                │
│  │                 │  │                 │  │                 │                │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │                │
│  │ │ CloudWatch  │ │  │ │    ECS      │ │  │ │    RDS      │ │                │
│  │ │    Logs     │ │  │ │  Container  │ │  │ │   Logs      │ │                │
│  │ └─────────────┘ │  │ │    Logs     │ │  │ └─────────────┘ │                │
│  │ ┌─────────────┐ │  │ └─────────────┘ │  │ ┌─────────────┐ │                │
│  │ │    EC2      │ │  │ ┌─────────────┐ │  │ │   Lambda    │ │                │
│  │ │   Logs      │ │  │ │    ALB      │ │  │ │    Logs     │ │                │
│  │ └─────────────┘ │  │ │   Logs      │ │  │ └─────────────┘ │                │
│  └─────────────────┘  │ └─────────────┘ │  └─────────────────┘                │
│           │            └─────────────────┘           │                         │
│           └─────────────────────┬─────────────────────┘                         │
│                                 │                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      DATA COLLECTION LAYER                             │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │   │
│  │  │   CloudWatch    │───▶│     Kinesis     │───▶│       S3        │    │   │
│  │  │   Log Groups    │    │  Data Streams   │    │   Raw Logs      │    │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    │   │
│  │           │                       │                       │            │   │
│  │           └───────────────────────┼───────────────────────┘            │   │
│  │                                   │                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Lambda Log Processor                        │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │   │   │
│  │  │  │   Parse     │  │   Filter    │  │      Enrich with        │ │   │   │
│  │  │  │    Logs     │─▶│   & Clean   │─▶│    Metadata & Tags      │ │   │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      PREPROCESSING LAYER                               │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │   │
│  │  │   Feature       │───▶│   Vectorization │───▶│   Batch Data    │    │   │
│  │  │  Extraction     │    │   (TF-IDF +     │    │   for Training  │    │   │
│  │  │                 │    │   Embeddings)   │    │                 │    │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        ML ANALYSIS LAYER                               │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │   │
│  │  │   XGBoost       │    │      LSTM       │    │   Ensemble      │    │   │
│  │  │  Classifier     │───▶│   Sequence      │───▶│   Predictor     │    │   │
│  │  │                 │    │    Model        │    │                 │    │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    │   │
│  │           │                       │                       │            │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    FastAPI Inference Service                  │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │   │   │
│  │  │  │   Model     │  │ Confidence  │  │    Remediation          │ │   │   │
│  │  │  │  Loading    │─▶│  Scoring    │─▶│   Recommendation        │ │   │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    AUTO-REMEDIATION ENGINE                             │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │   │
│  │  │   Decision      │───▶│      SSM        │───▶│   Execution     │    │   │
│  │  │    Engine       │    │   Automation    │    │    Monitor      │    │   │
│  │  │                 │    │   Documents     │    │                 │    │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    │   │
│  │           │                       │                       │            │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Remediation Scripts                         │   │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │   │   │
│  │  │  │   Service   │  │ Container   │  │      Database           │ │   │   │
│  │  │  │  Restart    │  │  Restart    │  │    Connection           │ │   │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      NOTIFICATION LAYER                                │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │   │
│  │  │      SNS        │───▶│     Slack       │    │     Email       │    │   │
│  │  │   Publisher     │    │   Webhook       │    │   Notifications │    │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        MONITORING & DASHBOARD                          │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │   │
│  │  │   CloudWatch    │───▶│    Grafana      │───▶│     React       │    │   │
│  │  │    Metrics      │    │   Dashboard     │    │   Frontend      │    │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Log Source Layer
- **CloudWatch Logs**: Centralized logging for all AWS services
- **EC2 Instance Logs**: Application and system logs from EC2 instances
- **ECS Container Logs**: Docker container stdout/stderr logs
- **RDS Logs**: Database error logs, slow query logs, general logs
- **Lambda Logs**: Function execution logs and errors
- **ALB Access Logs**: Load balancer request/response logs

### 2. Data Collection Layer
- **CloudWatch Log Groups**: Organized log streams by service/application
- **Kinesis Data Streams**: Real-time log streaming with auto-scaling
- **S3 Storage**: Durable storage for raw logs and processed data
- **Lambda Log Processor**: Serverless log parsing and enrichment

### 3. Preprocessing Layer
- **Feature Extraction**: Extract timestamps, error codes, service names, metrics
- **Text Vectorization**: TF-IDF and word embeddings for log messages
- **Data Normalization**: Standardize log formats across different sources
- **Batch Processing**: Prepare training datasets for ML models

### 4. ML Analysis Layer
- **XGBoost Classifier**: Gradient boosting for structured log features
- **LSTM Sequence Model**: Deep learning for temporal log patterns
- **Ensemble Predictor**: Combine multiple models for better accuracy
- **FastAPI Service**: RESTful API for real-time inference

### 5. Auto-Remediation Engine
- **Decision Engine**: Evaluate confidence scores and safety rules
- **SSM Automation**: AWS Systems Manager for secure script execution
- **Remediation Scripts**: Pre-built solutions for common issues
- **Execution Monitor**: Track remediation progress and success rates

### 6. Notification Layer
- **SNS Integration**: Publish alerts to multiple channels
- **Slack Webhooks**: Real-time team notifications
- **Email Alerts**: Detailed incident reports and summaries

### 7. Monitoring & Dashboard
- **CloudWatch Metrics**: System performance and health metrics
- **Grafana Dashboard**: Operational insights and visualizations
- **React Frontend**: Interactive incident management interface

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION DEPLOYMENT                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   ECS Cluster   │    │   Lambda Layer  │                    │
│  │                 │    │                 │                    │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │                    │
│  │ │  FastAPI    │ │    │ │Log Processor│ │                    │
│  │ │  Service    │ │    │ └─────────────┘ │                    │
│  │ └─────────────┘ │    │ ┌─────────────┐ │                    │
│  │ ┌─────────────┐ │    │ │ Remediation │ │                    │
│  │ │  Dashboard  │ │    │ │  Executor   │ │                    │
│  │ │   React     │ │    │ └─────────────┘ │                    │
│  │ └─────────────┘ │    │ ┌─────────────┐ │                    │
│  └─────────────────┘    │ │Notification │ │                    │
│                         │ │  Handler    │ │                    │
│  ┌─────────────────┐    │ └─────────────┘ │                    │
│  │      RDS        │    └─────────────────┘                    │
│  │   PostgreSQL    │                                           │
│  │                 │    ┌─────────────────┐                    │
│  │ ┌─────────────┐ │    │   S3 Buckets    │                    │
│  │ │  Incident   │ │    │                 │                    │
│  │ │  History    │ │    │ ┌─────────────┐ │                    │
│  │ └─────────────┘ │    │ │   Models    │ │                    │
│  │ ┌─────────────┐ │    │ └─────────────┘ │                    │
│  │ │   Model     │ │    │ ┌─────────────┐ │                    │
│  │ │ Metadata    │ │    │ │  Raw Logs   │ │                    │
│  │ └─────────────┘ │    │ └─────────────┘ │                    │
│  └─────────────────┘    │ ┌─────────────┐ │                    │
│                         │ │ Processed   │ │                    │
│                         │ │    Data     │ │                    │
│                         │ └─────────────┘ │                    │
│                         └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Security Architecture

- **IAM Roles**: Least-privilege access for all components
- **VPC Security**: Private subnets for sensitive components
- **Encryption**: At-rest and in-transit encryption for all data
- **Audit Logging**: Comprehensive CloudTrail logging
- **Secret Management**: AWS Secrets Manager for credentials