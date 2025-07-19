#!/usr/bin/env python3
"""
MSPKit SDK - Comprehensive Demo

This example demonstrates the enhanced capabilities of the MSPKit SDK
including MSP v2 support, Betaflight compatibility, and safety features.
"""

import time
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from mspkit import (
        ConnectionManager, FlightController, Telemetry, Control, 
        Config, Mission, Sensors, connect, get_flight_data
    )
except ImportError:
    print("Please install mspkit: pip install mspkit")
    exit(1)

def main():
    """Main demonstration function"""
    
    # Configuration - modify these for your setup
    SERIAL_PORT = '/dev/ttyUSB0'  # Change to your port (Windows: COM3, etc.)
    BAUDRATE = 115200
    FC_TYPE = FlightController.INAV  # or FlightController.BETAFLIGHT
    
    print("🚁 MSPKit SDK Enhanced Demo")
    print("=" * 50)
    
    # Connect to flight controller
    print(f"Connecting to {FC_TYPE.name} on {SERIAL_PORT}...")
    
    try:
        # Use the convenience connect function
        conn = connect(SERIAL_PORT, BAUDRATE, FC_TYPE)
        print(f"✅ Connected successfully!")
        print(f"   MSP v2 supported: {conn.msp_v2_supported}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    try:
        # 1. Flight Controller Information
        demo_fc_info(conn)
        
        # 2. Comprehensive Telemetry
        demo_telemetry(conn)
        
        # 3. Sensor Testing and Calibration
        demo_sensors(conn)
        
        # 4. Configuration Management
        demo_configuration(conn)
        
        # 5. Mission Planning (iNav only)
        if FC_TYPE == FlightController.INAV:
            demo_mission_planning(conn)
        
        # 6. Flight Control (with safety)
        demo_flight_control(conn)
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        conn.close()
        print("🔌 Connection closed")

def demo_fc_info(conn: ConnectionManager):
    """Demonstrate flight controller information retrieval"""
    print("\n📋 Flight Controller Information")
    print("-" * 40)
    
    telem = Telemetry(conn)
    
    # Get FC details
    api_version = telem.get_api_version()
    fc_variant = telem.get_fc_variant()
    fc_version = telem.get_fc_version()
    board_info = telem.get_board_info()
    
    if api_version:
        print(f"API Version: {api_version['api_version']}")
    if fc_variant:
        print(f"FC Variant: {fc_variant['fc_variant']}")
    if fc_version:
        print(f"FC Version: {fc_version['fc_version']}")
    if board_info:
        print(f"Board: {board_info['board_identifier']}")

def demo_telemetry(conn: ConnectionManager):
    """Demonstrate comprehensive telemetry data"""
    print("\n📊 Telemetry Data")
    print("-" * 40)
    
    # Get all telemetry in one call
    flight_data = get_flight_data(conn)
    
    # Display key telemetry
    if 'attitude' in flight_data:
        att = flight_data['attitude']
        print(f"Attitude: Roll={att['roll']:.1f}° Pitch={att['pitch']:.1f}° Yaw={att['yaw']:.1f}°")
    
    if 'gps' in flight_data:
        gps = flight_data['gps']
        print(f"GPS: {gps['num_satellites']} sats, {gps['fix_type']}, Lat={gps['latitude']:.6f}")
    
    if 'analog' in flight_data:
        analog = flight_data['analog']
        print(f"Battery: {analog['voltage']:.1f}V, {analog['amperage']:.1f}A")
    
    if 'status' in flight_data:
        status = flight_data['status']
        print(f"Armed: {status['armed']}, Flight modes: {', '.join(status['flight_modes'])}")
    
    # Show raw IMU data
    telem = Telemetry(conn)
    imu = telem.get_raw_imu()
    if imu:
        acc = imu['accelerometer']
        print(f"Accelerometer: X={acc['x']} Y={acc['y']} Z={acc['z']}")

def demo_sensors(conn: ConnectionManager):
    """Demonstrate sensor testing and calibration"""
    print("\n🔧 Sensor Management")
    print("-" * 40)
    
    sensors = Sensors(conn)
    
    # Run comprehensive sensor test
    print("Running sensor test suite...")
    test_results = sensors.run_sensor_test()
    
    print(f"Overall Status: {test_results['overall_status']}")
    for test_name, result in test_results['tests'].items():
        status_icon = "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'WARN' else "❌"
        print(f"  {status_icon} {test_name}: {result['message']}")
    
    # Check if calibration is needed
    calibration_needed = sensors.is_calibration_needed()
    needs_cal = any(calibration_needed.values())
    
    if needs_cal:
        print("\n⚠️  Some sensors may need calibration:")
        for sensor, needed in calibration_needed.items():
            if needed:
                print(f"  - {sensor}")
    else:
        print("✅ All sensors appear to be calibrated")

def demo_configuration(conn: ConnectionManager):
    """Demonstrate configuration management"""
    print("\n⚙️  Configuration Management")
    print("-" * 40)
    
    config = Config(conn)
    
    # Get current PID values
    pids = config.get_pid_values()
    if pids:
        print("Current PID values:")
        for axis, values in list(pids.items())[:3]:  # Show first 3 axes
            print(f"  {axis}: P={values['P']} I={values['I']} D={values['D']}")
    
    # Get RC tuning
    rc_tuning = config.get_rc_tuning()
    if rc_tuning:
        print(f"RC Rate: {rc_tuning['rc_rate']:.2f}")
        print(f"RC Expo: {rc_tuning['rc_expo']:.2f}")
    
    # Get enabled features
    features = config.get_features()
    if features:
        enabled_features = [name for name, enabled in features.items() if enabled]
        print(f"Enabled features: {', '.join(enabled_features[:5])}...")  # Show first 5
    
    # Create backup
    print("\nCreating configuration backup...")
    backup = config.backup_settings()
    if backup:
        print("✅ Configuration backup created successfully")

def demo_mission_planning(conn: ConnectionManager):
    """Demonstrate mission planning (iNav only)"""
    print("\n🗺️  Mission Planning (iNav)")
    print("-" * 40)
    
    mission = Mission(conn)
    
    # Create a simple test mission
    test_waypoints = [
        (47.6062, -122.3321, 50),  # Seattle area coordinates
        (47.6072, -122.3331, 60),
        (47.6082, -122.3341, 50),
    ]
    
    print(f"Creating mission with {len(test_waypoints)} waypoints...")
    if mission.create_simple_mission(test_waypoints, speed=500):
        info = mission.get_mission_info()
        print(f"✅ Mission created:")
        print(f"  Waypoints: {info['waypoint_count']}")
        print(f"  Distance: {info['total_distance_m']:.1f}m")
        print(f"  Altitude range: {info['min_altitude_m']:.1f}-{info['max_altitude_m']:.1f}m")
        
        # Save mission to file
        mission.save_mission_to_file("/tmp/demo_mission.json")
        print("  Mission saved to /tmp/demo_mission.json")
    else:
        print("❌ Failed to create mission")

def demo_flight_control(conn: ConnectionManager):
    """Demonstrate safe flight control"""
    print("\n🎮 Flight Control Demo (Safe Mode)")
    print("-" * 40)
    
    control = Control(conn)
    
    # Enable safety checks
    control.enable_safety(True)
    print("✅ Safety checks enabled")
    
    # Check current armed state
    telem = Telemetry(conn)
    status = telem.get_status()
    is_armed = status['armed'] if status else False
    
    print(f"Current armed state: {'ARMED' if is_armed else 'DISARMED'}")
    
    if not is_armed:
        print("\n⚠️  SAFETY DEMO - NOT ACTUALLY ARMING")
        print("This demo shows the control interface without arming the aircraft")
        
        # Demonstrate control commands (won't actually arm due to safety)
        print("\nDemonstrating control commands:")
        print("- Reset RC channels to safe values")
        control.reset_rc_channels()
        
        print("- Set flight mode to angle mode")
        control.enable_angle_mode()
        
        print("- Demonstrate attitude control (0% inputs)")
        control.set_attitude(roll_percent=0, pitch_percent=0, yaw_percent=0, throttle_percent=0)
        
        # Show last RC values
        rc_values = control.get_last_rc_values()
        print(f"Current RC channels: {rc_values[:8]}")
    else:
        print("🚨 AIRCRAFT IS ARMED - Skipping control demo for safety")

def wait_for_user():
    """Wait for user input to continue"""
    try:
        input("\nPress Enter to continue to next demo (Ctrl+C to exit)...")
    except KeyboardInterrupt:
        raise

if __name__ == "__main__":
    # Add interactive mode option
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Override wait function for interactive mode
        original_demo_fc_info = demo_fc_info
        original_demo_telemetry = demo_telemetry
        original_demo_sensors = demo_sensors
        original_demo_configuration = demo_configuration
        original_demo_mission_planning = demo_mission_planning
        original_demo_flight_control = demo_flight_control
        
        def wrap_demo(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                wait_for_user()
                return result
            return wrapper
        
        demo_fc_info = wrap_demo(original_demo_fc_info)
        demo_telemetry = wrap_demo(original_demo_telemetry)
        demo_sensors = wrap_demo(original_demo_sensors)
        demo_configuration = wrap_demo(original_demo_configuration)
        demo_mission_planning = wrap_demo(original_demo_mission_planning)
        demo_flight_control = wrap_demo(original_demo_flight_control)
    
    main()
