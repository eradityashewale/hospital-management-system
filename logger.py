"""
Logging module for Hospital Management System
Provides detailed logging for debugging and monitoring
"""
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
log_filename = f"logs/hospital_system_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger('HospitalSystem')

def log_button_click(button_name, module=None):
    """Log button click events"""
    message = f"Button clicked: {button_name}"
    if module:
        message += f" (Module: {module})"
    logger.info(message)

def log_dialog_open(dialog_name):
    """Log when a dialog opens"""
    logger.info(f"Dialog opened: {dialog_name}")

def log_dialog_close(dialog_name):
    """Log when a dialog closes"""
    logger.info(f"Dialog closed: {dialog_name}")

def log_database_operation(operation, table, success=True, details=""):
    """Log database operations"""
    status = "SUCCESS" if success else "FAILED"
    message = f"Database {operation} on {table}: {status}"
    if details:
        message += f" - {details}"
    if success:
        logger.info(message)
    else:
        logger.error(message)

def log_navigation(from_module, to_module):
    """Log navigation between modules"""
    logger.info(f"Navigation: {from_module} -> {to_module}")

def log_error(error_message, exception=None):
    """Log errors with exception details"""
    if exception:
        logger.error(f"{error_message}: {str(exception)}", exc_info=True)
    else:
        logger.error(error_message)

def log_info(message):
    """Log informational messages"""
    logger.info(message)

def log_debug(message):
    """Log debug messages"""
    logger.debug(message)

def log_warning(message):
    """Log warning messages"""
    logger.warning(message)

