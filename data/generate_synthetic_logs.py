#!/usr/bin/env python3
"""
Generate synthetic log data for AI-RecoverOps training
"""

import json
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

class SyntheticLogGenerator:
    def __init__(self):
        self.incident_types = {
            'high_cpu': {
                'patterns': [
                    'CPU usage exceeded 90% for 5 minutes',
                    'High CPU utilization detected on instance i-{instance_id}',
                    'Process consuming excessive CPU: {process_name}',
                    'Load average: {load_avg} exceeds threshold',
                    'CPU throttling detected on container {container_id}'
                ],
                'services': ['web-server', 'api-gateway', 'worker-service', 'database'],
                'severity': ['medium', 'high', 'critical'],
                'remediation': ['restart_service', 'scale_horizontally', 'optimize_code']
            },
            'memory_leak': {
                'patterns': [
                    'Memory usage increased to {memory_percent}% on {service_name}',
                    'OutOfMemoryError in application {app_name}',
                    'Container {container_id} killed due to OOM',
                    'Java heap space exceeded on {service_name}',
                    'Memory allocation failed for process {process_id}'
                ],
                'services': ['java-app', 'nodejs-service', 'python-worker', 'cache-service'],
                'severity': ['high', 'critical'],
                'remediation': ['restart_service', 'increase_memory_limit', 'optimize_memory_usage']
            },
            'disk_full': {
                'patterns': [
                    'Disk usage at {disk_percent}% on volume {volume_id}',
                    'No space left on device /dev/{device}',
                    'Disk full warning: {available_space}MB remaining',
                    'Log rotation failed due to insufficient disk space',
                    'Database write failed: disk full on {mount_point}'
                ],
                'services': ['log-service', 'database', 'file-storage', 'backup-service'],
                'severity': ['medium', 'high', 'critical'],
                'remediation': ['clean_logs', 'expand_volume', 'archive_old_data']
            },
            'permission_denied': {
                'patterns': [
                    'Permission denied accessing {resource_path}',
                    'Access denied for user {username} to {resource}',
                    'IAM role {role_name} lacks permission for {action}',
                    'S3 bucket {bucket_name} access forbidden',
                    'Database connection failed: insufficient privileges'
                ],
                'services': ['auth-service', 'file-service', 's3-connector', 'database'],
                'severity': ['medium', 'high'],
                'remediation': ['fix_permissions', 'update_iam_policy', 'rotate_credentials']
            },
            'service_crash': {
                'patterns': [
                    'Service {service_name} crashed with exit code {exit_code}',
                    'Unexpected termination of process {process_id}',
                    'Application {app_name} stopped responding',
                    'Container {container_id} exited unexpectedly',
                    'Fatal error in {service_name}: {error_message}'
                ],
                'services': ['web-server', 'api-service', 'worker', 'scheduler'],
                'severity': ['high', 'critical'],
                'remediation': ['restart_service', 'rollback_deployment', 'check_dependencies']
            },
            'port_in_use': {
                'patterns': [
                    'Port {port} already in use by process {process_id}',
                    'Failed to bind to address {ip}:{port}',
                    'Socket bind failed: address already in use',
                    'Cannot start service on port {port}: port occupied',
                    'Network port {port} conflict detected'
                ],
                'services': ['web-server', 'database', 'cache-service', 'monitoring'],
                'severity': ['medium', 'high'],
                'remediation': ['kill_conflicting_process', 'change_port', 'restart_service']
            },
            'db_connection_failure': {
                'patterns': [
                    'Database connection timeout to {db_host}:{db_port}',
                    'Connection pool exhausted for database {db_name}',
                    'Failed to connect to PostgreSQL: {error_message}',
                    'MySQL connection refused on {db_host}',
                    'Redis connection failed: {redis_error}'
                ],
                'services': ['database', 'api-service', 'cache-service', 'worker'],
                'severity': ['high', 'critical'],
                'remediation': ['restart_database', 'increase_connection_pool', 'check_network']
            },
            'container_oom': {
                'patterns': [
                    'Container {container_id} killed by OOM killer',
                    'Memory limit exceeded for container {container_name}',
                    'Pod {pod_name} evicted due to memory pressure',
                    'Docker container {container_id} OOMKilled',
                    'Kubernetes pod restart due to memory limit'
                ],
                'services': ['microservice-a', 'microservice-b', 'worker-pod', 'api-pod'],
                'severity': ['high', 'critical'],
                'remediation': ['increase_memory_limit', 'optimize_memory_usage', 'restart_container']
            }
        }
        
        self.aws_services = ['ec2', 'ecs', 'rds', 'lambda', 'alb', 'cloudwatch']
        self.log_levels = ['INFO', 'WARN', 'ERROR', 'FATAL', 'DEBUG']
        
    def generate_log_entry(self, incident_type: str) -> Dict[str, Any]:
        """Generate a single synthetic log entry"""
        config = self.incident_types[incident_type]
        
        # Generate timestamp (last 30 days)
        base_time = datetime.now() - timedelta(days=random.randint(0, 30))
        timestamp = base_time + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        # Select pattern and fill variables
        pattern = random.choice(config['patterns'])
        
        # Generate realistic values for pattern variables
        variables = {
            'instance_id': f"{random.choice(['abc123def', '456ghi789', 'xyz987uvw'])}",
            'process_name': random.choice(['java', 'python', 'nginx', 'postgres', 'redis']),
            'load_avg': f"{random.uniform(5.0, 15.0):.2f}",
            'container_id': f"{uuid.uuid4().hex[:12]}",
            'memory_percent': random.randint(85, 99),
            'service_name': random.choice(config['services']),
            'app_name': random.choice(['payment-service', 'user-service', 'order-service']),
            'process_id': random.randint(1000, 9999),
            'disk_percent': random.randint(85, 99),
            'volume_id': f"vol-{random.choice(['abc123', 'def456', 'ghi789'])}",
            'device': random.choice(['sda1', 'sdb1', 'nvme0n1p1']),
            'available_space': random.randint(10, 500),
            'mount_point': random.choice(['/var/log', '/opt/data', '/tmp']),
            'resource_path': random.choice(['/var/log/app.log', '/etc/config', '/opt/data']),
            'username': random.choice(['app-user', 'service-account', 'admin']),
            'resource': random.choice(['s3://bucket/file', 'database.table', 'api/endpoint']),
            'role_name': random.choice(['app-role', 'service-role', 'lambda-role']),
            'action': random.choice(['s3:GetObject', 'rds:Connect', 'ec2:DescribeInstances']),
            'bucket_name': random.choice(['app-logs', 'user-data', 'backup-storage']),
            'exit_code': random.choice([1, 2, 130, 137, 143]),
            'error_message': random.choice(['null pointer exception', 'connection refused', 'timeout']),
            'port': random.choice([80, 443, 3000, 5432, 6379, 8080]),
            'ip': f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            'db_host': f"db-{random.choice(['prod', 'staging', 'dev'])}.{random.choice(['us-east-1', 'us-west-2'])}.rds.amazonaws.com",
            'db_port': random.choice([5432, 3306, 6379]),
            'db_name': random.choice(['users', 'orders', 'products', 'analytics']),
            'redis_error': random.choice(['connection timeout', 'auth failed', 'max clients reached']),
            'container_name': random.choice(['web-app', 'api-service', 'worker', 'cache']),
            'pod_name': f"{random.choice(['web', 'api', 'worker'])}-{random.randint(1000, 9999)}"
        }
        
        # Fill pattern with variables
        try:
            message = pattern.format(**variables)
        except KeyError:
            message = pattern
            
        return {
            'timestamp': timestamp.isoformat(),
            'log_level': random.choice(['ERROR', 'FATAL', 'WARN']),
            'service': random.choice(config['services']),
            'aws_service': random.choice(self.aws_services),
            'instance_id': f"i-{random.choice(['abc123def456', '789ghi012jkl', 'mno345pqr678'])}",
            'message': message,
            'incident_type': incident_type,
            'severity': random.choice(config['severity']),
            'recommended_action': random.choice(config['remediation']),
            'source_ip': f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            'region': random.choice(['us-east-1', 'us-west-2', 'eu-west-1']),
            'environment': random.choice(['production', 'staging', 'development']),
            'correlation_id': str(uuid.uuid4()),
            'metadata': {
                'cpu_usage': random.uniform(0, 100) if 'cpu' in incident_type else None,
                'memory_usage': random.uniform(0, 100) if 'memory' in incident_type else None,
                'disk_usage': random.uniform(0, 100) if 'disk' in incident_type else None,
                'response_time': random.uniform(100, 5000) if 'service' in incident_type else None
            }
        }
    
    def generate_normal_logs(self, count: int) -> List[Dict[str, Any]]:
        """Generate normal (non-incident) log entries"""
        normal_logs = []
        
        normal_patterns = [
            "Request processed successfully in {response_time}ms",
            "User {user_id} authenticated successfully",
            "Database query executed in {query_time}ms",
            "Cache hit for key {cache_key}",
            "Scheduled job {job_name} completed successfully",
            "Health check passed for service {service_name}",
            "Configuration reloaded successfully",
            "Backup completed for database {db_name}",
            "SSL certificate renewed for {domain}",
            "Log rotation completed for {log_file}"
        ]
        
        for _ in range(count):
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            pattern = random.choice(normal_patterns)
            variables = {
                'response_time': random.randint(50, 500),
                'user_id': f"user_{random.randint(1000, 9999)}",
                'query_time': random.randint(10, 200),
                'cache_key': f"cache_{random.randint(100, 999)}",
                'job_name': random.choice(['backup', 'cleanup', 'report']),
                'service_name': random.choice(['web', 'api', 'worker']),
                'db_name': random.choice(['users', 'orders', 'products']),
                'domain': random.choice(['api.example.com', 'web.example.com']),
                'log_file': random.choice(['app.log', 'access.log', 'error.log'])
            }
            
            try:
                message = pattern.format(**variables)
            except KeyError:
                message = pattern
            
            normal_logs.append({
                'timestamp': timestamp.isoformat(),
                'log_level': random.choice(['INFO', 'DEBUG']),
                'service': random.choice(['web-server', 'api-service', 'database', 'cache']),
                'aws_service': random.choice(self.aws_services),
                'instance_id': f"i-{random.choice(['abc123def456', '789ghi012jkl'])}",
                'message': message,
                'incident_type': 'normal',
                'severity': 'info',
                'recommended_action': 'none',
                'source_ip': f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'region': random.choice(['us-east-1', 'us-west-2']),
                'environment': random.choice(['production', 'staging']),
                'correlation_id': str(uuid.uuid4()),
                'metadata': {
                    'cpu_usage': random.uniform(10, 60),
                    'memory_usage': random.uniform(20, 70),
                    'disk_usage': random.uniform(30, 80),
                    'response_time': random.uniform(50, 500)
                }
            })
        
        return normal_logs
    
    def generate_dataset(self, total_samples: int = 10000) -> List[Dict[str, Any]]:
        """Generate complete dataset with incidents and normal logs"""
        dataset = []
        
        # Generate incident logs (70% of dataset)
        incident_samples = int(total_samples * 0.7)
        samples_per_incident = incident_samples // len(self.incident_types)
        
        for incident_type in self.incident_types.keys():
            for _ in range(samples_per_incident):
                dataset.append(self.generate_log_entry(incident_type))
        
        # Generate normal logs (30% of dataset)
        normal_samples = total_samples - len(dataset)
        dataset.extend(self.generate_normal_logs(normal_samples))
        
        # Shuffle dataset
        random.shuffle(dataset)
        
        return dataset
    
    def save_to_csv(self, dataset: List[Dict[str, Any]], filename: str):
        """Save dataset to CSV file"""
        if not dataset:
            return
            
        fieldnames = dataset[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in dataset:
                # Convert metadata dict to JSON string for CSV
                row_copy = row.copy()
                row_copy['metadata'] = json.dumps(row['metadata'])
                writer.writerow(row_copy)
    
    def save_to_json(self, dataset: List[Dict[str, Any]], filename: str):
        """Save dataset to JSON file"""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(dataset, jsonfile, indent=2, default=str)

def main():
    """Generate synthetic log datasets"""
    generator = SyntheticLogGenerator()
    
    print("Generating synthetic log dataset...")
    
    # Generate training dataset (10,000 samples)
    train_dataset = generator.generate_dataset(10000)
    generator.save_to_csv(train_dataset, 'data/training_logs.csv')
    generator.save_to_json(train_dataset, 'data/training_logs.json')
    
    # Generate test dataset (2,000 samples)
    test_dataset = generator.generate_dataset(2000)
    generator.save_to_csv(test_dataset, 'data/test_logs.csv')
    generator.save_to_json(test_dataset, 'data/test_logs.json')
    
    print(f"Generated {len(train_dataset)} training samples")
    print(f"Generated {len(test_dataset)} test samples")
    
    # Print sample logs
    print("\nSample incident logs:")
    for i, incident_type in enumerate(list(generator.incident_types.keys())[:3]):
        sample = generator.generate_log_entry(incident_type)
        print(f"\n{i+1}. {incident_type.upper()}:")
        print(f"   Timestamp: {sample['timestamp']}")
        print(f"   Service: {sample['service']}")
        print(f"   Message: {sample['message']}")
        print(f"   Severity: {sample['severity']}")
        print(f"   Recommended Action: {sample['recommended_action']}")

if __name__ == "__main__":
    main()