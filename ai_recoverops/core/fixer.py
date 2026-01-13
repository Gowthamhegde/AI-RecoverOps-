"""
Base fixer interface for automated remediation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .models import Issue

class BaseFixer(ABC):
    """Base class for all automated fixers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    @abstractmethod
    async def can_fix(self, issue: Issue) -> bool:
        """Check if this fixer can handle the given issue"""
        pass
        
    @abstractmethod
    async def apply_fix(self, issue: Issue) -> bool:
        """Apply the fix and return success status"""
        pass
        
    @abstractmethod
    def get_fixer_type(self) -> str:
        """Return the type of fixer"""
        pass