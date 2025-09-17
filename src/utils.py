<<<<<<< HEAD
"""
Utility functions for DJI Tello operations.
"""

import time
import logging

def setup_logging():
    """Setup logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def safe_delay(seconds):
    """Safe delay with feedback."""
    print(f"Waiting {seconds} seconds...")
    time.sleep(seconds)

def check_battery_level(tello, min_level=20):
    """Check if battery level is sufficient for flight."""
    battery = tello.get_battery()
    if battery < min_level:
        print(f"Warning: Low battery ({battery}%). Minimum recommended: {min_level}%")
        return False
    return True

def emergency_stop(tello):
    """Emergency stop function."""
    try:
        tello.emergency()
        print("Emergency stop activated!")
    except Exception as e:
=======
"""
Utility functions for DJI Tello operations.
"""

import time
import logging

def setup_logging():
    """Setup logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def safe_delay(seconds):
    """Safe delay with feedback."""
    print(f"Waiting {seconds} seconds...")
    time.sleep(seconds)

def check_battery_level(tello, min_level=20):
    """Check if battery level is sufficient for flight."""
    battery = tello.get_battery()
    if battery < min_level:
        print(f"Warning: Low battery ({battery}%). Minimum recommended: {min_level}%")
        return False
    return True

def emergency_stop(tello):
    """Emergency stop function."""
    try:
        tello.emergency()
        print("Emergency stop activated!")
    except Exception as e:
>>>>>>> dea707e300b8a0d0602dd0c7554e56810d0958fe
        print(f"Emergency stop failed: {e}")