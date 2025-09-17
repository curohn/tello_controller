# DJI Tello SDK Project

A Python project for programming and controlling DJI Tello drones using the djitellopy SDK.

## Features

- **Basic Flight Control**: Takeoff, landing, movement in all directions
- **Camera Streaming**: Live video feed with photo capture capabilities
- **Advanced Maneuvers**: Complex flight patterns, flips, and autonomous navigation
- **Safety Features**: Battery monitoring, emergency stop, error handling
- **Computer Vision**: OpenCV integration for image processing

## Project Structure

```
dji_tello/
├── src/
│   ├── tello_controller.py    # Main drone control class
│   └── utils.py               # Utility functions
├── examples/
│   ├── basic_flight.py        # Simple takeoff, movement, and landing
│   ├── camera_demo.py         # Video streaming and photo capture
│   └── advanced_flight.py     # Complex patterns and maneuvers
├── tests/
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Prerequisites

- DJI Tello drone
- Python 3.7 or higher
- WiFi connection to Tello

## Installation

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Connect to Tello WiFi**:
   - Turn on your Tello drone
   - Connect your computer to the Tello WiFi network (usually named "TELLO-XXXXXX")

## Quick Start

### Basic Flight
```bash
python examples/basic_flight.py
```
This demonstrates:
- Connection to drone
- Battery check
- Takeoff and landing
- Basic movements (forward, back, rotate)

### Camera Demo
```bash
python examples/camera_demo.py
```
Features:
- Live video stream
- Photo capture (press 's')
- In-flight takeoff/landing (press 't'/'l')
- Quit with 'q'

### Advanced Flight
```bash
python examples/advanced_flight.py
```
Includes:
- Square and circular flight patterns
- Flip demonstrations
- Coordinated movements

## Safety Guidelines

⚠️ **Important Safety Notes:**
- Always fly in open areas away from people and obstacles
- Keep spare batteries charged
- Monitor battery levels (land when below 20%)
- Understand local drone regulations
- Have manual control ready for emergencies

## API Usage

### Basic Controller Usage

```python
from src.tello_controller import TelloController

# Initialize and connect
controller = TelloController()
controller.connect()

# Basic flight
controller.takeoff()
controller.tello.move_forward(50)  # Move 50cm forward
controller.land()

# Cleanup
controller.disconnect()
```

### Available Commands

**Movement Commands:**
- `move_forward(distance)`, `move_back(distance)`
- `move_left(distance)`, `move_right(distance)`
- `move_up(distance)`, `move_down(distance)`
- `rotate_clockwise(degrees)`, `rotate_counter_clockwise(degrees)`

**Advanced Commands:**
- `flip(direction)` - directions: 'l', 'r', 'f', 'b'
- `go_xyz_speed(x, y, z, speed)` - Move to coordinates
- `curve_xyz_speed(...)` - Curved flight paths

**Camera Commands:**
- `streamon()`, `streamoff()` - Control video stream
- `get_frame_read()` - Get frame reader object

**Status Commands:**
- `get_battery()` - Battery percentage
- `get_height()` - Current height in cm
- `get_temperature()` - Internal temperature
- `get_speed_x/y/z()` - Current speeds

## Troubleshooting

**Connection Issues:**
- Ensure Tello is powered on and in WiFi mode
- Check WiFi connection to Tello network
- Try restarting both drone and application

**Import Errors:**
- Install dependencies: `pip install -r requirements.txt`
- Check Python version (3.7+ required)

**Flight Issues:**
- Check battery level (minimum 20% recommended)
- Ensure sufficient space for maneuvers
- Calibrate drone if drifting occurs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is open source. Please follow local drone regulations and use responsibly.

## Resources

- [DJI Tello Official Documentation](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [djitellopy GitHub Repository](https://github.com/damiafuentes/DJITelloPy)
- [OpenCV Documentation](https://docs.opencv.org/)

---

**Happy Flying! 🚁**