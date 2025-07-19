# MSPKit SDK

A comprehensive Python SDK for iNav and Betaflight flight controllers, providing a DroneKit-style interface using the MSP (MultiWii Serial Protocol) v1 and v2.

## Features

- **🚁 Multi-FC Support**: Works with both iNav and Betaflight flight controllers
- **📡 MSP v1 & v2**: Full support for both MSP protocol versions with automatic detection
- **🛡️ Safety First**: Built-in safety checks, input validation, and error handling
- **📊 Comprehensive Telemetry**: Real-time access to attitude, GPS, sensors, and flight status
- **🎮 Flight Control**: Safe and intuitive flight control with multiple modes
- **🗺️ Mission Planning**: Advanced waypoint mission planning and management (iNav)
- **⚙️ Configuration**: Complete flight controller configuration management
- **🔧 Sensor Management**: Sensor calibration, testing, and health monitoring
- **📝 Extensive Logging**: Detailed logging for debugging and monitoring

## Installation

```bash
pip install mspkit
```

### CLI Tools
After installation, you can use the command-line interface:

```bash
# Get flight controller info
mspkit info -p /dev/ttyUSB0 -t INAV

# Stream telemetry data
mspkit telemetry -p /dev/ttyUSB0

# Upload mission from file
mspkit mission-upload mission.json -p /dev/ttyUSB0

# Download mission to file  
mspkit mission-download current_mission.json -p /dev/ttyUSB0

# Backup configuration
mspkit config-backup backup.json -p /dev/ttyUSB0
```

### Development Installation

```bash
git clone https://github.com/ShafiqSadat/mspkit
cd mspkit
pip install -e .[dev]
```

## Quick Start

### Basic Connection and Telemetry

```python
import mspkit
from mspkit import FlightController

# Connect to flight controller
conn = mspkit.connect('/dev/ttyUSB0', fc_type=FlightController.INAV)

# Get telemetry data
telem = mspkit.Telemetry(conn)

# Read attitude
attitude = telem.get_attitude()
print(f"Roll: {attitude['roll']:.1f}°, Pitch: {attitude['pitch']:.1f}°, Yaw: {attitude['yaw']:.1f}°")

# Read GPS
gps = telem.get_gps()
if gps['fix_type'] != 'NO_FIX':
    print(f"Position: {gps['latitude']:.6f}, {gps['longitude']:.6f}, Alt: {gps['altitude']:.1f}m")

# Get comprehensive flight data
flight_data = mspkit.get_flight_data(conn)
print(f"Armed: {flight_data['status']['armed']}")
```

### Flight Control

```python
from mspkit import Control

control = Control(conn)

# Enable safety checks (recommended)
control.enable_safety(True)

# Arm the aircraft (with safety checks)
if control.arm():
    print("Aircraft armed successfully")
    
    # Set flight mode
    control.enable_angle_mode()
    
    # Gentle takeoff
    control.set_throttle(30)  # 30% throttle
    
    # Set attitude (roll, pitch, yaw in percentage, -100 to 100)
    control.set_attitude(roll_percent=10, pitch_percent=5, yaw_percent=0)
    
    # Land
    control.set_throttle(0)
    control.disarm()
```

### Mission Planning (iNav)

```python
from mspkit import Mission

mission = Mission(conn)

# Create a simple mission
waypoints = [
    (47.6062, -122.3321, 50),  # Seattle coordinates, 50m altitude
    (47.6082, -122.3341, 60),
    (47.6102, -122.3361, 50),
]

if mission.create_simple_mission(waypoints, speed=500):  # 5 m/s
    print(f"Mission created with {mission.get_waypoint_count()} waypoints")
    
    # Upload to flight controller
    if mission.upload_mission():
        print("Mission uploaded successfully")
        
        # Save to file
        mission.save_mission_to_file("my_mission.json")
```

### Sensor Calibration

