"""
Incidents API Routes
CRUD operations for incidents and remediation tracking
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from database.models import Incident, Remediation, IncidentStatus, IncidentSeverity
from database.connection import get_db_session
from api.auth import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API
class IncidentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    severity: str
    source_type: Optional[str]
    repository: Optional[str]
    branch: Optional[str]
    failure_type: Optional[str]
    root_cause: Optional[str]
    confidence_score: Optional[float]
    detected_at: str
    resolved_at: Optional[str]

class IncidentUpdate(BaseModel):
    status: Optional[str]
    severity: Optional[str]
    description: Optional[str]

class RemediationResponse(BaseModel):
    id: str
    action_type: str
    description: str
    status: str
    success: Optional[bool]
    started_at: Optional[str]
    completed_at: Optional[str]

@router.get("/", response_model=List[IncidentResponse])
async def get_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    repository: Optional[str] = Query(None, description="Filter by repository"),
    limit: int = Query(100, le=1000, description="Maximum number of incidents to return"),
    offset: int = Query(0, ge=0, description="Number of incidents to skip")
):
    """
    Get list of incidents with optional filtering
    """
    try:
        async with get_db_session() as session:
            query = session.query(Incident)
            
            # Apply filters
            if status:
                query = query.filter(Incident.status == status)
            if severity:
                query = query.filter(Incident.severity == severity)
            if repository:
                query = query.filter(Incident.repository.ilike(f"%{repository}%"))
            
            # Apply pagination
            incidents = await session.execute(
                query.order_by(Incident.detected_at.desc())
                     .offset(offset)
                     .limit(limit)
            )
            
            return [
                IncidentResponse(
                    id=str(incident.id),
                    title=incident.title,
                    description=incident.description,
                    status=incident.status,
                    severity=incident.severity,
                    source_type=incident.source_type,
                    repository=incident.repository,
                    branch=incident.branch,
                    failure_type=incident.failure_type,
                    root_cause=incident.root_cause,
                    confidence_score=incident.confidence_score,
                    detected_at=incident.detected_at.isoformat(),
                    resolved_at=incident.resolved_at.isoformat() if incident.resolved_at else None
                )
                for incident in incidents
            ]
            
    except Exception as e:
        logger.error(f"Error getting incidents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve incidents")

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: UUID):
    """
    Get specific incident by ID
    """
    try:
        async with get_db_session() as session:
            incident = await session.get(Incident, incident_id)
            
            if not incident:
                raise HTTPException(status_code=404, detail="Incident not found")
            
            return IncidentResponse(
                id=str(incident.id),
                title=incident.title,
                description=incident.description,
                status=incident.status,
                severity=incident.severity,
                source_type=incident.source_type,
                repository=incident.repository,
                branch=incident.branch,
                failure_type=incident.failure_type,
                root_cause=incident.root_cause,
                confidence_score=incident.confidence_score,
                detected_at=incident.detected_at.isoformat(),
                resolved_at=incident.resolved_at.isoformat() if incident.resolved_at else None
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve incident")

@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    update_data: IncidentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update incident details
    """
    try:
        async with get_db_session() as session:
            incident = await session.get(Incident, incident_id)
            
            if not incident:
                raise HTTPException(status_code=404, detail="Incident not found")
            
            # Update fields
            if update_data.status:
                incident.status = update_data.status
            if update_data.severity:
                incident.severity = update_data.severity
            if update_data.description:
                incident.description = update_data.description
            
            await session.commit()
            
            return IncidentResponse(
                id=str(incident.id),
                title=incident.title,
                description=incident.description,
                status=incident.status,
                severity=incident.severity,
                source_type=incident.source_type,
                repository=incident.repository,
                branch=incident.branch,
                failure_type=incident.failure_type,
                root_cause=incident.root_cause,
                confidence_score=incident.confidence_score,
                detected_at=incident.detected_at.isoformat(),
                resolved_at=incident.resolved_at.isoformat() if incident.resolved_at else None
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update incident")

@router.get("/{incident_id}/remediations", response_model=List[RemediationResponse])
async def get_incident_remediations(incident_id: UUID):
    """
    Get remediations for a specific incident
    """
    try:
        async with get_db_session() as session:
            # Verify incident exists
            incident = await session.get(Incident, incident_id)
            if not incident:
                raise HTTPException(status_code=404, detail="Incident not found")
            
            # Get remediations
            remediations = await session.execute(
                session.query(Remediation)
                       .filter(Remediation.incident_id == incident_id)
                       .order_by(Remediation.created_at.desc())
            )
            
            return [
                RemediationResponse(
                    id=str(remediation.id),
                    action_type=remediation.action_type,
                    description=remediation.description,
                    status=remediation.status,
                    success=remediation.success,
                    started_at=remediation.started_at.isoformat() if remediation.started_at else None,
                    completed_at=remediation.completed_at.isoformat() if remediation.completed_at else None
                )
                for remediation in remediations
            ]
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting remediations for incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve remediations")

@router.post("/{incident_id}/remediate")
async def trigger_remediation(
    incident_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger remediation for an incident
    """
    try:
        async with get_db_session() as session:
            incident = await session.get(Incident, incident_id)
            
            if not incident:
                raise HTTPException(status_code=404, detail="Incident not found")
            
            if incident.status in ["resolved", "fixing"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot remediate incident with status: {incident.status}"
                )
            
            # Queue for remediation
            from database.redis_client import redis_client
            import json
            from datetime import datetime
            
            remediation_data = {
                "incident_id": str(incident_id),
                "triggered_by": current_user.get("username", "manual"),
                "manual_trigger": True,
                "queued_at": datetime.utcnow().isoformat()
            }
            
            await redis_client.rpush("remediation_queue", json.dumps(remediation_data))
            
            # Update incident status
            incident.status = "fixing"
            await session.commit()
            
            return {
                "message": "Remediation triggered successfully",
                "incident_id": str(incident_id),
                "status": "queued"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering remediation for incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger remediation")

@router.post("/{incident_id}/rollback")
async def rollback_incident(
    incident_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Rollback remediation for an incident
    """
    try:
        # Import here to avoid circular imports
        from remediation.executor import RemediationExecutor
        
        executor = RemediationExecutor()
        success = await executor.rollback_remediation(str(incident_id))
        
        if success:
            return {
                "message": "Rollback completed successfully",
                "incident_id": str(incident_id),
                "status": "rolled_back"
            }
        else:
            raise HTTPException(status_code=500, detail="Rollback failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to rollback incident")

@router.get("/stats/summary")
async def get_incident_stats():
    """
    Get incident statistics summary
    """
    try:
        async with get_db_session() as session:
            from sqlalchemy import func, and_
            from datetime import datetime, timedelta
            
            # Total incidents
            total_incidents = await session.execute(
                session.query(func.count(Incident.id))
            )
            total_count = total_incidents.scalar()
            
            # Active incidents
            active_incidents = await session.execute(
                session.query(func.count(Incident.id))
                       .filter(Incident.status.in_(["detected", "analyzing", "fixing"]))
            )
            active_count = active_incidents.scalar()
            
            # Resolved today
            today = datetime.utcnow().date()
            resolved_today = await session.execute(
                session.query(func.count(Incident.id))
                       .filter(and_(
                           Incident.status == "resolved",
                           func.date(Incident.resolved_at) == today
                       ))
            )
            resolved_today_count = resolved_today.scalar()
            
            # Success rate (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_incidents = await session.execute(
                session.query(func.count(Incident.id))
                       .filter(Incident.detected_at >= thirty_days_ago)
            )
            recent_count = recent_incidents.scalar()
            
            recent_resolved = await session.execute(
                session.query(func.count(Incident.id))
                       .filter(and_(
                           Incident.detected_at >= thirty_days_ago,
                           Incident.status == "resolved"
                       ))
            )
            recent_resolved_count = recent_resolved.scalar()
            
            success_rate = (recent_resolved_count / recent_count * 100) if recent_count > 0 else 0
            
            return {
                "total_incidents": total_count,
                "active_incidents": active_count,
                "resolved_today": resolved_today_count,
                "success_rate": round(success_rate, 1),
                "period": "last_30_days"
            }
            
    except Exception as e:
        logger.error(f"Error getting incident stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@router.get("/trends/daily")
async def get_daily_trends(days: int = Query(30, le=90, description="Number of days to include")):
    """
    Get daily incident trends
    """
    try:
        async with get_db_session() as session:
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Daily incident counts
            daily_counts = await session.execute(
                session.query(
                    func.date(Incident.detected_at).label('date'),
                    func.count(Incident.id).label('count')
                )
                .filter(Incident.detected_at >= start_date)
                .group_by(func.date(Incident.detected_at))
                .order_by(func.date(Incident.detected_at))
            )
            
            return [
                {
                    "date": str(row.date),
                    "incidents": row.count
                }
                for row in daily_counts
            ]
            
    except Exception as e:
        logger.error(f"Error getting daily trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trends")