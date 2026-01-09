"""
Utilities package for Hospital Management System
Contains helper functions and logging utilities
"""
from .logger import (
    log_info, log_error, log_warning, log_debug,
    log_button_click, log_navigation, log_dialog_open,
    log_dialog_close, log_database_operation
)
from .helpers import (
    generate_id, format_date, get_current_date,
    get_current_datetime, validate_email, validate_phone
)

__all__ = [
    'log_info', 'log_error', 'log_warning', 'log_debug',
    'log_button_click', 'log_navigation', 'log_dialog_open',
    'log_dialog_close', 'log_database_operation',
    'generate_id', 'format_date', 'get_current_date',
    'get_current_datetime', 'validate_email', 'validate_phone'
]
