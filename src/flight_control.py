<<<<<<< HEAD
#!/usr/bin/env python3
"""
General flight controller for DJI Tello drone.
Combines camera streaming with interactive flight commands.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import cv2
import time
import threading
from tello_controller import TelloController
from utils import safe_delay, check_battery_level, emergency_stop

class InteractiveTelloController:
    """Interactive controller with camera and command input."""
    
    def __init__(self):
        self.controller = TelloController()
        self.flying = False
        self.streaming = False
        self.running = True
        self.frame = None
        self.connected = False
        self.last_height = 0
        self.connection_lost_count = 0
        self.monitoring = False
        
    def start_video_stream(self):
        """Start video streaming in a separate thread."""
        try:
            print("Starting video stream...")
            self.controller.tello.streamon()
            time.sleep(2)
            self.streaming = True
            
            frame_reader = self.controller.tello.get_frame_read()
            
            while self.streaming and self.running:
                try:
                    current_frame = frame_reader.frame
                    if current_frame is not None:
                        self.frame = current_frame.copy()
                        
                        # Add status overlay with enhanced sensor data
                        try:
                            battery = self.controller.tello.get_battery()
                            height = self.controller.tello.get_height()
                            distance_tof = self.controller.tello.get_distance_tof()
                            
                            # Main status line
                            status_text = f"Flying: {self.flying} | Battery: {battery}%"
                            
                            # Height and ToF sensor data
                            height_text = f"Height: {height}cm | ToF Distance: {distance_tof}cm"
                            
                            # Additional flight info
                            try:
                                pitch = self.controller.tello.get_pitch()
                                roll = self.controller.tello.get_roll()
                                attitude_text = f"Pitch: {pitch:.1f}° | Roll: {roll:.1f}°"
                            except:
                                attitude_text = "Attitude: N/A"
                            
                        except Exception as e:
                            # Fallback if sensor readings fail
                            status_text = f"Flying: {self.flying} | Battery: N/A"
                            height_text = f"Height: N/A | ToF Distance: N/A"
                            attitude_text = "Sensors: Error"
                        
                        # Draw overlay with better formatting
                        cv2.putText(self.frame, status_text, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(self.frame, height_text, (10, 55), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(self.frame, attitude_text, (10, 80), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # Add ToF distance warning if too close to ground
                        try:
                            if distance_tof < 50:  # Warning if less than 50cm from ground
                                warning_text = "⚠️ LOW ALTITUDE WARNING!"
                                cv2.putText(self.frame, warning_text, (10, 110), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)  # Red text
                        except:
                            pass
                        
                        # Display frame
                        cv2.imshow('Tello Camera Feed', self.frame)
                        
                    # Non-blocking key check
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.running = False
                        break
                        
                except Exception as e:
                    print(f"Video stream error: {e}")
                    break
                    
        except Exception as e:
            print(f"Failed to start video stream: {e}")
            self.streaming = False
    
    def stop_video_stream(self):
        """Stop video streaming."""
        if self.streaming:
            self.streaming = False
            self.controller.tello.streamoff()
            cv2.destroyAllWindows()
            print("Video stream stopped.")
    
    def check_connection(self):
        """Check if drone is still connected and responsive."""
        try:
            # Try to get battery - this is a simple command to test connection
            battery = self.controller.tello.get_battery()
            if battery > 0:
                self.connected = True
                self.connection_lost_count = 0
                return True
        except Exception:
            pass
        
        self.connection_lost_count += 1
        if self.connection_lost_count > 3:
            self.connected = False
        return False
    
    def check_flight_state(self):
        """Check if drone is actually flying by checking height."""
        try:
            height = self.controller.tello.get_height()
            previous_height = self.last_height
            self.last_height = height
            
            # If height is very low (< 10cm) and we think we're flying, we probably crashed
            if self.flying and height < 10:
                print(f"\n⚠️  CRASH DETECTED! Height: {height}cm - Drone has landed!")
                print("   Updating flight state to: LANDED")
                self.flying = False
                
                # Immediate user notification
                print("\n🔄 You can now:")
                print("   - Type 'takeoff' to fly again")
                print("   - Type 'status' to check drone condition")
                print("   - Type 'reconnect' if connection seems lost")
                return False
            
            # If height is reasonable (> 30cm) and we think we're not flying, maybe we are
            elif not self.flying and height > 30:
                print(f"\n⚠️  UNEXPECTED FLIGHT! Height: {height}cm - Drone is airborne!")
                print("   Updating flight state to: FLYING")
                self.flying = True
                return True
            
            # Check for significant height changes that might indicate issues
            elif self.flying and previous_height > 0:
                height_change = abs(height - previous_height)
                if height_change > 50:  # Sudden height change > 50cm
                    print(f"⚠️  Sudden height change: {previous_height}cm → {height}cm")
                
            return self.flying
            
        except Exception as e:
            print(f"Could not check flight state: {e}")
            return self.flying
    
    def attempt_reconnection(self):
        """Attempt to reconnect to the drone."""
        print("🔄 Connection lost - attempting to reconnect...")
        
        try:
            # Disconnect and reconnect
            self.controller.disconnect()
            time.sleep(2)
            
            if self.controller.connect():
                print("✅ Reconnection successful!")
                self.connected = True
                self.connection_lost_count = 0
                
                # Check actual flight state after reconnection
                self.check_flight_state()
                return True
            else:
                print("❌ Reconnection failed")
                return False
                
        except Exception as e:
            print(f"Reconnection error: {e}")
            return False
    
    def monitor_connection_and_state(self):
        """Background monitoring of connection and flight state."""
        while self.monitoring and self.running:
            try:
                # Check connection every 2 seconds (faster than before)
                if not self.check_connection():
                    if not self.attempt_reconnection():
                        print("⚠️  Multiple reconnection attempts failed")
                        # Don't break - keep trying
                
                # Check flight state more frequently (every 1 second when flying)
                if self.flying:
                    self.check_flight_state()
                    time.sleep(1)  # Check more often when flying
                else:
                    self.check_flight_state()
                    time.sleep(2)  # Check less often when landed
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(2)  # Shorter retry time
    
    def start_monitoring(self):
        """Start background monitoring thread."""
        if not self.monitoring:
            self.monitoring = True
            monitor_thread = threading.Thread(target=self.monitor_connection_and_state)
            monitor_thread.daemon = True
            monitor_thread.start()
            print("📡 Connection and state monitoring started")
    
    def execute_command(self, command):
        """Execute a flight command with error handling."""
        command = command.lower().strip()
        parts = command.split()
        
        if not parts:
            return
            
        cmd = parts[0]
        
        # Check connection before executing commands
        if cmd not in ['help', '?', 'quit', 'exit', 'q', 'status', 'reconnect']:
            if not self.connected:
                print("❌ Not connected to drone! Attempting reconnection...")
                if not self.attempt_reconnection():
                    print("Cannot execute command - no connection")
                    return
        
        try:
            # Flight control commands
            if cmd == "takeoff":
                if not self.flying:
                    print("Taking off...")
                    self.controller.takeoff()
                    safe_delay(5)  # Wait for IMU stabilization
                    
                    # Verify takeoff was successful by checking height
                    if self.check_flight_state():
                        print("✅ Takeoff successful!")
                    else:
                        print("⚠️  Takeoff may have failed - check drone status")
                else:
                    print("Already flying!")
                    
            elif cmd == "land":
                if self.flying:
                    print("Landing...")
                    self.controller.land()
                    safe_delay(3)
                    
                    # Verify landing by checking height
                    if not self.check_flight_state():
                        print("✅ Landed successfully!")
                    else:
                        print("⚠️  Landing may have failed - drone still airborne")
                else:
                    print("Not flying!")
                    
            elif cmd == "emergency":
                print("🚨 EMERGENCY STOP!")
                emergency_stop(self.controller.tello)
                self.flying = False
                safe_delay(2)
                self.check_flight_state()  # Update actual state
                
            elif cmd == "reconnect":
                print("Manual reconnection requested...")
                self.attempt_reconnection()
                return
                
            # Movement commands (require distance parameter)
            elif cmd in ["forward", "back", "left", "right", "up", "down"]:
                if not self.flying:
                    print("Must takeoff first!")
                    return
                    
                distance = 50  # default
                if len(parts) > 1:
                    try:
                        distance = int(parts[1])
                        distance = max(20, min(distance, 500))  # Clamp between 20-500cm
                    except ValueError:
                        print("Invalid distance, using 50cm")
                
                print(f"Moving {cmd} {distance}cm...")
                self._try_movement(cmd, distance)
                
            # Rotation commands
            elif cmd in ["cw", "ccw", "rotate"]:
                if not self.flying:
                    print("Must takeoff first!")
                    return
                    
                degrees = 90  # default
                if len(parts) > 1:
                    try:
                        degrees = int(parts[1])
                        degrees = max(1, min(degrees, 360))  # Clamp between 1-360
                    except ValueError:
                        print("Invalid degrees, using 90")
                
                if cmd == "cw" or (cmd == "rotate" and len(parts) > 2 and parts[2] == "cw"):
                    print(f"Rotating clockwise {degrees} degrees...")
                    self.controller.tello.rotate_clockwise(degrees)
                else:
                    print(f"Rotating counter-clockwise {degrees} degrees...")
                    self.controller.tello.rotate_counter_clockwise(degrees)
                    
            # Flip commands
            elif cmd == "flip":
                if not self.flying:
                    print("Must takeoff first!")
                    return
                    
                direction = 'f'  # default forward
                if len(parts) > 1:
                    direction = parts[1].lower()
                    if direction not in ['f', 'b', 'l', 'r']:
                        print("Invalid flip direction. Use: f, b, l, r")
                        return
                
                directions = {'f': 'forward', 'b': 'backward', 'l': 'left', 'r': 'right'}
                print(f"Flipping {directions[direction]}...")
                self.controller.tello.flip(direction)
                
            # Status commands
            elif cmd == "status":
                print("\n=== Drone Status ===")
                try:
                    status = self.controller.get_status()
                    print(f"Battery: {status['battery']}%")
                    print(f"Height: {status['height']}cm")
                    print(f"Temperature: {status['temperature']}°F")
                    print(f"Speed: {status['speed']} cm/s")
                    print(f"Connected: {'Yes' if self.connected else 'No'}")
                    print(f"Flying (program): {'Yes' if self.flying else 'No'}")
                    print(f"Flying (actual): {'Yes' if status['height'] > 10 else 'No'}")
                    print("==================")
                except Exception as e:
                    print(f"Could not get full status: {e}")
                    print(f"Connected: {'Yes' if self.connected else 'No'}")
                    print(f"Flying (program): {'Yes' if self.flying else 'No'}")
                
            elif cmd == "battery":
                try:
                    battery = self.controller.tello.get_battery()
                    print(f"Battery: {battery}%")
                except Exception as e:
                    print(f"Could not get battery: {e}")
                
            # Photo command
            elif cmd == "photo":
                if self.frame is not None:
                    timestamp = int(time.time())
                    # Save photos to photos directory
                    photos_dir = os.path.join(os.path.dirname(__file__), '..', 'photos')
                    os.makedirs(photos_dir, exist_ok=True)  # Ensure directory exists
                    filename = os.path.join(photos_dir, f"tello_photo_{timestamp}.jpg")
                    cv2.imwrite(filename, self.frame)
                    print(f"Photo saved: {filename}")
                else:
                    print("No video frame available")
                    
            # Help command
            elif cmd in ["help", "?"]:
                self._show_help()
                
            # Quit command
            elif cmd in ["quit", "exit", "q"]:
                self.running = False
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
                
        except Exception as e:
            print(f"Command '{command}' failed: {e}")
            if "No valid imu" in str(e):
                print("IMU error detected. Try:")
                print("1. Type 'land' and restart drone")
                print("2. Use RC control mode")
                self._try_rc_movement()
    
    def _try_movement(self, direction, distance):
        """Try movement with fallback methods."""
        movement_map = {
            'forward': lambda d: self.controller.tello.move_forward(d),
            'back': lambda d: self.controller.tello.move_back(d),
            'left': lambda d: self.controller.tello.move_left(d),
            'right': lambda d: self.controller.tello.move_right(d),
            'up': lambda d: self.controller.tello.move_up(d),
            'down': lambda d: self.controller.tello.move_down(d)
        }
        
        try:
            # Try standard movement
            movement_map[direction](distance)
            print(f"Movement successful!")
        except Exception as e:
            if "No valid imu" in str(e):
                print("IMU error - trying RC control...")
                self._try_rc_movement_direction(direction, distance)
            else:
                raise e
    
    def _try_rc_movement_direction(self, direction, distance):
        """Try RC control for specific direction."""
        # Convert distance to speed and time
        speed = min(100, max(20, distance))  # Speed 20-100
        duration = distance / 50.0  # Approximate duration
        
        rc_map = {
            'forward': (0, speed, 0, 0),
            'back': (0, -speed, 0, 0),
            'left': (-speed, 0, 0, 0),
            'right': (speed, 0, 0, 0),
            'up': (0, 0, speed, 0),
            'down': (0, 0, -speed, 0)
        }
        
        if direction in rc_map:
            print(f"Using RC control for {direction}...")
            lr, fb, ud, yaw = rc_map[direction]
            self.controller.tello.send_rc_control(lr, fb, ud, yaw)
            time.sleep(duration)
            self.controller.tello.send_rc_control(0, 0, 0, 0)  # Stop
            print("RC movement completed!")
    
    def _try_rc_movement(self):
        """Suggest RC movement as fallback."""
        print("\nRC Control available - use these commands:")
        print("- rc forward/back/left/right/up/down [speed] [duration]")
        print("Example: 'rc forward 50 2' (speed 50, 2 seconds)")
    
    def _show_help(self):
        """Show available commands."""
        print("\n=== Available Commands ===")
        print("Flight Control:")
        print("  takeoff           - Take off")
        print("  land              - Land")
        print("  emergency         - Emergency stop")
        print("  reconnect         - Manual reconnection")
        print("\nMovement:")
        print("  forward [dist]    - Move forward (default 50cm)")
        print("  back [dist]       - Move backward")
        print("  left [dist]       - Move left")
        print("  right [dist]      - Move right")
        print("  up [dist]         - Move up")
        print("  down [dist]       - Move down")
        print("\nRotation:")
        print("  cw [degrees]      - Rotate clockwise (default 90°)")
        print("  ccw [degrees]     - Rotate counter-clockwise")
        print("\nTricks:")
        print("  flip [f/b/l/r]    - Flip (forward/back/left/right)")
        print("\nInfo:")
        print("  status            - Show detailed drone status")
        print("  battery           - Show battery level")
        print("  photo             - Take photo")
        print("\nGeneral:")
        print("  help/?            - Show this help")
        print("  quit/exit/q       - Quit program")
        print("  Press 'q' in video window to quit")
        print("\n🔄 Auto-features:")
        print("  • Auto-reconnection on connection loss")
        print("  • Crash detection via height monitoring")
        print("  • State synchronization with actual drone")
        print("========================\n")

def general_flight():
    """Main interactive flight function."""
    controller = InteractiveTelloController()
    
    print("=== DJI Tello General Flight Controller ===")
    print("Connecting to Tello...")
    
    if not controller.controller.connect():
        print("Failed to connect to Tello. Make sure drone is on and connected to WiFi.")
        return
    
    controller.connected = True  # Mark as connected
    
    try:
        # Check battery level
        battery = controller.controller.tello.get_battery()
        print(f"Connected! Battery: {battery}%")
        
        if battery < 20:
            print("Warning: Low battery! Consider charging before flight.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Start monitoring system
        controller.start_monitoring()
        
        # Start video stream in background thread
        video_thread = threading.Thread(target=controller.start_video_stream)
        video_thread.daemon = True
        video_thread.start()
        
        time.sleep(2)  # Let video start
        
        # Show help initially
        controller._show_help()
        
        # Main command loop
        print("Ready for commands! (Type 'help' for command list)")
        
        while controller.running:
            try:
                command = input("\nTello> ").strip()
                if command:
                    controller.execute_command(command)
                    
            except KeyboardInterrupt:
                print("\nKeyboard interrupt detected...")
                break
            except EOFError:
                print("\nInput ended...")
                break
        
        # Cleanup
        print("\nShutting down...")
        
        if controller.flying:
            print("Landing drone...")
            controller.controller.land()
        
        controller.stop_video_stream()
        
    except Exception as e:
        print(f"Flight error: {e}")
        if controller.flying:
            print("Emergency landing...")
            emergency_stop(controller.controller.tello)
    
    finally:
        controller.controller.disconnect()
        print("Flight session complete!")

if __name__ == "__main__":
=======
#!/usr/bin/env python3
"""
General flight controller for DJI Tello drone.
Combines camera streaming with interactive flight commands.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import cv2
import time
import threading
from tello_controller import TelloController
from utils import safe_delay, check_battery_level, emergency_stop

