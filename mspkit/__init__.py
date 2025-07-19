"""
MSPKit SDK - A comprehensive Python SDK for iNav and Betaflight flight controllers

This SDK provides a DroneKit-style interface for communicating with iNav and Betaflight
flight controllers using the MSP (MultiWii Serial Protocol) v1 and v2.

Key Features:
- MSP v1 and v2 support
- iNav and Betaflight compatibility
- Comprehensive telemetry data
- Safe flight control with validation
- Mission planning and waypoint management
- Sensor calibration and monitoring
- Configuration management

Basic Usage:
    from mspkit import ConnectionManager, Telemetry, Control
    
    # Connect to flight controller
    conn = ConnectionManager('/dev/ttyUSB0', fc_type=FlightController.INAV)
    
    # Get telemetry
    telem = Telemetry(conn)
    attitude = telem.get_attitude()
    
    # Control aircraft
    control = Control(conn)
    control.arm()
    control.set_throttle(20)  # 20% throttle
"""

# Core connection and protocol
from .core import ConnectionManager, INavConnection, MSPException, FlightController

# Main modules
from .telemetry import Telemetry
from .control import Control  
from .config import Config
from .mission import Mission, Waypoint
from .sensors import Sensors

# Constants and enums
from .msp_constants import (
    MSPCommands, MSPv2Commands, FlightModes, SensorStatus, 
    GPSFixType, NavState, FailsafePhase, RC_CHANNELS, PWM_VALUES
)

# Version info
__version__ = '0.2.0'
__author__ = 'MSPKit Contributors'
__license__ = 'MIT'

# Convenience imports for backward compatibility
INavConnection = ConnectionManager  # Alias for backward compatibility

# Quick start helper function
def connect(port: str, baudrate: int = 115200, fc_type: FlightController = FlightController.INAV, 
           timeout: float = 2.0) -> ConnectionManager:
    """
    Quick connect helper function
    
    Args:
        port: Serial port (e.g., '/dev/ttyUSB0' or 'COM3')
        baudrate: Baud rate (default: 115200)
        fc_type: Flight controller type (default: INAV)
        timeout: Connection timeout in seconds (default: 2.0)
    
    Returns:
        ConnectionManager instance
    
    Example:
        conn = mspkit.connect('/dev/ttyUSB0', fc_type=FlightController.BETAFLIGHT)
    """
    return ConnectionManager(port, baudrate, timeout, fc_type)

def get_flight_data(conn: ConnectionManager) -> dict:
    """
    Get comprehensive flight data in one call
    
    Args:
        conn: Connection manager instance
        
    Returns:
        Dictionary containing all available telemetry data
    """
    telem = Telemetry(conn)
    return telem.get_all_telemetry()

# Module-level exports
__all__ = [
    # Core classes
    'ConnectionManager', 'INavConnection', 'MSPException', 'FlightController',
    
    # Main modules
    'Telemetry', 'Control', 'Config', 'Mission', 'Waypoint', 'Sensors',
    
    # Constants
    'MSPCommands', 'MSPv2Commands', 'FlightModes', 'SensorStatus',
    'GPSFixType', 'NavState', 'FailsafePhase', 'RC_CHANNELS', 'PWM_VALUES',
    
    # Helper functions
    'connect', 'get_flight_data',
    
    # Version info
    '__version__', '__author__', '__license__'
]
