"""
Webhook Listener for CI/CD Platforms
Receives and processes webhooks from GitHub, GitLab, Jenkins, etc.
"""

import asyncio
import logging
import json
import hmac
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from fastapi import Request, HTTPException
from database.models import PipelineRun, PipelineStatus
from database.connection import get_db_session
from database.redis_client import redis_client
from config import settings

logger = logging.getLogger(__name__)

@dataclass
class WebhookEvent:
    platform: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    signature: Optional[str] = None

class WebhookListener:
    """Listens to and processes webhooks from various CI/CD platforms"""
    
    def __init__(self):
        self.running = False
        self.processed_events = set()  # Prevent duplicate processing
        
    async def start(self):
        """Start the webhook listener service"""
        self.running = True
        logger.info("📡 Starting Webhook Listener Service")
        
        # Start background processing
        asyncio.create_task(self._process_webhook_queue())
    
    async def stop(self):
        """Stop the webhook listener service"""
        self.running = False
        logger.info("🛑 Stopping Webhook Listener Service")
    
    def is_healthy(self) -> bool:
        """Check if the webhook listener is healthy"""
        return self.running
    
    async def handle_github_webhook(self, request: Request) -> Dict[str, str]:
        """Handle GitHub webhook events"""
        try:
            # Verify signature
            signature = request.headers.get("X-Hub-Signature-256")
            if not self._verify_github_signature(await request.body(), signature):
                raise HTTPException(status_code=403, detail="Invalid signature")
            
            # Parse payload
            payload = await request.json()
            event_type = request.headers.get("X-GitHub-Event")
            
            # Create webhook event
            webhook_event = WebhookEvent(
                platform="github",
                event_type=event_type,
                payload=payload,
                timestamp=datetime.utcnow(),
                signature=signature
            )
            
            # Queue for processing
            await self._queue_webhook_event(webhook_event)
            
            logger.info(f"📥 Received GitHub webhook: {event_type}")
            return {"status": "received", "event": event_type}
            
        except Exception as e:
            logger.error(f"Error handling GitHub webhook: {e}")
            raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    async def handle_gitlab_webhook(self, request: Request) -> Dict[str, str]:
        """Handle GitLab webhook events"""
        try:
            # Verify token
            token = request.headers.get("X-Gitlab-Token")
            if token != settings.GITLAB_WEBHOOK_SECRET:
                raise HTTPException(status_code=403, detail="Invalid token")
            
            # Parse payload
            payload = await request.json()
            event_type = request.headers.get("X-Gitlab-Event")
            
            # Create webhook event
            webhook_event = WebhookEvent(
                platform="gitlab",
                event_type=event_type,
                payload=payload,
                timestamp=datetime.utcnow()
            )
            
            # Queue for processing
            await self._queue_webhook_event(webhook_event)
            
            logger.info(f"📥 Received GitLab webhook: {event_type}")
            return {"status": "received", "event": event_type}
            
        except Exception as e:
            logger.error(f"Error handling GitLab webhook: {e}")
            raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    async def handle_jenkins_webhook(self, request: Request) -> Dict[str, str]:
        """Handle Jenkins webhook events"""
        try:
            # Parse payload
            payload = await request.json()
            
            # Create webhook event
            webhook_event = WebhookEvent(
                platform="jenkins",
                event_type="build_event",
                payload=payload,
                timestamp=datetime.utcnow()
            )
            
            # Queue for processing
            await self._queue_webhook_event(webhook_event)
            
            logger.info(f"📥 Received Jenkins webhook")
            return {"status": "received", "event": "build_event"}
            
        except Exception as e:
            logger.error(f"Error handling Jenkins webhook: {e}")
            raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    def _verify_github_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        try:
            if not settings.GITHUB_WEBHOOK_SECRET or not signature:
                return True  # Skip verification if no secret configured
            
            expected_signature = "sha256=" + hmac.new(
                settings.GITHUB_WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying GitHub signature: {e}")
            return False
    
    async def _queue_webhook_event(self, event: WebhookEvent):
        """Queue webhook event for processing"""
        try:
            event_data = {
                "platform": event.platform,
                "event_type": event.event_type,
                "payload": event.payload,
                "timestamp": event.timestamp.isoformat(),
                "signature": event.signature
            }
            
            await redis_client.rpush("webhook_queue", json.dumps(event_data))
            logger.debug(f"Queued webhook event: {event.platform}/{event.event_type}")
            
        except Exception as e:
            logger.error(f"Error queuing webhook event: {e}")
    
    async def _process_webhook_queue(self):
        """Process queued webhook events"""
        while self.running:
            try:
                # Get event from queue
                event_data = await redis_client.lpop("webhook_queue")
                if not event_data:
                    await asyncio.sleep(5)
                    continue
                
                event_info = json.loads(event_data)
                
                # Process based on platform
                if event_info["platform"] == "github":
                    await self._process_github_event(event_info)
                elif event_info["platform"] == "gitlab":
                    await self._process_gitlab_event(event_info)
                elif event_info["platform"] == "jenkins":
                    await self._process_jenkins_event(event_info)
                
            except Exception as e:
                logger.error(f"Error processing webhook queue: {e}")
                await asyncio.sleep(10)
    
    async def _process_github_event(self, event_info: Dict):
        """Process GitHub webhook event"""
        try:
            event_type = event_info["event_type"]
            payload = event_info["payload"]
            
            if event_type == "workflow_run":
                await self._process_github_workflow_run(payload)
            elif event_type == "check_run":
                await self._process_github_check_run(payload)
            elif event_type == "push":
                await self._process_github_push(payload)
            elif event_type == "pull_request":
                await self._process_github_pull_request(payload)
            
        except Exception as e:
            logger.error(f"Error processing GitHub event: {e}")
    
    async def _process_github_workflow_run(self, payload: Dict):
        """Process GitHub Actions workflow run event"""
        try:
            workflow_run = payload.get("workflow_run", {})
            action = payload.get("action")
            
            # Create or update pipeline run record
            pipeline_run = await self._create_or_update_pipeline_run(
                platform="github",
                pipeline_id=str(workflow_run.get("id")),
                run_number=workflow_run.get("run_number"),
                status=self._map_github_status(workflow_run.get("status"), workflow_run.get("conclusion")),
                repository=payload.get("repository", {}).get("full_name"),
                branch=workflow_run.get("head_branch"),
                commit_sha=workflow_run.get("head_sha"),
                commit_message=workflow_run.get("head_commit", {}).get("message"),
                author=workflow_run.get("head_commit", {}).get("author", {}).get("name"),
                started_at=workflow_run.get("created_at"),
                finished_at=workflow_run.get("updated_at"),
                logs_url=workflow_run.get("logs_url"),
                metadata={
                    "workflow_name": workflow_run.get("name"),
                    "event": workflow_run.get("event"),
                    "actor": workflow_run.get("actor", {}).get("login"),
                    "html_url": workflow_run.get("html_url")
                }
            )
            
            # If workflow failed, trigger failure detection
            if action == "completed" and workflow_run.get("conclusion") == "failure":
                await self._trigger_failure_detection(pipeline_run, payload)
            
        except Exception as e:
            logger.error(f"Error processing GitHub workflow run: {e}")
    
    async def _process_github_check_run(self, payload: Dict):
        """Process GitHub check run event"""
        try:
            check_run = payload.get("check_run", {})
            action = payload.get("action")
            
            # Only process completed check runs
            if action == "completed" and check_run.get("conclusion") == "failure":
                # Create pipeline run record for failed check
                pipeline_run = await self._create_or_update_pipeline_run(
                    platform="github",
                    pipeline_id=f"check_{check_run.get('id')}",
                    run_number=1,
                    status=PipelineStatus.FAILED,
                    repository=payload.get("repository", {}).get("full_name"),
                    branch=check_run.get("check_suite", {}).get("head_branch"),
                    commit_sha=check_run.get("head_sha"),
                    metadata={
                        "check_name": check_run.get("name"),
                        "html_url": check_run.get("html_url"),
                        "output": check_run.get("output", {})
                    }
                )
                
                await self._trigger_failure_detection(pipeline_run, payload)
            
        except Exception as e:
            logger.error(f"Error processing GitHub check run: {e}")
    
    async def _process_github_push(self, payload: Dict):
        """Process GitHub push event"""
        try:
            # Log push event for context
            repository = payload.get("repository", {}).get("full_name")
            branch = payload.get("ref", "").replace("refs/heads/", "")
            commits = payload.get("commits", [])
            
            logger.info(f"📝 Push to {repository}:{branch} - {len(commits)} commits")
            
            # Store push information for context in failure analysis
            push_data = {
                "repository": repository,
                "branch": branch,
                "commits": commits,
                "pusher": payload.get("pusher", {}).get("name"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in Redis for context
            await redis_client.setex(
                f"push_context:{repository}:{branch}",
                3600,  # 1 hour TTL
                json.dumps(push_data)
            )
            
        except Exception as e:
            logger.error(f"Error processing GitHub push: {e}")
    
    async def _process_github_pull_request(self, payload: Dict):
        """Process GitHub pull request event"""
        try:
            pr = payload.get("pull_request", {})
            action = payload.get("action")
            
            # Log PR events for context
            if action in ["opened", "synchronize", "closed"]:
                logger.info(f"📋 PR {action}: #{pr.get('number')} in {payload.get('repository', {}).get('full_name')}")
            
        except Exception as e:
            logger.error(f"Error processing GitHub pull request: {e}")
    
    async def _process_gitlab_event(self, event_info: Dict):
        """Process GitLab webhook event"""
        try:
            event_type = event_info["event_type"]
            payload = event_info["payload"]
            
            if event_type == "Pipeline Hook":
                await self._process_gitlab_pipeline(payload)
            elif event_type == "Job Hook":
                await self._process_gitlab_job(payload)
            elif event_type == "Push Hook":
                await self._process_gitlab_push(payload)
            
        except Exception as e:
            logger.error(f"Error processing GitLab event: {e}")
    
    async def _process_gitlab_pipeline(self, payload: Dict):
        """Process GitLab pipeline event"""
        try:
            object_attributes = payload.get("object_attributes", {})
            
            pipeline_run = await self._create_or_update_pipeline_run(
                platform="gitlab",
                pipeline_id=str(object_attributes.get("id")),
                run_number=object_attributes.get("id"),
                status=self._map_gitlab_status(object_attributes.get("status")),
                repository=payload.get("project", {}).get("path_with_namespace"),
                branch=object_attributes.get("ref"),
                commit_sha=object_attributes.get("sha"),
                started_at=object_attributes.get("created_at"),
                finished_at=object_attributes.get("finished_at"),
                metadata={
                    "pipeline_url": object_attributes.get("url"),
                    "source": object_attributes.get("source"),
                    "user": payload.get("user", {}).get("name")
                }
            )
            
            # If pipeline failed, trigger failure detection
            if object_attributes.get("status") == "failed":
                await self._trigger_failure_detection(pipeline_run, payload)
            
        except Exception as e:
            logger.error(f"Error processing GitLab pipeline: {e}")
    
    async def _process_gitlab_job(self, payload: Dict):
        """Process GitLab job event"""
        try:
            # Similar to pipeline processing but for individual jobs
            pass
            
        except Exception as e:
            logger.error(f"Error processing GitLab job: {e}")
    
    async def _process_gitlab_push(self, payload: Dict):
        """Process GitLab push event"""
        try:
            # Similar to GitHub push processing
            pass
            
        except Exception as e:
            logger.error(f"Error processing GitLab push: {e}")
    
    async def _process_jenkins_event(self, event_info: Dict):
        """Process Jenkins webhook event"""
        try:
            payload = event_info["payload"]
            
            # Jenkins webhook format varies, adapt as needed
            build_info = payload.get("build", {})
            
            pipeline_run = await self._create_or_update_pipeline_run(
                platform="jenkins",
                pipeline_id=f"{payload.get('name')}_{build_info.get('number')}",
                run_number=build_info.get("number"),
                status=self._map_jenkins_status(build_info.get("status")),
                repository=payload.get("repository"),
                branch=build_info.get("scm", {}).get("branch"),
                commit_sha=build_info.get("scm", {}).get("commit"),
                started_at=build_info.get("timestamp"),
                metadata={
                    "job_name": payload.get("name"),
                    "build_url": build_info.get("full_url")
                }
            )
            
            # If build failed, trigger failure detection
            if build_info.get("status") in ["FAILURE", "ABORTED"]:
                await self._trigger_failure_detection(pipeline_run, payload)
            
        except Exception as e:
            logger.error(f"Error processing Jenkins event: {e}")
    
    async def _create_or_update_pipeline_run(self, **kwargs) -> PipelineRun:
        """Create or update pipeline run record"""
        try:
            async with get_db_session() as session:
                # Check if pipeline run already exists
                existing_run = await session.execute(
                    session.query(PipelineRun).filter(
                        PipelineRun.pipeline_id == kwargs["pipeline_id"]
                    ).first()
                )
                
                if existing_run:
                    # Update existing record
                    for key, value in kwargs.items():
                        if hasattr(existing_run, key) and value is not None:
                            setattr(existing_run, key, value)
                    pipeline_run = existing_run
                else:
                    # Create new record
                    pipeline_run = PipelineRun(**kwargs)
                    session.add(pipeline_run)
                
                await session.commit()
                return pipeline_run
                
        except Exception as e:
            logger.error(f"Error creating/updating pipeline run: {e}")
            raise
    
    def _map_github_status(self, status: str, conclusion: str) -> PipelineStatus:
        """Map GitHub status to internal status"""
        if status == "completed":
            if conclusion == "success":
                return PipelineStatus.SUCCESS
            elif conclusion == "failure":
                return PipelineStatus.FAILED
            elif conclusion == "cancelled":
                return PipelineStatus.CANCELLED
        elif status == "in_progress":
            return PipelineStatus.RUNNING
        
        return PipelineStatus.PENDING
    
    def _map_gitlab_status(self, status: str) -> PipelineStatus:
        """Map GitLab status to internal status"""
        status_map = {
            "success": PipelineStatus.SUCCESS,
            "failed": PipelineStatus.FAILED,
            "canceled": PipelineStatus.CANCELLED,
            "running": PipelineStatus.RUNNING,
            "pending": PipelineStatus.PENDING
        }
        return status_map.get(status, PipelineStatus.PENDING)
    
    def _map_jenkins_status(self, status: str) -> PipelineStatus:
        """Map Jenkins status to internal status"""
        status_map = {
            "SUCCESS": PipelineStatus.SUCCESS,
            "FAILURE": PipelineStatus.FAILED,
            "ABORTED": PipelineStatus.CANCELLED,
            "UNSTABLE": PipelineStatus.FAILED
        }
        return status_map.get(status, PipelineStatus.RUNNING)
    
    async def _trigger_failure_detection(self, pipeline_run: PipelineRun, webhook_payload: Dict):
        """Trigger failure detection for failed pipeline"""
        try:
            # Create log entry for failure detection
            log_data = {
                "source_type": pipeline_run.source_type,
                "source_id": pipeline_run.pipeline_id,
                "repository": pipeline_run.repository,
                "branch": pipeline_run.branch,
                "commit_sha": pipeline_run.commit_sha,
                "message": f"Pipeline failed: {pipeline_run.error_message or 'Unknown error'}",
                "level": "ERROR",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "pipeline_run_id": str(pipeline_run.id),
                    "webhook_payload": webhook_payload
                }
            }
            
            # Queue for failure detection
            await redis_client.rpush("log_queue", json.dumps(log_data))
            
            logger.info(f"🚨 Triggered failure detection for pipeline: {pipeline_run.pipeline_id}")
            
        except Exception as e:
            logger.error(f"Error triggering failure detection: {e}")