class InteractiveTelloController:
    """Interactive controller with camera and command input."""
    
    def __init__(self):
        self.controller = TelloController()
        self.flying = False
        self.streaming = False
        self.running = True
        self.frame = None
        self.connected = False
        self.last_height = 0
        self.connection_lost_count = 0
        self.monitoring = False
        
    def start_video_stream(self):
        """Start video streaming in a separate thread."""
        try:
            print("Starting video stream...")
            self.controller.tello.streamon()
            time.sleep(2)
            self.streaming = True
            
            frame_reader = self.controller.tello.get_frame_read()
            
            while self.streaming and self.running:
                try:
                    current_frame = frame_reader.frame
                    if current_frame is not None:
                        self.frame = current_frame.copy()
                        
                        # Add status overlay with enhanced sensor data
                        try:
                            battery = self.controller.tello.get_battery()
                            height = self.controller.tello.get_height()
                            distance_tof = self.controller.tello.get_distance_tof()
                            
                            # Main status line
                            status_text = f"Flying: {self.flying} | Battery: {battery}%"
                            
                            # Height and ToF sensor data
                            height_text = f"Height: {height}cm | ToF Distance: {distance_tof}cm"
                            
                            # Additional flight info
                            try:
                                pitch = self.controller.tello.get_pitch()
                                roll = self.controller.tello.get_roll()
                                attitude_text = f"Pitch: {pitch:.1f}° | Roll: {roll:.1f}°"
                            except:
                                attitude_text = "Attitude: N/A"
                            
                        except Exception as e:
                            # Fallback if sensor readings fail
                            status_text = f"Flying: {self.flying} | Battery: N/A"
                            height_text = f"Height: N/A | ToF Distance: N/A"
                            attitude_text = "Sensors: Error"
                        
                        # Draw overlay with better formatting
                        cv2.putText(self.frame, status_text, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(self.frame, height_text, (10, 55), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(self.frame, attitude_text, (10, 80), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # Add ToF distance warning if too close to ground
                        try:
                            if distance_tof < 50:  # Warning if less than 50cm from ground
                                warning_text = "⚠️ LOW ALTITUDE WARNING!"
                                cv2.putText(self.frame, warning_text, (10, 110), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)  # Red text
                        except:
                            pass
                        
                        # Display frame
                        cv2.imshow('Tello Camera Feed', self.frame)
                        
                    # Non-blocking key check
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.running = False
                        break
                        
                except Exception as e:
                    print(f"Video stream error: {e}")
                    break
                    
        except Exception as e:
            print(f"Failed to start video stream: {e}")
            self.streaming = False
    
    def stop_video_stream(self):
        """Stop video streaming."""
        if self.streaming:
            self.streaming = False
            self.controller.tello.streamoff()
            cv2.destroyAllWindows()
            print("Video stream stopped.")
    
    def check_connection(self):
        """Check if drone is still connected and responsive."""
        try:
            # Try to get battery - this is a simple command to test connection
            battery = self.controller.tello.get_battery()
            if battery > 0:
                self.connected = True
                self.connection_lost_count = 0
                return True
        except Exception:
            pass
        
        self.connection_lost_count += 1
        if self.connection_lost_count > 3:
            self.connected = False
        return False
    
    def check_flight_state(self):
        """Check if drone is actually flying by checking height."""
        try:
            height = self.controller.tello.get_height()
            previous_height = self.last_height
            self.last_height = height
            
            # If height is very low (< 10cm) and we think we're flying, we probably crashed
            if self.flying and height < 10:
                print(f"\n⚠️  CRASH DETECTED! Height: {height}cm - Drone has landed!")
                print("   Updating flight state to: LANDED")
                self.flying = False
                
                # Immediate user notification
                print("\n🔄 You can now:")
                print("   - Type 'takeoff' to fly again")
                print("   - Type 'status' to check drone condition")
                print("   - Type 'reconnect' if connection seems lost")
                return False
            
            # If height is reasonable (> 30cm) and we think we're not flying, maybe we are
            elif not self.flying and height > 30:
                print(f"\n⚠️  UNEXPECTED FLIGHT! Height: {height}cm - Drone is airborne!")
                print("   Updating flight state to: FLYING")
                self.flying = True
                return True
            
            # Check for significant height changes that might indicate issues
            elif self.flying and previous_height > 0:
                height_change = abs(height - previous_height)
                if height_change > 50:  # Sudden height change > 50cm
                    print(f"⚠️  Sudden height change: {previous_height}cm → {height}cm")
                
            return self.flying
            
        except Exception as e:
            print(f"Could not check flight state: {e}")
            return self.flying
    
    def attempt_reconnection(self):
        """Attempt to reconnect to the drone."""
        print("🔄 Connection lost - attempting to reconnect...")
        
        try:
            # Disconnect and reconnect
            self.controller.disconnect()
            time.sleep(2)
            
            if self.controller.connect():
                print("✅ Reconnection successful!")
                self.connected = True
                self.connection_lost_count = 0
                
                # Check actual flight state after reconnection
                self.check_flight_state()
                return True
            else:
                print("❌ Reconnection failed")
                return False
                
        except Exception as e:
            print(f"Reconnection error: {e}")
            return False
    
    def monitor_connection_and_state(self):
        """Background monitoring of connection and flight state."""
        while self.monitoring and self.running:
            try:
                # Check connection every 2 seconds (faster than before)
                if not self.check_connection():
                    if not self.attempt_reconnection():
                        print("⚠️  Multiple reconnection attempts failed")
                        # Don't break - keep trying
                
                # Check flight state more frequently (every 1 second when flying)
                if self.flying:
                    self.check_flight_state()
                    time.sleep(1)  # Check more often when flying
                else:
                    self.check_flight_state()
                    time.sleep(2)  # Check less often when landed
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(2)  # Shorter retry time
    
    def start_monitoring(self):
        """Start background monitoring thread."""
        if not self.monitoring:
            self.monitoring = True
            monitor_thread = threading.Thread(target=self.monitor_connection_and_state)
            monitor_thread.daemon = True
            monitor_thread.start()
            print("📡 Connection and state monitoring started")
    
    def execute_command(self, command):
        """Execute a flight command with error handling."""
        command = command.lower().strip()
        parts = command.split()
        
        if not parts:
            return
            
        cmd = parts[0]
        
        # Check connection before executing commands
        if cmd not in ['help', '?', 'quit', 'exit', 'q', 'status', 'reconnect']:
            if not self.connected:
                print("❌ Not connected to drone! Attempting reconnection...")
                if not self.attempt_reconnection():
                    print("Cannot execute command - no connection")
                    return
        
        try:
            # Flight control commands
            if cmd == "takeoff":
                if not self.flying:
                    print("Taking off...")
                    self.controller.takeoff()
                    safe_delay(5)  # Wait for IMU stabilization
                    
                    # Verify takeoff was successful by checking height
                    if self.check_flight_state():
                        print("✅ Takeoff successful!")
                    else:
                        print("⚠️  Takeoff may have failed - check drone status")
                else:
                    print("Already flying!")
                    
            elif cmd == "land":
                if self.flying:
                    print("Landing...")
                    self.controller.land()
                    safe_delay(3)
                    
                    # Verify landing by checking height
                    if not self.check_flight_state():
                        print("✅ Landed successfully!")
                    else:
                        print("⚠️  Landing may have failed - drone still airborne")
                else:
                    print("Not flying!")
                    
            elif cmd == "emergency":
                print("🚨 EMERGENCY STOP!")
                emergency_stop(self.controller.tello)
                self.flying = False
                safe_delay(2)
                self.check_flight_state()  # Update actual state
                
            elif cmd == "reconnect":
                print("Manual reconnection requested...")
                self.attempt_reconnection()
                return
                
            # Movement commands (require distance parameter)
            elif cmd in ["forward", "back", "left", "right", "up", "down"]:
                if not self.flying:
                    print("Must takeoff first!")
                    return
                    
                distance = 50  # default
                if len(parts) > 1:
                    try:
                        distance = int(parts[1])
                        distance = max(20, min(distance, 500))  # Clamp between 20-500cm
                    except ValueError:
                        print("Invalid distance, using 50cm")
                
                print(f"Moving {cmd} {distance}cm...")
                self._try_movement(cmd, distance)
                
            # Rotation commands
            elif cmd in ["cw", "ccw", "rotate"]:
                if not self.flying:
                    print("Must takeoff first!")
                    return
                    
                degrees = 90  # default
                if len(parts) > 1:
                    try:
                        degrees = int(parts[1])
                        degrees = max(1, min(degrees, 360))  # Clamp between 1-360
                    except ValueError:
                        print("Invalid degrees, using 90")
                
                if cmd == "cw" or (cmd == "rotate" and len(parts) > 2 and parts[2] == "cw"):
                    print(f"Rotating clockwise {degrees} degrees...")
                    self.controller.tello.rotate_clockwise(degrees)
                else:
                    print(f"Rotating counter-clockwise {degrees} degrees...")
                    self.controller.tello.rotate_counter_clockwise(degrees)
                    
            # Flip commands
            elif cmd == "flip":
                if not self.flying:
                    print("Must takeoff first!")
                    return
                    
                direction = 'f'  # default forward
                if len(parts) > 1:
                    direction = parts[1].lower()
                    if direction not in ['f', 'b', 'l', 'r']:
                        print("Invalid flip direction. Use: f, b, l, r")
                        return
                
                directions = {'f': 'forward', 'b': 'backward', 'l': 'left', 'r': 'right'}
                print(f"Flipping {directions[direction]}...")
                self.controller.tello.flip(direction)
                
            # Status commands
            elif cmd == "status":
                print("\n=== Drone Status ===")
                try:
                    status = self.controller.get_status()
                    print(f"Battery: {status['battery']}%")
                    print(f"Height: {status['height']}cm")
                    print(f"Temperature: {status['temperature']}°F")
                    print(f"Speed: {status['speed']} cm/s")
                    print(f"Connected: {'Yes' if self.connected else 'No'}")
                    print(f"Flying (program): {'Yes' if self.flying else 'No'}")
                    print(f"Flying (actual): {'Yes' if status['height'] > 10 else 'No'}")
                    print("==================")
                except Exception as e:
                    print(f"Could not get full status: {e}")
                    print(f"Connected: {'Yes' if self.connected else 'No'}")
                    print(f"Flying (program): {'Yes' if self.flying else 'No'}")
                
            elif cmd == "battery":
                try:
                    battery = self.controller.tello.get_battery()
                    print(f"Battery: {battery}%")
                except Exception as e:
                    print(f"Could not get battery: {e}")
                
            # Photo command
            elif cmd == "photo":
                if self.frame is not None:
                    timestamp = int(time.time())
                    # Save photos to photos directory
                    photos_dir = os.path.join(os.path.dirname(__file__), '..', 'photos')
                    os.makedirs(photos_dir, exist_ok=True)  # Ensure directory exists
                    filename = os.path.join(photos_dir, f"tello_photo_{timestamp}.jpg")
                    cv2.imwrite(filename, self.frame)
                    print(f"Photo saved: {filename}")
                else:
                    print("No video frame available")
                    
            # Help command
            elif cmd in ["help", "?"]:
                self._show_help()
                
            # Quit command
            elif cmd in ["quit", "exit", "q"]:
                self.running = False
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
                
        except Exception as e:
            print(f"Command '{command}' failed: {e}")
            if "No valid imu" in str(e):
                print("IMU error detected. Try:")
                print("1. Type 'land' and restart drone")
                print("2. Use RC control mode")
                self._try_rc_movement()
    
    def _try_movement(self, direction, distance):
        """Try movement with fallback methods."""
        movement_map = {
            'forward': lambda d: self.controller.tello.move_forward(d),
            'back': lambda d: self.controller.tello.move_back(d),
            'left': lambda d: self.controller.tello.move_left(d),
            'right': lambda d: self.controller.tello.move_right(d),
            'up': lambda d: self.controller.tello.move_up(d),
            'down': lambda d: self.controller.tello.move_down(d)
        }
        
        try:
            # Try standard movement
            movement_map[direction](distance)
            print(f"Movement successful!")
        except Exception as e:
            if "No valid imu" in str(e):
                print("IMU error - trying RC control...")
                self._try_rc_movement_direction(direction, distance)
            else:
                raise e
    
    def _try_rc_movement_direction(self, direction, distance):
        """Try RC control for specific direction."""
        # Convert distance to speed and time
        speed = min(100, max(20, distance))  # Speed 20-100
        duration = distance / 50.0  # Approximate duration
        
        rc_map = {
            'forward': (0, speed, 0, 0),
            'back': (0, -speed, 0, 0),
            'left': (-speed, 0, 0, 0),
            'right': (speed, 0, 0, 0),
            'up': (0, 0, speed, 0),
            'down': (0, 0, -speed, 0)
        }
        
        if direction in rc_map:
            print(f"Using RC control for {direction}...")
            lr, fb, ud, yaw = rc_map[direction]
            self.controller.tello.send_rc_control(lr, fb, ud, yaw)
            time.sleep(duration)
            self.controller.tello.send_rc_control(0, 0, 0, 0)  # Stop
            print("RC movement completed!")
    
    def _try_rc_movement(self):
        """Suggest RC movement as fallback."""
        print("\nRC Control available - use these commands:")
        print("- rc forward/back/left/right/up/down [speed] [duration]")
        print("Example: 'rc forward 50 2' (speed 50, 2 seconds)")
    
    def _show_help(self):
        """Show available commands."""
        print("\n=== Available Commands ===")
        print("Flight Control:")
        print("  takeoff           - Take off")
        print("  land              - Land")
        print("  emergency         - Emergency stop")
        print("  reconnect         - Manual reconnection")
        print("\nMovement:")
        print("  forward [dist]    - Move forward (default 50cm)")
        print("  back [dist]       - Move backward")
        print("  left [dist]       - Move left")
        print("  right [dist]      - Move right")
        print("  up [dist]         - Move up")
        print("  down [dist]       - Move down")
        print("\nRotation:")
        print("  cw [degrees]      - Rotate clockwise (default 90°)")
        print("  ccw [degrees]     - Rotate counter-clockwise")
        print("\nTricks:")
        print("  flip [f/b/l/r]    - Flip (forward/back/left/right)")
        print("\nInfo:")
        print("  status            - Show detailed drone status")
        print("  battery           - Show battery level")
        print("  photo             - Take photo")
        print("\nGeneral:")
        print("  help/?            - Show this help")
        print("  quit/exit/q       - Quit program")
        print("  Press 'q' in video window to quit")
        print("\n🔄 Auto-features:")
        print("  • Auto-reconnection on connection loss")
        print("  • Crash detection via height monitoring")
        print("  • State synchronization with actual drone")
        print("========================\n")

def general_flight():
    """Main interactive flight function."""
    controller = InteractiveTelloController()
    
    print("=== DJI Tello General Flight Controller ===")
    print("Connecting to Tello...")
    
    if not controller.controller.connect():
        print("Failed to connect to Tello. Make sure drone is on and connected to WiFi.")
        return
    
    controller.connected = True  # Mark as connected
    
    try:
        # Check battery level
        battery = controller.controller.tello.get_battery()
        print(f"Connected! Battery: {battery}%")
        
        if battery < 20:
            print("Warning: Low battery! Consider charging before flight.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Start monitoring system
        controller.start_monitoring()
        
        # Start video stream in background thread
        video_thread = threading.Thread(target=controller.start_video_stream)
        video_thread.daemon = True
        video_thread.start()
        
        time.sleep(2)  # Let video start
        
        # Show help initially
        controller._show_help()
        
        # Main command loop
        print("Ready for commands! (Type 'help' for command list)")
        
        while controller.running:
            try:
                command = input("\nTello> ").strip()
                if command:
                    controller.execute_command(command)
                    
            except KeyboardInterrupt:
                print("\nKeyboard interrupt detected...")
                break
            except EOFError:
                print("\nInput ended...")
                break
        
        # Cleanup
        print("\nShutting down...")
        
        if controller.flying:
            print("Landing drone...")
            controller.controller.land()
        
        controller.stop_video_stream()
        
    except Exception as e:
        print(f"Flight error: {e}")
        if controller.flying:
            print("Emergency landing...")
            emergency_stop(controller.controller.tello)
    
    finally:
        controller.controller.disconnect()
        print("Flight session complete!")

if __name__ == "__main__":
>>>>>>> dea707e300b8a0d0602dd0c7554e56810d0958fe
    general_flight()