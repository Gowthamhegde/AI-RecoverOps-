#!/usr/bin/env python3
"""
AWS Lambda function for processing CloudWatch logs and triggering ML analysis
"""

import json
import boto3
import gzip
import base64
import logging
import os
from datetime import datetime
from typing import Dict, Any, List
import requests

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
ssm_client = boto3.client('ssm')

# Environment variables
ML_API_ENDPOINT = os.environ.get('ML_API_ENDPOINT', 'http://localhost:8000')
S3_BUCKET = os.environ.get('S3_BUCKET', 'ai-recoverops-logs')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', '0.8'))

def lambda_handler(event, context):
    """
    Main Lambda handler for processing CloudWatch logs
    """
    try:
        logger.info(f"Processing event: {json.dumps(event, default=str)}")
        
        # Process CloudWatch Logs event
        if 'awslogs' in event:
            return process_cloudwatch_logs(event, context)
        
        # Process direct log entries
        elif 'logs' in event:
            return process_direct_logs(event, context)
        
        # Process S3 event (batch processing)
        elif 'Records' in event and event['Records'][0].get('eventSource') == 'aws:s3':
            return process_s3_logs(event, context)
        
        else:
            logger.warning("Unknown event type")
            return {'statusCode': 400, 'body': 'Unknown event type'}
            
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def process_cloudwatch_logs(event, context):
    """Process CloudWatch Logs subscription filter event"""
    try:
        # Decode and decompress log data
        cw_data = event['awslogs']['data']
        compressed_payload = base64.b64decode(cw_data)
        uncompressed_payload = gzip.decompress(compressed_payload)
        log_data = json.loads(uncompressed_payload)
        
        logger.info(f"Processing {len(log_data['logEvents'])} log events")
        
        # Convert CloudWatch log events to our format
        processed_logs = []
        for log_event in log_data['logEvents']:
            processed_log = convert_cloudwatch_log(log_event, log_data)
            if processed_log:
                processed_logs.append(processed_log)
        
        if not processed_logs:
            logger.info("No logs to process")
            return {'statusCode': 200, 'body': 'No logs processed'}
        
        # Store raw logs in S3
        s3_key = store_logs_in_s3(processed_logs)
        
        # Send logs to ML API for analysis
        predictions = analyze_logs_with_ml(processed_logs)
        
        # Process predictions and trigger remediation if needed
        remediation_results = process_predictions(predictions, processed_logs)
        
        # Send notifications for critical incidents
        notification_results = send_notifications(predictions, processed_logs)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed_logs': len(processed_logs),
                's3_key': s3_key,
                'predictions': len(predictions),
                'remediations_triggered': len(remediation_results),
                'notifications_sent': len(notification_results)
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing CloudWatch logs: {e}")
        raise

def convert_cloudwatch_log(log_event, log_data):
    """Convert CloudWatch log event to standardized format"""
    try:
        message = log_event['message']
        timestamp = datetime.fromtimestamp(log_event['timestamp'] / 1000).isoformat()
        
        # Extract metadata from log group and stream
        log_group = log_data['logGroup']
        log_stream = log_data['logStream']
        
        # Determine service and AWS service from log group name
        service, aws_service = parse_log_group_name(log_group)
        
        # Extract log level from message
        log_level = extract_log_level(message)
        
        # Extract instance ID if available
        instance_id = extract_instance_id(log_stream, message)
        
        return {
            'timestamp': timestamp,
            'log_level': log_level,
            'service': service,
            'aws_service': aws_service,
            'instance_id': instance_id,
            'message': message,
            'source_ip': None,
            'region': os.environ.get('AWS_REGION', 'us-east-1'),
            'environment': determine_environment(log_group),
            'metadata': {
                'log_group': log_group,
                'log_stream': log_stream,
                'raw_timestamp': log_event['timestamp']
            }
        }
        
    except Exception as e:
        logger.error(f"Error converting log event: {e}")
        return None

def parse_log_group_name(log_group):
    """Parse service and AWS service from log group name"""
    # Examples:
    # /aws/lambda/my-function -> service: my-function, aws_service: lambda
    # /aws/ecs/my-cluster -> service: my-cluster, aws_service: ecs
    # /aws/rds/instance/my-db -> service: my-db, aws_service: rds
    
    parts = log_group.split('/')
    
    if len(parts) >= 3 and parts[1] == 'aws':
        aws_service = parts[2]
        service = parts[-1] if len(parts) > 3 else aws_service
    else:
        aws_service = 'ec2'  # Default
        service = parts[-1] if parts else 'unknown'
    
    return service, aws_service

