import struct
import time
import logging
from typing import Dict, Any, Optional, List
from .msp_constants import MSPCommands, FlightController

logger = logging.getLogger(__name__)

class Config:
    """Enhanced configuration management for flight controllers"""
    
    def __init__(self, conn):
        self.conn = conn
        self.fc_type = conn.fc_type
    
    def save_settings(self) -> bool:
        """Save current settings to EEPROM"""
        try:
            self.conn.send_msp(MSPCommands.MSP_EEPROM_WRITE)
            logger.info("Settings saved to EEPROM")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def reset_settings(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self.conn.send_msp(MSPCommands.MSP_RESET_CONF)
            logger.warning("Settings reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to reset settings: {e}")
            return False

    def select_profile(self, profile_id: int) -> bool:
        """Select PID/rate profile"""
        if profile_id < 0 or profile_id > 2:
            logger.error("Profile ID must be 0-2")
            return False
            
        try:
            data = struct.pack('<B', profile_id)
            self.conn.send_msp(MSPCommands.MSP_SELECT_SETTING, data)
            logger.info(f"Selected profile {profile_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to select profile: {e}")
            return False

    def get_pid_values(self) -> Optional[Dict[str, Any]]:
        """Get PID controller values"""
        self.conn.send_msp(MSPCommands.MSP_PID)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_PID and data:
            pids = {}
            pid_names = ['ROLL', 'PITCH', 'YAW', 'ALT', 'Pos', 'PosR', 'NavR', 'LEVEL', 'MAG', 'VEL']
            
            for i in range(min(len(pid_names), len(data) // 3)):
                offset = i * 3
                if offset + 2 < len(data):
                    p = data[offset]
                    i_val = data[offset + 1]
                    d = data[offset + 2]
                    pids[pid_names[i]] = {'P': p, 'I': i_val, 'D': d}
                    
            return pids
        return None

    def set_pid_values(self, pids: Dict[str, Dict[str, int]]) -> bool:
        """Set PID controller values"""
        try:
            # Get current PIDs first
            current_pids = self.get_pid_values()
            if not current_pids:
                logger.error("Could not retrieve current PID values")
                return False
            
            # Update with new values
            for axis, values in pids.items():
                if axis in current_pids:
                    if 'P' in values:
                        current_pids[axis]['P'] = max(0, min(255, values['P']))
                    if 'I' in values:
                        current_pids[axis]['I'] = max(0, min(255, values['I']))
                    if 'D' in values:
                        current_pids[axis]['D'] = max(0, min(255, values['D']))
            
            # Pack data for sending
            data = bytearray()
            for axis in ['ROLL', 'PITCH', 'YAW', 'ALT', 'Pos', 'PosR', 'NavR', 'LEVEL', 'MAG', 'VEL']:
                if axis in current_pids:
                    data.extend([
                        current_pids[axis]['P'],
                        current_pids[axis]['I'], 
                        current_pids[axis]['D']
                    ])
                else:
                    data.extend([0, 0, 0])  # Default values
            
            self.conn.send_msp(MSPCommands.MSP_SET_PID, bytes(data))
            logger.info("PID values updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set PID values: {e}")
            return False

    def get_rc_tuning(self) -> Optional[Dict[str, Any]]:
        """Get RC tuning parameters (rates, expo, etc.)"""
        self.conn.send_msp(MSPCommands.MSP_RC_TUNING)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_RC_TUNING and data:
            if len(data) >= 7:
                result = {
                    'rc_rate': data[0] / 100.0,
                    'rc_expo': data[1] / 100.0,
                    'roll_pitch_rate': data[2] / 100.0,
                    'yaw_rate': data[3] / 100.0,
                    'dyn_thr_pid': data[4] / 100.0,
                    'throttle_mid': data[5] / 100.0,
                    'throttle_expo': data[6] / 100.0
                }
                
                # Extended parameters if available
                if len(data) >= 11:
                    result.update({
                        'thr_pid_attenuation': data[7] / 100.0,
                        'rc_yaw_expo': data[8] / 100.0,
                        'rc_yaw_rate': data[9] / 100.0,
                        'rc_pitch_rate': data[10] / 100.0
                    })
                
                return result
        return None

    def set_rc_tuning(self, params: Dict[str, float]) -> bool:
        """Set RC tuning parameters"""
        try:
            current = self.get_rc_tuning()
            if not current:
                logger.error("Could not retrieve current RC tuning")
                return False
            
            # Update with new values
            for key, value in params.items():
                if key in current:
                    current[key] = max(0.0, min(2.55, value))  # Clamp to valid range
            
            # Pack data
            data = [
                int(current['rc_rate'] * 100),
                int(current['rc_expo'] * 100),
                int(current['roll_pitch_rate'] * 100),
                int(current['yaw_rate'] * 100),
                int(current['dyn_thr_pid'] * 100),
                int(current['throttle_mid'] * 100),
                int(current['throttle_expo'] * 100)
            ]
            
            # Extended parameters if supported
            if 'thr_pid_attenuation' in current:
                data.extend([
                    int(current['thr_pid_attenuation'] * 100),
                    int(current['rc_yaw_expo'] * 100),
                    int(current['rc_yaw_rate'] * 100),
                    int(current['rc_pitch_rate'] * 100)
                ])
            
            self.conn.send_msp(MSPCommands.MSP_SET_RC_TUNING, bytes(data))
            logger.info("RC tuning updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set RC tuning: {e}")
            return False

    def get_features(self) -> Optional[Dict[str, bool]]:
        """Get enabled features"""
        self.conn.send_msp(MSPCommands.MSP_FEATURE)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_FEATURE and data:
            if len(data) >= 4:
                feature_mask = struct.unpack('<I', data[:4])[0]
                
                # Common features
                features = {
                    'RX_PPM': bool(feature_mask & (1 << 0)),
                    'VBAT': bool(feature_mask & (1 << 1)),
                    'INFLIGHT_ACC_CAL': bool(feature_mask & (1 << 2)),
                    'RX_SERIAL': bool(feature_mask & (1 << 3)),
                    'MOTOR_STOP': bool(feature_mask & (1 << 4)),
                    'SERVO_TILT': bool(feature_mask & (1 << 5)),
                    'SOFTSERIAL': bool(feature_mask & (1 << 6)),
                    'GPS': bool(feature_mask & (1 << 7)),
                    'FAILSAFE': bool(feature_mask & (1 << 8)),
                    'SONAR': bool(feature_mask & (1 << 9)),
                    'TELEMETRY': bool(feature_mask & (1 << 10)),
                    'CURRENT_METER': bool(feature_mask & (1 << 11)),
                    '3D': bool(feature_mask & (1 << 12)),
                    'RX_PARALLEL_PWM': bool(feature_mask & (1 << 13)),
                    'RX_MSP': bool(feature_mask & (1 << 14)),
                    'RSSI_ADC': bool(feature_mask & (1 << 15)),
                    'LED_STRIP': bool(feature_mask & (1 << 16)),
                    'DISPLAY': bool(feature_mask & (1 << 17)),
                    'OSD': bool(feature_mask & (1 << 18)),
                    'BLACKBOX': bool(feature_mask & (1 << 19)),
                    'CHANNEL_FORWARDING': bool(feature_mask & (1 << 20)),
                    'TRANSPONDER': bool(feature_mask & (1 << 21)),
                    'AIRMODE': bool(feature_mask & (1 << 22))
                }
                
                # FC-specific features
                if self.fc_type == FlightController.INAV:
                    features.update({
                        'NAV': bool(feature_mask & (1 << 23)),
                        'FW_LAUNCH': bool(feature_mask & (1 << 24)),
                        'FW_AUTOTRIM': bool(feature_mask & (1 << 25))
                    })
                elif self.fc_type == FlightController.BETAFLIGHT:
                    features.update({
                        'ANTI_GRAVITY': bool(feature_mask & (1 << 23)),
                        'ESC_SENSOR': bool(feature_mask & (1 << 24))
                    })
                
                return features
        return None

    def set_feature(self, feature_name: str, enabled: bool) -> bool:
        """Enable/disable a specific feature"""
        try:
            current_features = self.get_features()
            if not current_features:
                logger.error("Could not retrieve current features")
                return False
            
            if feature_name not in current_features:
                logger.error(f"Unknown feature: {feature_name}")
                return False
            
            # Update feature
            current_features[feature_name] = enabled
            
            # Build feature mask
            feature_mask = 0
            feature_bits = {
                'RX_PPM': 0, 'VBAT': 1, 'INFLIGHT_ACC_CAL': 2, 'RX_SERIAL': 3,
                'MOTOR_STOP': 4, 'SERVO_TILT': 5, 'SOFTSERIAL': 6, 'GPS': 7,
                'FAILSAFE': 8, 'SONAR': 9, 'TELEMETRY': 10, 'CURRENT_METER': 11,
                '3D': 12, 'RX_PARALLEL_PWM': 13, 'RX_MSP': 14, 'RSSI_ADC': 15,
                'LED_STRIP': 16, 'DISPLAY': 17, 'OSD': 18, 'BLACKBOX': 19,
                'CHANNEL_FORWARDING': 20, 'TRANSPONDER': 21, 'AIRMODE': 22
            }
            
            # FC-specific features
            if self.fc_type == FlightController.INAV:
                feature_bits.update({'NAV': 23, 'FW_LAUNCH': 24, 'FW_AUTOTRIM': 25})
            elif self.fc_type == FlightController.BETAFLIGHT:
                feature_bits.update({'ANTI_GRAVITY': 23, 'ESC_SENSOR': 24})
            
            for feature, bit in feature_bits.items():
                if feature in current_features and current_features[feature]:
                    feature_mask |= (1 << bit)
            
            data = struct.pack('<I', feature_mask)
            self.conn.send_msp(MSPCommands.MSP_SET_FEATURE, data)
            logger.info(f"Feature {feature_name} {'enabled' if enabled else 'disabled'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set feature: {e}")
            return False

    def get_misc_settings(self) -> Optional[Dict[str, Any]]:
        """Get miscellaneous settings"""
        self.conn.send_msp(MSPCommands.MSP_MISC)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_MISC and data:
            if len(data) >= 22:
                mid_rc, min_throttle, max_throttle, min_command = struct.unpack('<HHHH', data[0:8])
                failsafe_throttle = struct.unpack('<H', data[8:10])[0]
                gps_provider, gps_baudrate, gps_ubx_sbas = struct.unpack('<BBB', data[10:13])
                multiwii_current_meter_output = data[13]
                rssi_channel = data[14]
                placeholder1 = data[15]
                mag_declination = struct.unpack('<h', data[16:18])[0] / 10.0
                vbat_scale, vbat_min, vbat_max = struct.unpack('<BBB', data[18:21])
                vbat_warning = data[21]
                
                return {
                    'mid_rc': mid_rc,
                    'min_throttle': min_throttle,
                    'max_throttle': max_throttle,
                    'min_command': min_command,
                    'failsafe_throttle': failsafe_throttle,
                    'gps_provider': gps_provider,
                    'gps_baudrate': gps_baudrate,
                    'gps_ubx_sbas': gps_ubx_sbas,
                    'multiwii_current_meter_output': multiwii_current_meter_output,
                    'rssi_channel': rssi_channel,
                    'mag_declination': mag_declination,
                    'vbat_scale': vbat_scale,
                    'vbat_min': vbat_min,
                    'vbat_max': vbat_max,
                    'vbat_warning': vbat_warning
                }
        return None

    def set_misc_settings(self, settings: Dict[str, Any]) -> bool:
        """Set miscellaneous settings"""
        try:
            current = self.get_misc_settings()
            if not current:
                logger.error("Could not retrieve current misc settings")
                return False
            
            # Update with new values
            current.update(settings)
            
            # Pack data
            data = struct.pack('<HHHHHBBBBBBHBBB',
                current['mid_rc'],
                current['min_throttle'],
                current['max_throttle'],
                current['min_command'],
                current['failsafe_throttle'],
                current['gps_provider'],
                current['gps_baudrate'],
                current['gps_ubx_sbas'],
                current['multiwii_current_meter_output'],
                current['rssi_channel'],
                0,  # placeholder
                int(current['mag_declination'] * 10),
                current['vbat_scale'],
                current['vbat_min'],
                current['vbat_max']
            )
            
            self.conn.send_msp(MSPCommands.MSP_SET_MISC, data)
            logger.info("Misc settings updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set misc settings: {e}")
            return False

    def get_box_names(self) -> Optional[List[str]]:
        """Get flight mode box names"""
        self.conn.send_msp(MSPCommands.MSP_BOXNAMES)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_BOXNAMES and data:
            names_str = data.decode('ascii').rstrip('\x00')
            return names_str.split(';') if names_str else []
        return None

    def get_box_ids(self) -> Optional[List[int]]:
        """Get flight mode box IDs"""
        self.conn.send_msp(MSPCommands.MSP_BOXIDS)
        code, data = self.conn.read_response()
        if code == MSPCommands.MSP_BOXIDS and data:
            return list(data)
        return None

    def backup_settings(self) -> Optional[Dict[str, Any]]:
        """Create a backup of current settings"""
        backup = {
            'timestamp': time.time(),
            'fc_type': self.fc_type.name,
            'pids': self.get_pid_values(),
            'rc_tuning': self.get_rc_tuning(),
            'features': self.get_features(),
            'misc': self.get_misc_settings(),
            'box_names': self.get_box_names(),
            'box_ids': self.get_box_ids()
        }
        
        # Remove None values
        backup = {k: v for k, v in backup.items() if v is not None}
        
        if len(backup) > 2:  # More than just timestamp and fc_type
            logger.info("Settings backup created")
            return backup
        else:
            logger.error("Failed to create settings backup")
            return None

    def restore_settings(self, backup: Dict[str, Any]) -> bool:
        """Restore settings from backup"""
        try:
            success_count = 0
            
            if 'pids' in backup and backup['pids']:
                if self.set_pid_values(backup['pids']):
                    success_count += 1
            
            if 'rc_tuning' in backup and backup['rc_tuning']:
                if self.set_rc_tuning(backup['rc_tuning']):
                    success_count += 1
            
            if 'misc' in backup and backup['misc']:
                if self.set_misc_settings(backup['misc']):
                    success_count += 1
            
            # Restore features
            if 'features' in backup and backup['features']:
                for feature, enabled in backup['features'].items():
                    self.set_feature(feature, enabled)
                success_count += 1
            
            if success_count > 0:
                logger.info(f"Settings restored ({success_count} categories)")
                return True
            else:
                logger.error("No settings were restored")
                return False
                
        except Exception as e:
            logger.error(f"Failed to restore settings: {e}")
            return False
