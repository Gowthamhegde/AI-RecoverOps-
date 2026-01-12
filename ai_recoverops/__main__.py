"""
Main entry point for AI-RecoverOps
"""

import click
import yaml
import asyncio
from pathlib import Path
from .core.engine import RecoverOpsEngine
from .utils.logger import setup_logger

@click.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--dry-run', is_flag=True, help='Run in simulation mode without applying fixes')
def main(config, verbose, dry_run):
    """AI-RecoverOps: Automatic Root Cause Fixer"""
    
    # Load configuration
    config_path = Path(config)
    if not config_path.exists():
        click.echo(f"Configuration file not found: {config}")
        return
    
    with open(config_path) as f:
        config_data = yaml.safe_load(f)
    
    # Setup logging
    log_level = "DEBUG" if verbose else config_data.get('ai_recoverops', {}).get('core', {}).get('log_level', 'INFO')
    logger = setup_logger(log_level)
    
    if dry_run:
        logger.info("Running in DRY-RUN mode - no fixes will be applied")
        config_data['ai_recoverops']['fixes']['auto_apply'] = False
    
    # Initialize and run engine
    engine = RecoverOpsEngine(config_data)
    
    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        logger.info("Shutting down AI-RecoverOps...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()