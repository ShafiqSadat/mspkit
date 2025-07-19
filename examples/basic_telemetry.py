#!/usr/bin/env python3
"""
Basic Telemetry Example

This example demonstrates how to connect to a flight controller and read basic telemetry data.
Perfect for beginners getting started with MSPKit.
"""

import time
import logging
from mspkit import connect, FlightController, Telemetry

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main telemetry reading function"""
    
    # Configuration
    SERIAL_PORT = '/dev/ttyUSB0'  # Change to your port (Windows: 'COM3', macOS: '/dev/tty.usbserial-*')
    FC_TYPE = FlightController.INAV  # or FlightController.BETAFLIGHT
    
    try:
        # Connect to flight controller
        print(f"Connecting to {FC_TYPE.name} on {SERIAL_PORT}...")
        conn = connect(SERIAL_PORT, fc_type=FC_TYPE)
        print("✅ Connected successfully!")
        
        # Create telemetry instance
        telem = Telemetry(conn)
        
        # Get basic info
        api_info = telem.get_api_version()
        print(f"Flight Controller: {api_info.get('fc_variant', 'Unknown')}")
        print(f"API Version: {api_info.get('version', 'Unknown')}")
        print(f"MSP Version: {api_info.get('msp_version', 'Unknown')}")
        print()
        
        # Read telemetry in a loop
        print("Reading telemetry data (Press Ctrl+C to stop)...")
        print("=" * 80)
        
        while True:
            try:
                # Get attitude data
                attitude = telem.get_attitude()
                roll = attitude.get('roll', 0)
                pitch = attitude.get('pitch', 0)
                yaw = attitude.get('yaw', 0)
                
                # Get GPS data
                gps = telem.get_gps()
                lat = gps.get('lat', 0)
                lon = gps.get('lon', 0)
                alt = gps.get('alt', 0)
                satellites = gps.get('num_sat', 0)
                fix_type = gps.get('fix_type', 0)
                
                # Get battery info
                battery = telem.get_battery()
                voltage = battery.get('voltage', 0)
                current = battery.get('current', 0)
                mah_drawn = battery.get('mah_drawn', 0)
                
                # Get RC channels
                rc = telem.get_rc_channels()
                throttle = rc.get('throttle', 1000) if rc else 1000
                
                # Get flight status
                status = telem.get_status()
                armed = status.get('armed', False)
                flight_mode = status.get('flight_mode_flags', 0)
                
                # Display data in a formatted way
                print(f"\r"
                      f"Attitude: R{roll:6.1f}° P{pitch:6.1f}° Y{yaw:6.1f}° | "
                      f"GPS: {lat:9.6f},{lon:10.6f} Alt:{alt:5.1f}m Sats:{satellites:2d} | "
                      f"Battery: {voltage:4.2f}V {current:6.1f}A {mah_drawn:5.0f}mAh | "
                      f"Throttle: {throttle:4d} | "
                      f"{'ARMED' if armed else 'DISARMED'}", 
                      end='', flush=True)
                
                time.sleep(0.1)  # 10Hz update rate
                
            except KeyboardInterrupt:
                print("\n\n🛑 Telemetry reading stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error reading telemetry: {e}")
                time.sleep(1)
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if the flight controller is connected")
        print("2. Verify the serial port path")
        print("3. Ensure no other software is using the port")
        print("4. Try a different baud rate or USB cable")
        
    finally:
        print("\nDisconnecting...")

if __name__ == "__main__":
    main()
