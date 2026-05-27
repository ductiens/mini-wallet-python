from datetime import datetime, timezone
from uuid6 import uuid7


def generate_id() -> str:
    """
    Generate a unique ID using UUID v7 (time-ordered).
    This ensures lexicographical sortability and better database index performance.
    """
    return str(uuid7())


def now_utc() -> datetime:
    """
    Get the current timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)
