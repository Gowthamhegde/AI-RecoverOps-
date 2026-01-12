"""
AI-RecoverOps - Universal DevOps Automation Platform
"""

__version__ = "1.0.0"
__author__ = "AI-RecoverOps Team"
__email__ = "team@ai-recoverops.com"
__description__ = "Universal DevOps Automation Platform with AI-powered incident detection and remediation"

from .core import AIOpsCore
from .cli import main

__all__ = ['AIOpsCore', 'main']