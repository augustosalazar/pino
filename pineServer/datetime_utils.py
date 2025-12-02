"""
Datetime Utilities - Centralized timezone management

This module ensures all datetime operations use Colombian timezone (America/Bogota)
to maintain consistency across the application, regardless of server location.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

# Colombian timezone
COLOMBIA_TZ = ZoneInfo("America/Bogota")


def now_colombia() -> datetime:
    """
    Get current datetime in Colombian timezone.
    
    Returns:
        datetime: Current datetime in America/Bogota timezone
    """
    return datetime.now(COLOMBIA_TZ)


def now_colombia_iso() -> str:
    """
    Get current datetime in Colombian timezone as ISO string.
    
    Returns:
        str: Current datetime in ISO format with timezone info
    """
    return now_colombia().isoformat()


def get_colombia_midnight() -> datetime:
    """
    Get midnight (00:00:00) of current day in Colombian timezone.
    
    Returns:
        datetime: Midnight of current day in Colombian timezone
    """
    now = now_colombia()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def is_same_day_colombia(dt1: datetime, dt2: datetime) -> bool:
    """
    Check if two datetimes are on the same day in Colombian timezone.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
    
    Returns:
        bool: True if both datetimes are on the same day
    """
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=COLOMBIA_TZ)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=COLOMBIA_TZ)
    
    dt1_colombia = dt1.astimezone(COLOMBIA_TZ)
    dt2_colombia = dt2.astimezone(COLOMBIA_TZ)
    
    return dt1_colombia.date() == dt2_colombia.date()


def parse_iso_to_colombia(iso_string: str) -> datetime:
    """
    Parse ISO string to datetime in Colombian timezone.
    
    Args:
        iso_string: ISO format datetime string
    
    Returns:
        datetime: Parsed datetime in Colombian timezone
    """
    dt = datetime.fromisoformat(iso_string)
    if dt.tzinfo is None:
        # If no timezone info, assume Colombian time
        dt = dt.replace(tzinfo=COLOMBIA_TZ)
    else:
        # Convert to Colombian time
        dt = dt.astimezone(COLOMBIA_TZ)
    return dt


def get_current_date_colombia() -> str:
    """
    Get current date in Colombian timezone (YYYY-MM-DD format).
    
    Returns:
        str: Current date in YYYY-MM-DD format
    """
    return now_colombia().strftime("%Y-%m-%d")


def get_current_time_colombia() -> str:
    """
    Get current time in Colombian timezone (HH:MM:SS format).
    
    Returns:
        str: Current time in HH:MM:SS format
    """
    return now_colombia().strftime("%H:%M:%S")
