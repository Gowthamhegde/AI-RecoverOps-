#!/usr/bin/env python3
"""
AWS Lambda function for executing remediation actions
"""

import json
import boto3
import logging
import os
from datetime import datetime
from typing import Dict, Any
import sys
sys.path.append('/opt/python')

# Import remediation modules
from remediation.service_fixer import ServiceFixer, DiskFixer, PermissionFixer
from remediation.database_fixer import DatabaseFixer, CacheFixer

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

# Environment variables
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
REMEDIATION_TABLE = os.environ.get('REMEDIATION_TABLE', 'ai-recoverops-remediations')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize remediation classes
service_fixer = ServiceFixer(AWS_REGION)
disk_fixer = DiskFixer(AWS_REGION)
permission_fixer = PermissionFixer(AWS_REGION)
database_fixer = DatabaseFixer(AWS_REGION)
cache_fixer = CacheFixer(AWS_REGION)

def lambda_handler(event, context):
    """
    Main Lambda handler for executing remediation actions
    """
    try:
        logger.info(f"Remediation event: {json.dumps(event, default=str)}")
        
        # Extract remediation parameters
        incident_type = event.get('incident_type')
        recommended_action = event.get('recommended_action')
        instance_id = event.get('instance_id')
        service_name = event.get('service_name')
        log_data = event.get('log_data', {})
        
        if not all([incident_type, recommended_action]):
            raise ValueError("Missing required parameters: incident_type, recommended_action")
        
        # Execute remediation based on action type
        result = execute_remediation(
            incident_type=incident_type,
            recommended_action=recommended_action,
            instance_id=instance_id,
            service_name=service_name,
            log_data=log_data
        )
        
        # Store remediation result
        store_remediation_result(result, event)
        
        # Send notification
        send_remediation_notification(result, event)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        logger.error(f"Error executing remediation: {e}")
        
        # Store failure result
        failure_result = {
            'success': False,
            'action': recommended_action if 'recommended_action' in locals() else 'unknown',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        store_remediation_result(failure_result, event)
        send_remediation_notification(failure_result, event)
        
        return {
            'statusCode': 500,
            'body': json.dumps(failure_result, default=str)
        }

def execute_remediation(incident_type: str, recommended_action: str, 
                       instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the appropriate remediation action"""
    
    logger.info(f"Executing remediation: {recommended_action} for {incident_type}")
    
    # Service-related remediations
    if recommended_action == 'restart_service':
        return handle_restart_service(incident_type, instance_id, service_name, log_data)
    
    elif recommended_action == 'scale_horizontally':
        return handle_scale_service(incident_type, instance_id, service_name, log_data)
    
    elif recommended_action == 'kill_conflicting_process':
        return handle_kill_process(incident_type, instance_id, service_name, log_data)
    
    # Disk-related remediations
    elif recommended_action == 'clean_logs':
        return handle_clean_logs(incident_type, instance_id, service_name, log_data)
    
    elif recommended_action == 'expand_volume':
        return handle_expand_volume(incident_type, instance_id, service_name, log_data)
    
    # Permission-related remediations
    elif recommended_action == 'fix_permissions':
        return handle_fix_permissions(incident_type, instance_id, service_name, log_data)
    
    elif recommended_action == 'update_iam_policy':
        return handle_update_iam_policy(incident_type, instance_id, service_name, log_data)
    
    # Database-related remediations
    elif recommended_action == 'restart_database':
        return handle_restart_database(incident_type, instance_id, service_name, log_data)
    
    elif recommended_action == 'optimize_database_queries':
        return handle_optimize_database(incident_type, instance_id, service_name, log_data)
    
    elif recommended_action == 'increase_connection_pool':
        return handle_increase_connections(incident_type, instance_id, service_name, log_data)
    
    # Cache-related remediations
    elif recommended_action == 'clear_cache':
        return handle_clear_cache(incident_type, instance_id, service_name, log_data)
    
    # Memory-related remediations
    elif recommended_action == 'increase_memory_limit':
        return handle_increase_memory(incident_type, instance_id, service_name, log_data)
    
    else:
        return {
            'success': False,
            'action': recommended_action,
            'error': f'Unknown remediation action: {recommended_action}',
            'timestamp': datetime.now().isoformat()
        }

def handle_restart_service(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle service restart remediation"""
    
    # Determine service type from log data
    aws_service = log_data.get('aws_service', 'ec2')
    
    if aws_service == 'ecs':
        # Extract cluster name from log data or use default
        cluster_name = extract_ecs_cluster_name(log_data, service_name)
        return service_fixer.restart_ecs_service(cluster_name, service_name)
    
    elif aws_service in ['ec2', 'lambda']:
        # Restart systemd service on EC2
        return service_fixer.restart_systemd_service(service_name, instance_id)
    
    else:
        return {
            'success': False,
            'action': 'restart_service',
            'error': f'Unsupported AWS service for restart: {aws_service}',
            'timestamp': datetime.now().isoformat()
        }

def handle_scale_service(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle horizontal scaling remediation"""
    
    aws_service = log_data.get('aws_service', 'ec2')
    
    if aws_service == 'ecs':
        cluster_name = extract_ecs_cluster_name(log_data, service_name)
        
        # Determine desired count based on incident type
        if incident_type == 'high_cpu':
            desired_count = 3  # Scale up for CPU issues
        elif incident_type == 'memory_leak':
            desired_count = 2  # Conservative scaling for memory issues
        else:
            desired_count = 2  # Default scaling
        
        return service_fixer.scale_ecs_service(cluster_name, service_name, desired_count)
    
    else:
        return {
            'success': False,
            'action': 'scale_horizontally',
            'error': f'Scaling not supported for AWS service: {aws_service}',
            'timestamp': datetime.now().isoformat()
        }

def handle_kill_process(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle process killing remediation"""
    
    # Extract port from log message
    port = extract_port_from_log(log_data.get('message', ''))
    
    if port:
        return service_fixer.kill_process_by_port(port, instance_id)
    else:
        return {
            'success': False,
            'action': 'kill_conflicting_process',
            'error': 'Could not extract port number from log message',
            'timestamp': datetime.now().isoformat()
        }

def handle_clean_logs(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle log cleanup remediation"""
    
    # Define log paths based on service type
    log_paths = ['/var/log', '/opt/app/logs', '/tmp']
    
    # Add service-specific log paths
    if 'nginx' in service_name.lower():
        log_paths.append('/var/log/nginx')
    elif 'apache' in service_name.lower():
        log_paths.append('/var/log/apache2')
    elif 'tomcat' in service_name.lower():
        log_paths.append('/opt/tomcat/logs')
    
    return disk_fixer.clean_log_files(instance_id, log_paths)

def handle_expand_volume(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle volume expansion remediation"""
    
    # Extract volume ID from instance metadata (would need to be implemented)
    volume_id = get_instance_root_volume(instance_id)
    
    if volume_id:
        # Increase volume size by 20GB
        current_size = get_volume_size(volume_id)
        new_size = current_size + 20
        
        return disk_fixer.expand_ebs_volume(instance_id, volume_id, new_size)
    else:
        return {
            'success': False,
            'action': 'expand_volume',
            'error': 'Could not determine volume ID for instance',
            'timestamp': datetime.now().isoformat()
        }

def handle_fix_permissions(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle permission fixing remediation"""
    
    # Extract file path from log message
    file_path = extract_file_path_from_log(log_data.get('message', ''))
    
    if file_path:
        # Determine appropriate owner and permissions
        if '/var/log' in file_path:
            owner = 'syslog:adm'
            permissions = '644'
        elif '/opt/app' in file_path:
            owner = 'app:app'
            permissions = '755'
        else:
            owner = 'root:root'
            permissions = '644'
        
        return permission_fixer.fix_file_permissions(file_path, owner, permissions, instance_id)
    else:
        return {
            'success': False,
            'action': 'fix_permissions',
            'error': 'Could not extract file path from log message',
            'timestamp': datetime.now().isoformat()
        }

def handle_update_iam_policy(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle IAM policy update remediation"""
    
    # Extract role name from log message or instance metadata
    role_name = extract_iam_role_from_log(log_data.get('message', ''))
    
    if role_name:
        # Create policy document based on the error
        policy_document = create_remediation_policy(log_data.get('message', ''))
        
        return permission_fixer.update_iam_policy(role_name, policy_document)
    else:
        return {
            'success': False,
            'action': 'update_iam_policy',
            'error': 'Could not extract IAM role from log message',
            'timestamp': datetime.now().isoformat()
        }

def handle_restart_database(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle database restart remediation"""
    
    # Extract database identifier from log data
    db_identifier = extract_db_identifier_from_log(log_data.get('message', ''))
    
    if db_identifier:
        return database_fixer.restart_rds_instance(db_identifier)
    else:
        return {
            'success': False,
            'action': 'restart_database',
            'error': 'Could not extract database identifier from log message',
            'timestamp': datetime.now().isoformat()
        }

def handle_optimize_database(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle database optimization remediation"""
    
    db_endpoint = extract_db_endpoint_from_log(log_data.get('message', ''))
    db_name = extract_db_name_from_log(log_data.get('message', ''))
    
    if db_endpoint and db_name:
        return database_fixer.optimize_database_queries(db_endpoint, db_name, instance_id)
    else:
        return {
            'success': False,
            'action': 'optimize_database_queries',
            'error': 'Could not extract database connection details from log message',
            'timestamp': datetime.now().isoformat()
        }

def handle_increase_connections(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle database connection increase remediation"""
    
    db_identifier = extract_db_identifier_from_log(log_data.get('message', ''))
    
    if db_identifier:
        # Increase max connections by 50%
        new_max_connections = 200  # Default increase
        return database_fixer.increase_rds_connections(db_identifier, new_max_connections)
    else:
        return {
            'success': False,
            'action': 'increase_connection_pool',
            'error': 'Could not extract database identifier from log message',
            'timestamp': datetime.now().isoformat()
        }

def handle_clear_cache(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle cache clearing remediation"""
    
    # Determine cache type from service name or log data
    if 'redis' in service_name.lower() or 'redis' in log_data.get('message', '').lower():
        redis_endpoint = extract_redis_endpoint_from_log(log_data.get('message', ''))
        if redis_endpoint:
            return cache_fixer.flush_redis_cache(redis_endpoint, instance_id)
    
    # Fallback to application cache clearing
    cache_path = '/tmp/cache'  # Default cache path
    return service_fixer.clear_application_cache(cache_path, instance_id)

def handle_increase_memory(incident_type: str, instance_id: str, service_name: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle memory limit increase remediation"""
    
    aws_service = log_data.get('aws_service', 'ec2')
    
    if aws_service == 'ecs':
        # This would require updating ECS task definition
        return {
            'success': False,
            'action': 'increase_memory_limit',
            'error': 'ECS memory limit increase requires task definition update (not implemented)',
            'timestamp': datetime.now().isoformat()
        }
    else:
        return {
            'success': False,
            'action': 'increase_memory_limit',
            'error': 'Memory limit increase not supported for this service type',
            'timestamp': datetime.now().isoformat()
        }

# Helper functions for extracting information from logs

def extract_ecs_cluster_name(log_data: Dict[str, Any], service_name: str) -> str:
    """Extract ECS cluster name from log data"""
    log_group = log_data.get('metadata', {}).get('log_group', '')
    
    # Parse cluster name from log group: /aws/ecs/cluster-name
    if '/aws/ecs/' in log_group:
        return log_group.split('/aws/ecs/')[-1].split('/')[0]
    
    return 'default'  # Fallback to default cluster

def extract_port_from_log(message: str) -> int:
    """Extract port number from log message"""
    import re
    
    # Look for port patterns
    port_patterns = [
        r'port (\d+)',
        r':(\d+)',
        r'Port: (\d+)',
        r'address.*:(\d+)'
    ]
    
    for pattern in port_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return None

def extract_file_path_from_log(message: str) -> str:
    """Extract file path from log message"""
    import re
    
    # Look for file path patterns
    path_patterns = [
        r'(/[^\s]+)',
        r'accessing ([^\s]+)',
        r'file ([^\s]+)',
        r'path: ([^\s]+)'
    ]
    
    for pattern in path_patterns:
        match = re.search(pattern, message)
        if match:
            path = match.group(1)
            if path.startswith('/') and len(path) > 1:
                return path
    
    return None

def extract_iam_role_from_log(message: str) -> str:
    """Extract IAM role name from log message"""
    import re
    
    role_patterns = [
        r'role ([^\s]+)',
        r'IAM role ([^\s]+)',
        r'role: ([^\s]+)'
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_db_identifier_from_log(message: str) -> str:
    """Extract RDS database identifier from log message"""
    import re
    
    # Look for RDS endpoint patterns
    rds_pattern = r'([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)\.rds\.amazonaws\.com'
    match = re.search(rds_pattern, message)
    
    if match:
        return match.group(1)
    
    return None

def extract_db_endpoint_from_log(message: str) -> str:
    """Extract database endpoint from log message"""
    import re
    
    endpoint_patterns = [
        r'([a-zA-Z0-9.-]+\.rds\.amazonaws\.com)',
        r'host: ([^\s]+)',
        r'endpoint: ([^\s]+)'
    ]
    
    for pattern in endpoint_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_db_name_from_log(message: str) -> str:
    """Extract database name from log message"""
    import re
    
    db_patterns = [
        r'database ([^\s]+)',
        r'db: ([^\s]+)',
        r'schema: ([^\s]+)'
    ]
    
    for pattern in db_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return 'postgres'  # Default database name

def extract_redis_endpoint_from_log(message: str) -> str:
    """Extract Redis endpoint from log message"""
    import re
    
    redis_patterns = [
        r'redis://([^\s/]+)',
        r'Redis.*host: ([^\s]+)',
        r'cache.*endpoint: ([^\s]+)'
    ]
    
    for pattern in redis_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def get_instance_root_volume(instance_id: str) -> str:
    """Get root volume ID for EC2 instance"""
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        
        instance = response['Reservations'][0]['Instances'][0]
        for block_device in instance.get('BlockDeviceMappings', []):
            if block_device['DeviceName'] in ['/dev/sda1', '/dev/xvda']:
                return block_device['Ebs']['VolumeId']
        
        return None
    except Exception as e:
        logger.error(f"Error getting root volume for {instance_id}: {e}")
        return None

def get_volume_size(volume_id: str) -> int:
    """Get current size of EBS volume"""
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_volumes(VolumeIds=[volume_id])
        return response['Volumes'][0]['Size']
    except Exception as e:
        logger.error(f"Error getting volume size for {volume_id}: {e}")
        return 20  # Default size

def create_remediation_policy(message: str) -> Dict[str, Any]:
    """Create IAM policy document based on error message"""
    
    # Basic policy template
    policy = {
        "Version": "2012-10-17",
        "Statement": []
    }
    
    # Add permissions based on error message
    if 's3:GetObject' in message:
        policy["Statement"].append({
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": ["arn:aws:s3:::*/*", "arn:aws:s3:::*"]
        })
    
    if 'rds:Connect' in message:
        policy["Statement"].append({
            "Effect": "Allow",
            "Action": ["rds:DescribeDBInstances", "rds:Connect"],
            "Resource": "*"
        })
    
    if 'ec2:DescribeInstances' in message:
        policy["Statement"].append({
            "Effect": "Allow",
            "Action": ["ec2:DescribeInstances", "ec2:DescribeVolumes"],
            "Resource": "*"
        })
    
    return policy

def store_remediation_result(result: Dict[str, Any], event: Dict[str, Any]):
    """Store remediation result in DynamoDB"""
    try:
        table = dynamodb.Table(REMEDIATION_TABLE)
        
        item = {
            'remediation_id': context.aws_request_id,
            'timestamp': datetime.now().isoformat(),
            'incident_type': event.get('incident_type'),
            'recommended_action': event.get('recommended_action'),
            'instance_id': event.get('instance_id'),
            'service_name': event.get('service_name'),
            'result': result,
            'event_data': event
        }
        
        table.put_item(Item=item)
        logger.info(f"Stored remediation result: {context.aws_request_id}")
        
    except Exception as e:
        logger.error(f"Error storing remediation result: {e}")

def send_remediation_notification(result: Dict[str, Any], event: Dict[str, Any]):
    """Send notification about remediation result"""
    try:
        if not SNS_TOPIC_ARN:
            return
        
        success = result.get('success', False)
        action = result.get('action', 'unknown')
        incident_type = event.get('incident_type', 'unknown')
        
        if success:
            subject = f"✅ AI-RecoverOps: Remediation Successful"
            message = f"""
Remediation completed successfully!

Incident Type: {incident_type}
Action Taken: {action}
Instance ID: {event.get('instance_id', 'N/A')}
Service: {event.get('service_name', 'N/A')}
Timestamp: {result.get('timestamp')}

The issue has been automatically resolved.
"""
        else:
            subject = f"❌ AI-RecoverOps: Remediation Failed"
            message = f"""
Remediation failed - manual intervention required.

Incident Type: {incident_type}
Attempted Action: {action}
Instance ID: {event.get('instance_id', 'N/A')}
Service: {event.get('service_name', 'N/A')}
Error: {result.get('error', 'Unknown error')}
Timestamp: {result.get('timestamp')}

Please investigate and resolve manually.
"""
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        
        logger.info(f"Sent remediation notification: {success}")
        
    except Exception as e:
        logger.error(f"Error sending remediation notification: {e}")