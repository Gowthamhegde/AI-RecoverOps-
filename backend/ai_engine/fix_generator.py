"""
AI-Powered Fix Generation Engine
Generates code patches, configuration fixes, and remediation scripts
"""

import asyncio
import logging
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import openai
from database.models import Incident, Remediation
from database.connection import get_db_session
from database.redis_client import redis_client
from config import settings

logger = logging.getLogger(__name__)

class FixType(str, Enum):
    CODE_PATCH = "code_patch"
    CONFIG_FIX = "config_fix"
    DEPENDENCY_UPDATE = "dependency_update"
    SCRIPT_FIX = "script_fix"
    YAML_FIX = "yaml_fix"
    DOCKERFILE_FIX = "dockerfile_fix"
    TERRAFORM_FIX = "terraform_fix"
    KUBERNETES_FIX = "kubernetes_fix"

@dataclass
class GeneratedFix:
    fix_type: FixType
    description: str
    content: str
    target_files: List[str]
    confidence: float
    validation_steps: List[str]
    rollback_data: Dict[str, Any]

class FixGenerator:
    """Advanced fix generation using LLM and template-based approaches"""
    
    def __init__(self):
        self.running = False
        self.openai_client = None
        self._initialize_openai()
        
        # Fix templates for common issues
        self.fix_templates = self._load_fix_templates()
        
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                logger.info("✅ OpenAI client initialized for fix generation")
            else:
                logger.warning("⚠️ OpenAI API key not provided, using template-based fixes")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
    
    def _load_fix_templates(self) -> Dict[str, Dict]:
        """Load fix templates for common issues"""
        return {
            "missing_dependency": {
                "python": {
                    "requirements.txt": "# Add missing dependency\n{package_name}=={version}\n",
                    "setup.py": "# Add to install_requires\n'{package_name}=={version}',\n"
                },
                "node": {
                    "package.json": {
                        "dependencies": {
                            "{package_name}": "{version}"
                        }
                    }
                },
                "docker": {
                    "Dockerfile": "RUN pip install {package_name}=={version}\n"
                }
            },
            "syntax_error": {
                "yaml": {
                    "common_fixes": [
                        "Fix indentation issues",
                        "Add missing quotes around strings",
                        "Fix list/dict syntax",
                        "Remove trailing commas"
                    ]
                },
                "json": {
                    "common_fixes": [
                        "Remove trailing commas",
                        "Add missing quotes around keys",
                        "Fix bracket/brace matching",
                        "Escape special characters"
                    ]
                }
            },
            "permission_error": {
                "dockerfile": {
                    "fix": "RUN chmod +x {file_path}\nUSER {user}\n"
                },
                "kubernetes": {
                    "securityContext": {
                        "runAsUser": 1000,
                        "runAsGroup": 1000,
                        "fsGroup": 1000
                    }
                }
            },
            "resource_limit": {
                "kubernetes": {
                    "resources": {
                        "limits": {
                            "memory": "{memory_limit}",
                            "cpu": "{cpu_limit}"
                        },
                        "requests": {
                            "memory": "{memory_request}",
                            "cpu": "{cpu_request}"
                        }
                    }
                }
            }
        }
    
    async def start(self):
        """Start the fix generation service"""
        self.running = True
        logger.info("🛠️ Starting Fix Generation Engine")
        
        while self.running:
            try:
                await self._process_pending_fixes()
                await asyncio.sleep(15)  # Check every 15 seconds
            except Exception as e:
                logger.error(f"Error in fix generation loop: {e}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Stop the fix generation service"""
        self.running = False
        logger.info("🛑 Stopping Fix Generation Engine")
    
    def is_healthy(self) -> bool:
        """Check if the fix generator is healthy"""
        return self.running
    
    async def _process_pending_fixes(self):
        """Process incidents pending fix generation"""
        try:
            # Get fix requests from Redis queue
            fix_data = await redis_client.lpop("fix_queue")
            if not fix_data:
                return
            
            fix_request = json.loads(fix_data)
            incident_id = fix_request["incident_id"]
            
            # Generate fixes for the incident
            fixes = await self.generate_fixes(incident_id)
            
            if fixes:
                await self._create_remediation_records(incident_id, fixes)
                await self._queue_for_remediation(incident_id, fixes)
                
        except Exception as e:
            logger.error(f"Error processing pending fixes: {e}")
    
    async def generate_fixes(self, incident_id: str) -> List[GeneratedFix]:
        """Generate fixes for an incident"""
        try:
            async with get_db_session() as session:
                # Get incident details
                incident = await session.get(Incident, incident_id)
                if not incident:
                    logger.error(f"Incident not found: {incident_id}")
                    return []
                
                logger.info(f"🔧 Generating fixes for incident: {incident.title}")
                
                # Determine fix approach based on failure type and available information
                if self.openai_client and incident.confidence_score > 0.7:
                    fixes = await self._llm_generate_fixes(incident)
                else:
                    fixes = await self._template_generate_fixes(incident)
                
                logger.info(f"✅ Generated {len(fixes)} fixes for incident {incident_id}")
                return fixes
                
        except Exception as e:
            logger.error(f"Error generating fixes for incident {incident_id}: {e}")
            return []
    
    async def _llm_generate_fixes(self, incident: Incident) -> List[GeneratedFix]:
        """Generate fixes using LLM"""
        try:
            # Build context for fix generation
            context = await self._build_fix_context(incident)
            
            # Generate different types of fixes
            fixes = []
            
            # Code/configuration fixes
            if incident.failure_type in ["build_failure", "syntax_error", "dependency_error"]:
                code_fix = await self._generate_code_fix(incident, context)
                if code_fix:
                    fixes.append(code_fix)
            
            # Infrastructure fixes
            if incident.failure_type in ["deployment_failure", "resource_error"]:
                infra_fix = await self._generate_infrastructure_fix(incident, context)
                if infra_fix:
                    fixes.append(infra_fix)
            
            # Configuration fixes
            config_fix = await self._generate_config_fix(incident, context)
            if config_fix:
                fixes.append(config_fix)
            
            return fixes
            
        except Exception as e:
            logger.error(f"Error in LLM fix generation: {e}")
            return await self._template_generate_fixes(incident)
    
    async def _build_fix_context(self, incident: Incident) -> Dict[str, Any]:
        """Build context for fix generation"""
        try:
            context = {
                "incident": {
                    "title": incident.title,
                    "failure_type": incident.failure_type,
                    "error_message": incident.error_message,
                    "root_cause": incident.root_cause,
                    "repository": incident.repository,
                    "branch": incident.branch,
                    "commit_sha": incident.commit_sha
                },
                "suggested_fixes": [],
                "file_contents": {},
                "repository_structure": []
            }
            
            # Extract suggested fixes from analysis
            if incident.analysis_data:
                rca_data = incident.analysis_data.get("root_cause_analysis", {})
                context["suggested_fixes"] = rca_data.get("suggested_fixes", [])
            
            # Get relevant file contents (in production, integrate with Git API)
            context["file_contents"] = await self._get_relevant_files(incident)
            
            return context
            
        except Exception as e:
            logger.error(f"Error building fix context: {e}")
            return {}
    
    async def _get_relevant_files(self, incident: Incident) -> Dict[str, str]:
        """Get relevant file contents for fix generation"""
        try:
            # In production, integrate with GitHub/GitLab API to get file contents
            # For now, return mock file contents based on failure type
            
            files = {}
            
            if incident.failure_type == "dependency_error":
                if "python" in incident.error_message.lower():
                    files["requirements.txt"] = "# Python dependencies\nrequests==2.28.0\nflask==2.0.1\n"
                elif "node" in incident.error_message.lower():
                    files["package.json"] = '{\n  "dependencies": {\n    "express": "^4.18.0"\n  }\n}'
            
            elif incident.failure_type == "deployment_failure":
                if "kubernetes" in incident.error_message.lower():
                    files["deployment.yaml"] = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
        resources:
          limits:
            memory: "128Mi"
            cpu: "100m"
"""
                elif "docker" in incident.error_message.lower():
                    files["Dockerfile"] = """FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
"""
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting relevant files: {e}")
            return {}
    
    async def _generate_code_fix(self, incident: Incident, context: Dict) -> Optional[GeneratedFix]:
        """Generate code/dependency fixes using LLM"""
        try:
            prompt = self._build_code_fix_prompt(incident, context)
            response = await self._call_openai_for_fix(prompt)
            
            fix_data = self._parse_fix_response(response)
            
            if fix_data:
                return GeneratedFix(
                    fix_type=FixType.CODE_PATCH,
                    description=fix_data.get("description", "Code fix"),
                    content=fix_data.get("content", ""),
                    target_files=fix_data.get("target_files", []),
                    confidence=fix_data.get("confidence", 0.7),
                    validation_steps=fix_data.get("validation_steps", []),
                    rollback_data={"original_content": context.get("file_contents", {})}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating code fix: {e}")
            return None
    
    def _build_code_fix_prompt(self, incident: Incident, context: Dict) -> str:
        """Build prompt for code fix generation"""
        prompt = f"""
You are an expert DevOps engineer. Generate a specific fix for this CI/CD failure.

INCIDENT:
- Type: {incident.failure_type}
- Error: {incident.error_message}
- Root Cause: {incident.root_cause}
- Repository: {incident.repository}

CONTEXT:
- Suggested fixes: {json.dumps(context.get('suggested_fixes', []))}
- File contents: {json.dumps(context.get('file_contents', {}), indent=2)}

Generate a specific fix that addresses the root cause. Provide:
1. Exact file changes (patches or complete file content)
2. List of files to modify
3. Validation steps to verify the fix
4. Confidence level (0.0-1.0)

Format as JSON:
{{
    "description": "Brief description of the fix",
    "content": "Exact file content or patch to apply",
    "target_files": ["file1.txt", "file2.py"],
    "validation_steps": ["step 1", "step 2"],
    "confidence": 0.85
}}
"""
        return prompt
    
    async def _generate_infrastructure_fix(self, incident: Incident, context: Dict) -> Optional[GeneratedFix]:
        """Generate infrastructure fixes (K8s, Docker, etc.)"""
        try:
            if "kubernetes" in incident.error_message.lower():
                return await self._generate_kubernetes_fix(incident, context)
            elif "docker" in incident.error_message.lower():
                return await self._generate_docker_fix(incident, context)
            else:
                return await self._generate_generic_infra_fix(incident, context)
                
        except Exception as e:
            logger.error(f"Error generating infrastructure fix: {e}")
            return None
    
    async def _generate_kubernetes_fix(self, incident: Incident, context: Dict) -> Optional[GeneratedFix]:
        """Generate Kubernetes-specific fixes"""
        try:
            error_message = incident.error_message.lower()
            
            # Resource limit issues
            if "memory" in error_message or "oom" in error_message:
                fix_content = """
# Increase memory limits
resources:
  limits:
    memory: "512Mi"
    cpu: "500m"
  requests:
    memory: "256Mi"
    cpu: "250m"
"""
                return GeneratedFix(
                    fix_type=FixType.KUBERNETES_FIX,
                    description="Increase memory limits to prevent OOM kills",
                    content=fix_content,
                    target_files=["deployment.yaml", "k8s/deployment.yaml"],
                    confidence=0.8,
                    validation_steps=[
                        "Apply the updated deployment",
                        "Check pod status",
                        "Monitor memory usage"
                    ],
                    rollback_data={"previous_limits": "128Mi"}
                )
            
            # Image pull issues
            elif "imagepullbackoff" in error_message or "image" in error_message:
                fix_content = """
# Fix image pull issues
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
      containers:
      - name: app
        image: myregistry.com/myapp:latest
        imagePullPolicy: Always
"""
                return GeneratedFix(
                    fix_type=FixType.KUBERNETES_FIX,
                    description="Fix image pull configuration",
                    content=fix_content,
                    target_files=["deployment.yaml"],
                    confidence=0.75,
                    validation_steps=[
                        "Verify image exists in registry",
                        "Check image pull secrets",
                        "Apply deployment"
                    ],
                    rollback_data={}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating Kubernetes fix: {e}")
            return None
    
    async def _generate_docker_fix(self, incident: Incident, context: Dict) -> Optional[GeneratedFix]:
        """Generate Docker-specific fixes"""
        try:
            error_message = incident.error_message.lower()
            
            if "permission denied" in error_message:
                fix_content = """
# Fix permission issues in Dockerfile
FROM python:3.9-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chown -R appuser:appuser /app

USER appuser
CMD ["python", "app.py"]
"""
                return GeneratedFix(
                    fix_type=FixType.DOCKERFILE_FIX,
                    description="Fix Docker permission issues",
                    content=fix_content,
                    target_files=["Dockerfile"],
                    confidence=0.8,
                    validation_steps=[
                        "Build Docker image",
                        "Run container",
                        "Verify permissions"
                    ],
                    rollback_data={}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating Docker fix: {e}")
            return None
    
    async def _generate_config_fix(self, incident: Incident, context: Dict) -> Optional[GeneratedFix]:
        """Generate configuration fixes"""
        try:
            if incident.failure_type == "syntax_error":
                return await self._generate_syntax_fix(incident, context)
            elif incident.failure_type == "dependency_error":
                return await self._generate_dependency_fix(incident, context)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error generating config fix: {e}")
            return None
    
    async def _generate_dependency_fix(self, incident: Incident, context: Dict) -> Optional[GeneratedFix]:
        """Generate dependency fixes"""
        try:
            error_message = incident.error_message
            
            # Extract package name from error message
            package_match = re.search(r"module '([^']+)' not found|package '([^']+)' not found", error_message, re.IGNORECASE)
            if package_match:
                package_name = package_match.group(1) or package_match.group(2)
                
                # Python dependency fix
                if "python" in error_message.lower() or ".py" in error_message:
                    fix_content = f"{package_name}==latest\n"
                    return GeneratedFix(
                        fix_type=FixType.DEPENDENCY_UPDATE,
                        description=f"Add missing Python package: {package_name}",
                        content=fix_content,
                        target_files=["requirements.txt"],
                        confidence=0.85,
                        validation_steps=[
                            f"pip install {package_name}",
                            "Run tests",
                            "Verify import works"
                        ],
                        rollback_data={"added_package": package_name}
                    )
                
                # Node.js dependency fix
                elif "node" in error_message.lower() or "npm" in error_message.lower():
                    fix_content = f'{{\n  "dependencies": {{\n    "{package_name}": "^latest"\n  }}\n}}'
                    return GeneratedFix(
                        fix_type=FixType.DEPENDENCY_UPDATE,
                        description=f"Add missing Node.js package: {package_name}",
                        content=fix_content,
                        target_files=["package.json"],
                        confidence=0.85,
                        validation_steps=[
                            f"npm install {package_name}",
                            "npm test",
                            "Verify require() works"
                        ],
                        rollback_data={"added_package": package_name}
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating dependency fix: {e}")
            return None
    
    async def _template_generate_fixes(self, incident: Incident) -> List[GeneratedFix]:
        """Generate fixes using templates (fallback method)"""
        try:
            fixes = []
            failure_type = incident.failure_type
            error_message = incident.error_message.lower()
            
            # Template-based fix generation
            if failure_type == "dependency_error":
                if "not found" in error_message:
                    fixes.append(GeneratedFix(
                        fix_type=FixType.DEPENDENCY_UPDATE,
                        description="Update dependencies to resolve missing packages",
                        content="# Add missing dependencies\n# Check requirements.txt or package.json",
                        target_files=["requirements.txt", "package.json"],
                        confidence=0.6,
                        validation_steps=[
                            "Install dependencies",
                            "Run build process",
                            "Verify functionality"
                        ],
                        rollback_data={}
                    ))
            
            elif failure_type == "syntax_error":
                fixes.append(GeneratedFix(
                    fix_type=FixType.CONFIG_FIX,
                    description="Fix configuration syntax errors",
                    content="# Review and fix syntax in configuration files",
                    target_files=["*.yaml", "*.yml", "*.json"],
                    confidence=0.7,
                    validation_steps=[
                        "Validate YAML/JSON syntax",
                        "Test configuration",
                        "Deploy changes"
                    ],
                    rollback_data={}
                ))
            
            elif failure_type == "permission_error":
                fixes.append(GeneratedFix(
                    fix_type=FixType.SCRIPT_FIX,
                    description="Fix permission issues",
                    content="# Fix file permissions\nchmod +x script.sh\n# Or update Dockerfile USER directive",
                    target_files=["Dockerfile", "scripts/*"],
                    confidence=0.75,
                    validation_steps=[
                        "Check file permissions",
                        "Test script execution",
                        "Verify container startup"
                    ],
                    rollback_data={}
                ))
            
            return fixes
            
        except Exception as e:
            logger.error(f"Error in template fix generation: {e}")
            return []
    
    async def _call_openai_for_fix(self, prompt: str) -> Dict:
        """Call OpenAI API for fix generation"""
        try:
            response = await self.openai_client.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert DevOps engineer who generates precise fixes for CI/CD failures."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            return response
            
        except Exception as e:
            logger.error(f"OpenAI API call for fix generation failed: {e}")
            raise
    
    def _parse_fix_response(self, response: Dict) -> Optional[Dict]:
        """Parse fix generation response"""
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Try to parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "description": "Generated fix",
                    "content": content,
                    "target_files": [],
                    "validation_steps": ["Apply fix", "Test changes"],
                    "confidence": 0.6
                }
                
        except Exception as e:
            logger.error(f"Error parsing fix response: {e}")
            return None
    
    async def _create_remediation_records(self, incident_id: str, fixes: List[GeneratedFix]):
        """Create remediation records in database"""
        try:
            async with get_db_session() as session:
                for fix in fixes:
                    remediation = Remediation(
                        incident_id=incident_id,
                        action_type=fix.fix_type,
                        description=fix.description,
                        fix_content=fix.content,
                        fix_type=fix.fix_type,
                        target_files=fix.target_files,
                        rollback_data=fix.rollback_data,
                        metadata={
                            "confidence": fix.confidence,
                            "validation_steps": fix.validation_steps,
                            "generated_at": datetime.utcnow().isoformat()
                        }
                    )
                    
                    session.add(remediation)
                
                await session.commit()
                logger.info(f"✅ Created {len(fixes)} remediation records for incident {incident_id}")
                
        except Exception as e:
            logger.error(f"Error creating remediation records: {e}")
    
    async def _queue_for_remediation(self, incident_id: str, fixes: List[GeneratedFix]):
        """Queue fixes for remediation execution"""
        try:
            remediation_data = {
                "incident_id": incident_id,
                "fixes": [
                    {
                        "fix_type": fix.fix_type,
                        "description": fix.description,
                        "content": fix.content,
                        "target_files": fix.target_files,
                        "confidence": fix.confidence
                    }
                    for fix in fixes
                ],
                "queued_at": datetime.utcnow().isoformat()
            }
            
            await redis_client.rpush("remediation_queue", json.dumps(remediation_data))
            logger.info(f"📤 Queued {len(fixes)} fixes for remediation: {incident_id}")
            
        except Exception as e:
            logger.error(f"Error queuing for remediation: {e}")
    
    async def _generate_generic_infra_fix(self, incident: Incident, context: Dict) -> Optional[GeneratedFix]:
        """Generate generic infrastructure fix"""
        try:
            # Generic infrastructure fix based on error patterns
            error_message = incident.error_message.lower()
            
            if "resource" in error_message and "limit" in error_message:
                return GeneratedFix(
                    fix_type=FixType.CONFIG_FIX,
                    description="Increase resource limits",
                    content="# Increase CPU/memory limits in configuration",
                    target_files=["deployment.yaml", "docker-compose.yml"],
                    confidence=0.6,
                    validation_steps=[
                        "Update resource limits",
                        "Redeploy application",
                        "Monitor resource usage"
                    ],
                    rollback_data={}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating generic infrastructure fix: {e}")
            return None
    
    async def _generate_syntax_fix(self, incident: Incident, context: Dict) -> Optional[GeneratedFix]:
        """Generate syntax error fixes"""
        try:
            error_message = incident.error_message.lower()
            
            if "yaml" in error_message or "yml" in error_message:
                return GeneratedFix(
                    fix_type=FixType.YAML_FIX,
                    description="Fix YAML syntax errors",
                    content="# Common YAML fixes:\n# - Fix indentation\n# - Add quotes around strings\n# - Remove trailing commas",
                    target_files=["*.yaml", "*.yml"],
                    confidence=0.7,
                    validation_steps=[
                        "Validate YAML syntax",
                        "Test configuration",
                        "Apply changes"
                    ],
                    rollback_data={}
                )
            
            elif "json" in error_message:
                return GeneratedFix(
                    fix_type=FixType.CONFIG_FIX,
                    description="Fix JSON syntax errors",
                    content="# Common JSON fixes:\n# - Remove trailing commas\n# - Add quotes around keys\n# - Fix bracket matching",
                    target_files=["*.json"],
                    confidence=0.7,
                    validation_steps=[
                        "Validate JSON syntax",
                        "Test configuration",
                        "Apply changes"
                    ],
                    rollback_data={}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating syntax fix: {e}")
            return None