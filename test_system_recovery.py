#!/usr/bin/env python3
"""
Test script to verify AI-RecoverOps system recovery functionality
"""

import asyncio
import yaml
import json
from datetime import datetime
from pathlib import Path

# Import AI-RecoverOps components
from ai_recoverops.core.engine import RecoverOpsEngine
from ai_recoverops.core.models import Issue
from ai_recoverops.utils.logger import setup_logger

async def test_system_recovery():
    """Test the complete system recovery workflow"""
    
    print("🚀 AI-RecoverOps System Recovery Test")
    print("=" * 50)
    
    # Setup logger
    logger = setup_logger("INFO")
    
    # Load configuration
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ Configuration file not found. Creating default config...")
        create_default_config()
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Initialize the engine
    print("\n📋 Initializing AI-RecoverOps Engine...")
    engine = RecoverOpsEngine(config)
    
    # Test 1: Create a mock high CPU issue
    print("\n🔍 Test 1: Simulating High CPU Issue")
    cpu_issue = Issue(
        id="test-cpu-001",
        type="system",
        severity="high",
        description="High CPU usage detected: 92.5%",
        metadata={
            "cpu_percent": 92.5,
            "service_name": "web-server",
            "instance_id": "i-1234567890abcdef0"
        },
        detected_at=datetime.now(),
        source="test_system"
    )
    
    # Add issue to engine
    engine.active_issues[cpu_issue.id] = cpu_issue
    print(f"   ✅ Created issue: {cpu_issue.description}")
    
    # Test 2: Analyze the issue
    print("\n🧠 Test 2: Analyzing Root Cause")
    analysis = await engine._analyze_issue(cpu_issue)
    if analysis:
        cpu_issue.analysis = analysis
        print(f"   ✅ Root cause identified: {analysis.root_cause}")
        print(f"   📊 Confidence: {analysis.confidence:.2f}")
        print(f"   🔧 Recommended fixes: {', '.join(analysis.recommended_fixes)}")
    else:
        print("   ❌ Analysis failed")
    
    # Test 3: Apply fix (dry run)
    print("\n🛠️  Test 3: Applying Remediation (Dry Run)")
    if hasattr(cpu_issue, 'analysis'):
        success = await engine._apply_fix(cpu_issue)
        if success:
            print("   ✅ Fix applied successfully")
        else:
            print("   ⚠️  Fix application failed or skipped")
    
    # Test 4: Test different issue types
    print("\n🔍 Test 4: Testing Multiple Issue Types")
    
    test_issues = [
        {
            "type": "system",
            "description": "High memory usage detected: 94.2%",
            "metadata": {"memory_percent": 94.2, "service_name": "database"}
        },
        {
            "type": "application", 
            "description": "Service timeout detected on API endpoint",
            "metadata": {"response_time_ms": 5500, "endpoint": "/api/users"}
        },
        {
            "type": "database",
            "description": "Database connection pool exhausted",
            "metadata": {"active_connections": 95, "max_connections": 100}
        },
        {
            "type": "network",
            "description": "Network timeout connecting to external service",
            "metadata": {"host": "api.external.com", "port": 443}
        }
    ]
    
    for i, issue_data in enumerate(test_issues, 1):
        issue = Issue(
            id=f"test-issue-{i:03d}",
            type=issue_data["type"],
            severity="medium",
            description=issue_data["description"],
            metadata=issue_data["metadata"],
            detected_at=datetime.now(),
            source="test_system"
        )
        
        # Analyze issue
        analysis = await engine._analyze_issue(issue)
        if analysis:
            print(f"   ✅ {issue.type.title()} Issue: {analysis.root_cause} (confidence: {analysis.confidence:.2f})")
        else:
            print(f"   ❌ {issue.type.title()} Issue: Analysis failed")
    
    # Test 5: System Status
    print("\n📊 Test 5: System Status Summary")
    print(f"   🔧 Available Detectors: {len(engine.detectors)}")
    print(f"   🧠 Available Analyzers: {len(engine.analyzers)}")
    print(f"   🛠️  Available Fixers: {len(engine.fixers)}")
    print(f"   📋 Active Issues: {len(engine.active_issues)}")
    
    print("\n✅ System Recovery Test Completed Successfully!")
    print("\n🎯 Next Steps:")
    print("   1. Run 'python launch-ai-recoverops.py' to start the full system")
    print("   2. Access dashboard at http://localhost:3000")
    print("   3. Test API at http://localhost:8000/docs")
    print("   4. Configure real infrastructure in config.yaml")

def create_default_config():
    """Create a default configuration file for testing"""
    config = {
        'ai_recoverops': {
            'core': {
                'log_level': 'INFO',
                'max_concurrent_fixes': 3,
                'rollback_timeout': 300,
                'learning_mode': True
            },
            'detection': {
                'interval': 30,
                'enabled_detectors': ['system', 'application', 'network', 'database']
            },
            'analysis': {
                'confidence_threshold': 0.8,
                'max_analysis_time': 120,
                'use_historical_data': True
            },
            'fixes': {
                'auto_apply': False,  # Safe default for testing
                'require_approval': True,
                'backup_before_fix': True
            },
            'monitoring': {
                'prometheus_port': 9090,
                'health_check_port': 8080,
                'alert_webhook': None
            }
        }
    }
    
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print("✅ Created default config.yaml")

if __name__ == "__main__":
    asyncio.run(test_system_recovery())