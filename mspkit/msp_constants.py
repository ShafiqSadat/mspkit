"""
MSP Command Constants for iNav and Betaflight Flight Controllers

This module contains MSP command codes for both iNav and Betaflight,
including MSP v1 and MSP v2 commands.
"""

from enum import IntEnum

class FlightController(IntEnum):
    """Supported flight controller types"""
    INAV = 1
    BETAFLIGHT = 2
    CLEANFLIGHT = 3

class MSPCommands(IntEnum):
    """Common MSP commands supported by both iNav and Betaflight"""
    
    # Status and Info
    MSP_API_VERSION = 1
    MSP_FC_VARIANT = 2
    MSP_FC_VERSION = 3
    MSP_BOARD_INFO = 4
    MSP_BUILD_INFO = 5
    MSP_STATUS = 101
    MSP_STATUS_EX = 150
    MSP_UID = 160
    
    # Configuration
    MSP_FEATURE = 36
    MSP_SET_FEATURE = 37
    MSP_BEEPER_CONFIG = 162
    MSP_SET_BEEPER_CONFIG = 163
    
    # Telemetry
    MSP_RAW_IMU = 102
    MSP_ATTITUDE = 108
    MSP_ALTITUDE = 109
    MSP_ANALOG = 110
    MSP_RAW_GPS = 106
    MSP_COMP_GPS = 107
    MSP_BATTERY_STATE = 130
    
    # RC and Control
    MSP_RC = 105
    MSP_SET_RAW_RC = 200
    MSP_RC_TUNING = 111
    MSP_SET_RC_TUNING = 204
    MSP_BOXNAMES = 116
    MSP_BOXIDS = 119
    MSP_MISC = 114
    MSP_SET_MISC = 207
    
    # PID Controller
    MSP_PID = 112
    MSP_SET_PID = 202
    MSP_PIDNAMES = 117
    MSP_PID_CONTROLLER = 59
    MSP_SET_PID_CONTROLLER = 60
    
    # Motors and Servos
    MSP_MOTOR = 104
    MSP_SET_MOTOR = 214
    MSP_SERVO = 103
    MSP_SET_SERVO = 212
    MSP_SERVO_CONFIGURATIONS = 120
    MSP_SET_SERVO_CONFIGURATION = 213
    
    # Waypoints and Navigation (iNav specific)
    MSP_WP = 118
    MSP_SET_WP = 209
    MSP_NAV_STATUS = 121
    MSP_NAV_CONFIG = 122
    MSP_SET_NAV_CONFIG = 215
    MSP_POSHOLD = 123
    MSP_SET_POSHOLD = 216
    
    # Calibration
    MSP_ACC_CALIBRATION = 205
    MSP_MAG_CALIBRATION = 206
    MSP_CALIBRATE_GYRO = 61
    
    # EEPROM
    MSP_EEPROM_WRITE = 250
    MSP_RESET_CONF = 208
    MSP_SELECT_SETTING = 210
    
    # Blackbox (Betaflight specific)
    MSP_BLACKBOX_CONFIG = 80
    MSP_SET_BLACKBOX_CONFIG = 81
    
    # OSD (Betaflight specific)
    MSP_OSD_CONFIG = 84
    MSP_SET_OSD_CONFIG = 85
    MSP_OSD_CHAR_READ = 86
    MSP_OSD_CHAR_WRITE = 87

