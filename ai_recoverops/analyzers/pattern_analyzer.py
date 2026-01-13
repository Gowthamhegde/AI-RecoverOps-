"""
Pattern-based root cause analyzer
"""

import re
from typing import Dict, Any, List
from ..core.analyzer import BaseAnalyzer
from ..core.models import Issue, Analysis
from ..utils.logger import get_logger

class PatternAnalyzer(BaseAnalyzer):
    """Analyzes issues using pattern matching and heuristics"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Define issue patterns
        self.patterns = {
            'high_cpu': {
                'regex': r'(cpu|processor).*?(high|usage|spike|100%|9[0-9]%)',
                'confidence': 0.9,
                'root_causes': ['resource_exhaustion', 'inefficient_algorithm', 'infinite_loop'],
                'fixes': ['restart_service', 'scale_horizontally', 'optimize_code']
            },
            'memory_leak': {
                'regex': r'(memory|ram).*?(leak|high|usage|oom|out of memory)',
                'confidence': 0.88,
                'root_causes': ['memory_leak', 'large_dataset', 'memory_fragmentation'],
                'fixes': ['restart_service', 'increase_memory_limit', 'optimize_memory_usage']
            },
            'disk_full': {
                'regex': r'(disk|storage|filesystem).*?(full|space|no space|100%)',
                'confidence': 0.95,
                'root_causes': ['disk_space_exhaustion', 'log_accumulation', 'temp_files'],
                'fixes': ['clean_logs', 'expand_storage', 'archive_old_data']
            },
            'service_down': {
                'regex': r'(service|server|application).*?(down|stopped|crashed|failed|unavailable)',
                'confidence': 0.92,
                'root_causes': ['service_crash', 'dependency_failure', 'resource_exhaustion'],
                'fixes': ['restart_service', 'check_dependencies', 'scale_horizontally']
            },
            'database_connection': {
                'regex': r'(database|db|sql).*?(connection|connect|timeout|refused)',
                'confidence': 0.89,
                'root_causes': ['connection_pool_exhaustion', 'database_overload', 'network_issue'],
                'fixes': ['restart_database', 'increase_max_connections', 'optimize_queries']
            },
            'network_timeout': {
                'regex': r'(network|connection|request).*?(timeout|slow|latency|unreachable)',
                'confidence': 0.85,
                'root_causes': ['network_congestion', 'dns_issue', 'firewall_blocking'],
                'fixes': ['check_network_config', 'restart_networking', 'update_dns']
            },
            'permission_denied': {
                'regex': r'(permission|access).*?(denied|forbidden|unauthorized|403)',
                'confidence': 0.93,
                'root_causes': ['incorrect_permissions', 'expired_credentials', 'security_policy'],
                'fixes': ['fix_permissions', 'update_credentials', 'check_security_groups']
            },
            'port_conflict': {
                'regex': r'(port|address).*?(in use|already|bind|conflict)',
                'confidence': 0.91,
                'root_causes': ['port_already_in_use', 'duplicate_service', 'zombie_process'],
                'fixes': ['kill_conflicting_process', 'change_port', 'restart_service']
            }
        }
        
    def can_analyze(self, issue: Issue) -> bool:
        """Check if this analyzer can handle the issue"""
        # Pattern analyzer can handle any issue with text description
        return bool(issue.description)
        
    async def analyze(self, issue: Issue) -> Analysis:
        """Analyze issue using pattern matching"""
        self.logger.info(f"Pattern analyzing issue: {issue.description}")
        
        # Find matching patterns
        matched_patterns = self._find_matching_patterns(issue.description)
        
        if not matched_patterns:
            return Analysis(
                issue_id=issue.id,
                root_cause='unknown_pattern',
                confidence=0.3,
                recommended_fixes=['manual_investigation'],
                analysis_data={
                    'matched_patterns': [],
                    'analysis_method': 'pattern_matching'
                }
            )
        
        # Get the best matching pattern
        best_pattern = max(matched_patterns, key=lambda x: x['confidence'])
        
        # Determine root cause based on context
        root_cause = self._determine_root_cause(best_pattern, issue)
        
        return Analysis(
            issue_id=issue.id,
            root_cause=root_cause,
            confidence=best_pattern['confidence'],
            recommended_fixes=best_pattern['fixes'],
            analysis_data={
                'matched_patterns': matched_patterns,
                'best_pattern': best_pattern['name'],
                'analysis_method': 'pattern_matching'
            }
        )
        
    def _find_matching_patterns(self, description: str) -> List[Dict[str, Any]]:
        """Find patterns that match the issue description"""
        matched = []
        description_lower = description.lower()
        
        for pattern_name, pattern_config in self.patterns.items():
            if re.search(pattern_config['regex'], description_lower, re.IGNORECASE):
                matched.append({
                    'name': pattern_name,
                    'confidence': pattern_config['confidence'],
                    'root_causes': pattern_config['root_causes'],
                    'fixes': pattern_config['fixes']
                })
        
        return matched
        
    def _determine_root_cause(self, pattern: Dict[str, Any], issue: Issue) -> str:
        """Determine the most likely root cause from pattern"""
        
        # Use metadata to refine root cause selection
        root_causes = pattern['root_causes']
        
        if pattern['name'] == 'high_cpu':
            cpu_usage = issue.metadata.get('cpu_percent', 0)
            if cpu_usage > 95:
                return 'resource_exhaustion'
            else:
                return 'inefficient_algorithm'
                
        elif pattern['name'] == 'memory_leak':
            memory_usage = issue.metadata.get('memory_percent', 0)
            if memory_usage > 95:
                return 'memory_leak'
            else:
                return 'large_dataset'
                
        elif pattern['name'] == 'service_down':
            if 'crash' in issue.description.lower():
                return 'service_crash'
            else:
                return 'dependency_failure'
                
        elif pattern['name'] == 'database_connection':
            if 'timeout' in issue.description.lower():
                return 'database_overload'
            else:
                return 'connection_pool_exhaustion'
        
        # Default to first root cause
        return root_causes[0] if root_causes else 'unknown_root_cause'
        
    def get_analyzer_type(self) -> str:
        return "pattern"