# AI-RecoverOps Project Structure

## 📁 Clean Project Organization

```
AI-RecoverOps/
├── 📁 backend/                          # Production FastAPI Backend
│   ├── 📁 ai_engine/                    # AI/ML Components
│   │   ├── failure_detector.py          # Failure detection engine
│   │   ├── root_cause_analyzer.py       # LLM-powered analysis
│   │   └── fix_generator.py             # Automated fix generation
│   ├── 📁 api/                          # API Routes
│   │   └── 📁 routes/                   # Route modules
│   │       ├── webhooks.py              # Webhook endpoints
│   │       └── incidents.py             # Incident management
│   ├── 📁 database/                     # Database Layer
│   │   ├── models.py                    # SQLAlchemy models
│   │   ├── connection.py                # Database connection
│   │   └── redis_client.py              # Redis client
│   ├── 📁 pipeline_monitor/             # CI/CD Monitoring
│   │   └── webhook_listener.py          # Webhook processing
│   ├── 📁 remediation/                  # Remediation Engine
│   │   └── executor.py                  # Fix execution
│   ├── config.py                        # Configuration management
│   └── main.py                          # FastAPI application
│
├── 📁 dashboard-v2/                     # Production React Dashboard
│   ├── 📁 src/
│   │   ├── 📁 pages/                    # Dashboard pages
│   │   │   └── Dashboard.js             # Main dashboard
│   │   ├── 📁 services/                 # API services
│   │   │   └── apiService.js            # API client
│   │   └── App.js                       # Main React app
│   └── package.json                     # Dependencies
│
├── 📁 deployment/                       # Deployment Configurations
│   ├── 📁 docker/                       # Docker deployment
│   │   ├── Dockerfile                   # Production Docker image
│   │   └── docker-compose.yml           # Complete stack
│   ├── 📁 kubernetes/                   # Kubernetes deployment
│   │   └── ai-recoverops-deployment.yaml # K8s manifests
│   └── 📁 terraform/                    # Infrastructure as Code
│       └── main.tf                      # Terraform config
│
├── 📁 cicd-integrations/                # CI/CD Platform Integrations
│   └── 📁 github-actions/               # GitHub Actions
│       └── ai-recoverops-integration.yml # Workflow integration
│
├── 📁 docs/                             # Comprehensive Documentation
│   ├── README.md                        # Main documentation
│   └── INSTALLATION.md                  # Installation guide
│
├── 📁 tests/                            # Test Suite
│   └── test_end_to_end.py               # E2E tests
│
├── 📁 demo/                             # Demo & Simulation
│   └── simulate_failures.py             # Failure simulation
│
├── 📁 ai_recoverops/                    # Legacy Core (Kept for compatibility)
│   ├── 📁 analyzers/                    # Analysis components
│   ├── 📁 detectors/                    # Detection components
│   ├── 📁 fixers/                       # Fix components
│   ├── 📁 core/                         # Core models
│   └── __main__.py                      # CLI entry point
│
├── 📁 aws/                              # AWS-specific components
│   ├── 📁 lambda_functions/             # Lambda functions
│   └── 📁 ssm_automation/               # SSM runbooks
│
├── 📁 notifications/                    # Notification services
│   └── slack_notifier.py                # Slack integration
│
├── 📁 ml/                               # Machine Learning
│   └── model_training.py                # Model training
│
├── 📁 data/                             # Data generation
│   └── generate_synthetic_logs.py       # Synthetic data
│
├── 📁 .github/                          # GitHub configuration
│   └── 📁 workflows/                    # GitHub Actions
│       └── ci-cd.yml                    # CI/CD pipeline
│
├── PRODUCTION_ARCHITECTURE.md           # Architecture documentation
├── CHANGELOG.md                         # Version history
├── LICENSE                              # MIT License
├── .gitignore                           # Git ignore rules
├── pyproject.toml                       # Python project config
├── requirements.txt                     # Python dependencies
├── setup.py                             # Package setup
└── README.md                            # Project README
```

## 🎯 Key Components

### **Production Backend** (`backend/`)
- **FastAPI Application**: Modern async Python web framework
- **AI Engine**: GPT-4 powered failure analysis and fix generation
- **Database Layer**: PostgreSQL with SQLAlchemy ORM
- **Redis Integration**: Message queues and caching
- **Webhook Processing**: Real-time CI/CD platform integration

### **Production Dashboard** (`dashboard-v2/`)
- **React 18**: Modern React with hooks and context
- **Real-time Updates**: WebSocket integration for live monitoring
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Controls**: Manual remediation and system management

### **Deployment Ready** (`deployment/`)
- **Docker**: Multi-stage production builds
- **Kubernetes**: Complete manifests with RBAC and scaling
- **Terraform**: Infrastructure as Code for AWS
- **Docker Compose**: Full stack deployment

### **CI/CD Integration** (`cicd-integrations/`)
- **GitHub Actions**: Workflow failure detection and auto-fixing
- **GitLab CI**: Pipeline integration and remediation
- **Jenkins**: Build failure handling

### **Comprehensive Testing** (`tests/`)
- **End-to-End Tests**: Complete workflow validation
- **Integration Tests**: Multi-component testing
- **Performance Tests**: Load and stress testing

### **Demo & Simulation** (`demo/`)
- **Failure Simulation**: Realistic DevOps failure scenarios
- **Interactive Demo**: Live demonstration capabilities
- **Monitoring Tools**: Real-time resolution tracking

## 🚀 Quick Start

1. **Clone Repository**:
   ```bash
   git clone https://github.com/ai-recoverops/ai-recoverops.git
   cd ai-recoverops
   ```

2. **Docker Deployment** (Recommended):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   docker-compose -f deployment/docker/docker-compose.yml up -d
   ```

3. **Access Points**:
   - Dashboard: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Demo the System**:
   ```bash
   python demo/simulate_failures.py simulate --count 5 --monitor
   ```

## 📚 Documentation

- **Main Documentation**: `docs/README.md`
- **Installation Guide**: `docs/INSTALLATION.md`
- **Architecture Overview**: `PRODUCTION_ARCHITECTURE.md`
- **API Documentation**: Available at `/docs` endpoint

## 🧪 Testing

```bash
# Run end-to-end tests
pytest tests/test_end_to_end.py -v

# Run failure simulation
python demo/simulate_failures.py simulate --type all --count 3
```

This clean structure provides a production-ready AI-RecoverOps system with clear separation of concerns and comprehensive documentation.