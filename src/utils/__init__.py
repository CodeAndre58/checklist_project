"""
utils/logger.py - Logging configuration for audit trail
"""
import structlog
import logging
from pathlib import Path
from datetime import datetime


def setup_logger(log_dir: Path = None) -> None:
    """Setup structured logging for audit trail"""
    if log_dir is None:
        log_dir = Path("output/logs")
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configura handler filelog con structlog
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    
    logger = structlog.get_logger()
    logger.info("logging_started", log_file=str(log_file))
    return logger


def get_logger(name: str = "prisma-analyzer"):
    """Get logger instance"""
    return structlog.get_logger(name)
