from loguru import logger
import sys

def get_logger(name: str = "multi_tenant_backend"):
    """
    Returns a configured Loguru logger for 
    
    Args:
        name (str): Name of the logger, typically the class or module name
    
    Features:
        - Coloured output for better readability
        - Structured logging format
        - INFO level by default
    """
    
    # Remove the default Loguru logger to avoid duplicate logs
    logger.remove()

    # Add a new logger with custom formatting and colorization
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
        level="INFO"
    )

    return logger.bind(name=name)
