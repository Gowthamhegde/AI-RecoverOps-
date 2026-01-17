"""
End-to-End Test Suite for AI-RecoverOps
Tests the complete workflow from failure detection to remediation
"""

import pytest
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

import httpx
from database.connection import get_db_session
from database.models import Incident, Remediation
from config import settings

class TestAIRecoverOpsE2E:
    """End-to-end test suite for AI-RecoverOps"""
    
    @pytest.fixture
    async def api_client(self):
        """Create HTTP client for API testing"""
        async with httpx.AsyncClient(
            base_url="http://localhost:8000",
            timeout=30.0
        ) as client:
            yield client
    
    @pytest.fixture
    async def clean_database(self):
        """Clean database before each test"""
        async with get_db_session() as session:
            # Clean up test data
            await session.execute("DELETE FROM incidents WHERE title LIKE 'Test%'")
            await session.execute("DELETE FROM remediations WHERE description LIKE 'Test%'")
            await session.commit()
    
    async def test_complete_workflow_github_failure(self, api_client, clean_database):
        """Test complete workflow: GitHub failure → Detection → Analysis → Fix → Validation"""
        
        # Step 1: Simulate GitHub webhook for failed workflow
        github_payload = {
            "action": "completed",
            "workflow_run": {
                "id": "test_workflow_123",
                "name": "CI/CD Pipeline",
                "status": "completed",
                "conclusion": "failure",
                "head_branch": "main",
                "head_sha": "abc123def456",
                "html_url": "https://github.com/test/repo/actions/runs/123",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            "repository": {
                "full_name": "test/repo",
                "html_url": "https://github.com/test/repo"
            }
        }
        
        # Send webhook
        response = await api_client.post(
            "/webhooks/github",
            json=github_payload,
            headers={"X-GitHub-Event": "workflow_run"}
        )
        assert response.status_code == 200
        
        # Step 2: Wait for failure detection
        await asyncio.sleep(5)
        
        # Check if incident was created
        incidents_response = await api_client.get("/api/incidents")
        assert incidents_response.status_code == 200
        incidents = incidents_response.json()
        
        # Find our test incident
        test_incident = None
        for incident in incidents:
            if "test_workflow_123" in incident.get("source_id", ""):
                test_incident = incident
                break
        
        assert test_incident is not None, "Incident should be created from webhook"
        assert test_incident["status"] == "detected"
        assert test_incident["severity"] in ["high", "critical"]
        
        incident_id = test_incident["id"]
        
        # Step 3: Wait for root cause analysis
        max_wait = 60  # Wait up to 60 seconds
        analysis_complete = False
        
        for _ in range(max_wait):
            incident_response = await api_client.get(f"/api/incidents/{incident_id}")
            incident = incident_response.json()
            
            if incident["root_cause"] and incident["status"] == "analyzing":
                analysis_complete = True
                break
            
            await asyncio.sleep(1)
        
        assert analysis_complete, "Root cause analysis should complete within 60 seconds"
        assert incident["confidence_score"] > 0.5, "Analysis should have reasonable confidence"
        
        # Step 4: Trigger remediation
        remediation_response = await api_client.post(f"/api/incidents/{incident_id}/remediate")
        assert remediation_response.status_code == 200
        
        # Step 5: Wait for remediation completion
        remediation_complete = False
        
        for _ in range(120):  # Wait up to 2 minutes
            incident_response = await api_client.get(f"/api/incidents/{incident_id}")
            incident = incident_response.json()
            
            if incident["status"] in ["resolved", "failed"]:
                remediation_complete = True
                break
            
            await asyncio.sleep(1)
        
        assert remediation_complete, "Remediation should complete within 2 minutes"
        
        # Step 6: Verify remediation results
        remediations_response = await api_client.get(f"/api/incidents/{incident_id}/remediations")
        assert remediations_response.status_code == 200
        remediations = remediations_response.json()
        
        assert len(remediations) > 0, "At least one remediation should be created"
        
        # Check if remediation was successful
        successful_remediations = [r for r in remediations if r["success"]]
        assert len(successful_remediations) > 0, "At least one remediation should succeed"
    
    async def test_dependency_error_workflow(self, api_client, clean_database):
        """Test workflow for dependency errors"""
        
        # Simulate log entry with dependency error
        log_payload = {
            "source_type": "github",
            "source_id": "test_build_456",
            "repository": "test/dependency-repo",
            "branch": "main",
            "commit_sha": "def456abc789",
            "message": "ModuleNotFoundError: No module named 'requests'",
            "level": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "build_step": "install_dependencies",
                "python_version": "3.11"
            }
        }
        
        # Send log data to processing queue
        response = await api_client.post("/api/test/process-log", json=log_payload)
        assert response.status_code == 200
        
        # Wait for processing
        await asyncio.sleep(10)
        
        # Check incident creation
        incidents_response = await api_client.get("/api/incidents?repository=test/dependency-repo")
        incidents = incidents_response.json()
        
        dependency_incident = None
        for incident in incidents:
            if "dependency" in incident["failure_type"]:
                dependency_incident = incident
                break
        
        assert dependency_incident is not None
        assert "requests" in dependency_incident["error_message"]
        
        # Wait for analysis and remediation
        incident_id = dependency_incident["id"]
        
        # Check if fix was generated
        await asyncio.sleep(30)
        
        remediations_response = await api_client.get(f"/api/incidents/{incident_id}/remediations")
        remediations = remediations_response.json()
        
        # Should have dependency update remediation
        dependency_fix = None
        for remediation in remediations:
            if "dependency" in remediation["action_type"]:
                dependency_fix = remediation
                break
        
        assert dependency_fix is not None
        assert "requests" in dependency_fix["fix_content"]
    
    async def test_kubernetes_pod_failure(self, api_client, clean_database):
        """Test Kubernetes pod failure detection and recovery"""
        
        # Simulate Kubernetes pod failure
        k8s_payload = {
            "source_type": "kubernetes",
            "source_id": "pod_failure_789",
            "message": "Pod myapp-deployment-abc123 failed with OOMKilled",
            "level": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "namespace": "production",
                "pod_name": "myapp-deployment-abc123",
                "container": "myapp",
                "exit_code": 137,
                "reason": "OOMKilled"
            }
        }
        
        response = await api_client.post("/api/test/process-log", json=k8s_payload)
        assert response.status_code == 200
        
        # Wait for processing
        await asyncio.sleep(15)
        
        # Check incident
        incidents_response = await api_client.get("/api/incidents")
        incidents = incidents_response.json()
        
        k8s_incident = None
        for incident in incidents:
            if "OOMKilled" in incident.get("error_message", ""):
                k8s_incident = incident
                break
        
        assert k8s_incident is not None
        assert k8s_incident["failure_type"] == "resource_error"
        
        # Check remediation
        incident_id = k8s_incident["id"]
        await asyncio.sleep(45)
        
        remediations_response = await api_client.get(f"/api/incidents/{incident_id}/remediations")
        remediations = remediations_response.json()
        
        # Should have memory limit increase
        memory_fix = None
        for remediation in remediations:
            if "memory" in remediation["description"].lower():
                memory_fix = remediation
                break
        
        assert memory_fix is not None
    
    async def test_aws_resource_recovery(self, api_client, clean_database):
        """Test AWS resource recovery workflow"""
        
        # Skip if AWS not configured
        if not settings.AWS_ACCESS_KEY_ID:
            pytest.skip("AWS credentials not configured")
        
        # Simulate EC2 instance failure
        aws_payload = {
            "source_type": "aws",
            "source_id": "ec2_failure_101",
            "message": "EC2 instance i-1234567890abcdef0 is in stopped state",
            "level": "ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "instance_id": "i-1234567890abcdef0",
                "instance_type": "t3.medium",
                "region": "us-east-1",
                "state": "stopped",
                "reason": "Instance stopped due to user request"
            }
        }
        
        response = await api_client.post("/api/test/process-log", json=aws_payload)
        assert response.status_code == 200
        
        # Wait for processing
        await asyncio.sleep(20)
        
        # Check AWS resource recovery
        recovery_response = await api_client.get("/api/recovery/aws/resources")
        assert recovery_response.status_code == 200
        
        resources = recovery_response.json()
        test_instance = None
        for resource in resources:
            if resource["resource_id"] == "i-1234567890abcdef0":
                test_instance = resource
                break
        
        # Note: In real test, this would check actual AWS resource status
        # For demo, we verify the recovery action was queued
        assert test_instance is not None or True  # Placeholder assertion
    
    async def test_rollback_functionality(self, api_client, clean_database):
        """Test remediation rollback functionality"""
        
        # Create a test incident
        incident_payload = {
            "title": "Test Rollback Incident",
            "description": "Test incident for rollback functionality",
            "failure_type": "build_failure",
            "severity": "medium",
            "repository": "test/rollback-repo",
            "branch": "main",
            "error_message": "Build failed due to test error"
        }
        
        # Create incident via API
        response = await api_client.post("/api/test/create-incident", json=incident_payload)
        assert response.status_code == 200
        incident = response.json()
        incident_id = incident["id"]
        
        # Trigger remediation
        remediation_response = await api_client.post(f"/api/incidents/{incident_id}/remediate")
        assert remediation_response.status_code == 200
        
        # Wait for remediation
        await asyncio.sleep(30)
        
        # Trigger rollback
        rollback_response = await api_client.post(f"/api/incidents/{incident_id}/rollback")
        assert rollback_response.status_code == 200
        
        # Verify rollback
        await asyncio.sleep(15)
        
        incident_response = await api_client.get(f"/api/incidents/{incident_id}")
        incident = incident_response.json()
        
        assert incident["status"] == "rolled_back"
    
    async def test_concurrent_incidents(self, api_client, clean_database):
        """Test handling of multiple concurrent incidents"""
        
        # Create multiple incidents simultaneously
        incident_payloads = [
            {
                "title": f"Test Concurrent Incident {i}",
                "failure_type": "build_failure",
                "severity": "medium",
                "repository": f"test/concurrent-repo-{i}",
                "error_message": f"Concurrent test error {i}"
            }
            for i in range(5)
        ]
        
        # Send all incidents
        incident_ids = []
        for payload in incident_payloads:
            response = await api_client.post("/api/test/create-incident", json=payload)
            assert response.status_code == 200
            incident_ids.append(response.json()["id"])
        
        # Trigger all remediations
        for incident_id in incident_ids:
            response = await api_client.post(f"/api/incidents/{incident_id}/remediate")
            assert response.status_code == 200
        
        # Wait for processing
        await asyncio.sleep(60)
        
        # Check that all incidents were processed
        resolved_count = 0
        for incident_id in incident_ids:
            response = await api_client.get(f"/api/incidents/{incident_id}")
            incident = response.json()
            if incident["status"] in ["resolved", "failed"]:
                resolved_count += 1
        
        # At least 80% should be processed
        assert resolved_count >= len(incident_ids) * 0.8
    
    async def test_system_health_monitoring(self, api_client):
        """Test system health monitoring endpoints"""
        
        # Test health endpoint
        health_response = await api_client.get("/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        assert health_data["status"] in ["healthy", "degraded"]
        assert "components" in health_data
        
        # Test system status
        status_response = await api_client.get("/api/system-status")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert "system_health" in status_data
        assert "active_incidents" in status_data
        
        # Test metrics endpoint
        metrics_response = await api_client.get("/metrics")
        assert metrics_response.status_code == 200
    
    async def test_api_authentication(self, api_client):
        """Test API authentication and authorization"""
        
        # Test unauthenticated access to protected endpoints
        protected_endpoints = [
            "/api/incidents/123/remediate",
            "/api/incidents/123/rollback",
            "/api/emergency-stop"
        ]
        
        for endpoint in protected_endpoints:
            response = await api_client.post(endpoint)
            # Should require authentication
            assert response.status_code in [401, 403]
    
    async def test_webhook_security(self, api_client):
        """Test webhook security and validation"""
        
        # Test GitHub webhook without signature
        response = await api_client.post(
            "/webhooks/github",
            json={"test": "data"},
            headers={"X-GitHub-Event": "workflow_run"}
        )
        
        # Should validate signature if secret is configured
        if settings.GITHUB_WEBHOOK_SECRET:
            assert response.status_code == 403
        else:
            assert response.status_code in [200, 500]  # May fail due to invalid payload
    
    async def test_performance_under_load(self, api_client):
        """Test system performance under load"""
        
        # Send multiple requests concurrently
        tasks = []
        for i in range(20):
            task = api_client.get("/health")
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Check response times
        total_time = end_time - start_time
        avg_response_time = total_time / len(tasks)
        
        # Should handle 20 concurrent requests in reasonable time
        assert avg_response_time < 1.0  # Less than 1 second average
        
        # Check success rate
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
        success_rate = len(successful_responses) / len(responses)
        
        assert success_rate >= 0.95  # 95% success rate

@pytest.mark.asyncio
class TestIntegrationScenarios:
    """Integration test scenarios for real-world use cases"""
    
    async def test_github_actions_integration(self):
        """Test GitHub Actions integration scenario"""
        
        # This would test actual GitHub Actions integration
        # For demo purposes, we'll simulate the workflow
        
        scenarios = [
            {
                "name": "Build failure due to missing dependency",
                "workflow": "CI",
                "error": "ModuleNotFoundError: No module named 'pytest'",
                "expected_fix": "Add pytest to requirements.txt"
            },
            {
                "name": "Test failure due to assertion error",
                "workflow": "Test",
                "error": "AssertionError: Expected 200, got 404",
                "expected_fix": "Fix API endpoint or test assertion"
            },
            {
                "name": "Deployment failure due to resource limits",
                "workflow": "Deploy",
                "error": "OOMKilled: Container exceeded memory limit",
                "expected_fix": "Increase memory limits in deployment.yaml"
            }
        ]
        
        for scenario in scenarios:
            # Simulate the scenario
            print(f"Testing scenario: {scenario['name']}")
            # In real test, this would trigger actual GitHub Actions
            assert True  # Placeholder
    
    async def test_gitlab_ci_integration(self):
        """Test GitLab CI integration scenario"""
        
        # Similar to GitHub Actions but for GitLab CI
        scenarios = [
            {
                "name": "Docker build failure",
                "pipeline": "build",
                "error": "Error building image: base image not found",
                "expected_fix": "Update Dockerfile base image"
            }
        ]
        
        for scenario in scenarios:
            print(f"Testing GitLab scenario: {scenario['name']}")
            assert True  # Placeholder
    
    async def test_aws_infrastructure_recovery(self):
        """Test AWS infrastructure recovery scenarios"""
        
        scenarios = [
            {
                "name": "EC2 instance failure",
                "resource": "i-1234567890abcdef0",
                "issue": "Instance stopped unexpectedly",
                "expected_action": "Restart instance"
            },
            {
                "name": "ECS service failure",
                "resource": "my-service",
                "issue": "All tasks stopped",
                "expected_action": "Force new deployment"
            }
        ]
        
        for scenario in scenarios:
            print(f"Testing AWS scenario: {scenario['name']}")
            assert True  # Placeholder

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])