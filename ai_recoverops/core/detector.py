"""
Base detector interface and common detection utilities
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .models import Issue

class BaseDetector(ABC):
    """Base class for all issue detectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    @abstractmethod
    async def initialize(self):
        """Initialize the detector"""
        pass
        
    @abstractmethod
    async def detect(self) -> List[Issue]:
        """Detect issues and return list of Issue objects"""
        pass
        
    @abstractmethod
    def get_detector_type(self) -> str:
        """Return the type of detector"""
        pass