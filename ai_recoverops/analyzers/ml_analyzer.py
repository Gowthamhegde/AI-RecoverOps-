"""
Machine Learning-based root cause analyzer
"""

import asyncio
import numpy as np
from typing import Dict, Any, List
from ..core.analyzer import BaseAnalyzer
from ..core.models import Issue, Analysis
from ..utils.logger import get_logger

class MLAnalyzer(BaseAnalyzer):
    """Analyzes issues using machine learning models"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # ML model confidence thresholds
        self.confidence_threshold = config.get('analysis', {}).get('confidence_threshold', 0.8)
        
    def can_analyze(self, issue: Issue) -> bool:
        """Check if this analyzer can handle the issue"""
        # ML analyzer can handle any type of issue
        return True
        
    async def analyze(self, issue: Issue) -> Analysis:
        """Analyze issue using ML models"""
        self.logger.info(f"ML analyzing issue: {issue.description}")
        
        # Extract features from issue
        features = self._extract_features(issue)
        
        # Predict root cause using ML model
        root_cause, confidence = await self._predict_root_cause(features, issue)
        
        # Get recommended fixes based on prediction
        recommended_fixes = self._get_ml_recommended_fixes(root_cause, issue)
        
        return Analysis(
            issue_id=issue.id,
            root_cause=root_cause,
            confidence=confidence,
            recommended_fixes=recommended_fixes,
            analysis_data={
                'features': features,
                'model_type': 'ensemble',
                'analysis_method': 'machine_learning'
            }
        )
        
    def _extract_features(self, issue: Issue) -> Dict[str, Any]:
        """Extract features from issue for ML model"""
        features = {
            'severity_score': {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}.get(issue.severity, 2),
            'issue_type_encoded': {'system': 0, 'application': 1, 'network': 2, 'database': 3}.get(issue.type, 0),
            'description_length': len(issue.description),
            'metadata_count': len(issue.metadata),
            'hour_of_day': issue.detected_at.hour,
            'day_of_week': issue.detected_at.weekday(),
            'is_weekend': 1 if issue.detected_at.weekday() >= 5 else 0,
        }
        
        # Add metadata features if available
        if 'cpu_percent' in issue.metadata:
            features['cpu_usage'] = issue.metadata['cpu_percent']
        if 'memory_percent' in issue.metadata:
            features['memory_usage'] = issue.metadata['memory_percent']
        if 'disk_percent' in issue.metadata:
            features['disk_usage'] = issue.metadata['disk_percent']
            
        return features
        
    async def _predict_root_cause(self, features: Dict[str, Any], issue: Issue) -> tuple:
        """Predict root cause using ML model"""
        
        # Simulate ML model prediction (in production, use actual trained models)
        description = issue.description.lower()
        
        # Rule-based classification with confidence scoring
        if 'cpu' in description and 'high' in description:
            if features.get('cpu_usage', 0) > 90:
                return 'resource_exhaustion', 0.92
            else:
                return 'inefficient_algorithm', 0.85
        elif 'memory' in description and ('high' in description or 'leak' in description):
            if features.get('memory_usage', 0) > 95:
                return 'memory_leak', 0.94
            else:
                return 'large_dataset_processing', 0.78
        elif 'disk' in description and 'full' in description:
            return 'disk_space_exhaustion', 0.96
        elif 'timeout' in description or 'slow' in description:
            if issue.type == 'database':
                return 'database_performance_issue', 0.88
            else:
                return 'network_latency', 0.82
        elif 'connection' in description and 'refused' in description:
            return 'service_unavailable', 0.90
        elif 'permission' in description or 'denied' in description:
            return 'permission_issue', 0.93
        else:
            return 'unknown_issue', 0.45
            
    def _get_ml_recommended_fixes(self, root_cause: str, issue: Issue) -> List[str]:
        """Get ML-recommended fixes based on root cause"""
        
        fix_mapping = {
            'resource_exhaustion': ['scale_horizontally', 'restart_service', 'optimize_code'],
            'inefficient_algorithm': ['optimize_code', 'add_caching', 'restart_service'],
            'memory_leak': ['restart_service', 'optimize_memory_usage', 'increase_memory_limit'],
            'large_dataset_processing': ['optimize_queries', 'add_pagination', 'increase_memory_limit'],
            'disk_space_exhaustion': ['clean_logs', 'expand_storage', 'archive_old_data'],
            'database_performance_issue': ['optimize_database_queries', 'add_indexes', 'restart_database'],
            'network_latency': ['check_network_config', 'optimize_routing', 'add_cdn'],
            'service_unavailable': ['restart_service', 'check_dependencies', 'scale_horizontally'],
            'permission_issue': ['fix_permissions', 'update_iam_policy', 'check_security_groups'],
            'unknown_issue': ['manual_investigation', 'collect_more_data']
        }
        
        return fix_mapping.get(root_cause, ['manual_investigation'])
        
    def get_analyzer_type(self) -> str:
        return "ml"