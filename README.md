# DJI Tello Controller

A professional Python SDK for controlling DJI Tello drones with advanced flight patterns, computer vision capabilities, and comprehensive safety features.

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🚁 Features

- **✈️ Advanced Flight Control**: Takeoff, landing, precise movement in all directions
- **📷 Real-time Camera Streaming**: Live video feed with photo capture capabilities  
- **🎯 Complex Flight Patterns**: Automated sequences, geometric patterns, and custom maneuvers
- **🛡️ Safety First**: Comprehensive battery monitoring, emergency protocols, and error handling
- **👁️ Computer Vision Ready**: OpenCV integration for image processing and autonomous navigation
- **📊 Flight Data**: Real-time telemetry and flight status monitoring

## 📁 Project Structure

```
tello_controller/
├── src/
│   ├── tello_controller.py    # Core drone control interface
│   ├── flight_control.py      # Advanced flight pattern implementations
│   └── utils.py              # Helper functions and utilities
├── examples/
│   ├── basic_flight_demo.py   # Simple takeoff, movement, and landing demo
│   └── advanced_patterns.py   # Complex flight patterns and maneuvers
├── photos/                    # Captured drone photos
├── tests/                     # Unit tests and test fixtures
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

## 🔧 Prerequisites

- DJI Tello or Tello EDU drone
- Python 3.8 or higher
- WiFi-enabled computer
- Well-ventilated, open flying area

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/curohn/tello_controller.git
   cd tello_controller
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Connect to Tello**:
   - Power on your Tello drone
   - Connect your computer to the Tello WiFi network (TELLO-XXXXXX)
   - Wait for solid connection light

### Basic Usage

Run the basic flight demonstration:
```bash
python examples/basic_flight_demo.py
```

Experience advanced flight patterns:
```bash
python examples/advanced_patterns.py
```

## 💻 API Reference

### Core Controller

```python
from src.tello_controller import TelloController

# Initialize controller
drone = TelloController()

# Connect and perform basic flight
if drone.connect():
    drone.takeoff()
    drone.move_forward(100)  # Move 100cm forward
    drone.rotate_clockwise(90)  # Turn 90 degrees
    drone.land()
    drone.disconnect()
```

### Advanced Flight Control

```python
from src.flight_control import FlightController

# Initialize advanced controller
controller = FlightController()

if controller.connect():
    # Execute predefined patterns
    controller.fly_square_pattern(100)  # 100cm square
    controller.fly_circle_pattern(50)   # 50cm radius circle
    controller.perform_flip_sequence()  # Multiple flips
    
    controller.disconnect()
```

### Available Commands

| Category | Command | Description |
|----------|---------|-------------|
| **Movement** | `move_forward(distance)` | Move forward by distance (cm) |
| | `move_back(distance)` | Move backward by distance (cm) |
| | `move_left(distance)` | Move left by distance (cm) |
| | `move_right(distance)` | Move right by distance (cm) |
| | `move_up(distance)` | Move up by distance (cm) |
| | `move_down(distance)` | Move down by distance (cm) |
| **Rotation** | `rotate_clockwise(degrees)` | Rotate clockwise |
| | `rotate_counter_clockwise(degrees)` | Rotate counter-clockwise |
| **Advanced** | `flip(direction)` | Perform flip ('l', 'r', 'f', 'b') |
| | `go_xyz_speed(x, y, z, speed)` | Move to coordinates with speed |
| **Camera** | `streamon()` | Enable video streaming |
| | `streamoff()` | Disable video streaming |
| | `take_picture()` | Capture and save photo |
| **Status** | `get_battery()` | Get battery percentage |
| | `get_height()` | Get current height (cm) |
| | `get_temperature()` | Get internal temperature |

## 🛡️ Safety Guidelines

> **⚠️ SAFETY FIRST**: Always prioritize safety when operating drones

- **🏞️ Environment**: Fly only in open areas away from people, buildings, and obstacles
- **🔋 Battery**: Monitor battery levels constantly; land when below 20%
- **📡 Connection**: Maintain strong WiFi connection; have manual override ready
- **🌤️ Weather**: Avoid flying in windy, rainy, or poor visibility conditions
- **📋 Regulations**: Understand and comply with local drone regulations
- **👥 Supervision**: Never leave drone unattended during operation

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configurations:
```env
TELLO_TIMEOUT=10
PHOTO_DIRECTORY=photos
LOG_LEVEL=INFO
```

### Safety Limits

Default safety parameters can be configured in `src/utils.py`:
- Minimum battery level: 20%
- Maximum flight height: 100m
- Connection timeout: 10 seconds

## 🐛 Troubleshooting

### Common Issues

**Connection Problems**
- ✅ Ensure Tello is powered and in WiFi mode
- ✅ Verify computer connection to Tello network
- ✅ Check for interference from other WiFi networks
- ✅ Restart drone and retry connection

**Flight Issues**
- ✅ Confirm battery level above 20%
- ✅ Calibrate drone on flat surface before flight
- ✅ Check for adequate flying space
- ✅ Verify no GPS interference (indoor flying)

**Import/Installation Issues**
- ✅ Confirm Python 3.8+ installation
- ✅ Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- ✅ Check virtual environment activation

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run with coverage:
```bash
python -m pytest tests/ --cov=src/
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/tello_controller.git
cd tello_controller

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DJI** for creating the Tello drone platform
- **[djitellopy](https://github.com/damiafuentes/DJITelloPy)** - Python SDK for Tello drones
- **OpenCV** - Computer vision capabilities
- **Community contributors** who have helped improve this project

## 📚 Resources

- [DJI Tello SDK 2.0 Documentation](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [djitellopy Documentation](https://djitellopy.readthedocs.io/)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [Drone Safety Guidelines](https://www.faa.gov/uas/recreational_fliers/)

---

<div align="center">

**Happy Flying! 🚁✨**

*Built with ❤️ for drone enthusiasts and developers*

[![GitHub stars](https://img.shields.io/github/stars/curohn/tello_controller.svg?style=social&label=Star)](https://github.com/curohn/tello_controller)
[![GitHub forks](https://img.shields.io/github/forks/curohn/tello_controller.svg?style=social&label=Fork)](https://github.com/curohn/tello_controller/fork)

</div>