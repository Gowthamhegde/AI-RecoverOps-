"""
Container-related automated fixes
"""

import asyncio
from typing import Dict, Any
from ..core.fixer import BaseFixer
from ..core.models import Issue
from ..utils.logger import get_logger

class ContainerFixer(BaseFixer):
    """Handles container-related fixes"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
    async def can_fix(self, issue: Issue) -> bool:
        """Check if this fixer can handle the issue"""
        return 'container' in issue.description.lower() or issue.metadata.get('container_id')
        
    async def apply_fix(self, issue: Issue) -> bool:
        """Apply container-related fix"""
        if not hasattr(issue, 'analysis'):
            return False
            
        recommended_fixes = issue.analysis.recommended_fixes
        
        for fix in recommended_fixes:
            if fix == 'scale_horizontally':
                return await self._scale_horizontally(issue)
            elif fix == 'increase_memory_limit':
                return await self._increase_memory_limit(issue)
            elif fix == 'restart_container':
                return await self._restart_container(issue)
                
        return False
        
    async def _scale_horizontally(self, issue: Issue) -> bool:
        """Scale containers horizontally"""
        try:
            current_replicas = issue.metadata.get('replicas', 1)
            new_replicas = min(current_replicas + 1, 10)  # Max 10 replicas
            
            self.logger.info(f"Scaling from {current_replicas} to {new_replicas} replicas")
            
            if not self.config.get('fixes', {}).get('auto_apply', False):
                self.logger.info(f"DRY RUN: Would scale to {new_replicas} replicas")
                return True
            
            # Simulate scaling
            await asyncio.sleep(3)
            self.logger.info(f"Successfully scaled to {new_replicas} replicas")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to scale horizontally: {e}")
            return False
            
    async def _increase_memory_limit(self, issue: Issue) -> bool:
        """Increase container memory limit"""
        try:
            current_memory = issue.metadata.get('memory_limit', '512Mi')
            
            # Parse and increase memory
            if 'Mi' in current_memory:
                memory_mb = int(current_memory.replace('Mi', ''))
                new_memory_mb = min(memory_mb * 2, 4096)  # Max 4GB
                new_memory = f"{new_memory_mb}Mi"
            else:
                new_memory = "1Gi"
            
            self.logger.info(f"Increasing memory limit from {current_memory} to {new_memory}")
            
            if not self.config.get('fixes', {}).get('auto_apply', False):
                self.logger.info(f"DRY RUN: Would increase memory to {new_memory}")
                return True
            
            # Simulate memory increase
            await asyncio.sleep(2)
            self.logger.info(f"Memory limit increased to {new_memory}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to increase memory limit: {e}")
            return False
            
    async def _restart_container(self, issue: Issue) -> bool:
        """Restart container"""
        try:
            container_id = issue.metadata.get('container_id', 'unknown')
            self.logger.info(f"Restarting container: {container_id}")
            
            if not self.config.get('fixes', {}).get('auto_apply', False):
                self.logger.info(f"DRY RUN: Would restart container {container_id}")
                return True
            
            # Simulate container restart
            await asyncio.sleep(2)
            self.logger.info(f"Container {container_id} restarted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart container: {e}")
            return False
            
    def get_fixer_type(self) -> str:
        return "container"