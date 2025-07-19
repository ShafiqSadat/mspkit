"""
Mission simulation and validation module
"""
import math
from typing import List, Dict, Any, Tuple
from .mission import Mission, Waypoint

class MissionSimulator:
    """Simulate mission execution and validate feasibility"""
    
    def __init__(self, mission: Mission):
        self.mission = mission
        self.vehicle_specs = {
            'max_speed': 15.0,  # m/s
            'max_climb_rate': 5.0,  # m/s
            'battery_capacity': 5000,  # mAh
            'power_consumption': 15.0,  # Ah at hover
            'safety_margin': 0.2  # 20% battery reserve
        }
    
    def validate_mission(self) -> Dict[str, Any]:
        """Comprehensive mission validation"""
        results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'estimated_time': 0,
            'estimated_battery': 0,
            'max_distance_from_home': 0
        }
        
        if not self.mission.waypoints:
            results['errors'].append("Mission has no waypoints")
            results['valid'] = False
            return results
        
        # Check each waypoint
        home_wp = self.mission.waypoints[0] if self.mission.waypoints else None
        
        for i, wp in enumerate(self.mission.waypoints):
            # Altitude checks
            if wp.alt > 120:  # FAA/EASA limit
                results['warnings'].append(f"Waypoint {i}: Altitude {wp.alt}m exceeds 120m")
            
            # Distance from home
            if home_wp:
                distance = self._calculate_distance(
                    home_wp.lat, home_wp.lon, wp.lat, wp.lon
                )
                results['max_distance_from_home'] = max(
                    results['max_distance_from_home'], distance
                )
                
                if distance > 500:  # Visual line of sight
                    results['warnings'].append(f"Waypoint {i}: {distance:.0f}m from home (VLOS concern)")
        
        # Estimate flight time and battery
        time_estimate, battery_estimate = self._estimate_flight_resources()
        results['estimated_time'] = time_estimate
        results['estimated_battery'] = battery_estimate
        
        if battery_estimate > (100 - self.vehicle_specs['safety_margin'] * 100):
            results['errors'].append(f"Mission requires {battery_estimate:.1f}% battery (exceeds safe limit)")
            results['valid'] = False
        
        return results
    
    def _estimate_flight_resources(self) -> Tuple[float, float]:
        """Estimate flight time and battery consumption"""
        total_time = 0
        total_distance = 0
        
        for i in range(1, len(self.mission.waypoints)):
            prev_wp = self.mission.waypoints[i-1]
            curr_wp = self.mission.waypoints[i]
            
            # Calculate segment distance and time
            horizontal_dist = self._calculate_distance(
                prev_wp.lat, prev_wp.lon, curr_wp.lat, curr_wp.lon
            )
            vertical_dist = abs(curr_wp.alt - prev_wp.alt)
            
            # Estimate time based on speed constraints
            speed = curr_wp.param1 / 100.0 if curr_wp.param1 > 0 else 5.0  # m/s
            speed = min(speed, self.vehicle_specs['max_speed'])
            
            horizontal_time = horizontal_dist / speed
            vertical_time = vertical_dist / self.vehicle_specs['max_climb_rate']
            
            segment_time = max(horizontal_time, vertical_time)
            total_time += segment_time
            total_distance += horizontal_dist
        
        # Estimate battery consumption (simplified model)
        hover_time = total_time * 0.3  # 30% hovering/maneuvering
        cruise_time = total_time * 0.7
        
        battery_percent = (
            (hover_time * self.vehicle_specs['power_consumption']) +
            (cruise_time * self.vehicle_specs['power_consumption'] * 0.8)
        ) / (self.vehicle_specs['battery_capacity'] / 1000) * 100
        
        return total_time, battery_percent
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula"""
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
