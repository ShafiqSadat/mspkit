import struct
import time
import math
import logging
from typing import Dict, Any, Optional, List, Tuple
from .msp_constants import MSPCommands, FlightController, NavState

logger = logging.getLogger(__name__)

class Waypoint:
    """Waypoint data class"""
    
    def __init__(self, lat: float, lon: float, alt: float, action: int = 1, 
                 param1: int = 0, param2: int = 0, param3: int = 0, flag: int = 0):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.action = action  # Waypoint action (1=WAYPOINT, 3=RTH, etc.)
        self.param1 = param1  # Speed or other parameter
        self.param2 = param2  # Additional parameter
        self.param3 = param3  # Additional parameter  
        self.flag = flag      # Waypoint flags
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'lat': self.lat,
            'lon': self.lon, 
            'alt': self.alt,
            'action': self.action,
            'param1': self.param1,
            'param2': self.param2,
            'param3': self.param3,
            'flag': self.flag
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Waypoint':
        return cls(
            lat=data['lat'],
            lon=data['lon'],
            alt=data['alt'],
            action=data.get('action', 1),
            param1=data.get('param1', 0),
            param2=data.get('param2', 0),
            param3=data.get('param3', 0),
            flag=data.get('flag', 0)
        )

class Mission:
    """Enhanced mission management for iNav flight controllers"""
    
    # Waypoint actions
    WAYPOINT_ACTION_WAYPOINT = 1
    WAYPOINT_ACTION_POSHOLD_UNLIM = 2
    WAYPOINT_ACTION_POSHOLD_TIME = 3
    WAYPOINT_ACTION_RTH = 4
    WAYPOINT_ACTION_SET_POI = 5
    WAYPOINT_ACTION_JUMP = 6
    WAYPOINT_ACTION_SET_HEAD = 7
    WAYPOINT_ACTION_LAND = 8
    
    # Maximum waypoints supported by iNav
    MAX_WAYPOINTS = 60
    
    def __init__(self, conn):
        self.conn = conn
        self.fc_type = conn.fc_type
        self.waypoints: List[Waypoint] = []
        self._mission_loaded = False
        
        if self.fc_type != FlightController.INAV:
            logger.warning("Mission planning primarily designed for iNav")

    def validate_coordinates(self, lat: float, lon: float, alt: float) -> bool:
        """Validate coordinate values"""
        if not (-90 <= lat <= 90):
            logger.error(f"Invalid latitude: {lat}")
            return False
        if not (-180 <= lon <= 180):
            logger.error(f"Invalid longitude: {lon}")
            return False
        if not (-1000 <= alt <= 10000):  # Reasonable altitude limits in meters
            logger.error(f"Invalid altitude: {alt}")
            return False
        return True

    def get_waypoint(self, wp_id: int) -> Optional[Waypoint]:
        """Get waypoint from flight controller"""
        if wp_id < 0 or wp_id >= self.MAX_WAYPOINTS:
            logger.error(f"Invalid waypoint ID: {wp_id}")
            return None
            
        try:
            data = struct.pack('<B', wp_id)
            self.conn.send_msp(MSPCommands.MSP_WP, data)
            code, response_data = self.conn.read_response()
            
            if code == MSPCommands.MSP_WP and response_data:
                if len(response_data) >= 21:  # Extended waypoint format
                    wp_id_resp, action, lat, lon, alt, param1, param2, param3, flag = struct.unpack('<BBiiihhhB', response_data[:21])
                    
                    if wp_id_resp == wp_id:
                        return Waypoint(
                            lat=lat / 1e7,
                            lon=lon / 1e7,
                            alt=alt / 100.0,
                            action=action,
                            param1=param1,
                            param2=param2,
                            param3=param3,
                            flag=flag
                        )
                elif len(response_data) >= 12:  # Basic waypoint format
                    lat, lon, alt = struct.unpack('<iii', response_data[0:12])
                    return Waypoint(
                        lat=lat / 1e7,
                        lon=lon / 1e7,
                        alt=alt / 100.0
                    )
        except Exception as e:
            logger.error(f"Failed to get waypoint {wp_id}: {e}")
            
        return None

    def set_waypoint(self, wp_id: int, waypoint: Waypoint, validate: bool = True) -> bool:
        """Set waypoint on flight controller"""
        if wp_id < 0 or wp_id >= self.MAX_WAYPOINTS:
            logger.error(f"Invalid waypoint ID: {wp_id}")
            return False
            
        if validate and not self.validate_coordinates(waypoint.lat, waypoint.lon, waypoint.alt):
            return False
        
        try:
            # Extended waypoint format
            data = struct.pack('<BBiiihhhB',
                wp_id,
                waypoint.action,
                int(waypoint.lat * 1e7),
                int(waypoint.lon * 1e7),
                int(waypoint.alt * 100),
                waypoint.param1,
                waypoint.param2,
                waypoint.param3,
                waypoint.flag
            )
            
            self.conn.send_msp(MSPCommands.MSP_SET_WP, data)
            time.sleep(0.1)  # Allow FC to process
            
            # Verify waypoint was set correctly
            if validate:
                verification = self.get_waypoint(wp_id)
                if verification:
                    lat_diff = abs(verification.lat - waypoint.lat)
                    lon_diff = abs(verification.lon - waypoint.lon)
                    alt_diff = abs(verification.alt - waypoint.alt)
                    
                    if lat_diff > 1e-6 or lon_diff > 1e-6 or alt_diff > 0.1:
                        logger.warning(f"Waypoint {wp_id} verification failed")
                        return False
            
            logger.debug(f"Set waypoint {wp_id}: {waypoint.lat:.6f}, {waypoint.lon:.6f}, {waypoint.alt:.1f}m")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set waypoint {wp_id}: {e}")
            return False

    def add_waypoint(self, lat: float, lon: float, alt: float, action: int = 1, 
                    param1: int = 0, param2: int = 0, param3: int = 0, flag: int = 0) -> bool:
        """Add waypoint to mission"""
        if len(self.waypoints) >= self.MAX_WAYPOINTS:
            logger.error(f"Maximum waypoints ({self.MAX_WAYPOINTS}) reached")
            return False
            
        if not self.validate_coordinates(lat, lon, alt):
            return False
            
        waypoint = Waypoint(lat, lon, alt, action, param1, param2, param3, flag)
        self.waypoints.append(waypoint)
        logger.info(f"Added waypoint {len(self.waypoints)}: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
        return True

    def insert_waypoint(self, index: int, lat: float, lon: float, alt: float, 
                       action: int = 1, param1: int = 0, param2: int = 0, 
                       param3: int = 0, flag: int = 0) -> bool:
        """Insert waypoint at specific index"""
        if index < 0 or index > len(self.waypoints):
            logger.error(f"Invalid waypoint index: {index}")
            return False
            
        if len(self.waypoints) >= self.MAX_WAYPOINTS:
            logger.error(f"Maximum waypoints ({self.MAX_WAYPOINTS}) reached")
            return False
            
        if not self.validate_coordinates(lat, lon, alt):
            return False
            
        waypoint = Waypoint(lat, lon, alt, action, param1, param2, param3, flag)
        self.waypoints.insert(index, waypoint)
        logger.info(f"Inserted waypoint at {index}: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
        return True

    def remove_waypoint(self, index: int) -> bool:
        """Remove waypoint at index"""
        if index < 0 or index >= len(self.waypoints):
            logger.error(f"Invalid waypoint index: {index}")
            return False
            
        removed = self.waypoints.pop(index)
        logger.info(f"Removed waypoint {index}: {removed.lat:.6f}, {removed.lon:.6f}")
        return True

    def clear_mission(self) -> bool:
        """Clear all waypoints from mission"""
        self.waypoints.clear()
        self._mission_loaded = False
        logger.info("Mission cleared")
        return True

    def upload_mission(self, validate: bool = True) -> bool:
        """Upload complete mission to flight controller"""
        if not self.waypoints:
            logger.error("No waypoints to upload")
            return False
            
        success_count = 0
        total_waypoints = len(self.waypoints)
        
        logger.info(f"Uploading mission with {total_waypoints} waypoints...")
        
        try:
            # Upload waypoints
            for i, waypoint in enumerate(self.waypoints):
                if self.set_waypoint(i, waypoint, validate):
                    success_count += 1
                else:
                    logger.error(f"Failed to upload waypoint {i}")
                    if validate:
                        return False
                
                # Progress feedback
                if (i + 1) % 10 == 0 or i == total_waypoints - 1:
                    logger.info(f"Uploaded {i + 1}/{total_waypoints} waypoints")
            
            # Clear any remaining waypoints on FC
            if success_count < self.MAX_WAYPOINTS:
                empty_wp = Waypoint(0, 0, 0, 0)  # Empty waypoint
                for i in range(success_count, min(success_count + 5, self.MAX_WAYPOINTS)):
                    self.set_waypoint(i, empty_wp, validate=False)
            
            if success_count == total_waypoints:
                self._mission_loaded = True
                logger.info(f"Mission upload successful: {success_count} waypoints")
                return True
            else:
                logger.error(f"Mission upload partial: {success_count}/{total_waypoints} waypoints")
                return False
                
        except Exception as e:
            logger.error(f"Mission upload failed: {e}")
            return False

    def download_mission(self) -> bool:
        """Download mission from flight controller"""
        self.waypoints.clear()
        
        logger.info("Downloading mission from flight controller...")
        
        try:
            for i in range(self.MAX_WAYPOINTS):
                waypoint = self.get_waypoint(i)
                if waypoint and (waypoint.lat != 0 or waypoint.lon != 0):
                    self.waypoints.append(waypoint)
                else:
                    break  # No more waypoints
            
            self._mission_loaded = True
            logger.info(f"Downloaded mission with {len(self.waypoints)} waypoints")
            return True
            
        except Exception as e:
            logger.error(f"Mission download failed: {e}")
            return False

    def get_mission_info(self) -> Dict[str, Any]:
        """Get mission information"""
        if not self.waypoints:
            return {"waypoint_count": 0, "mission_loaded": self._mission_loaded}
        
        # Calculate mission statistics
        total_distance = 0.0
        min_alt = float('inf')
        max_alt = float('-inf')
        
        for i, wp in enumerate(self.waypoints):
            min_alt = min(min_alt, wp.alt)
            max_alt = max(max_alt, wp.alt)
            
            if i > 0:
                # Calculate distance from previous waypoint
                prev_wp = self.waypoints[i-1]
                total_distance += self._calculate_distance(
                    prev_wp.lat, prev_wp.lon, wp.lat, wp.lon
                )
        
        return {
            "waypoint_count": len(self.waypoints),
            "mission_loaded": self._mission_loaded,
            "total_distance_m": total_distance,
            "min_altitude_m": min_alt if min_alt != float('inf') else 0,
            "max_altitude_m": max_alt if max_alt != float('-inf') else 0,
            "altitude_range_m": max_alt - min_alt if min_alt != float('inf') else 0
        }

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        import math
        
        R = 6371000  # Earth radius in meters
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    def create_simple_mission(self, waypoints_coords: List[Tuple[float, float, float]], 
                            speed: int = 500) -> bool:
        """Create a simple waypoint mission from coordinates"""
        self.clear_mission()
        
        for lat, lon, alt in waypoints_coords:
            if not self.add_waypoint(lat, lon, alt, 
                                   action=self.WAYPOINT_ACTION_WAYPOINT,
                                   param1=speed):  # Speed in cm/s
                return False
        
        # Add RTH at the end
        if waypoints_coords:
            last_lat, last_lon, last_alt = waypoints_coords[-1]
            self.add_waypoint(last_lat, last_lon, last_alt, 
                            action=self.WAYPOINT_ACTION_RTH)
        
        logger.info(f"Created simple mission with {len(self.waypoints)} waypoints")
        return True

    def create_survey_mission(self, center_lat: float, center_lon: float, 
                            width_m: float, height_m: float, altitude_m: float,
                            line_spacing_m: float = 50, speed: int = 500) -> bool:
        """Create a survey/mapping mission with parallel lines"""
        self.clear_mission()
        
        # Convert meters to degrees (approximate)
        lat_per_meter = 1 / 111320.0
        lon_per_meter = 1 / (111320.0 * math.cos(math.radians(center_lat)))
        
        half_width = width_m / 2
        half_height = height_m / 2
        
        # Calculate number of lines
        num_lines = int(width_m / line_spacing_m) + 1
        
        # Generate waypoints
        for line in range(num_lines):
            # Calculate X offset for this line
            x_offset = -half_width + (line * line_spacing_m)
            lon_offset = x_offset * lon_per_meter
            
            if line % 2 == 0:  # Even lines: bottom to top
                y_positions = [-half_height, half_height]
            else:  # Odd lines: top to bottom
                y_positions = [half_height, -half_height]
            
            for y_pos in y_positions:
                lat_offset = y_pos * lat_per_meter
                wp_lat = center_lat + lat_offset
                wp_lon = center_lon + lon_offset
                
                self.add_waypoint(wp_lat, wp_lon, altitude_m,
                                action=self.WAYPOINT_ACTION_WAYPOINT,
                                param1=speed)
        
        # Add RTH at center
        self.add_waypoint(center_lat, center_lon, altitude_m,
                        action=self.WAYPOINT_ACTION_RTH)
        
        logger.info(f"Created survey mission: {width_m}x{height_m}m, {num_lines} lines, {len(self.waypoints)} waypoints")
        return True

    def save_mission_to_file(self, filename: str) -> bool:
        """Save mission to file"""
        try:
            import json
            
            mission_data = {
                'version': '1.0',
                'fc_type': self.fc_type.name,
                'created': time.time(),
                'waypoints': [wp.to_dict() for wp in self.waypoints],
                'info': self.get_mission_info()
            }
            
            with open(filename, 'w') as f:
                json.dump(mission_data, f, indent=2)
            
            logger.info(f"Mission saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save mission: {e}")
            return False

    def load_mission_from_file(self, filename: str) -> bool:
        """Load mission from file"""
        try:
            import json
            
            with open(filename, 'r') as f:
                mission_data = json.load(f)
            
            self.clear_mission()
            
            for wp_data in mission_data.get('waypoints', []):
                waypoint = Waypoint.from_dict(wp_data)
                self.waypoints.append(waypoint)
            
            logger.info(f"Mission loaded from {filename}: {len(self.waypoints)} waypoints")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load mission: {e}")
            return False

    def get_waypoints(self) -> List[Dict[str, Any]]:
        """Get all waypoints as dictionaries"""
        return [wp.to_dict() for wp in self.waypoints]

    def is_mission_loaded(self) -> bool:
        """Check if mission is loaded on flight controller"""
        return self._mission_loaded

    def get_waypoint_count(self) -> int:
        """Get number of waypoints in mission"""
        return len(self.waypoints)
