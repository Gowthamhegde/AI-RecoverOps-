"""
AI-Powered Root Cause Analysis Engine
Uses LLM and pattern analysis to determine root causes of failures
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import openai
from database.models import Incident, LogEntry
from database.connection import get_db_session
from database.redis_client import redis_client
from config import settings

logger = logging.getLogger(__name__)

@dataclass
class RootCauseAnalysis:
    root_cause: str
    confidence: float
    explanation: str
    suggested_fixes: List[str]
    analysis_data: Dict[str, Any]

class RootCauseAnalyzer:
    """Advanced root cause analysis using LLM and pattern matching"""
    
    def __init__(self):
        self.running = False
        self.openai_client = None
        self._initialize_openai()
        
        # Knowledge base of common root causes
        self.knowledge_base = self._load_knowledge_base()
        
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                logger.info("✅ OpenAI client initialized")
            else:
                logger.warning("⚠️ OpenAI API key not provided, using fallback analysis")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
    
    def _load_knowledge_base(self) -> Dict[str, Dict]:
        """Load knowledge base of common failure patterns and root causes"""
        return {
            "build_failure": {
                "common_causes": [
                    "Missing dependencies",
                    "Version conflicts",
                    "Compilation errors",
                    "Environment configuration issues",
                    "Build tool configuration problems"
                ],
                "analysis_prompts": [
                    "Check package.json/requirements.txt for dependency issues",
                    "Verify build tool configuration",
                    "Check for syntax errors in source code",
                    "Validate environment variables"
                ]
            },
            "test_failure": {
                "common_causes": [
                    "Test assertion failures",
                    "Test environment issues",
                    "Data setup problems",
                    "Timing/race conditions",
                    "Mock/stub configuration issues"
                ],
                "analysis_prompts": [
                    "Analyze test assertion failures",
                    "Check test data setup",
                    "Verify mock configurations",
                    "Look for timing issues"
                ]
            },
            "deployment_failure": {
                "common_causes": [
                    "Resource constraints",
                    "Configuration errors",
                    "Network connectivity issues",
                    "Permission problems",
                    "Image/artifact issues"
                ],
                "analysis_prompts": [
                    "Check resource limits and quotas",
                    "Verify deployment configuration",
                    "Check network connectivity",
                    "Validate permissions and credentials"
                ]
            },
            "dependency_error": {
                "common_causes": [
                    "Package not found",
                    "Version incompatibility",
                    "Registry access issues",
                    "Circular dependencies",
                    "Missing system dependencies"
                ],
                "analysis_prompts": [
                    "Check package registry availability",
                    "Verify version compatibility",
                    "Look for circular dependency issues",
                    "Check system-level dependencies"
                ]
            }
        }
    
    async def start(self):
        """Start the root cause analysis service"""
        self.running = True
        logger.info("🧠 Starting Root Cause Analysis Engine")
        
        while self.running:
            try:
                await self._process_pending_incidents()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in root cause analysis loop: {e}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Stop the root cause analysis service"""
        self.running = False
        logger.info("🛑 Stopping Root Cause Analysis Engine")
    
    def is_healthy(self) -> bool:
        """Check if the analyzer is healthy"""
        return self.running
    
    async def _process_pending_incidents(self):
        """Process incidents pending root cause analysis"""
        try:
            # Get incidents from Redis queue
            incident_data = await redis_client.lpop("incident_queue")
            if not incident_data:
                return
            
            incident_info = json.loads(incident_data)
            incident_id = incident_info["incident_id"]
            
            # Perform root cause analysis
            analysis = await self.analyze_incident(incident_id)
            
            if analysis:
                await self._update_incident_with_analysis(incident_id, analysis)
                await self._queue_for_fix_generation(incident_id, analysis)
                
        except Exception as e:
            logger.error(f"Error processing pending incidents: {e}")
    
    async def analyze_incident(self, incident_id: str) -> Optional[RootCauseAnalysis]:
        """Perform comprehensive root cause analysis for an incident"""
        try:
            async with get_db_session() as session:
                # Get incident details
                incident = await session.get(Incident, incident_id)
                if not incident:
                    logger.error(f"Incident not found: {incident_id}")
                    return None
                
                logger.info(f"🔍 Analyzing incident: {incident.title}")
                
                # Gather context information
                context = await self._gather_analysis_context(incident)
                
                # Perform LLM-based analysis if available
                if self.openai_client:
                    analysis = await self._llm_root_cause_analysis(incident, context)
                else:
                    analysis = await self._pattern_based_analysis(incident, context)
                
                logger.info(f"✅ Analysis completed for incident {incident_id}: {analysis.root_cause}")
                return analysis
                
        except Exception as e:
            logger.error(f"Error analyzing incident {incident_id}: {e}")
            return None
    
    async def _gather_analysis_context(self, incident: Incident) -> Dict[str, Any]:
        """Gather contextual information for analysis"""
        try:
            context = {
                "incident": {
                    "title": incident.title,
                    "description": incident.description,
                    "failure_type": incident.failure_type,
                    "error_message": incident.error_message,
                    "severity": incident.severity,
                    "source_type": incident.source_type,
                    "repository": incident.repository,
                    "branch": incident.branch,
                    "commit_sha": incident.commit_sha
                },
                "logs": [],
                "recent_changes": [],
                "similar_incidents": []
            }
            
            # Get related logs
            if incident.source_id:
                context["logs"] = await self._get_related_logs(incident.source_id)
            
            # Get recent commits/changes
            if incident.repository and incident.commit_sha:
                context["recent_changes"] = await self._get_recent_changes(
                    incident.repository, incident.commit_sha
                )
            
            # Find similar historical incidents
            context["similar_incidents"] = await self._find_similar_incidents(incident)
            
            return context
            
        except Exception as e:
            logger.error(f"Error gathering analysis context: {e}")
            return {}
    
    async def _get_related_logs(self, source_id: str) -> List[Dict]:
        """Get logs related to the incident"""
        try:
            async with get_db_session() as session:
                from sqlalchemy import and_
                
                # Get logs from the same source around the incident time
                logs = await session.execute(
                    session.query(LogEntry).filter(
                        and_(
                            LogEntry.source_id == source_id,
                            LogEntry.level.in_(["ERROR", "WARN", "FATAL"])
                        )
                    ).order_by(LogEntry.timestamp.desc()).limit(50)
                )
                
                return [
                    {
                        "timestamp": log.timestamp.isoformat(),
                        "level": log.level,
                        "message": log.message,
                        "service": log.service,
                        "component": log.component
                    }
                    for log in logs
                ]
                
        except Exception as e:
            logger.error(f"Error getting related logs: {e}")
            return []
    
    async def _get_recent_changes(self, repository: str, commit_sha: str) -> List[Dict]:
        """Get recent changes from version control"""
        try:
            # In production, integrate with GitHub/GitLab API
            # For now, return mock data
            return [
                {
                    "commit": commit_sha[:8],
                    "message": "Recent commit message",
                    "author": "developer@example.com",
                    "files_changed": ["src/main.py", "requirements.txt"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent changes: {e}")
            return []
    
    async def _find_similar_incidents(self, incident: Incident) -> List[Dict]:
        """Find similar historical incidents"""
        try:
            async with get_db_session() as session:
                from sqlalchemy import and_
                
                # Find incidents with same failure type and repository
                similar = await session.execute(
                    session.query(Incident).filter(
                        and_(
                            Incident.failure_type == incident.failure_type,
                            Incident.repository == incident.repository,
                            Incident.id != incident.id,
                            Incident.status == "resolved"
                        )
                    ).order_by(Incident.detected_at.desc()).limit(5)
                )
                
                return [
                    {
                        "id": str(inc.id),
                        "title": inc.title,
                        "root_cause": inc.root_cause,
                        "resolution": "Resolved successfully",
                        "detected_at": inc.detected_at.isoformat()
                    }
                    for inc in similar
                ]
                
        except Exception as e:
            logger.error(f"Error finding similar incidents: {e}")
            return []
    
    async def _llm_root_cause_analysis(self, incident: Incident, context: Dict) -> RootCauseAnalysis:
        """Perform LLM-based root cause analysis"""
        try:
            # Construct prompt for LLM
            prompt = self._build_analysis_prompt(incident, context)
            
            # Call OpenAI API
            response = await self._call_openai_api(prompt)
            
            # Parse response
            analysis_result = self._parse_llm_response(response)
            
            return RootCauseAnalysis(
                root_cause=analysis_result.get("root_cause", "Unknown"),
                confidence=analysis_result.get("confidence", 0.7),
                explanation=analysis_result.get("explanation", ""),
                suggested_fixes=analysis_result.get("suggested_fixes", []),
                analysis_data={
                    "method": "llm_analysis",
                    "model": settings.OPENAI_MODEL,
                    "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response.get("usage", {}).get("completion_tokens", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            # Fallback to pattern-based analysis
            return await self._pattern_based_analysis(incident, context)
    
    def _build_analysis_prompt(self, incident: Incident, context: Dict) -> str:
        """Build prompt for LLM analysis"""
        prompt = f"""
You are an expert DevOps engineer analyzing a CI/CD failure. Provide a detailed root cause analysis.

INCIDENT DETAILS:
- Title: {incident.title}
- Type: {incident.failure_type}
- Error: {incident.error_message}
- Repository: {incident.repository}
- Branch: {incident.branch}

CONTEXT:
- Recent logs: {json.dumps(context.get('logs', [])[:5], indent=2)}
- Recent changes: {json.dumps(context.get('recent_changes', []), indent=2)}
- Similar incidents: {json.dumps(context.get('similar_incidents', []), indent=2)}

Please analyze this failure and provide:
1. Root cause (be specific)
2. Confidence level (0.0-1.0)
3. Detailed explanation
4. 3-5 specific suggested fixes
5. Prevention strategies

Format your response as JSON:
{{
    "root_cause": "specific root cause",
    "confidence": 0.85,
    "explanation": "detailed explanation of why this failure occurred",
    "suggested_fixes": [
        "specific fix 1",
        "specific fix 2",
        "specific fix 3"
    ],
    "prevention": [
        "prevention strategy 1",
        "prevention strategy 2"
    ]
}}
"""
        return prompt
    
    async def _call_openai_api(self, prompt: str) -> Dict:
        """Call OpenAI API for analysis"""
        try:
            response = await self.openai_client.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert DevOps engineer specializing in CI/CD failure analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_llm_response(self, response: Dict) -> Dict:
        """Parse LLM response"""
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Try to parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "root_cause": "Analysis completed",
                    "confidence": 0.7,
                    "explanation": content,
                    "suggested_fixes": ["Review the analysis above"]
                }
                
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {
                "root_cause": "Analysis failed",
                "confidence": 0.5,
                "explanation": "Failed to parse analysis response",
                "suggested_fixes": ["Manual investigation required"]
            }
    
    async def _pattern_based_analysis(self, incident: Incident, context: Dict) -> RootCauseAnalysis:
        """Fallback pattern-based analysis"""
        try:
            failure_type = incident.failure_type
            knowledge = self.knowledge_base.get(failure_type, {})
            
            # Analyze error message for specific patterns
            error_message = incident.error_message or ""
            root_cause = self._analyze_error_patterns(error_message, failure_type)
            
            # Generate suggested fixes based on failure type
            suggested_fixes = self._generate_pattern_fixes(failure_type, error_message)
            
            return RootCauseAnalysis(
                root_cause=root_cause,
                confidence=0.6,
                explanation=f"Pattern-based analysis identified {root_cause} as the likely cause",
                suggested_fixes=suggested_fixes,
                analysis_data={
                    "method": "pattern_analysis",
                    "knowledge_base_used": failure_type in self.knowledge_base
                }
            )
            
        except Exception as e:
            logger.error(f"Error in pattern-based analysis: {e}")
            return RootCauseAnalysis(
                root_cause="Unknown failure",
                confidence=0.3,
                explanation="Unable to determine root cause",
                suggested_fixes=["Manual investigation required"],
                analysis_data={"method": "fallback"}
            )
    
    def _analyze_error_patterns(self, error_message: str, failure_type: str) -> str:
        """Analyze error message patterns"""
        error_lower = error_message.lower()
        
        # Common error patterns
        if "not found" in error_lower or "missing" in error_lower:
            return "Missing dependency or resource"
        elif "permission denied" in error_lower or "access denied" in error_lower:
            return "Permission or access rights issue"
        elif "timeout" in error_lower or "timed out" in error_lower:
            return "Network or service timeout"
        elif "out of memory" in error_lower or "oom" in error_lower:
            return "Memory resource exhaustion"
        elif "syntax error" in error_lower or "parse error" in error_lower:
            return "Configuration or code syntax error"
        elif "connection refused" in error_lower or "connection failed" in error_lower:
            return "Network connectivity issue"
        else:
            return f"Generic {failure_type.replace('_', ' ')} issue"
    
    def _generate_pattern_fixes(self, failure_type: str, error_message: str) -> List[str]:
        """Generate suggested fixes based on patterns"""
        fixes = []
        error_lower = error_message.lower()
        
        if failure_type == "build_failure":
            fixes = [
                "Check and update dependencies in package.json/requirements.txt",
                "Verify build tool configuration",
                "Clear build cache and retry",
                "Check for syntax errors in source code"
            ]
        elif failure_type == "test_failure":
            fixes = [
                "Review failing test assertions",
                "Check test data setup and mocks",
                "Verify test environment configuration",
                "Update test dependencies"
            ]
        elif failure_type == "deployment_failure":
            fixes = [
                "Check resource limits and quotas",
                "Verify deployment configuration",
                "Check network connectivity and DNS",
                "Validate credentials and permissions"
            ]
        elif failure_type == "dependency_error":
            fixes = [
                "Update package registry configuration",
                "Check package version compatibility",
                "Clear dependency cache",
                "Verify network access to package registry"
            ]
        else:
            fixes = [
                "Review error logs for specific details",
                "Check system resources and configuration",
                "Verify network connectivity",
                "Consult documentation for the failing component"
            ]
        
        # Add specific fixes based on error message
        if "not found" in error_lower:
            fixes.insert(0, "Install or configure the missing component")
        elif "permission" in error_lower:
            fixes.insert(0, "Fix file permissions or access rights")
        elif "timeout" in error_lower:
            fixes.insert(0, "Increase timeout values or check network connectivity")
        
        return fixes[:5]  # Return top 5 fixes
    
    async def _update_incident_with_analysis(self, incident_id: str, analysis: RootCauseAnalysis):
        """Update incident with root cause analysis results"""
        try:
            async with get_db_session() as session:
                incident = await session.get(Incident, incident_id)
                if incident:
                    incident.root_cause = analysis.root_cause
                    incident.confidence_score = analysis.confidence
                    incident.status = "analyzing"
                    incident.analysis_data = {
                        **(incident.analysis_data or {}),
                        "root_cause_analysis": {
                            "explanation": analysis.explanation,
                            "suggested_fixes": analysis.suggested_fixes,
                            "analysis_method": analysis.analysis_data.get("method"),
                            "analyzed_at": datetime.utcnow().isoformat()
                        }
                    }
                    
                    await session.commit()
                    logger.info(f"✅ Updated incident {incident_id} with analysis")
                    
        except Exception as e:
            logger.error(f"Error updating incident with analysis: {e}")
    
    async def _queue_for_fix_generation(self, incident_id: str, analysis: RootCauseAnalysis):
        """Queue incident for fix generation"""
        try:
            fix_data = {
                "incident_id": incident_id,
                "root_cause": analysis.root_cause,
                "suggested_fixes": analysis.suggested_fixes,
                "confidence": analysis.confidence,
                "queued_at": datetime.utcnow().isoformat()
            }
            
            await redis_client.rpush("fix_queue", json.dumps(fix_data))
            logger.info(f"📤 Queued incident {incident_id} for fix generation")
            
        except Exception as e:
            logger.error(f"Error queuing for fix generation: {e}")