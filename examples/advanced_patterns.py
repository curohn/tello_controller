<<<<<<< HEAD
#!/usr/bin/env python3
"""
Advanced flight patterns for DJI Tello drone.
Demonstrates complex maneuvers and autonomous flight patterns.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tello_controller import TelloController
from utils import safe_delay, check_battery_level
import time

class FlightPatterns:
    """Collection of advanced flight patterns."""
    
    def __init__(self, controller):
        self.controller = controller
    
    def square_pattern(self, size=50):
        """Fly in a square pattern."""
        print(f"🔲 Flying {size}cm square pattern...")
        
        movements = [
            ('move_forward', size, 'Forward'),
            ('move_right', size, 'Right'),
            ('move_back', size, 'Back'),
            ('move_left', size, 'Left')
        ]
        
        for method, distance, direction in movements:
            print(f"   → Moving {direction} {distance}cm")
            getattr(self.controller.tello, method)(distance)
            safe_delay(2)
        
        print("✅ Square pattern complete!")
    
    def triangle_pattern(self, size=60):
        """Fly in a triangular pattern using rotation and forward movement."""
        print(f"🔺 Flying {size}cm triangle pattern...")
        
        for i in range(3):
            print(f"   → Side {i+1}/3: Forward {size}cm, rotate 120°")
            self.controller.tello.move_forward(size)
            safe_delay(2)
            self.controller.tello.rotate_clockwise(120)
            safe_delay(2)
        
        print("✅ Triangle pattern complete!")
    
    def figure_eight(self, radius=80):
        """Fly in a figure-8 pattern using curves."""
        print(f"∞ Flying figure-8 pattern (radius: {radius}cm)...")
        
        try:
            # First loop (clockwise)
            print("   → First loop (clockwise)")
            for i in range(4):
                self.controller.tello.curve_xyz_speed(
                    radius//2, 0, 0, radius, 0, 0, 30
                )
                safe_delay(3)
            
            # Second loop (counter-clockwise)  
            print("   → Second loop (counter-clockwise)")
            for i in range(4):
                self.controller.tello.curve_xyz_speed(
                    -radius//2, 0, 0, -radius, 0, 0, 30
                )
                safe_delay(3)
                
            print("✅ Figure-8 pattern complete!")
            
        except Exception as e:
            print(f"⚠️  Curve commands failed: {e}")
            print("   Trying simplified figure-8 with basic movements...")
            self._simple_figure_eight(radius)
    
    def _simple_figure_eight(self, radius):
        """Simplified figure-8 using basic movements."""
        # Simplified version using forward/rotate commands
        moves = [
            ('move_forward', radius//2), ('rotate_clockwise', 45),
            ('move_forward', radius//2), ('rotate_clockwise', 90),
            ('move_forward', radius//2), ('rotate_clockwise', 45),
            ('move_forward', radius//2), ('rotate_clockwise', 90),
        ]
        
        for move_type, value in moves:
            getattr(self.controller.tello, move_type)(value)
            safe_delay(1.5)
    
    def spiral_ascent(self, height=100, turns=3):
        """Spiral upward while rotating."""
        print(f"🌀 Spiral ascent: {height}cm height, {turns} turns...")
        
        height_per_turn = height // turns
        degrees_per_step = 360 // 8  # 8 steps per turn
        
        for turn in range(turns):
            print(f"   → Turn {turn+1}/{turns}")
            for step in range(8):
                self.controller.tello.move_up(height_per_turn // 8)
                self.controller.tello.rotate_clockwise(degrees_per_step)
                safe_delay(1)
        
        print("✅ Spiral ascent complete!")
        
        # Spiral back down
        print("🌀 Spiral descent...")
        for turn in range(turns):
            print(f"   → Descent turn {turn+1}/{turns}")
            for step in range(8):
                self.controller.tello.move_down(height_per_turn // 8)
                self.controller.tello.rotate_counter_clockwise(degrees_per_step)
                safe_delay(1)
        
        print("✅ Spiral descent complete!")

def advanced_flight_demo():
    """Main demo function with pattern selection."""
    controller = TelloController()
    
    print("=== Advanced Flight Patterns Demo ===")
    
    # Connect to drone
    print("Connecting to Tello...")
    if not controller.connect():
        print("❌ Failed to connect to Tello.")
        return False
    
    try:
        # Check battery level (need more for advanced patterns)
        battery = controller.tello.get_battery()
        print(f"✅ Connected! Battery: {battery}%")
        
        if battery < 50:
            print("⚠️  Advanced patterns require at least 50% battery for safety.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False
        
        # Take off and gain altitude
        print("🚁 Taking off...")
        controller.takeoff()
        safe_delay(3)
        
        print("📈 Gaining altitude for safety...")
        controller.tello.move_up(50)
        safe_delay(2)
        
        # Pattern selection
        patterns = FlightPatterns(controller)
        
        print("\n🎯 Select a flight pattern:")
        print("1. Square Pattern")
        print("2. Triangle Pattern") 
        print("3. Figure-8 Pattern")
        print("4. Spiral Ascent/Descent")
        print("5. All Patterns (Demo)")
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            patterns.square_pattern(60)
        elif choice == '2':
            patterns.triangle_pattern(70)
        elif choice == '3':
            patterns.figure_eight(80)
        elif choice == '4':
            patterns.spiral_ascent(80, 2)
        elif choice == '5':
            print("🎪 Running full demo (all patterns)...")
            patterns.square_pattern(50)
            safe_delay(3)
            patterns.triangle_pattern(50)
            safe_delay(3)
            patterns.figure_eight(60)
        else:
            print("Invalid choice - performing square pattern")
            patterns.square_pattern(60)
        
        # Return to center and land
        print("🎯 Returning to landing position...")
        try:
            controller.tello.go_xyz_speed(0, 0, 0, 30)
            safe_delay(3)
        except:
            print("   Go-to-coordinate failed, landing from current position")
        
        print("🛬 Landing...")
        controller.land()
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern error: {e}")
        print("🚨 Emergency landing...")
        controller.land()
        return False
    
    finally:
        controller.disconnect()
        print("✅ Advanced flight demo complete!")

if __name__ == "__main__":
    print("DJI Tello Advanced Flight Patterns")
    print("\n⚠️  SAFETY WARNING:")
    print("- Ensure you have at least 3x3 meters of open space")
    print("- Remove any obstacles from flight area")
    print("- Have manual control ready")
    print("- Monitor battery levels")
    
    response = input("\nReady for advanced flight demo? (y/n): ")
    
    if response.lower() == 'y':
        success = advanced_flight_demo()
        
        if success:
            print("\n🎉 Advanced patterns completed successfully!")
        else:
            print("\n⚠️  Demo encountered issues. Check environment and try again.")
    else:
=======
#!/usr/bin/env python3
"""
Advanced flight patterns for DJI Tello drone.
Demonstrates complex maneuvers and autonomous flight patterns.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tello_controller import TelloController
from utils import safe_delay, check_battery_level
import time

