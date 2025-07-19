# MSPKit SDK Examples

This directory contains comprehensive examples demonstrating all aspects of the MSPKit SDK. Each example is self-contained and includes detailed comments and safety considerations.

## 🚀 Quick Start Examples

### 1. Basic Telemetry (`basic_telemetry.py`)
**Perfect for beginners** - Shows how to connect and read real-time telemetry data.

```bash
python examples/basic_telemetry.py
```

**Features:**
- Simple connection setup
- Real-time attitude, GPS, and battery monitoring
- Error handling and troubleshooting tips
- 10Hz telemetry display

### 2. Complete Demo (`complete_demo.py`) 
**Comprehensive showcase** - Demonstrates all major SDK capabilities in one script.

```bash
python examples/complete_demo.py
```

**Features:**
- Interactive menu system
- All module demonstrations
- Complete workflow example
- Safety-first approach

## 🎮 Flight Control Examples

### 3. Flight Control (`flight_control.py`)
**⚠️ SAFETY CRITICAL** - Demonstrates safe flight control operations.

```bash
python examples/flight_control.py
```

**Features:**
- Pre-flight safety checks
- Safe arming/disarming procedures
- Controlled hover test
- Emergency stop procedures
- RC override demonstrations

**Safety Requirements:**
- Remove propellers before testing
- Secure aircraft during tests
- Have emergency stop ready
- Only use in safe environment

## 🗺️ Mission Planning Examples

### 4. Mission Planning (`mission_planning.py`)
**iNav only** - Advanced waypoint mission planning and management.

```bash
python examples/mission_planning.py
```

**Features:**
- Simple waypoint missions
- Automated survey patterns
- Search and rescue patterns
- Mission validation and simulation
- Real-time mission monitoring
- File-based mission save/load

**Mission Types:**
- **Simple Waypoint**: Basic rectangular flight pattern
- **Survey Mission**: Automated mapping with parallel lines
- **Search Pattern**: Expanding spiral for search operations

## 🔧 Configuration & Calibration

### 5. Sensor Calibration (`sensor_calibration.py`)
Essential for flight performance - Comprehensive sensor calibration procedures.

```bash
python examples/sensor_calibration.py
```

**Features:**
- Accelerometer 6-point calibration
- Magnetometer compass calibration
- Gyroscope zero-offset calibration
- Sensor health monitoring
- Automatic verification
- Full calibration sequence

### 6. Configuration Backup (`configuration_backup.py`)
Configuration management and tuning tools.

```bash
python examples/configuration_backup.py
```

**Features:**
- Complete configuration backup/restore
- Interactive PID tuning
- Feature toggle management
- Safe parameter modification
- Configuration validation

## 📊 Visualization & Monitoring

### 7. Real-time Visualization (`real_time_visualization.py`)
**Requires matplotlib** - Live data visualization and monitoring.

```bash
pip install matplotlib folium numpy
python examples/real_time_visualization.py
```

**Features:**
- Real-time attitude graphs
- Artificial horizon display
- Battery monitoring gauges
- GPS track mapping
- Multi-threaded data collection

### 8. Advanced Mission Planning (`advanced_mission_planning.py`)
**iNav only** - Complex mission scenarios with validation.

```bash
python examples/advanced_mission_planning.py
```

**Features:**
- Search and rescue missions
- Mission simulation and validation
- Battery consumption estimation
- Terrain consideration
- Emergency procedures

## 📋 Usage Guidelines

### Prerequisites

1. **Hardware Requirements:**
   - iNav or Betaflight flight controller
   - USB connection to computer
   - Stable power supply

2. **Software Requirements:**
   ```bash
   pip install mspkit
   # For visualization examples:
   pip install matplotlib folium numpy
   ```

### Safety First! ⚠️

**Before running any examples:**

1. **Remove propellers** - Essential for any motor/control testing
2. **Secure aircraft** - Prevent movement during calibration
3. **Check connections** - Ensure stable USB/serial connection
4. **Read documentation** - Understand each example before running
5. **Have emergency stop** - Know how to quickly disconnect power

### Common Configuration

Most examples use these default settings:
```python
SERIAL_PORT = '/dev/ttyUSB0'  # Linux/macOS
# SERIAL_PORT = 'COM3'        # Windows
FC_TYPE = FlightController.INAV  # or BETAFLIGHT
```

**Port Detection:**
- **Linux**: `/dev/ttyUSB0`, `/dev/ttyACM0`
- **macOS**: `/dev/tty.usbserial-*`, `/dev/tty.usbmodem*`  
- **Windows**: `COM3`, `COM4`, etc.

### Example Progression

**Recommended learning order:**

1. **Start Here**: `basic_telemetry.py` - Learn connections and data reading
2. **Explore**: `complete_demo.py` - See all capabilities overview
3. **Configure**: `sensor_calibration.py` - Essential for flight performance
4. **Plan**: `mission_planning.py` - Create autonomous missions (iNav)
5. **Visualize**: `real_time_visualization.py` - Monitor and analyze
6. **Control**: `flight_control.py` - Advanced control (with extreme caution)

### Troubleshooting

**Connection Issues:**
```bash
# Check available ports
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"

# Test basic connection
python -c "
import mspkit
conn = mspkit.connect('/dev/ttyUSB0')  # Adjust port
print('✅ Connected successfully!')
"
```

**Common Problems:**
- **Permission denied**: `sudo chmod 666 /dev/ttyUSB0` (Linux)
- **Port in use**: Close other applications (Mission Planner, etc.)
- **No response**: Check baud rate, try different USB cable
- **Import errors**: `pip install mspkit` or check Python path

### Example Modifications

**Change serial port:**
```python
SERIAL_PORT = '/dev/ttyACM0'  # Your specific port
```

**Change flight controller type:**
```python
FC_TYPE = FlightController.BETAFLIGHT  # or INAV
```

**Adjust telemetry rate:**
```python
time.sleep(0.1)  # 10Hz
time.sleep(0.05)  # 20Hz
```

## 📚 Additional Resources

- **Documentation**: [GitHub Wiki](https://github.com/ShafiqSadat/mspkit/wiki)
- **API Reference**: See docstrings in source code
- **Issues**: [GitHub Issues](https://github.com/ShafiqSadat/mspkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ShafiqSadat/mspkit/discussions)

## 🤝 Contributing Examples

Have a great example? We'd love to include it!

1. Follow existing code style and safety practices
2. Include comprehensive comments and error handling
3. Add safety warnings for any control operations
4. Test thoroughly before submitting
5. Update this README with your example

**Example template structure:**
```python
#!/usr/bin/env python3
"""
Example Title

Brief description of what this example demonstrates.
Include any safety warnings or special requirements.
"""

import logging
from mspkit import connect, FlightController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main example function"""
    # Your example code here
    pass

if __name__ == "__main__":
    main()
```

---

**Remember: Safety first, test carefully, and have fun exploring the capabilities of MSPKit! 🚁**
