"""
GenFlow Core Module

This package contains the core functionality of the GenFlow system,
including tools for content generation, data collection, and processing.
"""

__version__ = "0.1.0"

import os
import sys
import logging
from loguru import logger

# 初始化日志设置
# Consider moving log setup to a dedicated config/setup function if it gets complex
log_dir = "logs"
log_file = os.path.join(log_dir, "core.log")

# Ensure logs directory exists
try:
    os.makedirs(log_dir, exist_ok=True)
except OSError as e:
    # Use standard logging if Loguru setup fails due to directory issues
    logging.basicConfig(level=logging.WARNING)
    logging.warning(f"Could not create log directory {log_dir}: {e}. Loguru setup skipped.")

# Check if handlers are already configured to avoid duplicates
# Use _name as suggested by the AttributeError
if not any(handler._name == "core_log_handler" for handler in logger._core.handlers.values()):
    try:
        logger.add(
            log_file,
            rotation="1 day",
            retention="7 days",
            level="INFO",
            format="{time} {level} {message}" # Example format
        )
        logger.info("Loguru logger initialized for core module.")
    except Exception as e:
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Failed to initialize Loguru logger: {e}")

logger.debug("core package loaded.")

# You might want to export key components of the core module here if needed
# Example:
# from .some_core_component import CoreComponent
# __all__ = ["CoreComponent"]
