"""
DJI Tello SDK main module for drone control and communication.
"""

from djitellopy import Tello
import cv2
import time

class TelloController:
    """Main class for controlling DJI Tello drone."""
    
    def __init__(self):
        """Initialize Tello connection."""
        self.tello = Tello()
        self.connected = False
    
    def connect(self):
        """Connect to the Tello drone."""
        try:
            self.tello.connect()
            self.connected = True
            print(f"Battery: {self.tello.get_battery()}%")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the Tello drone."""
        if self.connected:
            self.tello.end()
            self.connected = False
    
    def takeoff(self):
        """Take off the drone."""
        if self.connected:
            self.tello.takeoff()
            print("Drone took off")
    
    def land(self):
        """Land the drone."""
        if self.connected:
            self.tello.land()
            print("Drone landed")
    
    def get_status(self):
        """Get drone status information."""
        if self.connected:
            return {
                'battery': self.tello.get_battery(),
                'height': self.tello.get_height(),
                'temperature': self.tello.get_temperature(),
                'speed': self.tello.get_speed_x()
            }
        return None