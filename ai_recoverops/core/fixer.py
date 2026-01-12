"""
Base fixer interface for automated issue resolution
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .engine import Issue

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
        """Apply fix for the issue. Returns True if successful"""
        pass
        
    @abstractmethod
    async def rollback_fix(self, issue: Issue) -> bool:
        """Rollback a previously applied fix"""
        pass
        
    @abstractmethod
    def get_fixer_type(self) -> str:
        """Return the type of fixer"""
        pass