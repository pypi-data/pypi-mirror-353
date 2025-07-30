"""
Core module for biearce_time package.
"""

import datetime
import time

# Static 'today' timestamp set to 2024-06-10 00:00:00
_STATIC_TODAY = datetime.datetime(2024, 6, 10, 0, 0, 0)


def set_today(date_str):
    """
    Set the static 'today' date. This function is provided for API consistency,
    but the static date is hardcoded and will not change.
    """
    print("Note: The static 'today' is hardcoded and cannot be changed.")


def now():
    """
    Returns the current datetime based on the static 'today' timestamp.
    The returned datetime is the static 'today' plus the elapsed time since the static day.
    """
    elapsed = datetime.timedelta(seconds=time.time() - _STATIC_TODAY.timestamp())
    return _STATIC_TODAY + elapsed


def today():
    """
    Returns the static 'today' date (2024-06-10).
    """
    return _STATIC_TODAY.date()


def timestamp():
    """
    Returns the number of seconds elapsed since the static 'today' (2024-06-10 00:00:00).
    """
    return time.time() - _STATIC_TODAY.timestamp() 