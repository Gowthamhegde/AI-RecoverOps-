"""
Base analyzer interface for root cause analysis
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .engine import Issue, Analysis

class BaseAnalyzer(ABC):
    """Base class for all root cause analyzers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    @abstractmethod
    def can_analyze(self, issue: Issue) -> bool:
        """Check if this analyzer can handle the given issue type"""
        pass
        
    @abstractmethod
    async def analyze(self, issue: Issue) -> Analysis:
        """Analyze issue and return root cause analysis"""
        pass
        
    @abstractmethod
    def get_analyzer_type(self) -> str:
        """Return the type of analyzer"""
        pass