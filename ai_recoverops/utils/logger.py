"""
Logging utilities for AI-RecoverOps
"""

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup main application logger"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file or 'ai_recoverops.log')
        ]
    )
    
    logger = logging.getLogger('ai_recoverops')
    logger.info(f"Logger initialized with level: {log_level}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module"""
    return logging.getLogger(f'ai_recoverops.{name}')