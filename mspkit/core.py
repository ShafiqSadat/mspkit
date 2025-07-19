import serial
import struct
import time
import logging
from typing import Optional, Tuple, Union
from enum import IntEnum
from .msp_constants import FlightController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MSP Protocol Constants
MSP_V1_HEADER = b'$M<'
MSP_V2_HEADER = b'$X<'
MSP_V1_RESPONSE = b'$M>'
MSP_V2_RESPONSE = b'$X>'
MSP_ERROR = b'$M!'

class MSPException(Exception):
    """Custom exception for MSP protocol errors"""
    pass

class ConnectionManager:
    """Enhanced connection class with MSP v1/v2 support and multiple FC compatibility"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0, 
                 fc_type: FlightController = FlightController.INAV):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.fc_type = fc_type
        self.ser: Optional[serial.Serial] = None
        self.msp_v2_supported = False
        self._connect()
        self._detect_msp_version()
        
    def _connect(self):
        """Establish serial connection with error handling"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Allow FC to initialize
            logger.info(f"Connected to {self.port} at {self.baudrate} baud")
        except serial.SerialException as e:
            raise MSPException(f"Failed to connect to {self.port}: {e}")
    
    def _detect_msp_version(self):
        """Detect if MSP v2 is supported"""
        try:
            # Try MSP v2 API version command
            self.send_msp_v2(1, b'')
            code, data = self.read_response()
            if code is not None:
                self.msp_v2_supported = True
                logger.info("MSP v2 protocol detected")
            else:
                logger.info("Using MSP v1 protocol")
        except:
            logger.info("Using MSP v1 protocol")

    def _calculate_checksum_v1(self, size: int, code: int, data: bytes) -> int:
        """Calculate MSP v1 checksum"""
        chk = size ^ code
        for b in data:
            chk ^= b
        return chk

    def _calculate_crc_v2(self, data: bytes) -> int:
        """Calculate CRC8 for MSP v2"""
        crc = 0
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0xD5
                else:
                    crc <<= 1
                crc &= 0xFF
        return crc

    def send_msp_v1(self, code: int, data: bytes = b'') -> None:
        """Send MSP v1 command"""
        if not self.ser:
            raise MSPException("Not connected")
            
        size = len(data)
        if size > 255:
            raise MSPException("MSP v1 payload too large (max 255 bytes)")
            
        chk = self._calculate_checksum_v1(size, code, data)
        packet = MSP_V1_HEADER + bytes([size, code]) + data + bytes([chk])
        
        try:
            self.ser.write(packet)
            logger.debug(f"Sent MSP v1 command: {code}, size: {size}")
        except serial.SerialException as e:
            raise MSPException(f"Failed to send MSP command: {e}")

    def send_msp_v2(self, code: int, data: bytes = b'') -> None:
        """Send MSP v2 command"""
        if not self.ser:
            raise MSPException("Not connected")
            
        size = len(data)
        if size > 65535:
            raise MSPException("MSP v2 payload too large (max 65535 bytes)")
        
        # MSP v2 header: $X< + flag + code(2) + size(2) + payload + crc
        flag = 0  # Request flag
        header_payload = struct.pack('<BHH', flag, code, size) + data
        crc = self._calculate_crc_v2(header_payload)
        packet = MSP_V2_HEADER + header_payload + bytes([crc])
        
        try:
            self.ser.write(packet)
            logger.debug(f"Sent MSP v2 command: {code}, size: {size}")
        except serial.SerialException as e:
            raise MSPException(f"Failed to send MSP command: {e}")

    def send_msp(self, code: int, data: bytes = b'', force_v1: bool = False) -> None:
        """Send MSP command using best available protocol version"""
        if self.msp_v2_supported and not force_v1 and len(data) <= 65535:
            self.send_msp_v2(code, data)
        else:
            self.send_msp_v1(code, data)

    def read_response(self, timeout: Optional[float] = None) -> Tuple[Optional[int], Optional[bytes]]:
        """Read MSP response with timeout and error handling"""
        if not self.ser:
            raise MSPException("Not connected")
            
        original_timeout = self.ser.timeout
        if timeout:
            self.ser.timeout = timeout
            
        try:
            # Look for header
            start_time = time.time()
            while time.time() - start_time < (timeout or self.timeout):
                byte = self.ser.read(1)
                if not byte:
                    continue
                    
                if byte == b'$':
                    header = b'$' + self.ser.read(2)
                    if header == MSP_V1_RESPONSE:
                        return self._read_v1_response()
                    elif header == MSP_V2_RESPONSE:
                        return self._read_v2_response()
                    elif header == MSP_ERROR:
                        logger.warning("Received MSP error response")
                        return None, None
                        
            logger.warning("MSP response timeout")
            return None, None
            
        except serial.SerialException as e:
            raise MSPException(f"Failed to read MSP response: {e}")
        finally:
            self.ser.timeout = original_timeout

    def _read_v1_response(self) -> Tuple[Optional[int], Optional[bytes]]:
        """Read MSP v1 response"""
        if not self.ser:
            return None, None
            
        try:
            size = ord(self.ser.read(1))
            code = ord(self.ser.read(1))
            data = self.ser.read(size)
            chk = ord(self.ser.read(1))
            
            # Verify checksum
            expected_chk = self._calculate_checksum_v1(size, code, data)
            if chk != expected_chk:
                logger.warning("MSP v1 checksum mismatch")
                return None, None
                
            return code, data
        except (struct.error, TypeError) as e:
            logger.error(f"MSP v1 response parsing error: {e}")
            return None, None

    def _read_v2_response(self) -> Tuple[Optional[int], Optional[bytes]]:
        """Read MSP v2 response"""
        if not self.ser:
            return None, None
            
        try:
            flag = ord(self.ser.read(1))
            code, size = struct.unpack('<HH', self.ser.read(4))
            data = self.ser.read(size)
            crc = ord(self.ser.read(1))
            
            # Verify CRC
            header_payload = bytes([flag]) + struct.pack('<HH', code, size) + data
            expected_crc = self._calculate_crc_v2(header_payload)
            if crc != expected_crc:
                logger.warning("MSP v2 CRC mismatch")
                return None, None
                
            return code, data
        except (struct.error, TypeError) as e:
            logger.error(f"MSP v2 response parsing error: {e}")
            return None, None

    def close(self):
        """Close connection"""
        if self.ser:
            self.ser.close()
            self.ser = None
            logger.info("Connection closed")

    def flush(self):
        """Flush serial buffers"""
        if self.ser:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self.ser is not None and self.ser.is_open

# Backward compatibility alias
INavConnection = ConnectionManager
