"""
Issue detectors for various system components
"""

from .system_detector import SystemDetector
from .application_detector import ApplicationDetector
from .network_detector import NetworkDetector
from .database_detector import DatabaseDetector

def get_detector_registry():
    """Return registry of available detectors"""
    return {
        'system': SystemDetector,
        'application': ApplicationDetector,
        'network': NetworkDetector,
        'database': DatabaseDetector,
    }