def extract_log_level(message):
    """Extract log level from message"""
    message_upper = message.upper()
    
    if 'FATAL' in message_upper or 'CRITICAL' in message_upper:
        return 'FATAL'
    elif 'ERROR' in message_upper:
        return 'ERROR'
    elif 'WARN' in message_upper or 'WARNING' in message_upper:
        return 'WARN'
    elif 'INFO' in message_upper:
        return 'INFO'
    elif 'DEBUG' in message_upper:
        return 'DEBUG'
    else:
        return 'INFO'  # Default

def extract_instance_id(log_stream, message):
    """Extract instance ID from log stream or message"""
    # Try to extract from log stream name
    if 'i-' in log_stream:
        parts = log_stream.split('i-')
        if len(parts) > 1:
            return f"i-{parts[1].split('/')[0].split('-')[0]}"
    
    # Try to extract from message
    if 'i-' in message:
        import re
        match = re.search(r'i-[a-f0-9]{8,17}', message)
        if match:
            return match.group(0)
    
    return 'unknown'

def determine_environment(log_group):
    """Determine environment from log group name"""
    log_group_lower = log_group.lower()
    
    if 'prod' in log_group_lower or 'production' in log_group_lower:
        return 'production'
    elif 'stag' in log_group_lower or 'staging' in log_group_lower:
        return 'staging'
    elif 'dev' in log_group_lower or 'development' in log_group_lower:
        return 'development'
    else:
        return 'production'  # Default to production for safety

def store_logs_in_s3(logs):
    """Store processed logs in S3 for batch processing and training"""
    try:
        timestamp = datetime.now().strftime('%Y/%m/%d/%H')
        s3_key = f"processed-logs/{timestamp}/{context.aws_request_id}.json"
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(logs, default=str),
            ContentType='application/json'
        )
        
        logger.info(f"Stored {len(logs)} logs in S3: s3://{S3_BUCKET}/{s3_key}")
        return s3_key
        
    except Exception as e:
        logger.error(f"Error storing logs in S3: {e}")
        return None

def analyze_logs_with_ml(logs):
    """Send logs to ML API for incident prediction"""
    try:
        # Prepare request payload
        payload = {
            'logs': logs,
            'model_type': 'ensemble'
        }
        
        # Call ML API
        response = requests.post(
            f"{ML_API_ENDPOINT}/predict",
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"ML analysis completed in {result['processing_time_ms']}ms")
            return result['predictions']
        else:
            logger.error(f"ML API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error calling ML API: {e}")
        return []

def process_predictions(predictions, logs):
    """Process ML predictions and trigger remediation if needed"""
    remediation_results = []
    
    for i, prediction in enumerate(predictions):
        try:
            incident_type = prediction['incident_type']
            confidence = prediction['confidence']
            recommended_action = prediction['recommended_action']
            
            # Skip normal logs and low confidence predictions
            if incident_type == 'normal' or confidence < CONFIDENCE_THRESHOLD:
                continue
            
            log_entry = logs[i] if i < len(logs) else {}
            
            logger.info(f"High confidence incident detected: {incident_type} (confidence: {confidence})")
            
            # Trigger remediation based on incident type and confidence
            if confidence >= 0.9 and should_auto_remediate(incident_type, log_entry):
                result = trigger_remediation(incident_type, recommended_action, log_entry)
                remediation_results.append(result)
            else:
                logger.info(f"Manual intervention required for {incident_type}")
                
        except Exception as e:
            logger.error(f"Error processing prediction {i}: {e}")
    
    return remediation_results

def should_auto_remediate(incident_type, log_entry):
    """Determine if incident should be auto-remediated"""
    # Safety rules for auto-remediation
    safe_actions = [
        'high_cpu',
        'memory_leak', 
        'disk_full',
        'service_crash',
        'container_oom'
    ]
    
    # Don't auto-remediate in production for critical incidents
    environment = log_entry.get('environment', 'production')
    if environment == 'production' and incident_type in ['permission_denied', 'db_connection_failure']:
        return False
    
    return incident_type in safe_actions

