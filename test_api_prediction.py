#!/usr/bin/env python3
"""
Test the AI-RecoverOps API prediction functionality
"""

import requests
import json
from datetime import datetime

def test_api_prediction():
    """Test the API prediction endpoint"""
    
    print("🧪 Testing AI-RecoverOps API Prediction")
    print("=" * 50)
    
    # Test data - simulate various log entries
    test_logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "log_level": "ERROR",
            "service": "web-server",
            "aws_service": "ec2",
            "instance_id": "i-1234567890abcdef0",
            "message": "High CPU usage detected: 94.2% - system overloaded",
            "source_ip": "10.0.1.100",
            "region": "us-east-1",
            "environment": "production",
            "metadata": {
                "cpu_usage": 94.2,
                "memory_usage": 78.5,
                "disk_usage": 45.2
            }
        },
        {
            "timestamp": datetime.now().isoformat(),
            "log_level": "FATAL",
            "service": "database",
            "aws_service": "rds",
            "instance_id": "db-instance-1",
            "message": "Database connection pool exhausted - max connections reached",
            "region": "us-east-1",
            "environment": "production",
            "metadata": {
                "active_connections": 98,
                "max_connections": 100
            }
        },
        {
            "timestamp": datetime.now().isoformat(),
            "log_level": "ERROR",
            "service": "api-gateway",
            "aws_service": "ecs",
            "instance_id": "ecs-task-123",
            "message": "Container memory usage critical - OOM kill imminent",
            "region": "us-east-1",
            "environment": "production",
            "metadata": {
                "memory_usage": 97.8,
                "container_id": "abc123def456"
            }
        }
    ]
    
    # Prepare request
    prediction_request = {
        "logs": test_logs,
        "model_type": "ensemble"
    }
    
    try:
        # Make API request
        print("📡 Sending prediction request to API...")
        response = requests.post(
            "http://localhost:8000/predict",
            json=prediction_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Prediction successful!")
            print(f"⏱️  Processing time: {result['processing_time_ms']:.2f}ms")
            print(f"🤖 Model used: {result['model_used']}")
            print("\n📊 Predictions:")
            
            for i, prediction in enumerate(result['predictions'], 1):
                print(f"\n   Log {i}:")
                print(f"   🔍 Incident Type: {prediction['incident_type']}")
                print(f"   📊 Confidence: {prediction['confidence']:.2f}")
                print(f"   🛠️  Recommended Action: {prediction['recommended_action']}")
                print(f"   ⚠️  Severity: {prediction['severity']}")
                
                if 'incident_id' in prediction:
                    print(f"   🆔 Incident ID: {prediction['incident_id']}")
            
            print(f"\n✅ Successfully processed {len(result['predictions'])} log entries")
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_dashboard_data():
    """Test the dashboard data endpoint"""
    
    print("\n🎯 Testing Dashboard Data Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/api/dashboard", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Dashboard data retrieved successfully!")
            print(f"📊 Total Incidents: {data['stats']['totalIncidents']}")
            print(f"🚨 Active Incidents: {data['stats']['activeIncidents']}")
            print(f"✅ Resolved Today: {data['stats']['resolvedToday']}")
            print(f"🤖 Auto-Remediation Rate: {data['stats']['autoRemediationRate']}%")
            print(f"⏱️  Avg Resolution Time: {data['stats']['avgResolutionTime']}s")
            print(f"💚 System Health: {data['stats']['systemHealth']}%")
            
        else:
            print(f"❌ Dashboard request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")

def test_incidents_endpoint():
    """Test the incidents endpoint"""
    
    print("\n📋 Testing Incidents Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/api/incidents", timeout=10)
        
        if response.status_code == 200:
            incidents = response.json()
            
            print(f"✅ Retrieved {len(incidents)} incidents")
            
            if incidents:
                print("\n🔍 Recent incidents:")
                for incident in incidents[:3]:  # Show first 3
                    print(f"   • {incident['type']} - {incident['severity']} - {incident['description'][:50]}...")
            else:
                print("   No incidents found")
                
        else:
            print(f"❌ Incidents request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing incidents: {e}")

if __name__ == "__main__":
    test_api_prediction()
    test_dashboard_data()
    test_incidents_endpoint()
    
    print("\n🎉 API Testing Complete!")
    print("\n💡 Next steps:")
    print("   • Visit http://localhost:8000/docs for interactive API docs")
    print("   • Use the prediction endpoint to test your own log data")
    print("   • Check the incidents endpoint for detected issues")