class FlightPatterns:
    """Collection of advanced flight patterns."""
    
    def __init__(self, controller):
        self.controller = controller
    
    def square_pattern(self, size=50):
        """Fly in a square pattern."""
        print(f"🔲 Flying {size}cm square pattern...")
        
        movements = [
            ('move_forward', size, 'Forward'),
            ('move_right', size, 'Right'),
            ('move_back', size, 'Back'),
            ('move_left', size, 'Left')
        ]
        
        for method, distance, direction in movements:
            print(f"   → Moving {direction} {distance}cm")
            getattr(self.controller.tello, method)(distance)
            safe_delay(2)
        
        print("✅ Square pattern complete!")
    
    def triangle_pattern(self, size=60):
        """Fly in a triangular pattern using rotation and forward movement."""
        print(f"🔺 Flying {size}cm triangle pattern...")
        
        for i in range(3):
            print(f"   → Side {i+1}/3: Forward {size}cm, rotate 120°")
            self.controller.tello.move_forward(size)
            safe_delay(2)
            self.controller.tello.rotate_clockwise(120)
            safe_delay(2)
        
        print("✅ Triangle pattern complete!")
    
    def figure_eight(self, radius=80):
        """Fly in a figure-8 pattern using curves."""
        print(f"∞ Flying figure-8 pattern (radius: {radius}cm)...")
        
        try:
            # First loop (clockwise)
            print("   → First loop (clockwise)")
            for i in range(4):
                self.controller.tello.curve_xyz_speed(
                    radius//2, 0, 0, radius, 0, 0, 30
                )
                safe_delay(3)
            
            # Second loop (counter-clockwise)  
            print("   → Second loop (counter-clockwise)")
            for i in range(4):
                self.controller.tello.curve_xyz_speed(
                    -radius//2, 0, 0, -radius, 0, 0, 30
                )
                safe_delay(3)
                
            print("✅ Figure-8 pattern complete!")
            
        except Exception as e:
            print(f"⚠️  Curve commands failed: {e}")
            print("   Trying simplified figure-8 with basic movements...")
            self._simple_figure_eight(radius)
    
    def _simple_figure_eight(self, radius):
        """Simplified figure-8 using basic movements."""
        # Simplified version using forward/rotate commands
        moves = [
            ('move_forward', radius//2), ('rotate_clockwise', 45),
            ('move_forward', radius//2), ('rotate_clockwise', 90),
            ('move_forward', radius//2), ('rotate_clockwise', 45),
            ('move_forward', radius//2), ('rotate_clockwise', 90),
        ]
        
        for move_type, value in moves:
            getattr(self.controller.tello, move_type)(value)
            safe_delay(1.5)
    
    def spiral_ascent(self, height=100, turns=3):
        """Spiral upward while rotating."""
        print(f"🌀 Spiral ascent: {height}cm height, {turns} turns...")
        
        height_per_turn = height // turns
        degrees_per_step = 360 // 8  # 8 steps per turn
        
        for turn in range(turns):
            print(f"   → Turn {turn+1}/{turns}")
            for step in range(8):
                self.controller.tello.move_up(height_per_turn // 8)
                self.controller.tello.rotate_clockwise(degrees_per_step)
                safe_delay(1)
        
        print("✅ Spiral ascent complete!")
        
        # Spiral back down
        print("🌀 Spiral descent...")
        for turn in range(turns):
            print(f"   → Descent turn {turn+1}/{turns}")
            for step in range(8):
                self.controller.tello.move_down(height_per_turn // 8)
                self.controller.tello.rotate_counter_clockwise(degrees_per_step)
                safe_delay(1)
        
        print("✅ Spiral descent complete!")

def advanced_flight_demo():
    """Main demo function with pattern selection."""
    controller = TelloController()
    
    print("=== Advanced Flight Patterns Demo ===")
    
    # Connect to drone
    print("Connecting to Tello...")
    if not controller.connect():
        print("❌ Failed to connect to Tello.")
        return False
    
    try:
        # Check battery level (need more for advanced patterns)
        battery = controller.tello.get_battery()
        print(f"✅ Connected! Battery: {battery}%")
        
        if battery < 50:
            print("⚠️  Advanced patterns require at least 50% battery for safety.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False
        
        # Take off and gain altitude
        print("🚁 Taking off...")
        controller.takeoff()
        safe_delay(3)
        
        print("📈 Gaining altitude for safety...")
        controller.tello.move_up(50)
        safe_delay(2)
        
        # Pattern selection
        patterns = FlightPatterns(controller)
        
        print("\n🎯 Select a flight pattern:")
        print("1. Square Pattern")
        print("2. Triangle Pattern") 
        print("3. Figure-8 Pattern")
        print("4. Spiral Ascent/Descent")
        print("5. All Patterns (Demo)")
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            patterns.square_pattern(60)
        elif choice == '2':
            patterns.triangle_pattern(70)
        elif choice == '3':
            patterns.figure_eight(80)
        elif choice == '4':
            patterns.spiral_ascent(80, 2)
        elif choice == '5':
            print("🎪 Running full demo (all patterns)...")
            patterns.square_pattern(50)
            safe_delay(3)
            patterns.triangle_pattern(50)
            safe_delay(3)
            patterns.figure_eight(60)
        else:
            print("Invalid choice - performing square pattern")
            patterns.square_pattern(60)
        
        # Return to center and land
        print("🎯 Returning to landing position...")
        try:
            controller.tello.go_xyz_speed(0, 0, 0, 30)
            safe_delay(3)
        except:
            print("   Go-to-coordinate failed, landing from current position")
        
        print("🛬 Landing...")
        controller.land()
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern error: {e}")
        print("🚨 Emergency landing...")
        controller.land()
        return False
    
    finally:
        controller.disconnect()
        print("✅ Advanced flight demo complete!")

if __name__ == "__main__":
    print("DJI Tello Advanced Flight Patterns")
    print("\n⚠️  SAFETY WARNING:")
    print("- Ensure you have at least 3x3 meters of open space")
    print("- Remove any obstacles from flight area")
    print("- Have manual control ready")
    print("- Monitor battery levels")
    
    response = input("\nReady for advanced flight demo? (y/n): ")
    
    if response.lower() == 'y':
        success = advanced_flight_demo()
        
        if success:
            print("\n🎉 Advanced patterns completed successfully!")
        else:
            print("\n⚠️  Demo encountered issues. Check environment and try again.")
    else:
>>>>>>> dea707e300b8a0d0602dd0c7554e56810d0958fe
        print("Demo cancelled. Fly safely!")