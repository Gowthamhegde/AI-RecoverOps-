"""
Core RecoverOps Engine - Orchestrates detection, analysis, and fixing
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime
from .models import Issue, Analysis
from ..utils.logger import get_logger
from ..detectors import get_detector_registry
from ..analyzers import get_analyzer_registry
from ..fixers import get_fixer_registry

class RecoverOpsEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config['ai_recoverops']
        self.logger = get_logger(__name__)
        
        # Component registries
        self.detectors = get_detector_registry()
        self.analyzers = get_analyzer_registry()
        self.fixers = get_fixer_registry()
        
        # Runtime state
        self.active_issues = {}
        self.fix_history = []
        self.running = False
        
    async def run(self):
        """Main engine loop"""
        self.logger.info("Starting AI-RecoverOps Engine")
        self.running = True
        
        # Initialize components
        await self._initialize_components()
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._detection_loop()),
            asyncio.create_task(self._analysis_loop()),
            asyncio.create_task(self._fix_loop()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Engine error: {e}")
        finally:
            self.running = False
            
    async def _initialize_components(self):
        """Initialize all detectors, analyzers, and fixers"""
        enabled_detectors = self.config['detection']['enabled_detectors']
        
        for detector_name in enabled_detectors:
            if detector_name in self.detectors:
                detector = self.detectors[detector_name](self.config)
                await detector.initialize()
                
    async def _detection_loop(self):
        """Continuous issue detection"""
        interval = self.config['detection']['interval']
        
        while self.running:
            try:
                for detector_name, detector_class in self.detectors.items():
                    if detector_name in self.config['detection']['enabled_detectors']:
                        detector = detector_class(self.config)
                        issues = await detector.detect()
                        
                        for issue in issues:
                            if issue.id not in self.active_issues:
                                self.active_issues[issue.id] = issue
                                self.logger.info(f"New issue detected: {issue.description}")
                                
            except Exception as e:
                self.logger.error(f"Detection error: {e}")
                
            await asyncio.sleep(interval)
            
    async def _analysis_loop(self):
        """Analyze detected issues for root causes"""
        while self.running:
            try:
                for issue_id, issue in list(self.active_issues.items()):
                    if not hasattr(issue, 'analysis'):
                        analysis = await self._analyze_issue(issue)
                        if analysis and analysis.confidence >= self.config['analysis']['confidence_threshold']:
                            issue.analysis = analysis
                            self.logger.info(f"Root cause identified for {issue_id}: {analysis.root_cause}")
                            
            except Exception as e:
                self.logger.error(f"Analysis error: {e}")
                
            await asyncio.sleep(5)
            
    async def _fix_loop(self):
        """Apply fixes to analyzed issues"""
        while self.running:
            try:
                for issue_id, issue in list(self.active_issues.items()):
                    if hasattr(issue, 'analysis') and not hasattr(issue, 'fix_applied'):
                        if self.config['fixes']['auto_apply'] or not self.config['fixes']['require_approval']:
                            success = await self._apply_fix(issue)
                            if success:
                                issue.fix_applied = True
                                self.logger.info(f"Fix applied successfully for {issue_id}")
                                
            except Exception as e:
                self.logger.error(f"Fix error: {e}")
                
            await asyncio.sleep(10)
            
    async def _analyze_issue(self, issue: Issue) -> Analysis:
        """Analyze an issue to determine root cause"""
        for analyzer_name, analyzer_class in self.analyzers.items():
            analyzer = analyzer_class(self.config)
            if analyzer.can_analyze(issue):
                return await analyzer.analyze(issue)
        return None
        
    async def _apply_fix(self, issue: Issue) -> bool:
        """Apply recommended fix for an issue"""
        if not hasattr(issue, 'analysis'):
            return False
            
        for fix_name in issue.analysis.recommended_fixes:
            if fix_name in self.fixers:
                fixer = self.fixers[fix_name](self.config)
                if await fixer.can_fix(issue):
                    return await fixer.apply_fix(issue)
        return False