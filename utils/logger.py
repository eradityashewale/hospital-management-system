"""
Logging module for Hospital Management System
Provides detailed logging for debugging and monitoring
"""
import logging
import os
import sys
from datetime import datetime

# Determine the base directory for logs
# If running from Program Files (installed), use AppData
# Otherwise, use the current directory (development mode)
def get_app_data_dir():
    """Get the application data directory for logs and database"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        # Check if we're in Program Files
        exe_dir = os.path.dirname(sys.executable)
        if 'Program Files' in exe_dir or 'Program Files (x86)' in exe_dir:
            # Use AppData for installed applications
            appdata = os.getenv('APPDATA', os.path.expanduser('~'))
            app_dir = os.path.join(appdata, 'Hospital Management System')
            if not os.path.exists(app_dir):
                os.makedirs(app_dir)
            return app_dir
        else:
            # Use executable directory if not in Program Files
            return exe_dir
    else:
        # Running from source (development mode)
        return os.path.dirname(os.path.abspath(__file__))

# Get application data directory
app_data_dir = get_app_data_dir()

# Create logs directory in the appropriate location
logs_dir = os.path.join(app_data_dir, 'logs')
if not os.path.exists(logs_dir):
    try:
        os.makedirs(logs_dir)
    except OSError:
        # Fallback to current directory if AppData fails
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

# Configure logging
log_filename = os.path.join(logs_dir, f"hospital_system_{datetime.now().strftime('%Y%m%d')}.log")

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