class MSPv2Commands(IntEnum):
    """MSP v2 specific commands"""
    
    # Common MSP v2 commands
    MSP2_COMMON_SETTING = 0x1003
    MSP2_COMMON_SET_SETTING = 0x1004
    MSP2_COMMON_MOTOR_MIXER = 0x1005
    MSP2_COMMON_SET_MOTOR_MIXER = 0x1006
    
    # iNav specific MSP v2
    MSP2_INAV_STATUS = 0x2000
    MSP2_INAV_OPTICAL_FLOW = 0x2001
    MSP2_INAV_ANALOG = 0x2002
    MSP2_INAV_MISC = 0x2003
    MSP2_INAV_SET_MISC = 0x2004
    MSP2_INAV_BATTERY_CONFIG = 0x2005
    MSP2_INAV_SET_BATTERY_CONFIG = 0x2006
    MSP2_INAV_RATE_PROFILE = 0x2007
    MSP2_INAV_SET_RATE_PROFILE = 0x2008
    MSP2_INAV_AIR_SPEED = 0x2009
    MSP2_INAV_OUTPUT_MAPPING = 0x200A
    MSP2_INAV_MC_BRAKING = 0x200B
    MSP2_INAV_SET_MC_BRAKING = 0x200C
    MSP2_INAV_MIXER = 0x200D
    MSP2_INAV_SET_MIXER = 0x200E
    
    # Betaflight specific MSP v2
    MSP2_BETAFLIGHT_BIND = 0x3000
    MSP2_BETAFLIGHT_TX_INFO = 0x3001
    MSP2_BETAFLIGHT_VTX_CONFIG = 0x3002
    MSP2_BETAFLIGHT_SET_VTX_CONFIG = 0x3003

class FlightModes(IntEnum):
    """Flight mode bit positions (common for both FC types)"""
    
    # Common modes
    ARM = 0
    ANGLE = 1
    HORIZON = 2
    MAG = 3
    BARO = 4
    GPS_HOME = 5  # Return to Home
    GPS_HOLD = 6  # Position Hold
    HEADFREE = 7
    HEADADJ = 8
    CAMSTAB = 9
    
    # iNav specific modes
    NAV_ALTHOLD = 10
    NAV_POSHOLD = 11
    NAV_RTH = 12
    NAV_WP = 13
    NAV_LAUNCH = 14
    MANUAL = 15
    
    # Betaflight specific modes
    ACRO_TRAINER = 10
    OSD_SW = 11
    TELEMETRY = 12
    SERVO1 = 13
    SERVO2 = 14
    SERVO3 = 15

class SensorStatus(IntEnum):
    """Sensor status flags"""
    
    ACC = 1 << 0
    BARO = 1 << 1
    MAG = 1 << 2
    GPS = 1 << 3
    SONAR = 1 << 4
    OPTICAL_FLOW = 1 << 5
    PITOT = 1 << 6
    TEMPERATURE = 1 << 7

class GPSFixType(IntEnum):
    """GPS fix types"""
    
    NO_GPS = 0
    NO_FIX = 1
    FIX_2D = 2
    FIX_3D = 3

class NavState(IntEnum):
    """Navigation states (iNav specific)"""
    
    IDLE = 0
    ALTHOLD = 1
    POSHOLD_2D = 2
    POSHOLD_3D = 3
    RTH_START = 4
    RTH_ENROUTE = 5
    RTH_LOITER = 6
    RTH_LANDING = 7
    RTH_FINISHING = 8
    RTH_FINISHED = 9
    WP_ENROUTE = 10
    WP_REACHED = 11
    MANUAL = 12
    EMERGENCY_LANDING = 13
    LAUNCH = 14
    COURSE_HOLD = 15
    CRUISE = 16

class FailsafePhase(IntEnum):
    """Failsafe phases"""
    
    IDLE = 0
    RX_LOSS_DETECTED = 1
    LANDING = 2
    LANDED = 3
    RX_LOSS_MONITORING = 4
    RX_LOSS_RECOVERED = 5
    GPS_RESCUE = 6

# RC Channel mappings (typical setup)
RC_CHANNELS = {
    'ROLL': 0,
    'PITCH': 1,
    'YAW': 2,
    'THROTTLE': 3,
    'AUX1': 4,
    'AUX2': 5,
    'AUX3': 6,
    'AUX4': 7,
    'AUX5': 8,
    'AUX6': 9,
    'AUX7': 10,
    'AUX8': 11
}

# Standard PWM values
PWM_VALUES = {
    'MIN': 1000,
    'NEUTRAL': 1500,
    'MAX': 2000,
    'ARM_THRESHOLD': 1300,
    'DISARM_THRESHOLD': 1300
}