def trigger_remediation(incident_type, recommended_action, log_entry):
    """Trigger automated remediation action"""
    try:
        logger.info(f"Triggering remediation: {recommended_action} for {incident_type}")
        
        # Get instance ID and other metadata
        instance_id = log_entry.get('instance_id', 'unknown')
        service = log_entry.get('service', 'unknown')
        
        # Prepare remediation parameters
        remediation_params = {
            'incident_type': incident_type,
            'recommended_action': recommended_action,
            'instance_id': instance_id,
            'service': service,
            'log_entry': log_entry
        }
        
        # Execute remediation via SSM automation
        response = ssm_client.start_automation_execution(
            DocumentName='AI-RecoverOps-Remediation',
            Parameters={
                'IncidentType': [incident_type],
                'RecommendedAction': [recommended_action],
                'InstanceId': [instance_id],
                'ServiceName': [service],
                'LogData': [json.dumps(log_entry)]
            }
        )
        
        automation_execution_id = response['AutomationExecutionId']
        
        logger.info(f"Remediation triggered: {automation_execution_id}")
        
        return {
            'success': True,
            'incident_type': incident_type,
            'recommended_action': recommended_action,
            'automation_execution_id': automation_execution_id,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering remediation: {e}")
        return {
            'success': False,
            'incident_type': incident_type,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def send_notifications(predictions, logs):
    """Send notifications for critical incidents"""
    notification_results = []
    
    try:
        # Filter high-severity incidents
        critical_incidents = []
        for i, prediction in enumerate(predictions):
            if (prediction['confidence'] >= CONFIDENCE_THRESHOLD and 
                prediction['incident_type'] != 'normal'):
                
                log_entry = logs[i] if i < len(logs) else {}
                critical_incidents.append({
                    'prediction': prediction,
                    'log': log_entry
                })
        
        if not critical_incidents:
            return notification_results
        
        # Prepare notification message
        message = format_notification_message(critical_incidents)
        
        # Send SNS notification
        if SNS_TOPIC_ARN:
            response = sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='AI-RecoverOps: Critical Incidents Detected',
                Message=message
            )
            
            notification_results.append({
                'type': 'sns',
                'message_id': response['MessageId'],
                'incidents_count': len(critical_incidents)
            })
        
        logger.info(f"Sent notifications for {len(critical_incidents)} critical incidents")
        
    except Exception as e:
        logger.error(f"Error sending notifications: {e}")
    
    return notification_results

def format_notification_message(incidents):
    """Format notification message for critical incidents"""
    message_lines = [
        "🚨 AI-RecoverOps Alert: Critical Incidents Detected",
        f"Timestamp: {datetime.now().isoformat()}",
        f"Total Incidents: {len(incidents)}",
        "",
        "Incident Details:"
    ]
    
    for i, incident in enumerate(incidents[:5], 1):  # Limit to 5 incidents
        prediction = incident['prediction']
        log = incident['log']
        
        message_lines.extend([
            f"{i}. {prediction['incident_type'].upper()}",
            f"   Confidence: {prediction['confidence']:.2%}",
            f"   Service: {log.get('service', 'unknown')}",
            f"   Instance: {log.get('instance_id', 'unknown')}",
            f"   Recommended Action: {prediction['recommended_action']}",
            f"   Message: {log.get('message', '')[:100]}...",
            ""
        ])
    
    if len(incidents) > 5:
        message_lines.append(f"... and {len(incidents) - 5} more incidents")
    
    message_lines.extend([
        "",
        "🔧 Auto-remediation may have been triggered for eligible incidents.",
        "📊 Check the AI-RecoverOps dashboard for detailed analysis.",
        "",
        "This is an automated alert from AI-RecoverOps."
    ])
    
    return "\n".join(message_lines)

def process_direct_logs(event, context):
    """Process logs sent directly to the Lambda function"""
    try:
        logs = event['logs']
        logger.info(f"Processing {len(logs)} direct log entries")
        
        # Analyze logs
        predictions = analyze_logs_with_ml(logs)
        
        # Process predictions
        remediation_results = process_predictions(predictions, logs)
        
        # Send notifications
        notification_results = send_notifications(predictions, logs)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'predictions': predictions,
                'remediations_triggered': len(remediation_results),
                'notifications_sent': len(notification_results)
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing direct logs: {e}")
        raise

def process_s3_logs(event, context):
    """Process logs from S3 batch events"""
    try:
        results = []
        
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            logger.info(f"Processing S3 object: s3://{bucket}/{key}")
            
            # Download and process log file
            response = s3_client.get_object(Bucket=bucket, Key=key)
            log_data = json.loads(response['Body'].read())
            
            # Analyze logs
            predictions = analyze_logs_with_ml(log_data)
            
            # Process predictions
            remediation_results = process_predictions(predictions, log_data)
            
            results.append({
                's3_key': key,
                'predictions': len(predictions),
                'remediations': len(remediation_results)
            })
        
        return {
            'statusCode': 200,
            'body': json.dumps({'processed_files': results})
        }
        
    except Exception as e:
        logger.error(f"Error processing S3 logs: {e}")
        raise