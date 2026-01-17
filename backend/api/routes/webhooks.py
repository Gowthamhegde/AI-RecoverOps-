"""
Webhook API Routes
Endpoints for receiving webhooks from CI/CD platforms
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any
import logging

from pipeline_monitor.webhook_listener import WebhookListener
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Global webhook listener instance
webhook_listener = WebhookListener()

@router.post("/github")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint
    Receives events from GitHub Actions, PRs, pushes, etc.
    """
    try:
        return await webhook_listener.handle_github_webhook(request)
    except Exception as e:
        logger.error(f"GitHub webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/gitlab")
async def gitlab_webhook(request: Request):
    """
    GitLab webhook endpoint
    Receives events from GitLab CI/CD, merge requests, pushes, etc.
    """
    try:
        return await webhook_listener.handle_gitlab_webhook(request)
    except Exception as e:
        logger.error(f"GitLab webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/jenkins")
async def jenkins_webhook(request: Request):
    """
    Jenkins webhook endpoint
    Receives build notifications from Jenkins
    """
    try:
        return await webhook_listener.handle_jenkins_webhook(request)
    except Exception as e:
        logger.error(f"Jenkins webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/generic")
async def generic_webhook(request: Request, payload: Dict[Any, Any]):
    """
    Generic webhook endpoint for custom integrations
    """
    try:
        logger.info(f"Received generic webhook: {payload}")
        return {"status": "received", "message": "Generic webhook processed"}
    except Exception as e:
        logger.error(f"Generic webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/health")
async def webhook_health():
    """
    Health check for webhook service
    """
    return {
        "status": "healthy",
        "webhook_listener": webhook_listener.is_healthy(),
        "supported_platforms": ["github", "gitlab", "jenkins"]
    }