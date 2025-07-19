#!/usr/bin/env python3
"""
Sensor Calibration Example

This example demonstrates sensor calibration procedures including:
- Accelerometer calibration
- Magnetometer/compass calibration
- Gyroscope calibration
- Sensor health monitoring

Essential for accurate flight performance and navigation.
"""

import time
import logging
from mspkit import connect, FlightController, Sensors, Telemetry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorCalibrator:
    """Comprehensive sensor calibration and monitoring"""
    
    def __init__(self, serial_port: str, fc_type: FlightController):
        self.conn = connect(serial_port, fc_type=fc_type)
        self.sensors = Sensors(self.conn)
        self.telemetry = Telemetry(self.conn)
        self.fc_type = fc_type
        
        print(f"✅ Connected to {fc_type.name} flight controller")
    
    def check_sensor_health(self) -> dict:
        """Check the health status of all sensors"""
        print("\n🔍 Checking Sensor Health...")
        
        sensor_status = self.sensors.get_sensor_status()
        sensor_data = {}
        
        # Get sensor readings
        try:
            imu = self.telemetry.get_imu_raw()
            sensor_data['accelerometer'] = {
                'x': imu.get('acc_x', 0),
                'y': imu.get('acc_y', 0),
                'z': imu.get('acc_z', 0),
                'enabled': sensor_status.get('acc', False)
            }
            
            sensor_data['gyroscope'] = {
                'x': imu.get('gyro_x', 0),
                'y': imu.get('gyro_y', 0),
                'z': imu.get('gyro_z', 0),
                'enabled': sensor_status.get('gyro', False)
            }
            
            sensor_data['magnetometer'] = {
                'x': imu.get('mag_x', 0),
                'y': imu.get('mag_y', 0),
                'z': imu.get('mag_z', 0),
                'enabled': sensor_status.get('mag', False)
            }
            
            # GPS status
            gps = self.telemetry.get_gps()
            sensor_data['gps'] = {
                'fix_type': gps.get('fix_type', 0),
                'satellites': gps.get('num_sat', 0),
                'hdop': gps.get('hdop', 0),
                'enabled': sensor_status.get('gps', False)
            }
            
            # Barometer
            sensor_data['barometer'] = {
                'altitude': gps.get('alt', 0),
                'enabled': sensor_status.get('baro', False)
            }
            
        except Exception as e:
            print(f"⚠️  Error reading sensor data: {e}")
            return {}
        
        # Display sensor health
        print("\n📊 Sensor Health Report:")
        print("-" * 50)
        
        for sensor, data in sensor_data.items():
            status = "✅ OK" if data.get('enabled', False) else "❌ DISABLED"
            print(f"{sensor.upper():12s}: {status}")
            
            if sensor == 'accelerometer':
                acc_magnitude = (data['x']**2 + data['y']**2 + data['z']**2) ** 0.5
                print(f"              Magnitude: {acc_magnitude:.0f} (expected ~1000)")
                
            elif sensor == 'gyroscope':
                gyro_noise = max(abs(data['x']), abs(data['y']), abs(data['z']))
                print(f"              Max noise: {gyro_noise:.0f} (should be <50)")
                
            elif sensor == 'magnetometer':
                mag_magnitude = (data['x']**2 + data['y']**2 + data['z']**2) ** 0.5
                print(f"              Magnitude: {mag_magnitude:.0f}")
                
            elif sensor == 'gps':
                fix_types = ["No Fix", "Dead Reckoning", "2D Fix", "3D Fix", "GPS+Dead Reckoning", "Time Only"]
                fix_type_str = fix_types[min(data['fix_type'], len(fix_types)-1)]
                print(f"              Fix: {fix_type_str}, Sats: {data['satellites']}, HDOP: {data['hdop']/100:.1f}")
        
        return sensor_data
    
    def calibrate_accelerometer(self) -> bool:
        """Calibrate accelerometer (6-point calibration)"""
        print("\n📐 Accelerometer Calibration")
        print("This requires positioning the aircraft in 6 orientations:")
        print("1. Level (top up)")
        print("2. Upside down (bottom up)") 
        print("3. Left side down")
        print("4. Right side down")
        print("5. Nose down")
        print("6. Nose up")
        print()
        
        positions = [
            "level (top up)",
            "upside down (bottom up)",
            "left side down", 
            "right side down",
            "nose down",
            "nose up"
        ]
        
        print("⚠️  Ensure the aircraft is stable and not moving during calibration!")
        input("Press Enter when ready to start...")
        
        calibration_data = []
        
        for i, position in enumerate(positions):
            print(f"\n📍 Position {i+1}/6: Place aircraft {position}")
            input("Position aircraft and press Enter to capture...")
            
            # Capture accelerometer data
            print("📊 Capturing data...")
            samples = []
            
            for _ in range(50):  # 50 samples over 1 second
                try:
                    imu = self.telemetry.get_imu_raw()
                    samples.append([
                        imu.get('acc_x', 0),
                        imu.get('acc_y', 0), 
                        imu.get('acc_z', 0)
                    ])
                    time.sleep(0.02)
                except:
                    continue
            
            if samples:
                # Average the samples
                avg_x = sum(s[0] for s in samples) / len(samples)
                avg_y = sum(s[1] for s in samples) / len(samples)
                avg_z = sum(s[2] for s in samples) / len(samples)
                
                calibration_data.append([avg_x, avg_y, avg_z])
                print(f"✅ Captured: X={avg_x:.0f}, Y={avg_y:.0f}, Z={avg_z:.0f}")
            else:
                print("❌ Failed to capture data")
                return False
        
        # Start calibration on flight controller
        print("\n🔧 Starting accelerometer calibration on flight controller...")
        
        if self.sensors.calibrate_accelerometer():
            print("✅ Accelerometer calibration completed successfully!")
            print("🔧 Verifying calibration...")
            
            # Wait a moment for calibration to settle
            time.sleep(2)
            
            # Check if calibration improved
            imu = self.telemetry.get_imu_raw()
            acc_magnitude = (imu.get('acc_x', 0)**2 + imu.get('acc_y', 0)**2 + imu.get('acc_z', 0)**2) ** 0.5
            
            if 950 <= acc_magnitude <= 1050:  # Should be close to 1000 when level
                print(f"✅ Calibration verified: magnitude = {acc_magnitude:.0f}")
                return True
            else:
                print(f"⚠️  Calibration questionable: magnitude = {acc_magnitude:.0f} (expected ~1000)")
                return False
        else:
            print("❌ Accelerometer calibration failed")
            return False
    
    def calibrate_magnetometer(self) -> bool:
        """Calibrate magnetometer/compass"""
        print("\n🧭 Magnetometer Calibration")
        print("This requires slowly rotating the aircraft in all directions")
        print("to map the magnetic field distortions.")
        print()
        print("Instructions:")
        print("1. Hold the aircraft level")
        print("2. Slowly rotate 360° horizontally (yaw)")
        print("3. Then tilt and rotate in all orientations")
        print("4. Continue for about 60 seconds")
        print()
        
        input("Press Enter when ready to start calibration...")
        
        # Start magnetometer calibration
        print("🔧 Starting magnetometer calibration...")
        
        if self.sensors.calibrate_magnetometer():
            print("✅ Magnetometer calibration command sent")
            print("\n🔄 Now perform the rotation sequence...")
            print("Rotate the aircraft slowly in all orientations for 60 seconds")
            
            # Monitor calibration progress
            start_time = time.time()
            calibration_time = 60  # seconds
            
            while time.time() - start_time < calibration_time:
                remaining = calibration_time - (time.time() - start_time)
                
                # Get magnetometer readings to show activity
                try:
                    imu = self.telemetry.get_imu_raw()
                    mag_x = imu.get('mag_x', 0)
                    mag_y = imu.get('mag_y', 0) 
                    mag_z = imu.get('mag_z', 0)
                    magnitude = (mag_x**2 + mag_y**2 + mag_z**2) ** 0.5
                    
                    print(f"\r🧭 Calibrating... {remaining:.0f}s remaining | "
                          f"Mag: X={mag_x:5.0f} Y={mag_y:5.0f} Z={mag_z:5.0f} |{magnitude:5.0f}|",
                          end='', flush=True)
                except:
                    print(f"\r🧭 Calibrating... {remaining:.0f}s remaining", end='', flush=True)
                
                time.sleep(0.2)
            
            print("\n✅ Magnetometer calibration time completed")
            print("🔧 Verifying calibration...")
            
            # The FC should automatically save the calibration
            time.sleep(2)
            
            # Check compass heading stability
            headings = []
            for _ in range(10):
                attitude = self.telemetry.get_attitude()
                headings.append(attitude.get('yaw', 0))
                time.sleep(0.1)
            
            if headings:
                heading_std = (sum((h - sum(headings)/len(headings))**2 for h in headings) / len(headings)) ** 0.5
                if heading_std < 5:  # Less than 5 degrees variation
                    print(f"✅ Calibration verified: heading stable (±{heading_std:.1f}°)")
                    return True
                else:
                    print(f"⚠️  Heading unstable: ±{heading_std:.1f}° variation")
            
            return True
        else:
            print("❌ Magnetometer calibration failed to start")
            return False
    
    def calibrate_gyroscope(self) -> bool:
        """Calibrate gyroscope"""
        print("\n🌀 Gyroscope Calibration")
        print("This calibrates the gyroscope zero offset.")
        print("The aircraft must be completely still during calibration.")
        print()
        
        input("Ensure aircraft is still and press Enter to start...")
        
        print("🔧 Starting gyroscope calibration...")
        print("⚠️  Do NOT move the aircraft for the next 10 seconds!")
        
        if self.sensors.calibrate_gyroscope():
            print("✅ Gyroscope calibration command sent")
            
            # Monitor gyro noise during calibration
            start_time = time.time()
            calibration_time = 10
            
            max_noise = 0
            while time.time() - start_time < calibration_time:
                remaining = calibration_time - (time.time() - start_time)
                
                try:
                    imu = self.telemetry.get_imu_raw()
                    gyro_x = abs(imu.get('gyro_x', 0))
                    gyro_y = abs(imu.get('gyro_y', 0))
                    gyro_z = abs(imu.get('gyro_z', 0))
                    current_noise = max(gyro_x, gyro_y, gyro_z)
                    max_noise = max(max_noise, current_noise)
                    
                    print(f"\r🌀 Calibrating... {remaining:.0f}s | "
                          f"Gyro noise: {current_noise:.0f} (max: {max_noise:.0f})",
                          end='', flush=True)
                except:
                    print(f"\r🌀 Calibrating... {remaining:.0f}s", end='', flush=True)
                
                time.sleep(0.1)
            
            print(f"\n✅ Gyroscope calibration completed")
            
            if max_noise < 50:
                print(f"✅ Low noise detected: {max_noise:.0f} (good)")
                return True
            else:
                print(f"⚠️  High noise detected: {max_noise:.0f} (check vibration)")
                return False
        else:
            print("❌ Gyroscope calibration failed")
            return False
    
    def save_calibration(self) -> bool:
        """Save calibration to EEPROM"""
        print("\n💾 Saving calibration to EEPROM...")
        
        if self.sensors.save_config():
            print("✅ Calibration saved successfully")
            return True
        else:
            print("❌ Failed to save calibration")
            return False

