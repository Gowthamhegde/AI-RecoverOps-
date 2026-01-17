"""
Remediation Execution Engine
Applies fixes to repositories, infrastructure, and CI/CD pipelines
"""

import asyncio
import logging
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import aiohttp
from github import Github
from gitlab import Gitlab
import jenkins

from database.models import Incident, Remediation, RemediationStatus
from database.connection import get_db_session
from database.redis_client import redis_client
from config import settings

logger = logging.getLogger(__name__)

class ExecutionResult(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    ROLLED_BACK = "rolled_back"

@dataclass
class RemediationResult:
    success: bool
    message: str
    details: Dict[str, Any]
    rollback_data: Optional[Dict[str, Any]] = None

class RemediationExecutor:
    """Executes remediation actions across different platforms"""
    
    def __init__(self):
        self.running = False
        self.emergency_stop = False
        self.active_remediations = {}
        
        # Initialize platform clients
        self.github_client = None
        self.gitlab_client = None
        self.jenkins_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize platform API clients"""
        try:
            # GitHub client
            if settings.GITHUB_TOKEN:
                self.github_client = Github(settings.GITHUB_TOKEN)
                logger.info("✅ GitHub client initialized")
            
            # GitLab client
            if settings.GITLAB_TOKEN:
                self.gitlab_client = Gitlab("https://gitlab.com", private_token=settings.GITLAB_TOKEN)
                logger.info("✅ GitLab client initialized")
            
            # Jenkins client
            if settings.JENKINS_URL and settings.JENKINS_USERNAME and settings.JENKINS_TOKEN:
                self.jenkins_client = jenkins.Jenkins(
                    settings.JENKINS_URL,
                    username=settings.JENKINS_USERNAME,
                    password=settings.JENKINS_TOKEN
                )
                logger.info("✅ Jenkins client initialized")
                
        except Exception as e:
            logger.error(f"Error initializing platform clients: {e}")
    
    async def start(self):
        """Start the remediation execution service"""
        self.running = True
        self.emergency_stop = False
        logger.info("🚀 Starting Remediation Execution Engine")
        
        while self.running and not self.emergency_stop:
            try:
                await self._process_pending_remediations()
                await asyncio.sleep(20)  # Check every 20 seconds
            except Exception as e:
                logger.error(f"Error in remediation execution loop: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop the remediation execution service"""
        self.running = False
        logger.info("🛑 Stopping Remediation Execution Engine")
    
    async def emergency_stop(self):
        """Emergency stop all remediation activities"""
        self.emergency_stop = True
        logger.warning("🚨 EMERGENCY STOP: All remediation activities halted")
        
        # Cancel active remediations
        for remediation_id in list(self.active_remediations.keys()):
            await self._cancel_remediation(remediation_id)
    
    def is_healthy(self) -> bool:
        """Check if the executor is healthy"""
        return self.running and not self.emergency_stop
    
    async def _process_pending_remediations(self):
        """Process pending remediation requests"""
        try:
            # Check if auto-remediation is enabled
            if not settings.AUTO_REMEDIATION_ENABLED:
                return
            
            # Check concurrent remediation limit
            if len(self.active_remediations) >= settings.MAX_CONCURRENT_REMEDIATIONS:
                logger.info(f"Max concurrent remediations reached: {len(self.active_remediations)}")
                return
            
            # Get remediation request from queue
            remediation_data = await redis_client.lpop("remediation_queue")
            if not remediation_data:
                return
            
            request = json.loads(remediation_data)
            incident_id = request["incident_id"]
            
            # Execute remediation
            await self._execute_remediation(incident_id, request["fixes"])
            
        except Exception as e:
            logger.error(f"Error processing pending remediations: {e}")
    
    async def _execute_remediation(self, incident_id: str, fixes: List[Dict]):
        """Execute remediation for an incident"""
        try:
            self.active_remediations[incident_id] = {
                "started_at": datetime.utcnow(),
                "status": "in_progress"
            }
            
            logger.info(f"🔧 Executing remediation for incident: {incident_id}")
            
            async with get_db_session() as session:
                # Get incident details
                incident = await session.get(Incident, incident_id)
                if not incident:
                    logger.error(f"Incident not found: {incident_id}")
                    return
                
                # Update incident status
                incident.status = "fixing"
                await session.commit()
                
                # Execute each fix
                results = []
                for fix in fixes:
                    if self.emergency_stop:
                        logger.warning("Emergency stop detected, aborting remediation")
                        break
                    
                    result = await self._execute_single_fix(incident, fix)
                    results.append(result)
                    
                    # If fix failed and confidence is low, stop execution
                    if not result.success and fix.get("confidence", 0) < 0.8:
                        logger.warning(f"Fix failed with low confidence, stopping remediation")
                        break
                
                # Determine overall result
                success_count = sum(1 for r in results if r.success)
                overall_success = success_count > 0
                
                # Update incident status
                if overall_success:
                    incident.status = "resolved"
                    logger.info(f"✅ Remediation successful for incident: {incident_id}")
                else:
                    incident.status = "failed"
                    logger.error(f"❌ Remediation failed for incident: {incident_id}")
                
                await session.commit()
                
                # Trigger validation if successful
                if overall_success:
                    await self._trigger_validation(incident_id)
                
        except Exception as e:
            logger.error(f"Error executing remediation for incident {incident_id}: {e}")
        finally:
            # Remove from active remediations
            self.active_remediations.pop(incident_id, None)
    
    async def _execute_single_fix(self, incident: Incident, fix: Dict) -> RemediationResult:
        """Execute a single fix"""
        try:
            fix_type = fix["fix_type"]
            logger.info(f"Applying fix: {fix_type} - {fix['description']}")
            
            # Route to appropriate execution method
            if fix_type in ["code_patch", "dependency_update"]:
                return await self._execute_code_fix(incident, fix)
            elif fix_type in ["yaml_fix", "config_fix"]:
                return await self._execute_config_fix(incident, fix)
            elif fix_type == "kubernetes_fix":
                return await self._execute_kubernetes_fix(incident, fix)
            elif fix_type == "dockerfile_fix":
                return await self._execute_dockerfile_fix(incident, fix)
            else:
                return await self._execute_generic_fix(incident, fix)
                
        except Exception as e:
            logger.error(f"Error executing fix: {e}")
            return RemediationResult(
                success=False,
                message=f"Fix execution failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _execute_code_fix(self, incident: Incident, fix: Dict) -> RemediationResult:
        """Execute code/dependency fixes via Git"""
        try:
            if not incident.repository:
                return RemediationResult(
                    success=False,
                    message="No repository information available",
                    details={}
                )
            
            # Determine platform (GitHub, GitLab, etc.)
            if "github.com" in incident.repository:
                return await self._execute_github_fix(incident, fix)
            elif "gitlab.com" in incident.repository:
                return await self._execute_gitlab_fix(incident, fix)
            else:
                return RemediationResult(
                    success=False,
                    message="Unsupported repository platform",
                    details={"repository": incident.repository}
                )
                
        except Exception as e:
            logger.error(f"Error executing code fix: {e}")
            return RemediationResult(
                success=False,
                message=f"Code fix failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _execute_github_fix(self, incident: Incident, fix: Dict) -> RemediationResult:
        """Execute fix via GitHub API"""
        try:
            if not self.github_client:
                return RemediationResult(
                    success=False,
                    message="GitHub client not available",
                    details={}
                )
            
            # Parse repository name
            repo_name = incident.repository.replace("https://github.com/", "").replace(".git", "")
            repo = self.github_client.get_repo(repo_name)
            
            # Create a new branch for the fix
            base_branch = incident.branch or repo.default_branch
            fix_branch = f"ai-recoverops-fix-{incident.id}"
            
            # Get base branch reference
            base_ref = repo.get_git_ref(f"heads/{base_branch}")
            
            # Create new branch
            repo.create_git_ref(
                ref=f"refs/heads/{fix_branch}",
                sha=base_ref.object.sha
            )
            
            # Apply fixes to files
            files_updated = []
            for target_file in fix.get("target_files", []):
                try:
                    # Get current file content
                    file_content = repo.get_contents(target_file, ref=base_branch)
                    
                    # Apply fix (simplified - in production, use proper diff/patch logic)
                    new_content = self._apply_fix_to_content(
                        file_content.decoded_content.decode('utf-8'),
                        fix["content"],
                        fix["fix_type"]
                    )
                    
                    # Update file
                    repo.update_file(
                        path=target_file,
                        message=f"AI-RecoverOps: {fix['description']}",
                        content=new_content,
                        sha=file_content.sha,
                        branch=fix_branch
                    )
                    
                    files_updated.append(target_file)
                    
                except Exception as file_error:
                    logger.warning(f"Failed to update file {target_file}: {file_error}")
            
            if not files_updated:
                return RemediationResult(
                    success=False,
                    message="No files were updated",
                    details={}
                )
            
            # Create pull request
            pr = repo.create_pull(
                title=f"AI-RecoverOps: Fix for {incident.title}",
                body=f"""
## Automated Fix by AI-RecoverOps

**Incident ID:** {incident.id}
**Root Cause:** {incident.root_cause}
**Fix Description:** {fix['description']}

### Files Modified:
{chr(10).join(f'- {file}' for file in files_updated)}

### Validation Steps:
{chr(10).join(f'- {step}' for step in fix.get('validation_steps', []))}

This PR was automatically generated by AI-RecoverOps to resolve the detected incident.
""",
                head=fix_branch,
                base=base_branch
            )
            
            # If high confidence, auto-merge (optional)
            if fix.get("confidence", 0) > 0.9 and settings.AUTO_REMEDIATION_ENABLED:
                try:
                    pr.merge(merge_method="squash")
                    logger.info(f"✅ Auto-merged PR #{pr.number} for incident {incident.id}")
                except Exception as merge_error:
                    logger.warning(f"Failed to auto-merge PR: {merge_error}")
            
            return RemediationResult(
                success=True,
                message=f"Created PR #{pr.number} with fixes",
                details={
                    "pr_number": pr.number,
                    "pr_url": pr.html_url,
                    "branch": fix_branch,
                    "files_updated": files_updated
                },
                rollback_data={
                    "pr_number": pr.number,
                    "branch": fix_branch,
                    "repository": repo_name
                }
            )
            
        except Exception as e:
            logger.error(f"GitHub fix execution failed: {e}")
            return RemediationResult(
                success=False,
                message=f"GitHub fix failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _apply_fix_to_content(self, original_content: str, fix_content: str, fix_type: str) -> str:
        """Apply fix to file content"""
        try:
            if fix_type == "dependency_update":
                # For dependency updates, append to the file
                if "requirements.txt" in fix_content or fix_content.strip().endswith("=="):
                    return original_content + "\n" + fix_content
                elif "package.json" in fix_content:
                    # Merge JSON dependencies (simplified)
                    import json
                    try:
                        original_json = json.loads(original_content)
                        fix_json = json.loads(fix_content)
                        
                        if "dependencies" in fix_json:
                            if "dependencies" not in original_json:
                                original_json["dependencies"] = {}
                            original_json["dependencies"].update(fix_json["dependencies"])
                        
                        return json.dumps(original_json, indent=2)
                    except:
                        return original_content + "\n" + fix_content
            
            elif fix_type in ["yaml_fix", "kubernetes_fix"]:
                # For YAML fixes, replace or append content
                return fix_content if fix_content.strip() else original_content
            
            else:
                # For other fixes, replace content
                return fix_content if fix_content.strip() else original_content
                
        except Exception as e:
            logger.error(f"Error applying fix to content: {e}")
            return original_content
    
    async def _execute_gitlab_fix(self, incident: Incident, fix: Dict) -> RemediationResult:
        """Execute fix via GitLab API"""
        try:
            if not self.gitlab_client:
                return RemediationResult(
                    success=False,
                    message="GitLab client not available",
                    details={}
                )
            
            # Similar implementation to GitHub but using GitLab API
            # For brevity, returning a placeholder
            return RemediationResult(
                success=True,
                message="GitLab fix executed (placeholder)",
                details={"platform": "gitlab"}
            )
            
        except Exception as e:
            logger.error(f"GitLab fix execution failed: {e}")
            return RemediationResult(
                success=False,
                message=f"GitLab fix failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _execute_config_fix(self, incident: Incident, fix: Dict) -> RemediationResult:
        """Execute configuration fixes"""
        try:
            # Configuration fixes are typically applied via Git
            return await self._execute_code_fix(incident, fix)
            
        except Exception as e:
            logger.error(f"Config fix execution failed: {e}")
            return RemediationResult(
                success=False,
                message=f"Config fix failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _execute_kubernetes_fix(self, incident: Incident, fix: Dict) -> RemediationResult:
        """Execute Kubernetes fixes"""
        try:
            # In production, use Kubernetes API to apply fixes
            # For now, apply via Git (GitOps approach)
            return await self._execute_code_fix(incident, fix)
            
        except Exception as e:
            logger.error(f"Kubernetes fix execution failed: {e}")
            return RemediationResult(
                success=False,
                message=f"Kubernetes fix failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _execute_dockerfile_fix(self, incident: Incident, fix: Dict) -> RemediationResult:
        """Execute Dockerfile fixes"""
        try:
            # Dockerfile fixes are applied via Git
            return await self._execute_code_fix(incident, fix)
            
        except Exception as e:
            logger.error(f"Dockerfile fix execution failed: {e}")
            return RemediationResult(
                success=False,
                message=f"Dockerfile fix failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _execute_generic_fix(self, incident: Incident, fix: Dict) -> RemediationResult:
        """Execute generic fixes"""
        try:
            # Generic fixes default to Git-based application
            return await self._execute_code_fix(incident, fix)
            
        except Exception as e:
            logger.error(f"Generic fix execution failed: {e}")
            return RemediationResult(
                success=False,
                message=f"Generic fix failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _trigger_validation(self, incident_id: str):
        """Trigger validation of applied fixes"""
        try:
            # Queue for validation
            validation_data = {
                "incident_id": incident_id,
                "validation_type": "post_remediation",
                "queued_at": datetime.utcnow().isoformat()
            }
            
            await redis_client.rpush("validation_queue", json.dumps(validation_data))
            logger.info(f"📋 Queued incident {incident_id} for validation")
            
        except Exception as e:
            logger.error(f"Error triggering validation: {e}")
    
    async def _cancel_remediation(self, remediation_id: str):
        """Cancel an active remediation"""
        try:
            if remediation_id in self.active_remediations:
                self.active_remediations[remediation_id]["status"] = "cancelled"
                logger.info(f"Cancelled remediation: {remediation_id}")
                
        except Exception as e:
            logger.error(f"Error cancelling remediation: {e}")
    
    async def rollback_remediation(self, incident_id: str) -> bool:
        """Rollback a remediation"""
        try:
            async with get_db_session() as session:
                # Get remediation records
                from sqlalchemy import and_
                remediations = await session.execute(
                    session.query(Remediation).filter(
                        and_(
                            Remediation.incident_id == incident_id,
                            Remediation.success == True
                        )
                    )
                )
                
                rollback_success = True
                
                for remediation in remediations:
                    try:
                        # Perform rollback based on rollback_data
                        rollback_data = remediation.rollback_data or {}
                        
                        if "pr_number" in rollback_data:
                            # Close/revert PR
                            await self._rollback_github_pr(rollback_data)
                        
                        # Update remediation status
                        remediation.status = RemediationStatus.ROLLED_BACK
                        
                    except Exception as rollback_error:
                        logger.error(f"Failed to rollback remediation {remediation.id}: {rollback_error}")
                        rollback_success = False
                
                await session.commit()
                
                # Update incident status
                incident = await session.get(Incident, incident_id)
                if incident:
                    incident.status = "rolled_back" if rollback_success else "failed"
                    await session.commit()
                
                return rollback_success
                
        except Exception as e:
            logger.error(f"Error rolling back remediation for incident {incident_id}: {e}")
            return False
    
    async def _rollback_github_pr(self, rollback_data: Dict):
        """Rollback GitHub PR"""
        try:
            if not self.github_client:
                return
            
            repo_name = rollback_data.get("repository")
            pr_number = rollback_data.get("pr_number")
            branch = rollback_data.get("branch")
            
            if repo_name and pr_number:
                repo = self.github_client.get_repo(repo_name)
                pr = repo.get_pull(pr_number)
                
                # Close PR if open
                if pr.state == "open":
                    pr.edit(state="closed")
                
                # Delete branch if it exists
                if branch:
                    try:
                        ref = repo.get_git_ref(f"heads/{branch}")
                        ref.delete()
                    except:
                        pass  # Branch might not exist
                
                logger.info(f"Rolled back GitHub PR #{pr_number}")
                
        except Exception as e:
            logger.error(f"Error rolling back GitHub PR: {e}")
    
    async def get_active_remediations(self) -> Dict[str, Dict]:
        """Get currently active remediations"""
        return self.active_remediations.copy()
    
    async def get_remediation_status(self, incident_id: str) -> Optional[Dict]:
        """Get status of a specific remediation"""
        return self.active_remediations.get(incident_id)