#!/usr/bin/env python3
"""
Advanced Mission Planning Example

This example demonstrates advanced mission planning capabilities including:
- Mission validation and simulation
- Terrain following missions
- Emergency procedures
- Real-time mission monitoring
"""

import logging
import time
from mspkit import connect, FlightController
from mspkit.mission import Mission
from mspkit.mission_simulator import MissionSimulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_search_and_rescue_mission():
    """Create a search and rescue pattern mission"""
    # Connect to flight controller
    conn = connect('/dev/ttyUSB0', fc_type=FlightController.INAV)
    mission = Mission(conn)
    
    # Define search area (example coordinates)
    search_center = (37.7749, -122.4194, 50)  # San Francisco, 50m altitude
    search_radius = 200  # meters
    
    # Create expanding square search pattern
    mission.clear_mission()
    
    # Starting point
    mission.add_waypoint(*search_center, action=Mission.WAYPOINT_ACTION_WAYPOINT)
    
    # Create expanding square pattern
    angles = [0, 90, 180, 270]  # North, East, South, West
    for radius in range(50, search_radius + 1, 50):
        for angle in angles:
            import math
            lat_offset = radius * math.cos(math.radians(angle)) / 111320.0
            lon_offset = radius * math.sin(math.radians(angle)) / (111320.0 * math.cos(math.radians(search_center[0])))
            
            new_lat = search_center[0] + lat_offset
            new_lon = search_center[1] + lon_offset
            
            mission.add_waypoint(
                new_lat, new_lon, search_center[2],
                action=Mission.WAYPOINT_ACTION_WAYPOINT,
                param1=300  # Slow speed for detailed observation
            )
    
    # Return to home
    mission.add_waypoint(*search_center, action=Mission.WAYPOINT_ACTION_RTH)
    
    # Validate mission before upload
    simulator = MissionSimulator(mission)
    validation = simulator.validate_mission()
    
    print(f"Mission Validation Results:")
    print(f"Valid: {validation['valid']}")
    print(f"Estimated time: {validation['estimated_time']:.1f} seconds")
    print(f"Estimated battery: {validation['estimated_battery']:.1f}%")
    print(f"Max distance from home: {validation['max_distance_from_home']:.0f}m")
    
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['errors']:
        print("Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
        return False
    
    # Upload mission if valid
    if validation['valid']:
        print("Uploading mission...")
        if mission.upload_mission():
            print("Mission uploaded successfully!")
            
            # Save mission for future use
            mission.save_mission_to_file("search_rescue_mission.json")
            print("Mission saved to file")
            return True
    
    return False

def monitor_mission_execution(conn):
    """Monitor mission execution in real-time"""
    from mspkit import Telemetry
    
    telem = Telemetry(conn)
    
    print("Monitoring mission execution...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            # Get current status
            attitude = telem.get_attitude()
            gps = telem.get_gps()
            nav_status = telem.get_nav_status()
            
            print(f"\rAlt: {gps.get('alt', 0):.1f}m | "
                  f"GPS: {gps.get('lat', 0):.6f}, {gps.get('lon', 0):.6f} | "
                  f"WP: {nav_status.get('waypoint_number', 0)} | "
                  f"Mode: {nav_status.get('nav_state', 'UNKNOWN')}", end='')
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

if __name__ == "__main__":
    if create_search_and_rescue_mission():
        # Optionally monitor execution
        response = input("Start mission monitoring? (y/n): ")
        if response.lower() == 'y':
            conn = connect('/dev/ttyUSB0', fc_type=FlightController.INAV)
            monitor_mission_execution(conn)