def main():
    """Main sensor calibration demonstration"""
    
    SERIAL_PORT = '/dev/ttyUSB0'
    FC_TYPE = FlightController.INAV  # Change as needed
    
    print("🔧 MSPKit Sensor Calibration Example")
    print("=" * 50)
    print("This example helps calibrate flight controller sensors")
    print("for optimal performance and accuracy.")
    print()
    
    try:
        calibrator = SensorCalibrator(SERIAL_PORT, FC_TYPE)
        
        while True:
            print("\n🔧 Sensor Calibration Menu:")
            print("1. Check sensor health")
            print("2. Calibrate accelerometer")
            print("3. Calibrate magnetometer/compass")
            print("4. Calibrate gyroscope")
            print("5. Save calibration to EEPROM")
            print("6. Full calibration sequence")
            print("7. Exit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == '1':
                calibrator.check_sensor_health()
                
            elif choice == '2':
                calibrator.calibrate_accelerometer()
                
            elif choice == '3':
                calibrator.calibrate_magnetometer()
                
            elif choice == '4':
                calibrator.calibrate_gyroscope()
                
            elif choice == '5':
                calibrator.save_calibration()
                
            elif choice == '6':
                print("\n🔧 Starting Full Calibration Sequence")
                print("This will calibrate all sensors in sequence.")
                print()
                
                response = input("Continue with full calibration? (yes/no): ")
                if response.lower() == 'yes':
                    # Full sequence
                    success = True
                    
                    # 1. Check initial health
                    calibrator.check_sensor_health()
                    
                    # 2. Gyroscope (should be first - needs stillness)
                    print("\n" + "="*50)
                    if not calibrator.calibrate_gyroscope():
                        success = False
                    
                    # 3. Accelerometer
                    print("\n" + "="*50)
                    if not calibrator.calibrate_accelerometer():
                        success = False
                    
                    # 4. Magnetometer
                    print("\n" + "="*50)
                    if not calibrator.calibrate_magnetometer():
                        success = False
                    
                    # 5. Save calibration
                    print("\n" + "="*50)
                    calibrator.save_calibration()
                    
                    # 6. Final health check
                    print("\n" + "="*50)
                    calibrator.check_sensor_health()
                    
                    if success:
                        print("\n✅ Full calibration sequence completed successfully!")
                    else:
                        print("\n⚠️  Calibration completed with some issues")
                
            elif choice == '7':
                print("👋 Exiting sensor calibration")
                break
                
            else:
                print("❌ Invalid option")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
