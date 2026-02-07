"""
Utility functions for Hospital Management System
"""
import uuid
from datetime import datetime, date


def generate_id(prefix: str) -> str:
    """Generate unique ID with prefix"""
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{prefix}-{unique_id}"


def format_date(date_str: str) -> str:
    """Format date string for display"""
    try:
        if isinstance(date_str, str):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        return date_str
    except:
        return date_str


def get_current_date() -> str:
    """Get current date as string"""
    return datetime.now().strftime('%Y-%m-%d')


def get_current_datetime() -> str:
    """Get current datetime as string"""
    return datetime.now().isoformat()


def get_current_time() -> str:
    """Get current time as string in HH:MM format"""
    return datetime.now().strftime('%H:%M')


def validate_email(email: str) -> bool:
    """Simple email validation"""
    return '@' in email and '.' in email.split('@')[1]


def validate_phone(phone: str) -> bool:
    """Simple phone validation"""
    return phone.replace('-', '').replace(' ', '').replace('+', '').isdigit()

