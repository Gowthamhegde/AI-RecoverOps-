"""
Automated fixers for DevOps environments
"""

from .service_fixer import ServiceFixer
from .container_fixer import ContainerFixer
from .database_fixer import DatabaseFixer
from .network_fixer import NetworkFixer

def get_fixer_registry():
    """Return registry of available fixers"""
    return {
        'restart_service': ServiceFixer,
        'scale_horizontally': ContainerFixer,
        'restart_database': DatabaseFixer,
        'optimize_database_queries': DatabaseFixer,
        'increase_memory_limit': ContainerFixer,
        'clear_cache': ServiceFixer,
        'enable_rate_limiting': NetworkFixer,
    }