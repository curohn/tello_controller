#!/usr/bin/env python3
"""
Basic flight example for DJI Tello drone.
Simple takeoff, hover, and landing demonstration.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tello_controller import TelloController
from utils import safe_delay, check_battery_level

def basic_flight_demo():
    """Perform a basic flight demonstration."""
    controller = TelloController()
    
    print("=== Basic Flight Demo ===")
    print("This demo will: takeoff → hover 5 seconds → land")
    
    # Connect to drone
    print("Connecting to Tello...")
    if not controller.connect():
        print("❌ Failed to connect to Tello.")
        print("Make sure drone is on and connected to WiFi.")
        return False
    
    try:
        # Check battery level
        battery = controller.controller.tello.get_battery()
        print(f"✅ Connected! Battery: {battery}%")
        
        if not check_battery_level(controller.tello, min_level=30):
            response = input("⚠️  Low battery. Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False
        
        # Basic flight sequence
        print("\n🚁 Starting basic flight sequence...")
        
        # Take off
        print("1. Taking off...")
        controller.takeoff()
        safe_delay(3)
        print("✅ Takeoff complete!")
        
        # Get status
        status = controller.get_status()
        print(f"📊 Flight status: Height={status['height']}cm, Battery={status['battery']}%")
        
        # Hover
        print("2. Hovering for 5 seconds...")
        safe_delay(5)
        
        # Land
        print("3. Landing...")
        controller.land()
        print("✅ Landing complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Flight error: {e}")
        print("🚨 Emergency landing...")
        controller.land()
        return False
    
    finally:
        controller.disconnect()
        print("✅ Demo complete!")

if __name__ == "__main__":
    print("DJI Tello Basic Flight Demo")
    print("Make sure your Tello is:")
    print("- Powered on")
    print("- Connected to WiFi")
    print("- In an open area")
    
    input("\nPress Enter to start demo...")
    success = basic_flight_demo()
    
    if success:
        print("\n🎉 Demo completed successfully!")
    else:
        print("\n⚠️  Demo encountered issues. Check drone and try again.")