```python
from mspkit import Sensors

sensors = Sensors(conn)

# Run sensor health check
test_results = sensors.run_sensor_test()
print(f"Sensor test: {test_results['overall_status']}")

# Calibrate sensors
print("Starting sensor calibration...")
print("1. Keep aircraft level and stationary for gyro/accel calibration")
input("Press Enter when ready...")

if sensors.calibrate_all_sensors(include_mag=True):
    print("All sensors calibrated successfully!")
else:
    print("Some sensors failed calibration")
```

### Configuration Management

```python
from mspkit import Config

config = Config(conn)

# Backup current settings
backup = config.backup_settings()
if backup:
    print("Settings backed up successfully")

# Modify PID values
new_pids = {
    'ROLL': {'P': 40, 'I': 30, 'D': 23},
    'PITCH': {'P': 40, 'I': 30, 'D': 23}
}

if config.set_pid_values(new_pids):
    print("PID values updated")
    
    # Save to EEPROM
    config.save_settings()
```

## Protocol Support

### MSP Commands Supported

The SDK supports 100+ MSP commands including:

- **Status & Info**: API version, FC variant, board info, build info
- **Telemetry**: Attitude, GPS, IMU, altitude, battery, RC channels
- **Configuration**: PID tuning, RC tuning, features, misc settings
- **Control**: RC override, motor control, servo control
- **Navigation**: Waypoints, navigation status (iNav)
- **Calibration**: Accelerometer, magnetometer, gyroscope
- **Advanced**: Blackbox config, OSD settings, VTX control

### Flight Controller Compatibility

| Feature | iNav | Betaflight | Cleanflight |
|---------|------|------------|-------------|
| Basic Telemetry | ✅ | ✅ | ✅ |
| Flight Control | ✅ | ✅ | ✅ |
| Configuration | ✅ | ✅ | ✅ |
| Mission Planning | ✅ | ❌ | ❌ |
| Navigation Modes | ✅ | ❌ | ❌ |
| MSP v2 | ✅ | ✅ | ❌ |

## Safety Features

- **Input Validation**: All control inputs are validated and clamped to safe ranges
- **Arming Checks**: Prevents arming with high throttle or unsafe conditions
- **Connection Monitoring**: Automatic detection of connection loss
- **Emergency Stop**: Immediate throttle cut and disarm functionality
- **Timeout Handling**: All MSP commands have configurable timeouts
- **Error Recovery**: Graceful handling of communication errors

## Examples

The `examples/` directory contains comprehensive examples:

- `basic_telemetry.py` - Reading telemetry data
- `flight_control.py` - Basic flight control
- `mission_planning.py` - Creating and uploading missions
- `sensor_calibration.py` - Sensor calibration procedures
- `configuration_backup.py` - Backing up and restoring settings
- `live_monitoring.py` - Real-time telemetry monitoring

## API Reference

### Core Classes

- **ConnectionManager**: Main connection class with MSP v1/v2 support
- **Telemetry**: Comprehensive telemetry data access
- **Control**: Safe flight control with validation
- **Mission**: Mission planning and waypoint management
- **Config**: Configuration management and backup/restore
- **Sensors**: Sensor calibration and health monitoring

### Constants and Enums

- **FlightController**: Supported flight controller types
- **MSPCommands**: All supported MSP command codes
- **FlightModes**: Flight mode bit definitions
- **SensorStatus**: Sensor status flags
- **GPSFixType**: GPS fix type definitions

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests.

### Development Setup

```bash
# Clone repository
git clone https://github.com/ShafiqSadat/mspkit
cd mspkit

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black mspkit/
isort mspkit/

# Type checking
mypy mspkit/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **iNav Project**: For the excellent flight controller firmware
- **Betaflight Project**: For the robust flight controller platform  
- **DroneKit**: For inspiration on the API design
- **MSP Protocol**: MultiWii Serial Protocol specification

## Support

- **Documentation**: [Wiki](https://github.com/ShafiqSadat/mspkit/wiki)
- **Issues**: [GitHub Issues](https://github.com/ShafiqSadat/mspkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ShafiqSadat/mspkit/discussions)

## Disclaimer

This software is for educational and experimental purposes. Always follow local regulations and safety guidelines when operating unmanned aircraft. The developers are not responsible for any damage or accidents caused by the use of this software.
