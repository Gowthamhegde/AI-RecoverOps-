"""
Core data models for AI-RecoverOps
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any

@dataclass
class Issue:
    id: str
    type: str
    severity: str
    description: str
    metadata: Dict[str, Any]
    detected_at: datetime
    source: str

@dataclass
class Analysis:
    issue_id: str
    root_cause: str
    confidence: float
    recommended_fixes: List[str]
    analysis_data: Dict[str, Any]