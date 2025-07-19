import struct
import logging
from typing import Dict, Any, Optional, List
from .msp_constants import MSPCommands, MSPv2Commands, FlightController, SensorStatus, GPSFixType, NavState

logger = logging.getLogger(__name__)

class Telemetry:
    """Enhanced telemetry class supporting both iNav and Betaflight"""
    
    def __init__(self, conn):
        self.conn = conn
        self.fc_type = conn.fc_type
        
    def get_api_version(self) -> Optional[Dict[str, Any]]:
        """Get flight controller API version"""
        self.conn.send_msp(MSPCommands.MSP_API_VERSION)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_API_VERSION and data:
            if len(data) >= 3:
                version = f"{data[1]}.{data[2]}.{data[0]}"
                return {"api_version": version, "protocol_version": data[0]}
        return None
    
    def get_fc_variant(self) -> Optional[Dict[str, Any]]:
        """Get flight controller variant (INAV, BTFL, etc.)"""
        self.conn.send_msp(MSPCommands.MSP_FC_VARIANT)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_FC_VARIANT and data:
            variant = data.decode('ascii').rstrip('\x00')
            return {"fc_variant": variant}
        return None
    
    def get_fc_version(self) -> Optional[Dict[str, Any]]:
        """Get flight controller version"""
        self.conn.send_msp(MSPCommands.MSP_FC_VERSION)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_FC_VERSION and data:
            if len(data) >= 3:
                version = f"{data[0]}.{data[1]}.{data[2]}"
                return {"fc_version": version}
        return None
    
    def get_board_info(self) -> Optional[Dict[str, Any]]:
        """Get board information"""
        self.conn.send_msp(MSPCommands.MSP_BOARD_INFO)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_BOARD_INFO and data:
            if len(data) >= 8:
                board_id = data[:4].decode('ascii').rstrip('\x00')
                hardware_revision = struct.unpack('<H', data[4:6])[0]
                return {
                    "board_identifier": board_id,
                    "hardware_revision": hardware_revision
                }
        return None

    def get_attitude(self) -> Optional[Dict[str, float]]:
        """Get attitude (roll, pitch, yaw)"""
        self.conn.send_msp(MSPCommands.MSP_ATTITUDE)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_ATTITUDE and data:
            if len(data) >= 6:
                roll, pitch, yaw = struct.unpack('<hhh', data[:6])
                return {
                    "roll": roll / 10.0,
                    "pitch": pitch / 10.0, 
                    "yaw": yaw
                }
        return None

    def get_raw_imu(self) -> Optional[Dict[str, Any]]:
        """Get raw IMU data (accelerometer, gyroscope, magnetometer)"""
        self.conn.send_msp(MSPCommands.MSP_RAW_IMU)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_RAW_IMU and data:
            if len(data) >= 18:
                acc_x, acc_y, acc_z = struct.unpack('<hhh', data[0:6])
                gyro_x, gyro_y, gyro_z = struct.unpack('<hhh', data[6:12])
                mag_x, mag_y, mag_z = struct.unpack('<hhh', data[12:18])
                return {
                    "accelerometer": {"x": acc_x, "y": acc_y, "z": acc_z},
                    "gyroscope": {"x": gyro_x, "y": gyro_y, "z": gyro_z},
                    "magnetometer": {"x": mag_x, "y": mag_y, "z": mag_z}
                }
        return None

    def get_gps(self) -> Optional[Dict[str, Any]]:
        """Get GPS data"""
        self.conn.send_msp(MSPCommands.MSP_RAW_GPS)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_RAW_GPS and data:
            if len(data) >= 16:
                fix_type = data[0]
                num_sats = data[1] 
                lat, lon, alt = struct.unpack('<iii', data[2:14])
                speed, ground_course = struct.unpack('<HH', data[14:18]) if len(data) >= 18 else (0, 0)
                
                return {
                    "fix_type": GPSFixType(fix_type).name,
                    "num_satellites": num_sats,
                    "latitude": lat / 1e7,
                    "longitude": lon / 1e7,
                    "altitude": alt / 100.0,
                    "speed": speed / 100.0,  # m/s
                    "ground_course": ground_course / 10.0  # degrees
                }
        return None

    def get_altitude(self) -> Optional[Dict[str, Any]]:
        """Get altitude data"""
        self.conn.send_msp(MSPCommands.MSP_ALTITUDE)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_ALTITUDE and data:
            if len(data) >= 6:
                altitude, vario = struct.unpack('<ih', data[:6])
                return {
                    "altitude": altitude / 100.0,  # meters
                    "vertical_speed": vario  # cm/s
                }
        return None

    def get_analog(self) -> Optional[Dict[str, Any]]:
        """Get analog sensor data (battery, current, etc.)"""
        self.conn.send_msp(MSPCommands.MSP_ANALOG)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_ANALOG and data:
            if len(data) >= 7:
                voltage = data[0] / 10.0  # Volts
                mah_drawn = struct.unpack('<H', data[1:3])[0]  # mAh
                rssi = struct.unpack('<H', data[3:5])[0]
                amperage = struct.unpack('<h', data[5:7])[0] / 100.0  # Amps
                
                result = {
                    "voltage": voltage,
                    "mah_drawn": mah_drawn,
                    "rssi": rssi,
                    "amperage": amperage
                }
                
                # Extended data for newer firmware
                if len(data) >= 9:
                    voltage_2 = struct.unpack('<H', data[7:9])[0] / 100.0
                    result["voltage_2"] = voltage_2
                    
                return result
        return None

    def get_battery_state(self) -> Optional[Dict[str, Any]]:
        """Get detailed battery state (if supported)"""
        self.conn.send_msp(MSPCommands.MSP_BATTERY_STATE)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_BATTERY_STATE and data:
            if len(data) >= 8:
                cells = data[0]
                capacity = struct.unpack('<H', data[1:3])[0]
                voltage = data[3] / 10.0
                mah_drawn = struct.unpack('<H', data[4:6])[0]
                amperage = struct.unpack('<h', data[6:8])[0] / 100.0
                
                result = {
                    "cell_count": cells,
                    "capacity": capacity,
                    "voltage": voltage,
                    "mah_drawn": mah_drawn,
                    "amperage": amperage
                }
                
                # Battery state flags (if available)
                if len(data) >= 9:
                    state = data[8]
                    result["state"] = state
                    result["battery_ok"] = (state & 0x01) == 0
                    result["battery_warning"] = (state & 0x02) != 0
                    result["battery_critical"] = (state & 0x04) != 0
                    
                return result
        return None

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get flight controller status"""
        self.conn.send_msp(MSPCommands.MSP_STATUS)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_STATUS and data:
            if len(data) >= 11:
                cycle_time, i2c_errors, sensor, flags = struct.unpack('<HHHH', data[:8])
                current_conf = data[8]
                
                # Parse sensor status
                sensors_detected = {
                    "accelerometer": bool(sensor & SensorStatus.ACC),
                    "barometer": bool(sensor & SensorStatus.BARO), 
                    "magnetometer": bool(sensor & SensorStatus.MAG),
                    "gps": bool(sensor & SensorStatus.GPS),
                    "sonar": bool(sensor & SensorStatus.SONAR),
                    "optical_flow": bool(sensor & SensorStatus.OPTICAL_FLOW),
                    "pitot": bool(sensor & SensorStatus.PITOT)
                }
                
                return {
                    "cycle_time": cycle_time,
                    "i2c_errors": i2c_errors,
                    "sensor_status": sensor,
                    "sensors_detected": sensors_detected,
                    "flight_mode_flags": flags,
                    "current_profile": current_conf,
                    "armed": bool(flags & (1 << 0)),
                    "flight_modes": self._parse_flight_modes(flags)
                }
        return None

    def get_status_ex(self) -> Optional[Dict[str, Any]]:
        """Get extended status (if supported)"""
        self.conn.send_msp(MSPCommands.MSP_STATUS_EX)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_STATUS_EX and data:
            status = self.get_status()
            if status and len(data) >= 13:
                # Additional data in STATUS_EX
                current_pid_profile = data[11]
                status["current_pid_profile"] = current_pid_profile
                
                if len(data) >= 15:
                    cpu_load = struct.unpack('<H', data[13:15])[0]
                    status["cpu_load"] = cpu_load
                    
                return status
        return None

    def get_nav_status(self) -> Optional[Dict[str, Any]]:
        """Get navigation status (iNav specific)"""
        if self.fc_type != FlightController.INAV:
            logger.warning("Navigation status only available on iNav")
            return None
            
        self.conn.send_msp(MSPCommands.MSP_NAV_STATUS)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_NAV_STATUS and data:
            if len(data) >= 7:
                nav_mode = data[0]
                nav_state = data[1]
                action = data[2]
                wp_number = data[3]
                nav_error = data[4]
                heading_hold_target = struct.unpack('<h', data[5:7])[0]
                
                return {
                    "nav_mode": nav_mode,
                    "nav_state": NavState(nav_state).name if nav_state < len(NavState) else nav_state,
                    "action": action,
                    "waypoint_number": wp_number,
                    "nav_error": nav_error,
                    "heading_hold_target": heading_hold_target
                }
        return None

    def get_rc_channels(self) -> Optional[Dict[str, Any]]:
        """Get RC channel values"""
        self.conn.send_msp(MSPCommands.MSP_RC)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_RC and data:
            channels = []
            for i in range(0, len(data), 2):
                if i + 1 < len(data):
                    channel = struct.unpack('<H', data[i:i+2])[0]
                    channels.append(channel)
                    
            return {
                "channels": channels,
                "num_channels": len(channels)
            }
        return None

    def get_motor_values(self) -> Optional[Dict[str, Any]]:
        """Get motor output values"""
        self.conn.send_msp(MSPCommands.MSP_MOTOR)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_MOTOR and data:
            motors = []
            for i in range(0, len(data), 2):
                if i + 1 < len(data):
                    motor = struct.unpack('<H', data[i:i+2])[0]
                    motors.append(motor)
                    
            return {
                "motors": motors,
                "num_motors": len(motors)
            }
        return None

    def _parse_flight_modes(self, flags: int) -> List[str]:
        """Parse flight mode flags into readable names"""
        modes = []
        if flags & (1 << 0): modes.append("ARMED")
        if flags & (1 << 1): modes.append("ANGLE")
        if flags & (1 << 2): modes.append("HORIZON")
        if flags & (1 << 3): modes.append("MAG")
        if flags & (1 << 4): modes.append("BARO")
        if flags & (1 << 5): modes.append("GPS_HOME")
        if flags & (1 << 6): modes.append("GPS_HOLD")
        if flags & (1 << 7): modes.append("HEADFREE")
        if flags & (1 << 8): modes.append("HEADADJ")
        if flags & (1 << 9): modes.append("CAMSTAB")
        
        # FC-specific modes
        if self.fc_type == FlightController.INAV:
            if flags & (1 << 10): modes.append("NAV_ALTHOLD")
            if flags & (1 << 11): modes.append("NAV_POSHOLD")
            if flags & (1 << 12): modes.append("NAV_RTH")
            if flags & (1 << 13): modes.append("NAV_WP")
            if flags & (1 << 14): modes.append("NAV_LAUNCH")
            if flags & (1 << 15): modes.append("MANUAL")
        elif self.fc_type == FlightController.BETAFLIGHT:
            if flags & (1 << 10): modes.append("ACRO_TRAINER")
            if flags & (1 << 11): modes.append("OSD_SW")
            if flags & (1 << 12): modes.append("TELEMETRY")
            
        return modes

    def get_all_telemetry(self) -> Dict[str, Any]:
        """Get comprehensive telemetry data"""
        telemetry = {}
        
        # Core telemetry
        if attitude := self.get_attitude():
            telemetry["attitude"] = attitude
            
        if gps := self.get_gps():
            telemetry["gps"] = gps
            
        if analog := self.get_analog():
            telemetry["analog"] = analog
            
        if status := self.get_status():
            telemetry["status"] = status
            
        if altitude := self.get_altitude():
            telemetry["altitude"] = altitude
            
        # Extended telemetry
        if battery := self.get_battery_state():
            telemetry["battery"] = battery
            
        if rc := self.get_rc_channels():
            telemetry["rc"] = rc
            
        if motors := self.get_motor_values():
            telemetry["motors"] = motors
            
        # iNav specific
        if self.fc_type == FlightController.INAV:
            if nav := self.get_nav_status():
                telemetry["navigation"] = nav
                
        return telemetry
