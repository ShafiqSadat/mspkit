import struct
import time
import logging
from typing import Dict, Any, Optional, List
from .msp_constants import MSPCommands, FlightController

logger = logging.getLogger(__name__)

class Sensors:
    """Enhanced sensor management and calibration"""
    
    def __init__(self, conn):
        self.conn = conn
        self.fc_type = conn.fc_type
        self._calibration_in_progress = False

    def calibrate_accelerometer(self) -> bool:
        """Calibrate accelerometer - aircraft must be level and stationary"""
        if self._calibration_in_progress:
            logger.warning("Calibration already in progress")
            return False
            
        try:
            logger.info("Starting accelerometer calibration - keep aircraft level and stationary")
            self.conn.send_msp(MSPCommands.MSP_ACC_CALIBRATION)
            self._calibration_in_progress = True
            
            # Wait for calibration to complete (typically 2-5 seconds)
            time.sleep(5)
            self._calibration_in_progress = False
            
            logger.info("Accelerometer calibration completed")
            return True
            
        except Exception as e:
            logger.error(f"Accelerometer calibration failed: {e}")
            self._calibration_in_progress = False
            return False

    def calibrate_magnetometer(self) -> bool:
        """Calibrate magnetometer - requires 360-degree rotation"""
        if self._calibration_in_progress:
            logger.warning("Calibration already in progress")
            return False
            
        try:
            logger.info("Starting magnetometer calibration - rotate aircraft 360° in all axes")
            self.conn.send_msp(MSPCommands.MSP_MAG_CALIBRATION)
            self._calibration_in_progress = True
            
            # Magnetometer calibration takes longer (30+ seconds)
            logger.info("Magnetometer calibration in progress (30+ seconds)...")
            time.sleep(35)
            self._calibration_in_progress = False
            
            logger.info("Magnetometer calibration completed")
            return True
            
        except Exception as e:
            logger.error(f"Magnetometer calibration failed: {e}")
            self._calibration_in_progress = False
            return False

    def calibrate_gyroscope(self) -> bool:
        """Calibrate gyroscope - aircraft must be stationary"""
        if self._calibration_in_progress:
            logger.warning("Calibration already in progress")
            return False
            
        try:
            logger.info("Starting gyroscope calibration - keep aircraft completely stationary")
            self.conn.send_msp(MSPCommands.MSP_CALIBRATE_GYRO)
            self._calibration_in_progress = True
            
            # Gyro calibration is quick (1-2 seconds)
            time.sleep(3)
            self._calibration_in_progress = False
            
            logger.info("Gyroscope calibration completed")
            return True
            
        except Exception as e:
            logger.error(f"Gyroscope calibration failed: {e}")
            self._calibration_in_progress = False
            return False

    def get_sensor_status(self) -> Optional[Dict[str, Any]]:
        """Get detailed sensor status and health"""
        from .telemetry import Telemetry
        
        telem = Telemetry(self.conn)
        status = telem.get_status()
        
        if not status:
            return None
            
        sensor_status = status.get('sensor_status', 0)
        sensors_detected = status.get('sensors_detected', {})
        
        # Get raw IMU data for health check
        imu_data = telem.get_raw_imu()
        
        health_status = {}
        if imu_data:
            # Check accelerometer health
            acc = imu_data['accelerometer']
            acc_magnitude = (acc['x']**2 + acc['y']**2 + acc['z']**2)**0.5
            health_status['accelerometer_healthy'] = 800 < acc_magnitude < 1200  # ~1g expected
            
            # Check gyroscope health (should be near zero when stationary)
            gyro = imu_data['gyroscope']
            gyro_magnitude = (gyro['x']**2 + gyro['y']**2 + gyro['z']**2)**0.5
            health_status['gyroscope_healthy'] = gyro_magnitude < 100  # Low noise when stationary
            
            # Check magnetometer health
            mag = imu_data['magnetometer']
            mag_magnitude = (mag['x']**2 + mag['y']**2 + mag['z']**2)**0.5
            health_status['magnetometer_healthy'] = 100 < mag_magnitude < 2000  # Reasonable range
        
        # GPS health
        gps_data = telem.get_gps()
        if gps_data:
            health_status['gps_healthy'] = gps_data['num_satellites'] >= 6
            health_status['gps_fix_quality'] = gps_data['fix_type']
        
        # Battery health
        battery_data = telem.get_battery_state() or telem.get_analog()
        if battery_data:
            voltage = battery_data.get('voltage', 0)
            health_status['battery_healthy'] = voltage > 10.0  # Above critical voltage
            health_status['battery_voltage'] = voltage
        
        return {
            'sensors_detected': sensors_detected,
            'sensor_status_mask': sensor_status,
            'health_status': health_status,
            'calibration_in_progress': self._calibration_in_progress
        }

    def run_sensor_test(self) -> Dict[str, Any]:
        """Run comprehensive sensor test suite"""
        logger.info("Running sensor test suite...")
        
        test_results: Dict[str, Any] = {
            'timestamp': time.time(),
            'overall_status': 'PASS',
            'tests': {}
        }
        
        from .telemetry import Telemetry
        telem = Telemetry(self.conn)
        
        # Test 1: Basic connectivity
        status = telem.get_status()
        test_results['tests']['connectivity'] = {
            'status': 'PASS' if status else 'FAIL',
            'message': 'MSP communication working' if status else 'MSP communication failed'
        }
        
        if not status:
            test_results['overall_status'] = 'FAIL'
            return test_results
        
        # Test 2: IMU sensors
        imu_data = telem.get_raw_imu()
        if imu_data:
            acc = imu_data['accelerometer']
            gyro = imu_data['gyroscope']
            mag = imu_data['magnetometer']
            
            # Accelerometer test
            acc_mag = (acc['x']**2 + acc['y']**2 + acc['z']**2)**0.5
            acc_test = 'PASS' if 800 < acc_mag < 1200 else 'WARN'
            test_results['tests']['accelerometer'] = {
                'status': acc_test,
                'magnitude': acc_mag,
                'values': acc,
                'message': f'Magnitude: {acc_mag:.1f} (expected ~1000)'
            }
            
            # Gyroscope test
            gyro_mag = (gyro['x']**2 + gyro['y']**2 + gyro['z']**2)**0.5
            gyro_test = 'PASS' if gyro_mag < 200 else 'WARN'
            test_results['tests']['gyroscope'] = {
                'status': gyro_test,
                'magnitude': gyro_mag,
                'values': gyro,
                'message': f'Magnitude: {gyro_mag:.1f} (should be low when stationary)'
            }
            
            # Magnetometer test
            mag_mag = (mag['x']**2 + mag['y']**2 + mag['z']**2)**0.5
            mag_test = 'PASS' if 100 < mag_mag < 2000 else 'WARN'
            test_results['tests']['magnetometer'] = {
                'status': mag_test,
                'magnitude': mag_mag,
                'values': mag,
                'message': f'Magnitude: {mag_mag:.1f} (typical range 100-2000)'
            }
            
            if acc_test == 'FAIL' or gyro_test == 'FAIL' or mag_test == 'FAIL':
                test_results['overall_status'] = 'WARN'
        else:
            test_results['tests']['imu'] = {
                'status': 'FAIL',
                'message': 'Could not read IMU data'
            }
            test_results['overall_status'] = 'FAIL'
        
        # Test 3: GPS
        gps_data = telem.get_gps()
        if gps_data:
            gps_test = 'PASS' if gps_data['num_satellites'] >= 6 else 'WARN'
            test_results['tests']['gps'] = {
                'status': gps_test,
                'satellites': gps_data['num_satellites'],
                'fix_type': gps_data['fix_type'],
                'message': f"{gps_data['num_satellites']} satellites, {gps_data['fix_type']} fix"
            }
        else:
            test_results['tests']['gps'] = {
                'status': 'WARN',
                'message': 'GPS data not available'
            }
        
        # Test 4: Battery/Power
        battery = telem.get_battery_state() or telem.get_analog()
        if battery:
            voltage = battery.get('voltage', 0)
            battery_test = 'PASS' if voltage > 10.0 else 'WARN'
            test_results['tests']['battery'] = {
                'status': battery_test,
                'voltage': voltage,
                'message': f'Voltage: {voltage:.1f}V'
            }
        else:
            test_results['tests']['battery'] = {
                'status': 'WARN',
                'message': 'Battery data not available'
            }
        
        # Test 5: Flight controller info
        api_version = telem.get_api_version()
        fc_variant = telem.get_fc_variant()
        fc_version = telem.get_fc_version()
        
        if api_version and fc_variant and fc_version:
            test_results['tests']['flight_controller'] = {
                'status': 'PASS',
                'api_version': api_version['api_version'],
                'variant': fc_variant['fc_variant'],
                'version': fc_version['fc_version'],
                'message': f"{fc_variant['fc_variant']} {fc_version['fc_version']}"
            }
        else:
            test_results['tests']['flight_controller'] = {
                'status': 'WARN',
                'message': 'Could not read FC information'
            }
        
        # Determine overall status
        fail_count = sum(1 for test in test_results['tests'].values() if test['status'] == 'FAIL')
        warn_count = sum(1 for test in test_results['tests'].values() if test['status'] == 'WARN')
        
        if fail_count > 0:
            test_results['overall_status'] = 'FAIL'
        elif warn_count > 0:
            test_results['overall_status'] = 'WARN'
        
        logger.info(f"Sensor test completed: {test_results['overall_status']} ({fail_count} failures, {warn_count} warnings)")
        return test_results

    def calibrate_all_sensors(self, include_mag: bool = True) -> bool:
        """Perform full sensor calibration sequence"""
        logger.info("Starting full sensor calibration sequence")
        
        success_count = 0
        
        # 1. Calibrate gyroscope first (quick and requires stationary)
        logger.info("Step 1/3: Gyroscope calibration")
        if self.calibrate_gyroscope():
            success_count += 1
        else:
            logger.error("Gyroscope calibration failed")
        
        time.sleep(2)  # Brief pause between calibrations
        
        # 2. Calibrate accelerometer (also requires stationary)
        logger.info("Step 2/3: Accelerometer calibration")
        if self.calibrate_accelerometer():
            success_count += 1
        else:
            logger.error("Accelerometer calibration failed")
        
        time.sleep(2)
        
        # 3. Calibrate magnetometer (requires movement)
        if include_mag:
            logger.info("Step 3/3: Magnetometer calibration")
            logger.info("IMPORTANT: Rotate the aircraft 360° in all axes during this step")
            if self.calibrate_magnetometer():
                success_count += 1
            else:
                logger.error("Magnetometer calibration failed")
        else:
            logger.info("Step 3/3: Skipping magnetometer calibration")
            success_count += 1  # Count as success since it was skipped intentionally
        
        total_steps = 3 if include_mag else 2
        if success_count == total_steps:
            logger.info("Full sensor calibration completed successfully")
            return True
        else:
            logger.error(f"Sensor calibration partially failed: {success_count}/{total_steps} successful")
            return False

    def get_calibration_status(self) -> Dict[str, Any]:
        """Get sensor calibration status"""
        return {
            'calibration_in_progress': self._calibration_in_progress,
            'last_calibration': getattr(self, '_last_calibration_time', None),
            'sensors_available': self.get_sensor_status()
        }

    def is_calibration_needed(self) -> Dict[str, bool]:
        """Check if sensors need calibration based on their current readings"""
        needs_calibration = {
            'accelerometer': False,
            'magnetometer': False,
            'gyroscope': False
        }
        
        sensor_status = self.get_sensor_status()
        if not sensor_status:
            return needs_calibration
        
        health = sensor_status.get('health_status', {})
        
        # Check if sensors are unhealthy (may need calibration)
        needs_calibration['accelerometer'] = not health.get('accelerometer_healthy', True)
        needs_calibration['magnetometer'] = not health.get('magnetometer_healthy', True)
        needs_calibration['gyroscope'] = not health.get('gyroscope_healthy', True)
        
        return needs_calibration

    def wait_for_gps_fix(self, min_satellites: int = 6, timeout_seconds: int = 60) -> bool:
        """Wait for GPS to achieve good fix"""
        logger.info(f"Waiting for GPS fix with {min_satellites}+ satellites...")
        
        from .telemetry import Telemetry
        telem = Telemetry(self.conn)
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            gps_data = telem.get_gps()
            if gps_data:
                sats = gps_data['num_satellites']
                fix_type = gps_data['fix_type']
                
                if sats >= min_satellites and fix_type in ['FIX_3D']:
                    logger.info(f"GPS fix achieved: {sats} satellites, {fix_type}")
                    return True
                
                logger.info(f"GPS status: {sats} satellites, {fix_type}")
            
            time.sleep(2)
        
        logger.warning(f"GPS fix timeout after {timeout_seconds} seconds")
        return False

    def sensor_warmup(self, duration_seconds: int = 30) -> bool:
        """Allow sensors to warm up and stabilize"""
        logger.info(f"Sensor warmup period: {duration_seconds} seconds")
        
        from .telemetry import Telemetry
        telem = Telemetry(self.conn)
        
        start_time = time.time()
        last_report = 0
        
        while time.time() - start_time < duration_seconds:
            elapsed = time.time() - start_time
            
            # Report progress every 10 seconds
            if elapsed - last_report >= 10:
                remaining = duration_seconds - elapsed
                logger.info(f"Warmup in progress... {remaining:.0f} seconds remaining")
                last_report = elapsed
                
                # Check sensor status
                status = telem.get_status()
                if status:
                    logger.debug(f"Sensors detected: {status.get('sensors_detected', {})}")
            
            time.sleep(1)
        
        logger.info("Sensor warmup completed")
        return True
