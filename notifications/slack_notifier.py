#!/usr/bin/env python3
"""
Slack notification handler for AI-RecoverOps
"""

import json
import requests
import logging
from datetime import datetime
from typing import Dict, Any, List
import os

logger = logging.getLogger(__name__)

class SlackNotifier:
    """Handle Slack notifications for AI-RecoverOps incidents"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.environ.get('SLACK_WEBHOOK_URL')
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
    
    def send_incident_alert(self, incidents: List[Dict[str, Any]]) -> bool:
        """Send incident alert to Slack"""
        if not self.webhook_url:
            logger.error("Slack webhook URL not configured")
            return False
        
        try:
            # Prepare Slack message
            message = self._format_incident_message(incidents)
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Sent Slack alert for {len(incidents)} incidents")
                return True
            else:
                logger.error(f"Slack API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def send_remediation_update(self, remediation_result: Dict[str, Any]) -> bool:
        """Send remediation update to Slack"""
        if not self.webhook_url:
            return False
        
        try:
            message = self._format_remediation_message(remediation_result)
            
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending remediation update: {e}")
            return False
    
    def _format_incident_message(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format incident alert message for Slack"""
        
        # Count incidents by severity
        critical_count = sum(1 for i in incidents if i.get('severity') == 'critical')
        high_count = sum(1 for i in incidents if i.get('severity') == 'high')
        medium_count = sum(1 for i in incidents if i.get('severity') == 'medium')
        
        # Determine alert color
        if critical_count > 0:
            color = "danger"
            emoji = "🚨"
        elif high_count > 0:
            color = "warning"
            emoji = "⚠️"
        else:
            color = "good"
            emoji = "ℹ️"
        
        # Create main message
        main_text = f"{emoji} *AI-RecoverOps Alert*: {len(incidents)} incident(s) detected"
        
        # Create attachment with incident details
        attachment = {
            "color": color,
            "title": "Incident Summary",
            "fields": [
                {
                    "title": "Total Incidents",
                    "value": str(len(incidents)),
                    "short": True
                },
                {
                    "title": "Severity Breakdown",
                    "value": f"Critical: {critical_count}\nHigh: {high_count}\nMedium: {medium_count}",
                    "short": True
                },
                {
                    "title": "Timestamp",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "short": True
                }
            ],
            "footer": "AI-RecoverOps",
            "ts": int(datetime.now().timestamp())
        }
        
        # Add incident details
        incident_blocks = []
        for i, incident in enumerate(incidents[:5], 1):  # Limit to 5 incidents
            prediction = incident.get('prediction', {})
            log = incident.get('log', {})
            
            incident_text = (
                f"*{i}. {prediction.get('incident_type', 'Unknown').replace('_', ' ').title()}*\n"
                f"• Confidence: {prediction.get('confidence', 0):.1%}\n"
                f"• Service: `{log.get('service', 'unknown')}`\n"
                f"• Instance: `{log.get('instance_id', 'unknown')}`\n"
                f"• Action: `{prediction.get('recommended_action', 'none')}`\n"
                f"• Message: _{log.get('message', '')[:100]}..._"
            )
            
            incident_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": incident_text
                }
            })
        
        if len(incidents) > 5:
            incident_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_... and {len(incidents) - 5} more incidents_"
                }
            })
        
        # Add action buttons
        action_block = {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Dashboard"
                    },
                    "url": "https://ai-recoverops-dashboard.example.com",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Logs"
                    },
                    "url": "https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups"
                }
            ]
        }
        
        return {
            "text": main_text,
            "attachments": [attachment],
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} AI-RecoverOps Alert"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Detected *{len(incidents)} incident(s)* requiring attention"
                    }
                },
                {
                    "type": "divider"
                }
            ] + incident_blocks + [
                {
                    "type": "divider"
                },
                action_block
            ]
        }
    
    def _format_remediation_message(self, remediation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format remediation update message for Slack"""
        
        success = remediation_result.get('success', False)
        action = remediation_result.get('action', 'unknown')
        incident_type = remediation_result.get('incident_type', 'unknown')
        
        if success:
            color = "good"
            emoji = "✅"
            title = "Remediation Successful"
        else:
            color = "danger"
            emoji = "❌"
            title = "Remediation Failed"
        
        main_text = f"{emoji} *AI-RecoverOps*: {title}"
        
        # Create attachment
        attachment = {
            "color": color,
            "title": title,
            "fields": [
                {
                    "title": "Incident Type",
                    "value": incident_type.replace('_', ' ').title(),
                    "short": True
                },
                {
                    "title": "Action Taken",
                    "value": action.replace('_', ' ').title(),
                    "short": True
                },
                {
                    "title": "Instance ID",
                    "value": remediation_result.get('instance_id', 'N/A'),
                    "short": True
                },
                {
                    "title": "Service",
                    "value": remediation_result.get('service_name', 'N/A'),
                    "short": True
                }
            ],
            "footer": "AI-RecoverOps Auto-Remediation",
            "ts": int(datetime.now().timestamp())
        }
        
        if not success:
            attachment["fields"].append({
                "title": "Error",
                "value": remediation_result.get('error', 'Unknown error'),
                "short": False
            })
        
        return {
            "text": main_text,
            "attachments": [attachment]
        }

class EmailNotifier:
    """Handle email notifications for AI-RecoverOps"""
    
    def __init__(self, sns_topic_arn: str = None):
        self.sns_topic_arn = sns_topic_arn or os.environ.get('SNS_TOPIC_ARN')
        
        if self.sns_topic_arn:
            import boto3
            self.sns_client = boto3.client('sns')
        else:
            logger.warning("SNS topic ARN not configured for email notifications")
    
    def send_incident_report(self, incidents: List[Dict[str, Any]]) -> bool:
        """Send detailed incident report via email"""
        if not self.sns_topic_arn:
            return False
        
        try:
            subject = f"AI-RecoverOps Incident Report - {len(incidents)} incidents detected"
            message = self._format_email_report(incidents)
            
            self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Subject=subject,
                Message=message
            )
            
            logger.info(f"Sent email report for {len(incidents)} incidents")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    def _format_email_report(self, incidents: List[Dict[str, Any]]) -> str:
        """Format detailed email report"""
        
        lines = [
            "AI-RecoverOps Incident Report",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Total Incidents: {len(incidents)}",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 20
        ]
        
        # Summary by severity
        severity_counts = {}
        incident_type_counts = {}
        
        for incident in incidents:
            severity = incident.get('severity', 'unknown')
            incident_type = incident.get('prediction', {}).get('incident_type', 'unknown')
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            incident_type_counts[incident_type] = incident_type_counts.get(incident_type, 0) + 1
        
        lines.extend([
            "Severity Distribution:",
            f"  Critical: {severity_counts.get('critical', 0)}",
            f"  High: {severity_counts.get('high', 0)}",
            f"  Medium: {severity_counts.get('medium', 0)}",
            "",
            "Top Incident Types:",
        ])
        
        # Sort incident types by count
        sorted_types = sorted(incident_type_counts.items(), key=lambda x: x[1], reverse=True)
        for incident_type, count in sorted_types[:5]:
            lines.append(f"  {incident_type.replace('_', ' ').title()}: {count}")
        
        lines.extend([
            "",
            "DETAILED INCIDENT LIST",
            "-" * 25
        ])
        
        # Detailed incident information
        for i, incident in enumerate(incidents, 1):
            prediction = incident.get('prediction', {})
            log = incident.get('log', {})
            
            lines.extend([
                f"{i}. {prediction.get('incident_type', 'Unknown').replace('_', ' ').title()}",
                f"   Confidence: {prediction.get('confidence', 0):.1%}",
                f"   Severity: {incident.get('severity', 'unknown').title()}",
                f"   Service: {log.get('service', 'unknown')}",
                f"   Instance: {log.get('instance_id', 'unknown')}",
                f"   Timestamp: {log.get('timestamp', 'unknown')}",
                f"   Recommended Action: {prediction.get('recommended_action', 'none')}",
                f"   Message: {log.get('message', '')[:200]}...",
                ""
            ])
        
        lines.extend([
            "NEXT STEPS",
            "-" * 10,
            "1. Review the AI-RecoverOps dashboard for real-time status",
            "2. Check if auto-remediation has been triggered for eligible incidents",
            "3. Manually investigate and resolve any remaining issues",
            "4. Monitor system performance after remediation",
            "",
            "Dashboard: https://ai-recoverops-dashboard.example.com",
            "CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups",
            "",
            "This is an automated report from AI-RecoverOps.",
            "For support, contact: devops-team@example.com"
        ])
        
        return "\n".join(lines)

# Lambda function for SNS-triggered notifications
def lambda_handler(event, context):
    """Lambda handler for processing SNS notifications"""
    
    try:
        # Parse SNS message
        for record in event['Records']:
            if record['EventSource'] == 'aws:sns':
                message = json.loads(record['Sns']['Message'])
                
                # Initialize notifiers
                slack_notifier = SlackNotifier()
                email_notifier = EmailNotifier()
                
                # Determine notification type
                if 'incidents' in message:
                    # Incident alert
                    incidents = message['incidents']
                    
                    # Send Slack notification
                    slack_notifier.send_incident_alert(incidents)
                    
                    # Send email report for critical incidents
                    critical_incidents = [i for i in incidents if i.get('severity') == 'critical']
                    if critical_incidents:
                        email_notifier.send_incident_report(critical_incidents)
                
                elif 'remediation_result' in message:
                    # Remediation update
                    remediation_result = message['remediation_result']
                    slack_notifier.send_remediation_update(remediation_result)
        
        return {'statusCode': 200, 'body': 'Notifications sent successfully'}
        
    except Exception as e:
        logger.error(f"Error processing notification: {e}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

if __name__ == "__main__":
    # Test notifications
    test_incidents = [
        {
            'prediction': {
                'incident_type': 'high_cpu',
                'confidence': 0.95,
                'recommended_action': 'restart_service'
            },
            'log': {
                'service': 'web-server',
                'instance_id': 'i-1234567890abcdef0',
                'message': 'CPU usage exceeded 95% for 5 minutes',
                'timestamp': datetime.now().isoformat()
            },
            'severity': 'critical'
        }
    ]
    
    slack_notifier = SlackNotifier()
    slack_notifier.send_incident_alert(test_incidents)