#!/usr/bin/env python3
"""
Complete Demo - MSPKit SDK Showcase

This comprehensive example demonstrates all major capabilities of MSPKit:
- Connection and basic telemetry
- Flight control operations
- Mission planning and execution
- Sensor calibration
- Configuration management
- Real-time monitoring

Perfect for demonstrating the full capabilities of the SDK.
"""

import time
import json
import logging
from typing import Dict, Any
from mspkit import (
    connect, FlightController, Telemetry, Control, 
    Mission, Config, Sensors
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MSPKitDemo:
    """Complete demonstration of MSPKit capabilities"""
    
    def __init__(self, serial_port: str, fc_type: FlightController):
        print(f"🚁 MSPKit SDK Complete Demo")
        print("=" * 50)
        print(f"Connecting to {fc_type.name} on {serial_port}...")
        
        # Initialize connection and modules
        self.conn = connect(serial_port, fc_type=fc_type)
        self.telemetry = Telemetry(self.conn)
        self.control = Control(self.conn)
        self.mission = Mission(self.conn)
        self.config = Config(self.conn)
        self.sensors = Sensors(self.conn)
        self.fc_type = fc_type
        
        print("✅ All modules initialized successfully!")
        
        # Get basic info
        self._show_system_info()
    
    def _show_system_info(self):
        """Display basic system information"""
        print("\n📊 System Information:")
        try:
            api_info = self.telemetry.get_api_version()
            build_info = self.telemetry.get_build_info()
            
            print(f"   Flight Controller: {api_info.get('fc_variant', 'Unknown')}")
            print(f"   Firmware Version: {build_info.get('version', 'Unknown')}")
            print(f"   API Version: {api_info.get('version', 'Unknown')}")
            print(f"   Build Date: {build_info.get('build_date', 'Unknown')}")
            
        except Exception as e:
            print(f"   ⚠️  Could not read system info: {e}")
    
    def demo_telemetry_monitoring(self, duration: int = 10):
        """Demonstrate real-time telemetry monitoring"""
        print(f"\n📡 Telemetry Monitoring Demo ({duration}s)")
        print("-" * 50)
        
        start_time = time.time()
        sample_count = 0
        
        print("Real-time telemetry data:")
        print("Time | Roll  | Pitch | Yaw   | Alt   | Battery | GPS Sats")
        print("-" * 65)
        
        try:
            while time.time() - start_time < duration:
                # Get telemetry data
                attitude = self.telemetry.get_attitude()
                gps = self.telemetry.get_gps()
                battery = self.telemetry.get_battery()
                
                elapsed = time.time() - start_time
                roll = attitude.get('roll', 0)
                pitch = attitude.get('pitch', 0)
                yaw = attitude.get('yaw', 0)
                alt = gps.get('alt', 0)
                voltage = battery.get('voltage', 0)
                satellites = gps.get('num_sat', 0)
                
                print(f"{elapsed:4.1f} | {roll:5.1f} | {pitch:5.1f} | {yaw:5.1f} | {alt:5.1f} | {voltage:7.2f} | {satellites:8d}")
                
                sample_count += 1
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring interrupted")
        
        print(f"\n✅ Collected {sample_count} telemetry samples")
    
    def demo_sensor_health_check(self):
        """Demonstrate sensor health monitoring"""
        print("\n🔍 Sensor Health Check Demo")
        print("-" * 50)
        
        try:
            # Get sensor status
            sensor_status = self.sensors.get_sensor_status()
            
            # Get raw sensor data
            imu = self.telemetry.get_imu_raw()
            gps = self.telemetry.get_gps()
            
            # Analyze sensor health
            sensors_to_check = {
                'Accelerometer': {
                    'enabled': sensor_status.get('acc', False),
                    'data': (imu.get('acc_x', 0), imu.get('acc_y', 0), imu.get('acc_z', 0)),
                    'test': lambda data: 900 < (data[0]**2 + data[1]**2 + data[2]**2)**0.5 < 1100
                },
                'Gyroscope': {
                    'enabled': sensor_status.get('gyro', False),
                    'data': (imu.get('gyro_x', 0), imu.get('gyro_y', 0), imu.get('gyro_z', 0)),
                    'test': lambda data: all(abs(x) < 100 for x in data)  # Low noise when still
                },
                'Magnetometer': {
                    'enabled': sensor_status.get('mag', False),
                    'data': (imu.get('mag_x', 0), imu.get('mag_y', 0), imu.get('mag_z', 0)),
                    'test': lambda data: (data[0]**2 + data[1]**2 + data[2]**2)**0.5 > 100
                },
                'GPS': {
                    'enabled': sensor_status.get('gps', False),
                    'data': (gps.get('fix_type', 0), gps.get('num_sat', 0)),
                    'test': lambda data: data[0] >= 2 and data[1] >= 4
                },
                'Barometer': {
                    'enabled': sensor_status.get('baro', False),
                    'data': gps.get('alt', 0),
                    'test': lambda data: -1000 < data < 10000
                }
            }
            
            print("Sensor Health Report:")
            for sensor_name, sensor_info in sensors_to_check.items():
                enabled = sensor_info['enabled']
                data = sensor_info['data']
                healthy = sensor_info['test'](data) if enabled else False
                
                status_icon = "✅" if enabled and healthy else "⚠️" if enabled else "❌"
                print(f"   {status_icon} {sensor_name:12s}: {'Enabled' if enabled else 'Disabled':8s} - {'Healthy' if healthy else 'Check' if enabled else 'N/A'}")
                
                # Show data for debugging
                if enabled:
                    if isinstance(data, tuple) and len(data) == 3:
                        print(f"      Data: X={data[0]:6.0f} Y={data[1]:6.0f} Z={data[2]:6.0f}")
                    else:
                        print(f"      Data: {data}")
            
        except Exception as e:
            print(f"❌ Sensor check failed: {e}")
    
    def demo_simple_mission(self):
        """Demonstrate mission planning and upload"""
        print("\n🗺️  Mission Planning Demo")
        print("-" * 50)
        
        try:
            # Create a simple square mission
            print("Creating a simple square mission...")
            
            # Get current GPS position or use default
            gps = self.telemetry.get_gps()
            home_lat = gps.get('lat', 37.7749) if gps.get('fix_type', 0) >= 2 else 37.7749
            home_lon = gps.get('lon', -122.4194) if gps.get('fix_type', 0) >= 2 else -122.4194
            
            print(f"   Home position: {home_lat:.6f}, {home_lon:.6f}")
            
            # Clear any existing mission
            self.mission.clear_mission()
            
            # Create square waypoints (50m x 50m)
            import math
            lat_per_meter = 1 / 111320.0
            lon_per_meter = 1 / (111320.0 * math.cos(math.radians(home_lat)))
            
            waypoints = [
                (home_lat, home_lon, 30),  # Start
                (home_lat + 50 * lat_per_meter, home_lon, 30),  # North
                (home_lat + 50 * lat_per_meter, home_lon + 50 * lon_per_meter, 30),  # Northeast
                (home_lat, home_lon + 50 * lon_per_meter, 30),  # East
                (home_lat, home_lon, 30),  # Return home
            ]
            
            for i, (lat, lon, alt) in enumerate(waypoints):
                action = Mission.WAYPOINT_ACTION_WAYPOINT if i < len(waypoints) - 1 else Mission.WAYPOINT_ACTION_RTH
                speed = 500  # 5 m/s
                
                success = self.mission.add_waypoint(lat, lon, alt, action=action, param1=speed)
                if success:
                    print(f"   ✅ Added waypoint {i+1}: {lat:.6f}, {lon:.6f}, {alt}m")
                else:
                    print(f"   ❌ Failed to add waypoint {i+1}")
            
            # Show mission info
            info = self.mission.get_mission_info()
            print(f"\n📊 Mission Statistics:")
            print(f"   Waypoints: {info['waypoint_count']}")
            print(f"   Total distance: {info['total_distance_m']:.0f}m")
            print(f"   Altitude range: {info['min_altitude_m']:.0f}m - {info['max_altitude_m']:.0f}m")
            
            # Save mission to file
            filename = "demo_mission.json"
            if self.mission.save_mission_to_file(filename):
                print(f"   ✅ Mission saved to {filename}")
            
            # Optionally upload to FC (only if iNav)
            if self.fc_type == FlightController.INAV:
                upload = input("\n   Upload mission to flight controller? (yes/no): ")
                if upload.lower() == 'yes':
                    print("   📤 Uploading mission...")
                    if self.mission.upload_mission():
                        print("   ✅ Mission uploaded successfully!")
                    else:
                        print("   ❌ Mission upload failed")
            else:
                print("   ⚠️  Mission upload requires iNav flight controller")
                
        except Exception as e:
            print(f"❌ Mission demo failed: {e}")
    
    def demo_configuration_info(self):
        """Demonstrate configuration reading"""
        print("\n⚙️  Configuration Demo")
        print("-" * 50)
        
        try:
            # PID configuration
            print("Current PID Settings:")
            pid_config = self.config.get_pid_config()
            if pid_config:
                print(f"   Roll:  P={pid_config.get('roll_p', 0):3.0f}  I={pid_config.get('roll_i', 0):3.0f}  D={pid_config.get('roll_d', 0):3.0f}")
                print(f"   Pitch: P={pid_config.get('pitch_p', 0):3.0f}  I={pid_config.get('pitch_i', 0):3.0f}  D={pid_config.get('pitch_d', 0):3.0f}")
                print(f"   Yaw:   P={pid_config.get('yaw_p', 0):3.0f}  I={pid_config.get('yaw_i', 0):3.0f}  D={pid_config.get('yaw_d', 0):3.0f}")
            
            # Feature status
            print("\nEnabled Features:")
            features = self.config.get_features()
            if features:
                enabled_features = [name for name, enabled in features.items() if enabled]
                print(f"   {', '.join(enabled_features[:10]) if enabled_features else 'None'}")
                if len(enabled_features) > 10:
                    print(f"   ... and {len(enabled_features) - 10} more")
            
            # RC configuration
            print("\nRC Configuration:")
            rc_tuning = self.config.get_rc_tuning()
            if rc_tuning:
                print(f"   RC Rate: {rc_tuning.get('rc_rate', 0):.2f}")
                print(f"   Expo: {rc_tuning.get('rc_expo', 0):.2f}")
                print(f"   Super Rate: {rc_tuning.get('super_rate', 0):.2f}")
            
        except Exception as e:
            print(f"❌ Configuration demo failed: {e}")
    
    def demo_flight_control_safety(self):
        """Demonstrate safe flight control operations"""
        print("\n🎮 Flight Control Safety Demo")
        print("-" * 50)
        print("⚠️  This demo only shows RC override - NO ARMING!")
        
        try:
            # Check if already armed
            status = self.telemetry.get_status()
            if status.get('armed', False):
                print("⚠️  Flight controller is ARMED - aborting control demo for safety")
                return
            
            print("Demonstrating RC override (aircraft disarmed)...")
            
            # Show current RC values
            rc = self.telemetry.get_rc_channels()
            if rc:
                print(f"Current RC: Throttle={rc.get('throttle', 1000)} Roll={rc.get('roll', 1500)} Pitch={rc.get('pitch', 1500)} Yaw={rc.get('yaw', 1500)}")
            
            # Demonstrate RC override with safe values
            print("Setting RC override with neutral values...")
            
            # Safe neutral values
            safe_rc = {
                'throttle': 1000,  # Minimum throttle
                'roll': 1500,     # Neutral
                'pitch': 1500,    # Neutral
                'yaw': 1500       # Neutral
            }
            
            if self.control.set_rc_override(**safe_rc):
                print("✅ RC override set successfully")
                time.sleep(2)
                
                # Clear override
                if self.control.clear_rc_override():
                    print("✅ RC override cleared")
                else:
                    print("⚠️  Failed to clear RC override")
            else:
                print("❌ RC override failed")
        
        except Exception as e:
            print(f"❌ Flight control demo failed: {e}")
    
    def demo_complete_workflow(self):
        """Demonstrate a complete workflow"""
        print("\n🔄 Complete Workflow Demo")
        print("-" * 50)
        print("This demonstrates a typical MSPKit workflow:")
        print("1. System check and sensor health")
        print("2. Configuration backup")
        print("3. Mission planning")
        print("4. Real-time monitoring")
        print()
        
        try:
            # 1. System check
            print("Step 1: System Health Check")
            self.demo_sensor_health_check()
            input("\nPress Enter to continue...")
            
            # 2. Configuration backup
            print("\nStep 2: Configuration Backup")
            backup_file = f"demo_backup_{int(time.time())}.json"
            
            # Simple backup (just PID for demo)
            pid_config = self.config.get_pid_config()
            features = self.config.get_features()
            
            backup_data = {
                'timestamp': time.time(),
                'fc_type': self.fc_type.name,
                'pid_config': pid_config,
                'features': features
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"✅ Configuration backed up to {backup_file}")
            input("\nPress Enter to continue...")
            
            # 3. Mission planning
            print("\nStep 3: Mission Planning")
            self.demo_simple_mission()
            input("\nPress Enter to continue...")
            
            # 4. Monitoring
            print("\nStep 4: Real-time Monitoring")
            self.demo_telemetry_monitoring(duration=5)
            
            print("\n✅ Complete workflow demonstration finished!")
            
        except KeyboardInterrupt:
            print("\n🛑 Workflow interrupted")
        except Exception as e:
            print(f"❌ Workflow demo failed: {e}")

def main():
    """Main demonstration"""
    
    SERIAL_PORT = '/dev/ttyUSB0'  # Change as needed
    FC_TYPE = FlightController.INAV  # Change as needed
    
    print("🚁 MSPKit SDK Complete Demonstration")
    print("=" * 60)
    print("This example showcases all major capabilities of MSPKit")
    print()
    
    try:
        demo = MSPKitDemo(SERIAL_PORT, FC_TYPE)
        
        while True:
            print("\n🎯 Demo Menu:")
            print("1. Telemetry monitoring (10s)")
            print("2. Sensor health check")
            print("3. Mission planning demo")
            print("4. Configuration info")
            print("5. Flight control safety demo")
            print("6. Complete workflow demo")
            print("7. System information")
            print("8. Exit")
            
            choice = input("\nSelect demo (1-8): ").strip()
            
            if choice == '1':
                demo.demo_telemetry_monitoring()
                
            elif choice == '2':
                demo.demo_sensor_health_check()
                
            elif choice == '3':
                demo.demo_simple_mission()
                
            elif choice == '4':
                demo.demo_configuration_info()
                
            elif choice == '5':
                demo.demo_flight_control_safety()
                
            elif choice == '6':
                demo.demo_complete_workflow()
                
            elif choice == '7':
                demo._show_system_info()
                
            elif choice == '8':
                print("👋 Thank you for using MSPKit SDK!")
                print("Visit the documentation for more examples and guides.")
                break
                
            else:
                print("❌ Invalid option")
    
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("\nTroubleshooting:")
        print("1. Check serial port connection")
        print("2. Verify flight controller is powered")
        print("3. Ensure correct FC type selected")
        print("4. Try different baud rate or USB cable")

if __name__ == "__main__":
    main()
