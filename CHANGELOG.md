# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-07-19

### Added
- Initial public release of MSPKit SDK
- Complete MSP v1 and v2 protocol support
- DroneKit-style API for iNav and Betaflight flight controllers
- Comprehensive telemetry data access (attitude, GPS, sensors, battery)
- Safe flight control with input validation and safety checks
- Advanced mission planning and waypoint management (iNav)
- Complete configuration management with backup/restore
- Sensor calibration and health monitoring
- Command-line interface (CLI) tools
- Extensive examples and documentation
- Support for Python 3.7-3.11

### Features
- **Multi-FC Support**: iNav and Betaflight compatibility
- **Safety First**: Built-in safety checks and error handling
- **Real-time Telemetry**: Comprehensive flight data access
- **Flight Control**: Intuitive control interface
- **Mission Planning**: Advanced waypoint missions (iNav only)
- **Configuration**: Complete FC configuration management
- **Sensor Management**: Calibration and health monitoring
- **CLI Tools**: Command-line utilities for common tasks

### Technical Details
- MSP v1 and v2 protocol implementations
- Automatic protocol version detection
- Thread-safe connection management
- Comprehensive error handling and recovery
- Extensive logging for debugging
- Type hints and documentation
- Unit tests and CI/CD pipeline

### Examples Included
- Basic telemetry reading
- Flight control demonstrations
- Mission planning and upload
- Sensor calibration procedures
- Configuration backup and restore
- Real-time monitoring applications

## [Unreleased]

### Planned
- Add support for more flight controller variants
- Implement OSD configuration
- Add blackbox data analysis tools
- Enhanced mission planning features
- Real-time plotting and visualization
- Mobile app connectivity
- More comprehensive test coverage
