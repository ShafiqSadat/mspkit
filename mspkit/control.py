import struct
import time
import logging
from typing import List, Dict, Any, Optional
from .msp_constants import MSPCommands, RC_CHANNELS, PWM_VALUES, FlightController, FlightModes

logger = logging.getLogger(__name__)

class Control:
    """Enhanced control class with safety features and multi-FC support"""
    
    def __init__(self, conn):
        self.conn = conn
        self.fc_type = conn.fc_type
        self._last_rc_values: List[int] = [PWM_VALUES['NEUTRAL']] * 16
        self._safety_enabled = True
        self._is_armed = False
        
    def enable_safety(self, enabled: bool = True):
        """Enable/disable safety checks"""
        self._safety_enabled = enabled
        logger.info(f"Safety checks {'enabled' if enabled else 'disabled'}")
        
    def _validate_channel_value(self, value: int) -> int:
        """Validate and clamp PWM channel value"""
        return max(PWM_VALUES['MIN'], min(PWM_VALUES['MAX'], value))
    
    def _validate_channels(self, channels: List[int]) -> List[int]:
        """Validate all channel values"""
        validated = []
        for i, value in enumerate(channels):
            if isinstance(value, (int, float)):
                validated.append(self._validate_channel_value(int(value)))
            else:
                logger.warning(f"Invalid channel {i} value: {value}, using neutral")
                validated.append(PWM_VALUES['NEUTRAL'])
        return validated
    
    def _check_armed_state(self) -> bool:
        """Check if the aircraft is armed"""
        # Import here to avoid circular import
        from .telemetry import Telemetry
        telem = Telemetry(self.conn)
        status = telem.get_status()
        if status:
            self._is_armed = status.get('armed', False)
            return self._is_armed
        return False
    
    def _safety_check(self, operation: str) -> bool:
        """Perform safety checks before critical operations"""
        if not self._safety_enabled:
            return True
            
        if operation in ['arm', 'disarm']:
            return True  # Always allow arming/disarming
            
        if operation in ['emergency_stop', 'failsafe']:
            return True  # Always allow emergency operations
            
        # Check if armed for flight operations
        if operation in ['send_rc', 'set_throttle']:
            armed = self._check_armed_state()
            if not armed and operation == 'set_throttle':
                logger.error("Cannot set throttle when disarmed")
                return False
                
        return True

    def send_rc(self, channels: List[int], validate: bool = True) -> bool:
        """Send RC channel values with validation and safety checks"""
        if not self._safety_check('send_rc'):
            return False
            
        if validate:
            channels = self._validate_channels(channels)
            
        # Ensure we have at least 8 channels
        while len(channels) < 8:
            channels.append(PWM_VALUES['NEUTRAL'])
            
        # Limit to 16 channels (MSP limitation)
        channels = channels[:16]
        
        try:
            # Pack up to 16 channels
            data = struct.pack(f'<{len(channels)}H', *channels)
            self.conn.send_msp(MSPCommands.MSP_SET_RAW_RC, data)
            self._last_rc_values = channels.copy()
            logger.debug(f"Sent RC channels: {channels[:8]}")
            return True
        except Exception as e:
            logger.error(f"Failed to send RC channels: {e}")
            return False

    def arm(self, throttle_check: bool = True) -> bool:
        """Arm the aircraft with safety checks"""
        if throttle_check and self._safety_enabled:
            # Check throttle is low
            if (len(self._last_rc_values) > RC_CHANNELS['THROTTLE'] and 
                self._last_rc_values[RC_CHANNELS['THROTTLE']] > PWM_VALUES['ARM_THRESHOLD']):
                logger.error("Cannot arm: throttle too high")
                return False
        
        # Standard arming sequence: Yaw right + low throttle
        channels = [PWM_VALUES['NEUTRAL']] * 16
        channels[RC_CHANNELS['THROTTLE']] = PWM_VALUES['MIN']
        channels[RC_CHANNELS['YAW']] = PWM_VALUES['MAX']  # Yaw right
        
        # Send arming command
        success = self.send_rc(channels, validate=False)
        if success:
            time.sleep(0.5)  # Hold for arming
            # Return to neutral
            channels[RC_CHANNELS['YAW']] = PWM_VALUES['NEUTRAL']
            self.send_rc(channels, validate=False)
            logger.info("Arming sequence sent")
            
        return success

    def disarm(self, force: bool = False) -> bool:
        """Disarm the aircraft"""
        if not force and self._safety_enabled:
            # Check if safe to disarm (low throttle)
            if (len(self._last_rc_values) > RC_CHANNELS['THROTTLE'] and 
                self._last_rc_values[RC_CHANNELS['THROTTLE']] > PWM_VALUES['DISARM_THRESHOLD']):
                logger.warning("Disarming with throttle not at minimum")
        
        # Standard disarming sequence: Yaw left + low throttle
        channels = [PWM_VALUES['NEUTRAL']] * 16
        channels[RC_CHANNELS['THROTTLE']] = PWM_VALUES['MIN']
        channels[RC_CHANNELS['YAW']] = PWM_VALUES['MIN']  # Yaw left
        
        success = self.send_rc(channels, validate=False)
        if success:
            time.sleep(0.5)  # Hold for disarming
            # Return to neutral
            channels[RC_CHANNELS['YAW']] = PWM_VALUES['NEUTRAL']
            self.send_rc(channels, validate=False)
            logger.info("Disarming sequence sent")
            
        return success

    def emergency_stop(self) -> bool:
        """Emergency stop - immediately cut throttle and disarm"""
        logger.warning("EMERGENCY STOP activated")
        
        # Cut throttle immediately
        channels = [PWM_VALUES['NEUTRAL']] * 16
        channels[RC_CHANNELS['THROTTLE']] = PWM_VALUES['MIN']
        
        success = self.send_rc(channels, validate=False)
        if success:
            # Attempt to disarm
            self.disarm(force=True)
            
        return success

    def set_throttle(self, throttle_percent: float) -> bool:
        """Set throttle as percentage (0-100)"""
        if not self._safety_check('set_throttle'):
            return False
            
        throttle_percent = max(0, min(100, throttle_percent))
        throttle_pwm = int(PWM_VALUES['MIN'] + 
                          (throttle_percent / 100.0) * 
                          (PWM_VALUES['MAX'] - PWM_VALUES['MIN']))
        
        channels = self._last_rc_values.copy()
        channels[RC_CHANNELS['THROTTLE']] = throttle_pwm
        
        return self.send_rc(channels)

    def set_attitude(self, roll_percent: float = 0, pitch_percent: float = 0, 
                    yaw_percent: float = 0, throttle_percent: Optional[float] = None) -> bool:
        """Set attitude control inputs as percentages (-100 to 100 for roll/pitch/yaw)"""
        if not self._safety_check('send_rc'):
            return False
            
        # Clamp values
        roll_percent = max(-100, min(100, roll_percent))
        pitch_percent = max(-100, min(100, pitch_percent))
        yaw_percent = max(-100, min(100, yaw_percent))
        
        # Convert to PWM values
        roll_pwm = int(PWM_VALUES['NEUTRAL'] + (roll_percent / 100.0) * 500)
        pitch_pwm = int(PWM_VALUES['NEUTRAL'] + (pitch_percent / 100.0) * 500)
        yaw_pwm = int(PWM_VALUES['NEUTRAL'] + (yaw_percent / 100.0) * 500)
        
        channels = self._last_rc_values.copy()
        channels[RC_CHANNELS['ROLL']] = roll_pwm
        channels[RC_CHANNELS['PITCH']] = pitch_pwm
        channels[RC_CHANNELS['YAW']] = yaw_pwm
        
        if throttle_percent is not None:
            throttle_percent = max(0, min(100, throttle_percent))
            throttle_pwm = int(PWM_VALUES['MIN'] + 
                              (throttle_percent / 100.0) * 
                              (PWM_VALUES['MAX'] - PWM_VALUES['MIN']))
            channels[RC_CHANNELS['THROTTLE']] = throttle_pwm
        
        return self.send_rc(channels)

    def set_aux_channel(self, aux_number: int, value: int) -> bool:
        """Set auxiliary channel value"""
        if aux_number < 1 or aux_number > 8:
            logger.error(f"Invalid AUX channel number: {aux_number}")
            return False
            
        channel_index = RC_CHANNELS['AUX1'] + (aux_number - 1)
        if channel_index >= len(self._last_rc_values):
            logger.error(f"AUX{aux_number} channel index out of range")
            return False
            
        channels = self._last_rc_values.copy()
        channels[channel_index] = self._validate_channel_value(value)
        
        return self.send_rc(channels)

    def set_flight_mode(self, mode: str, enable: bool = True) -> bool:
        """Set flight mode using predefined configurations"""
        aux_value = PWM_VALUES['MAX'] if enable else PWM_VALUES['MIN']
        
        # Common modes for both FC types
        mode_mappings = {
            'ANGLE': ('AUX1', 1),
            'HORIZON': ('AUX1', 2),  # Three-position switch
            'MAG': ('AUX2', 1),
            'BARO': ('AUX3', 1),
            'HEADFREE': ('AUX4', 1),
        }
        
        # FC-specific modes
        if self.fc_type == FlightController.INAV:
            mode_mappings.update({
                'NAV_ALTHOLD': ('AUX5', 1),
                'NAV_POSHOLD': ('AUX6', 1),
                'NAV_RTH': ('AUX7', 1),
                'NAV_WP': ('AUX8', 1),
                'MANUAL': ('AUX2', 2),  # Example mapping
            })
        elif self.fc_type == FlightController.BETAFLIGHT:
            mode_mappings.update({
                'ACRO_TRAINER': ('AUX5', 1),
                'OSD_SW': ('AUX6', 1),
                'TURTLE': ('AUX7', 1),  # Turtle mode
                'VTX_PIT': ('AUX8', 1),  # VTX pit mode
            })
        
        if mode not in mode_mappings:
            logger.error(f"Unknown flight mode: {mode}")
            return False
            
        aux_name, aux_num = mode_mappings[mode]
        aux_channel = int(aux_name.replace('AUX', ''))
        
        return self.set_aux_channel(aux_channel, aux_value)

    # Convenience methods for common flight modes
    def enable_angle_mode(self) -> bool:
        """Enable angle (stabilized) mode"""
        return self.set_flight_mode('ANGLE', True)
    
    def enable_horizon_mode(self) -> bool:
        """Enable horizon mode"""
        return self.set_flight_mode('HORIZON', True)
    
    def enable_manual_mode(self) -> bool:
        """Enable manual mode (acro for Betaflight)"""
        if self.fc_type == FlightController.BETAFLIGHT:
            # Disable angle and horizon for acro
            self.set_flight_mode('ANGLE', False)
            self.set_flight_mode('HORIZON', False)
            return True
        else:
            return self.set_flight_mode('MANUAL', True)

    # iNav specific navigation modes
    def enable_nav_althold(self) -> bool:
        """Enable altitude hold mode (iNav)"""
        if self.fc_type != FlightController.INAV:
            logger.warning("Altitude hold only available on iNav")
            return False
        return self.set_flight_mode('NAV_ALTHOLD', True)
    
    def enable_nav_poshold(self) -> bool:
        """Enable position hold mode (iNav)"""
        if self.fc_type != FlightController.INAV:
            logger.warning("Position hold only available on iNav")
            return False
        return self.set_flight_mode('NAV_POSHOLD', True)
    
    def enable_nav_rth(self) -> bool:
        """Enable return to home mode (iNav)"""
        if self.fc_type != FlightController.INAV:
            logger.warning("RTH only available on iNav")
            return False
        return self.set_flight_mode('NAV_RTH', True)
    
    def enable_nav_wp(self) -> bool:
        """Enable waypoint mode (iNav)"""
        if self.fc_type != FlightController.INAV:
            logger.warning("Waypoint mode only available on iNav")
            return False
        return self.set_flight_mode('NAV_WP', True)

    def get_last_rc_values(self) -> List[int]:
        """Get the last sent RC channel values"""
        return self._last_rc_values.copy()
    
    def reset_rc_channels(self) -> bool:
        """Reset all RC channels to neutral/safe values"""
        channels = [PWM_VALUES['NEUTRAL']] * 16
        channels[RC_CHANNELS['THROTTLE']] = PWM_VALUES['MIN']  # Throttle to minimum
        return self.send_rc(channels)
