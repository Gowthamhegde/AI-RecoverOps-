"""
DevOps-focused root cause analyzer
"""

import asyncio
from typing import Dict, Any, List
from ..core.analyzer import BaseAnalyzer
from ..core.engine import Issue, Analysis
from ..utils.logger import get_logger

class DevOpsAnalyzer(BaseAnalyzer):
    """Analyzes issues using DevOps best practices and patterns"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # DevOps knowledge base
        self.root_cause_patterns = {
            'high_cpu': {
                'causes': ['resource_leak', 'inefficient_algorithm', 'ddos_attack', 'autoscaling_failure'],
                'fixes': ['restart_service', 'scale_horizontally', 'optimize_code', 'enable_rate_limiting']
            },
            'high_memory': {
                'causes': ['memory_leak', 'large_dataset_processing', 'cache_overflow', 'memory_fragmentation'],
                'fixes': ['restart_service', 'increase_memory_limit', 'optimize_memory_usage', 'clear_cache']
            },
            'service_timeout': {
                'causes': ['network_latency', 'database_slowdown', 'resource_exhaustion', 'deadlock'],
                'fixes': ['increase_timeout', 'optimize_database_queries', 'add_connection_pooling', 'restart_service']
            },
            'container_down': {
                'causes': ['oom_kill', 'health_check_failure', 'image_pull_failure', 'resource_limits'],
                'fixes': ['increase_memory_limit', 'fix_health_check', 'update_image_tag', 'adjust_resource_limits']
            },
            'database_connections': {
                'causes': ['connection_leak', 'high_traffic', 'long_running_transactions', 'missing_connection_pooling'],
                'fixes': ['restart_database', 'increase_max_connections', 'optimize_queries', 'implement_connection_pooling']
            }
        }
        
    def can_analyze(self, issue: Issue) -> bool:
        """Check if this analyzer can handle the issue"""
        return issue.type in ['system', 'application', 'network', 'database']
        
    async def analyze(self, issue: Issue) -> Analysis:
        """Analyze issue and determine root cause"""
        self.logger.info(f"Analyzing issue: {issue.description}")
        
        # Determine issue pattern
        issue_pattern = self._classify_issue_pattern(issue)
        
        # Get historical context
        historical_context = await self._get_historical_context(issue)
        
        # Analyze system state
        system_state = await self._analyze_system_state(issue)
        
        # Determine root cause
        root_cause, confidence = self._determine_root_cause(issue, issue_pattern, historical_context, system_state)
        
        # Get recommended fixes
        recommended_fixes = self._get_recommended_fixes(issue_pattern, root_cause)
        
        return Analysis(
            issue_id=issue.id,
            root_cause=root_cause,
            confidence=confidence,
            recommended_fixes=recommended_fixes,
            analysis_data={
                'issue_pattern': issue_pattern,
                'historical_context': historical_context,
                'system_state': system_state,
                'analysis_method': 'devops_patterns'
            }
        )
        
    def _classify_issue_pattern(self, issue: Issue) -> str:
        """Classify the issue into known patterns"""
        description = issue.description.lower()
        
        if 'cpu' in description and 'high' in description:
            return 'high_cpu'
        elif 'memory' in description and 'high' in description:
            return 'high_memory'
        elif 'timeout' in description or 'response time' in description:
            return 'service_timeout'
        elif 'container' in description and ('down' in description or 'exited' in description):
            return 'container_down'
        elif 'connection' in description and 'database' in description:
            return 'database_connections'
        elif 'disk' in description and 'high' in description:
            return 'high_disk_usage'
        elif 'network' in description or 'connectivity' in description:
            return 'network_issue'
        else:
            return 'unknown_pattern'
            
    async def _get_historical_context(self, issue: Issue) -> Dict[str, Any]:
        """Get historical context for similar issues"""
        # In a real implementation, this would query a database of historical issues
        return {
            'similar_issues_count': 0,
            'last_occurrence': None,
            'common_resolution': None,
            'frequency': 'first_time'
        }
        
    async def _analyze_system_state(self, issue: Issue) -> Dict[str, Any]:
        """Analyze current system state for additional context"""
        system_state = {}
        
        try:
            # Check system metrics
            import psutil
            
            system_state.update({
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': {p.mountpoint: psutil.disk_usage(p.mountpoint).percent 
                              for p in psutil.disk_partitions() 
                              if p.fstype and p.mountpoint != '/'},
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                'process_count': len(psutil.pids())
            })
            
            # Check Docker containers if available
            try:
                process = await asyncio.create_subprocess_exec(
                    'docker', 'stats', '--no-stream', '--format', 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    container_stats = []
                    lines = stdout.decode().strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            parts = line.split('\t')
                            if len(parts) >= 3:
                                container_stats.append({
                                    'name': parts[0],
                                    'cpu_percent': parts[1],
                                    'memory_usage': parts[2]
                                })
                    system_state['container_stats'] = container_stats
                    
            except Exception:
                pass
                
        except Exception as e:
            self.logger.warning(f"Failed to get system state: {e}")
            
        return system_state
        
    def _determine_root_cause(self, issue: Issue, pattern: str, historical: Dict, system_state: Dict) -> tuple:
        """Determine the most likely root cause"""
        
        if pattern in self.root_cause_patterns:
            causes = self.root_cause_patterns[pattern]['causes']
            
            # Apply heuristics based on system state and issue metadata
            if pattern == 'high_cpu':
                cpu_percent = system_state.get('cpu_percent', 0)
                if cpu_percent > 95:
                    return 'resource_exhaustion', 0.9
                elif issue.metadata.get('cpu_percent', 0) > 90:
                    return 'inefficient_algorithm', 0.8
                else:
                    return 'resource_leak', 0.7
                    
            elif pattern == 'high_memory':
                memory_percent = system_state.get('memory_percent', 0)
                if memory_percent > 95:
                    return 'memory_leak', 0.9
                else:
                    return 'large_dataset_processing', 0.7
                    
            elif pattern == 'service_timeout':
                if 'database' in issue.description.lower():
                    return 'database_slowdown', 0.8
                else:
                    return 'network_latency', 0.7
                    
            elif pattern == 'container_down':
                if 'oom' in issue.metadata.get('status', '').lower():
                    return 'oom_kill', 0.95
                else:
                    return 'health_check_failure', 0.8
                    
            elif pattern == 'database_connections':
                active_connections = issue.metadata.get('active_connections', 0)
                max_connections = issue.metadata.get('max_connections', 100)
                if active_connections / max_connections > 0.9:
                    return 'connection_leak', 0.9
                else:
                    return 'high_traffic', 0.8
                    
            # Default to first cause with medium confidence
            return causes[0], 0.6
        else:
            return 'unknown_root_cause', 0.3
            
    def _get_recommended_fixes(self, pattern: str, root_cause: str) -> List[str]:
        """Get recommended fixes based on pattern and root cause"""
        
        if pattern in self.root_cause_patterns:
            base_fixes = self.root_cause_patterns[pattern]['fixes']
            
            # Prioritize fixes based on root cause
            prioritized_fixes = []
            
            if root_cause == 'resource_exhaustion':
                prioritized_fixes = ['scale_horizontally', 'restart_service', 'optimize_code']
            elif root_cause == 'memory_leak':
                prioritized_fixes = ['restart_service', 'optimize_memory_usage', 'increase_memory_limit']
            elif root_cause == 'oom_kill':
                prioritized_fixes = ['increase_memory_limit', 'optimize_memory_usage']
            elif root_cause == 'database_slowdown':
                prioritized_fixes = ['optimize_database_queries', 'add_connection_pooling', 'restart_database']
            elif root_cause == 'connection_leak':
                prioritized_fixes = ['restart_service', 'implement_connection_pooling', 'optimize_queries']
            else:
                prioritized_fixes = base_fixes
                
            return prioritized_fixes[:3]  # Return top 3 fixes
        else:
            return ['manual_investigation']
            
    def get_analyzer_type(self) -> str:
        return "devops"