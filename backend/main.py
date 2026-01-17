#!/usr/bin/env python3
"""
AI-RecoverOps Production Backend
Main FastAPI application entry point
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer
import uvicorn

from api.routes import incidents, pipelines, recovery, webhooks, dashboard
from api.middleware import RateLimitMiddleware, LoggingMiddleware
from database.connection import init_database, close_database
from pipeline_monitor.webhook_listener import WebhookListener
from log_parser.stream_processor import LogStreamProcessor
from ai_engine.failure_detector import FailureDetector
from ai_engine.root_cause_analyzer import RootCauseAnalyzer
from ai_engine.fix_generator import FixGenerator
from remediation.executor import RemediationExecutor
from aws_recovery.resource_manager import AWSResourceManager
from database.models import SystemHealth
from api.auth import get_current_user
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global components
webhook_listener = None
log_processor = None
failure_detector = None
root_cause_analyzer = None
fix_generator = None
remediation_executor = None
aws_recovery = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global webhook_listener, log_processor, failure_detector
    global root_cause_analyzer, fix_generator, remediation_executor, aws_recovery
    
    logger.info("🚀 Starting AI-RecoverOps Production System")
    
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized")
        
        # Initialize core components
        webhook_listener = WebhookListener()
        log_processor = LogStreamProcessor()
        failure_detector = FailureDetector()
        root_cause_analyzer = RootCauseAnalyzer()
        fix_generator = FixGenerator()
        remediation_executor = RemediationExecutor()
        aws_recovery = AWSResourceManager()
        
        # Start background services
        asyncio.create_task(webhook_listener.start())
        asyncio.create_task(log_processor.start())
        asyncio.create_task(failure_detector.start())
        
        logger.info("✅ All services started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start services: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🛑 Shutting down AI-RecoverOps")
        
        if webhook_listener:
            await webhook_listener.stop()
        if log_processor:
            await log_processor.stop()
        if failure_detector:
            await failure_detector.stop()
            
        await close_database()
        logger.info("✅ Cleanup completed")

# Create FastAPI application
app = FastAPI(
    title="AI-RecoverOps Production API",
    description="Autonomous DevOps Recovery System - AI SRE Engineer",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(pipelines.router, prefix="/api/pipelines", tags=["pipelines"])
app.include_router(recovery.router, prefix="/api/recovery", tags=["recovery"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/health")
async def health_check():
    """Production health check endpoint"""
    try:
        # Check database connectivity
        from database.connection import get_db_session
        async with get_db_session() as session:
            await session.execute("SELECT 1")
        
        # Check Redis connectivity
        from database.redis_client import redis_client
        await redis_client.ping()
        
        # Check component health
        component_health = {
            "webhook_listener": webhook_listener.is_healthy() if webhook_listener else False,
            "log_processor": log_processor.is_healthy() if log_processor else False,
            "failure_detector": failure_detector.is_healthy() if failure_detector else False,
            "ai_analyzer": root_cause_analyzer.is_healthy() if root_cause_analyzer else False,
            "fix_generator": fix_generator.is_healthy() if fix_generator else False,
            "remediation_executor": remediation_executor.is_healthy() if remediation_executor else False,
            "aws_recovery": aws_recovery.is_healthy() if aws_recovery else False,
        }
        
        all_healthy = all(component_health.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": "2026-01-14T00:00:00Z",
            "version": "2.0.0",
            "components": component_health,
            "uptime": "running",
            "environment": settings.ENVIRONMENT
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def get_metrics():
    """Prometheus-compatible metrics endpoint"""
    try:
        from database.metrics import MetricsCollector
        metrics = MetricsCollector()
        return await metrics.get_prometheus_metrics()
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics unavailable")

@app.post("/api/emergency-stop")
async def emergency_stop(current_user: dict = Depends(get_current_user)):
    """Emergency stop all automated remediation"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if remediation_executor:
            await remediation_executor.emergency_stop()
        
        logger.warning(f"Emergency stop triggered by {current_user.get('username')}")
        return {"message": "Emergency stop activated", "status": "stopped"}
        
    except Exception as e:
        logger.error(f"Emergency stop failed: {e}")
        raise HTTPException(status_code=500, detail="Emergency stop failed")

@app.get("/api/system-status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        from database.queries import get_system_metrics
        
        metrics = await get_system_metrics()
        
        return {
            "system_health": "operational",
            "active_incidents": metrics.get("active_incidents", 0),
            "resolved_today": metrics.get("resolved_today", 0),
            "success_rate": metrics.get("success_rate", 0.0),
            "avg_resolution_time": metrics.get("avg_resolution_time", 0),
            "pipelines_monitored": metrics.get("pipelines_monitored", 0),
            "aws_resources_managed": metrics.get("aws_resources_managed", 0),
            "last_update": "2026-01-14T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time dashboard updates"""
    from api.websocket_manager import WebSocketManager
    
    manager = WebSocketManager()
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and send updates
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level="info"
    )