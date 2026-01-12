#!/usr/bin/env python3
"""
Service remediation scripts for AI-RecoverOps
"""

import subprocess
import logging
import json
import time
from typing import Dict, Any, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class ServiceFixer:
    """Handle service-related remediation actions"""
    
    def __init__(self, aws_region: str = 'us-east-1'):
        self.aws_region = aws_region
        self.ec2_client = boto3.client('ec2', region_name=aws_region)
        self.ecs_client = boto3.client('ecs', region_name=aws_region)
        self.ssm_client = boto3.client('ssm', region_name=aws_region)
        
    def restart_systemd_service(self, service_name: str, instance_id: str) -> Dict[str, Any]:
        """Restart a systemd service on EC2 instance using SSM"""
        try:
            logger.info(f"Restarting service {service_name} on instance {instance_id}")
            
            # Create SSM command
            command = f"""
            #!/bin/bash
            echo "Restarting service: {service_name}"
            sudo systemctl stop {service_name}
            sleep 5
            sudo systemctl start {service_name}
            sudo systemctl status {service_name}
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment=f"AI-RecoverOps: Restart {service_name}",
                TimeoutSeconds=300
            )
            
            command_id = response['Command']['CommandId']
            
            # Wait for command completion
            waiter = self.ssm_client.get_waiter('command_executed')
            waiter.wait(
                CommandId=command_id,
                InstanceId=instance_id,
                WaiterConfig={'Delay': 5, 'MaxAttempts': 12}
            )
            
            # Get command output
            output = self.ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            success = output['Status'] == 'Success'
            
            return {
                'success': success,
                'action': 'restart_service',
                'service_name': service_name,
                'instance_id': instance_id,
                'command_id': command_id,
                'output': output.get('StandardOutputContent', ''),
                'error': output.get('StandardErrorContent', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to restart service {service_name}: {e}")
            return {
                'success': False,
                'action': 'restart_service',
                'service_name': service_name,
                'instance_id': instance_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def restart_ecs_service(self, cluster_name: str, service_name: str) -> Dict[str, Any]:
        """Restart ECS service by forcing new deployment"""
        try:
            logger.info(f"Restarting ECS service {service_name} in cluster {cluster_name}")
            
            # Force new deployment
            response = self.ecs_client.update_service(
                cluster=cluster_name,
                service=service_name,
                forceNewDeployment=True
            )
            
            service_arn = response['service']['serviceArn']
            
            # Wait for deployment to stabilize
            waiter = self.ecs_client.get_waiter('services_stable')
            waiter.wait(
                cluster=cluster_name,
                services=[service_name],
                WaiterConfig={'Delay': 15, 'MaxAttempts': 20}
            )
            
            return {
                'success': True,
                'action': 'restart_ecs_service',
                'cluster_name': cluster_name,
                'service_name': service_name,
                'service_arn': service_arn,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to restart ECS service {service_name}: {e}")
            return {
                'success': False,
                'action': 'restart_ecs_service',
                'cluster_name': cluster_name,
                'service_name': service_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def scale_ecs_service(self, cluster_name: str, service_name: str, desired_count: int) -> Dict[str, Any]:
        """Scale ECS service to desired task count"""
        try:
            logger.info(f"Scaling ECS service {service_name} to {desired_count} tasks")
            
            response = self.ecs_client.update_service(
                cluster=cluster_name,
                service=service_name,
                desiredCount=desired_count
            )
            
            return {
                'success': True,
                'action': 'scale_ecs_service',
                'cluster_name': cluster_name,
                'service_name': service_name,
                'desired_count': desired_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to scale ECS service {service_name}: {e}")
            return {
                'success': False,
                'action': 'scale_ecs_service',
                'cluster_name': cluster_name,
                'service_name': service_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def kill_process_by_port(self, port: int, instance_id: str) -> Dict[str, Any]:
        """Kill process using specific port"""
        try:
            logger.info(f"Killing process on port {port} on instance {instance_id}")
            
            command = f"""
            #!/bin/bash
            echo "Finding process on port {port}"
            PID=$(sudo lsof -ti:{port})
            if [ ! -z "$PID" ]; then
                echo "Killing process $PID on port {port}"
                sudo kill -9 $PID
                echo "Process killed successfully"
            else
                echo "No process found on port {port}"
            fi
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment=f"AI-RecoverOps: Kill process on port {port}",
                TimeoutSeconds=60
            )
            
            command_id = response['Command']['CommandId']
            
            # Wait for command completion
            time.sleep(10)
            
            output = self.ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            success = output['Status'] == 'Success'
            
            return {
                'success': success,
                'action': 'kill_process_by_port',
                'port': port,
                'instance_id': instance_id,
                'command_id': command_id,
                'output': output.get('StandardOutputContent', ''),
                'error': output.get('StandardErrorContent', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to kill process on port {port}: {e}")
            return {
                'success': False,
                'action': 'kill_process_by_port',
                'port': port,
                'instance_id': instance_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def clear_application_cache(self, cache_path: str, instance_id: str) -> Dict[str, Any]:
        """Clear application cache directory"""
        try:
            logger.info(f"Clearing cache at {cache_path} on instance {instance_id}")
            
            command = f"""
            #!/bin/bash
            echo "Clearing cache directory: {cache_path}"
            if [ -d "{cache_path}" ]; then
                sudo rm -rf {cache_path}/*
                echo "Cache cleared successfully"
            else
                echo "Cache directory not found: {cache_path}"
            fi
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment=f"AI-RecoverOps: Clear cache {cache_path}",
                TimeoutSeconds=120
            )
            
            command_id = response['Command']['CommandId']
            
            # Wait for command completion
            time.sleep(10)
            
            output = self.ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            success = output['Status'] == 'Success'
            
            return {
                'success': success,
                'action': 'clear_cache',
                'cache_path': cache_path,
                'instance_id': instance_id,
                'command_id': command_id,
                'output': output.get('StandardOutputContent', ''),
                'error': output.get('StandardErrorContent', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to clear cache {cache_path}: {e}")
            return {
                'success': False,
                'action': 'clear_cache',
                'cache_path': cache_path,
                'instance_id': instance_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class DiskFixer:
    """Handle disk space related issues"""
    
    def __init__(self, aws_region: str = 'us-east-1'):
        self.aws_region = aws_region
        self.ssm_client = boto3.client('ssm', region_name=aws_region)
        self.ec2_client = boto3.client('ec2', region_name=aws_region)
    
    def clean_log_files(self, instance_id: str, log_paths: List[str] = None) -> Dict[str, Any]:
        """Clean old log files to free disk space"""
        try:
            if log_paths is None:
                log_paths = ['/var/log', '/opt/app/logs', '/tmp']
            
            logger.info(f"Cleaning log files on instance {instance_id}")
            
            command = f"""
            #!/bin/bash
            echo "Cleaning log files..."
            
            # Clean system logs older than 7 days
            find /var/log -name "*.log" -type f -mtime +7 -exec rm -f {{}} \\;
            find /var/log -name "*.log.*" -type f -mtime +7 -exec rm -f {{}} \\;
            
            # Clean application logs
            for path in {' '.join(log_paths)}; do
                if [ -d "$path" ]; then
                    echo "Cleaning logs in $path"
                    find "$path" -name "*.log" -type f -mtime +3 -exec rm -f {{}} \\;
                    find "$path" -name "*.log.*" -type f -mtime +3 -exec rm -f {{}} \\;
                fi
            done
            
            # Clean temp files
            find /tmp -type f -mtime +1 -exec rm -f {{}} \\;
            
            # Show disk usage after cleanup
            df -h
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment="AI-RecoverOps: Clean log files",
                TimeoutSeconds=300
            )
            
            command_id = response['Command']['CommandId']
            
            # Wait for command completion
            waiter = self.ssm_client.get_waiter('command_executed')
            waiter.wait(
                CommandId=command_id,
                InstanceId=instance_id,
                WaiterConfig={'Delay': 10, 'MaxAttempts': 30}
            )
            
            output = self.ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            success = output['Status'] == 'Success'
            
            return {
                'success': success,
                'action': 'clean_log_files',
                'instance_id': instance_id,
                'log_paths': log_paths,
                'command_id': command_id,
                'output': output.get('StandardOutputContent', ''),
                'error': output.get('StandardErrorContent', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to clean log files: {e}")
            return {
                'success': False,
                'action': 'clean_log_files',
                'instance_id': instance_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def expand_ebs_volume(self, instance_id: str, volume_id: str, new_size_gb: int) -> Dict[str, Any]:
        """Expand EBS volume and extend filesystem"""
        try:
            logger.info(f"Expanding volume {volume_id} to {new_size_gb}GB")
            
            # Modify volume size
            self.ec2_client.modify_volume(
                VolumeId=volume_id,
                Size=new_size_gb
            )
            
            # Wait for volume modification to complete
            waiter = self.ec2_client.get_waiter('volume_in_use')
            waiter.wait(VolumeIds=[volume_id])
            
            # Extend filesystem on the instance
            command = """
            #!/bin/bash
            echo "Extending filesystem..."
            
            # Get the root device
            ROOT_DEVICE=$(df / | tail -1 | awk '{print $1}')
            echo "Root device: $ROOT_DEVICE"
            
            # Extend partition (for newer instances with NVMe)
            if [[ $ROOT_DEVICE == *"nvme"* ]]; then
                sudo growpart /dev/nvme0n1 1
                sudo resize2fs /dev/nvme0n1p1
            else
                # For older instance types
                sudo growpart /dev/xvda 1
                sudo resize2fs /dev/xvda1
            fi
            
            # Show new disk usage
            df -h
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment="AI-RecoverOps: Extend filesystem",
                TimeoutSeconds=300
            )
            
            command_id = response['Command']['CommandId']
            
            return {
                'success': True,
                'action': 'expand_ebs_volume',
                'instance_id': instance_id,
                'volume_id': volume_id,
                'new_size_gb': new_size_gb,
                'command_id': command_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to expand volume {volume_id}: {e}")
            return {
                'success': False,
                'action': 'expand_ebs_volume',
                'instance_id': instance_id,
                'volume_id': volume_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class PermissionFixer:
    """Handle permission-related issues"""
    
    def __init__(self, aws_region: str = 'us-east-1'):
        self.aws_region = aws_region
        self.iam_client = boto3.client('iam', region_name=aws_region)
        self.ssm_client = boto3.client('ssm', region_name=aws_region)
    
    def fix_file_permissions(self, file_path: str, owner: str, permissions: str, instance_id: str) -> Dict[str, Any]:
        """Fix file permissions on EC2 instance"""
        try:
            logger.info(f"Fixing permissions for {file_path} on instance {instance_id}")
            
            command = f"""
            #!/bin/bash
            echo "Fixing permissions for {file_path}"
            
            if [ -e "{file_path}" ]; then
                sudo chown {owner} {file_path}
                sudo chmod {permissions} {file_path}
                echo "Permissions fixed successfully"
                ls -la {file_path}
            else
                echo "File not found: {file_path}"
                exit 1
            fi
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment=f"AI-RecoverOps: Fix permissions for {file_path}",
                TimeoutSeconds=60
            )
            
            command_id = response['Command']['CommandId']
            
            # Wait for command completion
            time.sleep(10)
            
            output = self.ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            success = output['Status'] == 'Success'
            
            return {
                'success': success,
                'action': 'fix_file_permissions',
                'file_path': file_path,
                'owner': owner,
                'permissions': permissions,
                'instance_id': instance_id,
                'command_id': command_id,
                'output': output.get('StandardOutputContent', ''),
                'error': output.get('StandardErrorContent', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fix permissions for {file_path}: {e}")
            return {
                'success': False,
                'action': 'fix_file_permissions',
                'file_path': file_path,
                'instance_id': instance_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def update_iam_policy(self, role_name: str, policy_document: Dict[str, Any]) -> Dict[str, Any]:
        """Update IAM role policy"""
        try:
            logger.info(f"Updating IAM policy for role {role_name}")
            
            policy_name = f"{role_name}-AutoRemediation-Policy"
            
            # Put role policy
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
            
            return {
                'success': True,
                'action': 'update_iam_policy',
                'role_name': role_name,
                'policy_name': policy_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update IAM policy for role {role_name}: {e}")
            return {
                'success': False,
                'action': 'update_iam_policy',
                'role_name': role_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }