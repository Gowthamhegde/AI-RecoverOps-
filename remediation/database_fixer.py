#!/usr/bin/env python3
"""
Database remediation scripts for AI-RecoverOps
"""

import boto3
import logging
import time
from typing import Dict, Any, List
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class DatabaseFixer:
    """Handle database-related remediation actions"""
    
    def __init__(self, aws_region: str = 'us-east-1'):
        self.aws_region = aws_region
        self.rds_client = boto3.client('rds', region_name=aws_region)
        self.ssm_client = boto3.client('ssm', region_name=aws_region)
        
    def restart_rds_instance(self, db_instance_identifier: str) -> Dict[str, Any]:
        """Restart RDS database instance"""
        try:
            logger.info(f"Restarting RDS instance {db_instance_identifier}")
            
            # Reboot the DB instance
            response = self.rds_client.reboot_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                ForceFailover=False
            )
            
            # Wait for instance to be available
            waiter = self.rds_client.get_waiter('db_instance_available')
            waiter.wait(
                DBInstanceIdentifier=db_instance_identifier,
                WaiterConfig={'Delay': 30, 'MaxAttempts': 20}
            )
            
            return {
                'success': True,
                'action': 'restart_rds_instance',
                'db_instance_identifier': db_instance_identifier,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to restart RDS instance {db_instance_identifier}: {e}")
            return {
                'success': False,
                'action': 'restart_rds_instance',
                'db_instance_identifier': db_instance_identifier,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def increase_rds_connections(self, db_instance_identifier: str, new_max_connections: int) -> Dict[str, Any]:
        """Increase max_connections parameter for RDS instance"""
        try:
            logger.info(f"Increasing max connections for {db_instance_identifier} to {new_max_connections}")
            
            # Get current parameter group
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=db_instance_identifier
            )
            
            db_instance = response['DBInstances'][0]
            parameter_group_name = db_instance['DBParameterGroups'][0]['DBParameterGroupName']
            
            # Modify parameter group
            self.rds_client.modify_db_parameter_group(
                DBParameterGroupName=parameter_group_name,
                Parameters=[
                    {
                        'ParameterName': 'max_connections',
                        'ParameterValue': str(new_max_connections),
                        'ApplyMethod': 'immediate'
                    }
                ]
            )
            
            # Reboot instance to apply changes
            self.rds_client.reboot_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                ForceFailover=False
            )
            
            return {
                'success': True,
                'action': 'increase_rds_connections',
                'db_instance_identifier': db_instance_identifier,
                'parameter_group_name': parameter_group_name,
                'new_max_connections': new_max_connections,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to increase connections for {db_instance_identifier}: {e}")
            return {
                'success': False,
                'action': 'increase_rds_connections',
                'db_instance_identifier': db_instance_identifier,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def kill_long_running_queries(self, db_endpoint: str, db_name: str, instance_id: str) -> Dict[str, Any]:
        """Kill long-running database queries"""
        try:
            logger.info(f"Killing long-running queries on {db_endpoint}")
            
            # PostgreSQL query to kill long-running queries
            command = f"""
            #!/bin/bash
            export PGPASSWORD="${{DB_PASSWORD}}"
            
            echo "Finding long-running queries..."
            
            # Kill queries running longer than 5 minutes
            psql -h {db_endpoint} -U ${{DB_USERNAME}} -d {db_name} -c "
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND now() - query_start > interval '5 minutes'
            AND query NOT LIKE '%pg_stat_activity%'
            AND pid != pg_backend_pid();
            "
            
            echo "Long-running queries terminated"
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment="AI-RecoverOps: Kill long-running queries",
                TimeoutSeconds=120
            )
            
            command_id = response['Command']['CommandId']
            
            # Wait for command completion
            time.sleep(15)
            
            output = self.ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            success = output['Status'] == 'Success'
            
            return {
                'success': success,
                'action': 'kill_long_running_queries',
                'db_endpoint': db_endpoint,
                'db_name': db_name,
                'instance_id': instance_id,
                'command_id': command_id,
                'output': output.get('StandardOutputContent', ''),
                'error': output.get('StandardErrorContent', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to kill long-running queries: {e}")
            return {
                'success': False,
                'action': 'kill_long_running_queries',
                'db_endpoint': db_endpoint,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def optimize_database_queries(self, db_endpoint: str, db_name: str, instance_id: str) -> Dict[str, Any]:
        """Run database optimization commands"""
        try:
            logger.info(f"Optimizing database {db_name}")
            
            command = f"""
            #!/bin/bash
            export PGPASSWORD="${{DB_PASSWORD}}"
            
            echo "Running database optimization..."
            
            # Update table statistics
            psql -h {db_endpoint} -U ${{DB_USERNAME}} -d {db_name} -c "ANALYZE;"
            
            # Reindex tables if needed
            psql -h {db_endpoint} -U ${{DB_USERNAME}} -d {db_name} -c "REINDEX DATABASE {db_name};"
            
            # Vacuum analyze
            psql -h {db_endpoint} -U ${{DB_USERNAME}} -d {db_name} -c "VACUUM ANALYZE;"
            
            echo "Database optimization completed"
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment="AI-RecoverOps: Optimize database",
                TimeoutSeconds=600
            )
            
            command_id = response['Command']['CommandId']
            
            return {
                'success': True,
                'action': 'optimize_database_queries',
                'db_endpoint': db_endpoint,
                'db_name': db_name,
                'instance_id': instance_id,
                'command_id': command_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
            return {
                'success': False,
                'action': 'optimize_database_queries',
                'db_endpoint': db_endpoint,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class CacheFixer:
    """Handle cache-related remediation actions"""
    
    def __init__(self, aws_region: str = 'us-east-1'):
        self.aws_region = aws_region
        self.elasticache_client = boto3.client('elasticache', region_name=aws_region)
        self.ssm_client = boto3.client('ssm', region_name=aws_region)
    
    def restart_elasticache_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """Restart ElastiCache Redis cluster"""
        try:
            logger.info(f"Restarting ElastiCache cluster {cluster_id}")
            
            # Reboot cache cluster
            response = self.elasticache_client.reboot_cache_cluster(
                CacheClusterId=cluster_id,
                CacheNodeIdsToReboot=['0001']  # Primary node
            )
            
            # Wait for cluster to be available
            waiter = self.elasticache_client.get_waiter('cache_cluster_available')
            waiter.wait(
                CacheClusterId=cluster_id,
                WaiterConfig={'Delay': 30, 'MaxAttempts': 20}
            )
            
            return {
                'success': True,
                'action': 'restart_elasticache_cluster',
                'cluster_id': cluster_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to restart ElastiCache cluster {cluster_id}: {e}")
            return {
                'success': False,
                'action': 'restart_elasticache_cluster',
                'cluster_id': cluster_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def flush_redis_cache(self, redis_endpoint: str, instance_id: str) -> Dict[str, Any]:
        """Flush Redis cache"""
        try:
            logger.info(f"Flushing Redis cache at {redis_endpoint}")
            
            command = f"""
            #!/bin/bash
            echo "Flushing Redis cache..."
            
            # Connect to Redis and flush all data
            redis-cli -h {redis_endpoint} FLUSHALL
            
            echo "Redis cache flushed successfully"
            """
            
            response = self.ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    'commands': [command]
                },
                Comment="AI-RecoverOps: Flush Redis cache",
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
                'action': 'flush_redis_cache',
                'redis_endpoint': redis_endpoint,
                'instance_id': instance_id,
                'command_id': command_id,
                'output': output.get('StandardOutputContent', ''),
                'error': output.get('StandardErrorContent', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to flush Redis cache: {e}")
            return {
                'success': False,
                'action': 'flush_redis_cache',
                'redis_endpoint': redis_endpoint,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }