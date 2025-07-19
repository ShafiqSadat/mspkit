#!/usr/bin/env python3
"""
Mission Planning Example

This example demonstrates comprehensive mission planning capabilities:
- Creating different types of missions
- Mission validation and simulation
- Upload/download operations
- Real-time mission monitoring

Supports iNav flight controllers with waypoint navigation.
"""

import time
import math
import json
import logging
from typing import List, Tuple
from mspkit import connect, FlightController, Mission, Telemetry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MissionPlanner:
    """Advanced mission planning and management"""
    
    def __init__(self, serial_port: str):
        self.conn = connect(serial_port, fc_type=FlightController.INAV)
        self.mission = Mission(self.conn)
        self.telemetry = Telemetry(self.conn)
        
        print(f"✅ Connected to iNav flight controller")
        
    def create_simple_waypoint_mission(self) -> bool:
        """Create a simple rectangular waypoint mission"""
        print("\n📍 Creating Simple Waypoint Mission")
        
        # Get current position as home
        gps = self.telemetry.get_gps()
        home_lat = gps.get('lat', 37.7749)  # Default to San Francisco
        home_lon = gps.get('lon', -122.4194)
        
        if gps.get('fix_type', 0) < 2:
            print("⚠️  No GPS fix, using default coordinates")
            home_lat, home_lon = 37.7749, -122.4194
        
        altitude = 50  # 50 meter altitude
        
        # Create rectangular mission (100m x 100m)
        self.mission.clear_mission()
        
        # Convert meters to degrees (approximate)
        lat_per_meter = 1 / 111320.0
        lon_per_meter = 1 / (111320.0 * math.cos(math.radians(home_lat)))
        
        waypoints = [
            (home_lat, home_lon, altitude),  # Home/Start
            (home_lat + 100 * lat_per_meter, home_lon, altitude),  # North
            (home_lat + 100 * lat_per_meter, home_lon + 100 * lon_per_meter, altitude),  # Northeast
            (home_lat, home_lon + 100 * lon_per_meter, altitude),  # East
            (home_lat, home_lon, altitude),  # Return to start
        ]
        
        for i, (lat, lon, alt) in enumerate(waypoints):
            action = Mission.WAYPOINT_ACTION_WAYPOINT
            speed = 500  # 5 m/s in cm/s
            
            # Last waypoint should be RTH
            if i == len(waypoints) - 1:
                action = Mission.WAYPOINT_ACTION_RTH
            
            self.mission.add_waypoint(lat, lon, alt, action=action, param1=speed)
            print(f"   Added waypoint {i+1}: {lat:.6f}, {lon:.6f}, {alt}m")
        
        print(f"✅ Created mission with {self.mission.get_waypoint_count()} waypoints")
        return True
    
    def create_survey_mission(self) -> bool:
        """Create an automated survey/mapping mission"""
        print("\n🗺️  Creating Survey Mission")
        
        # Survey parameters
        center_lat = 37.7749
        center_lon = -122.4194
        width_m = 200
        height_m = 200
        altitude_m = 60
        line_spacing_m = 30
        speed = 400  # 4 m/s
        
        print(f"   Survey area: {width_m}x{height_m}m")
        print(f"   Line spacing: {line_spacing_m}m")
        print(f"   Altitude: {altitude_m}m")
        
        success = self.mission.create_survey_mission(
            center_lat, center_lon, width_m, height_m, 
            altitude_m, line_spacing_m, speed
        )
        
        if success:
            info = self.mission.get_mission_info()
            print(f"✅ Survey mission created:")
            print(f"   Waypoints: {info['waypoint_count']}")
            print(f"   Distance: {info['total_distance_m']:.0f}m")
            print(f"   Estimated time: {info['total_distance_m']/4:.0f}s")
        
        return success
    
    def create_search_pattern_mission(self) -> bool:
        """Create a search and rescue spiral pattern"""
        print("\n🔍 Creating Search Pattern Mission")
        
        # Search parameters
        center_lat = 37.7749
        center_lon = -122.4194
        max_radius = 150  # meters
        altitude = 40
        speed = 300  # 3 m/s for detailed observation
        
        self.mission.clear_mission()
        
        # Convert meters to degrees
        lat_per_meter = 1 / 111320.0
        lon_per_meter = 1 / (111320.0 * math.cos(math.radians(center_lat)))
        
        # Create expanding spiral
        angles = []
        radii = []
        
        for radius in range(20, max_radius + 1, 20):  # Expand by 20m each loop
            for angle in range(0, 360, 30):  # 30-degree increments
                angles.append(angle)
                radii.append(radius)
        
        # Add center point first
        self.mission.add_waypoint(center_lat, center_lon, altitude, 
                                action=Mission.WAYPOINT_ACTION_WAYPOINT, param1=speed)
        
        # Add spiral waypoints
        for angle, radius in zip(angles, radii):
            lat_offset = radius * math.cos(math.radians(angle)) * lat_per_meter
            lon_offset = radius * math.sin(math.radians(angle)) * lon_per_meter
            
            wp_lat = center_lat + lat_offset
            wp_lon = center_lon + lon_offset
            
            self.mission.add_waypoint(wp_lat, wp_lon, altitude,
                                    action=Mission.WAYPOINT_ACTION_WAYPOINT,
                                    param1=speed)
        
        # Return to center and land
        self.mission.add_waypoint(center_lat, center_lon, altitude,
                                action=Mission.WAYPOINT_ACTION_RTH)
        
        info = self.mission.get_mission_info()
        print(f"✅ Search pattern created:")
        print(f"   Waypoints: {info['waypoint_count']}")
        print(f"   Max radius: {max_radius}m")
        print(f"   Total distance: {info['total_distance_m']:.0f}m")
        
        return True
    
    def validate_mission(self) -> bool:
        """Validate current mission for safety and feasibility"""
        print("\n🔍 Validating Mission")
        
        if self.mission.get_waypoint_count() == 0:
            print("❌ No mission loaded")
            return False
        
        info = self.mission.get_mission_info()
        waypoints = self.mission.get_waypoints()
        
        warnings = []
        errors = []
        
        # Check waypoint limits
        if info['waypoint_count'] > Mission.MAX_WAYPOINTS:
            errors.append(f"Too many waypoints: {info['waypoint_count']} > {Mission.MAX_WAYPOINTS}")
        
        # Check altitude limits
        max_alt = info['max_altitude_m']
        if max_alt > 120:  # FAA/EASA limit
            warnings.append(f"Maximum altitude {max_alt:.0f}m exceeds 120m limit")
        
        # Check distance limits
        total_distance = info['total_distance_m']
        if total_distance > 2000:  # 2km limit for visual line of sight
            warnings.append(f"Total distance {total_distance:.0f}m may exceed VLOS")
        
        # Estimate flight time (rough calculation)
        avg_speed = 5.0  # m/s average
        estimated_time = total_distance / avg_speed
        if estimated_time > 1200:  # 20 minutes
            warnings.append(f"Estimated flight time {estimated_time/60:.1f}min may exceed battery life")
        
        # Check for valid coordinates
        for i, wp in enumerate(waypoints):
            if not (-90 <= wp['lat'] <= 90):
                errors.append(f"Waypoint {i}: Invalid latitude {wp['lat']}")
            if not (-180 <= wp['lon'] <= 180):
                errors.append(f"Waypoint {i}: Invalid longitude {wp['lon']}")
            if wp['alt'] < 0:
                errors.append(f"Waypoint {i}: Negative altitude {wp['alt']}")
        
        # Display results
        print(f"📊 Mission Validation Results:")
        print(f"   Waypoints: {info['waypoint_count']}")
        print(f"   Total distance: {total_distance:.0f}m")
        print(f"   Altitude range: {info['min_altitude_m']:.0f}m - {info['max_altitude_m']:.0f}m")
        print(f"   Estimated time: {estimated_time/60:.1f} minutes")
        
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        if errors:
            print("\n❌ Errors:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ Mission validation passed")
        return True
    
    def upload_mission(self) -> bool:
        """Upload mission to flight controller"""
        if not self.validate_mission():
            return False
        
        print("\n📤 Uploading mission to flight controller...")
        
        if self.mission.upload_mission():
            print("✅ Mission uploaded successfully")
            return True
        else:
            print("❌ Mission upload failed")
            return False
    
    def download_mission(self) -> bool:
        """Download mission from flight controller"""
        print("\n📥 Downloading mission from flight controller...")
        
        if self.mission.download_mission():
            info = self.mission.get_mission_info()
            print(f"✅ Mission downloaded: {info['waypoint_count']} waypoints")
            return True
        else:
            print("❌ Mission download failed")
            return False
    
    def save_mission(self, filename: str) -> bool:
        """Save mission to file"""
        print(f"\n💾 Saving mission to {filename}...")
        
        if self.mission.save_mission_to_file(filename):
            print(f"✅ Mission saved to {filename}")
            return True
        else:
            print(f"❌ Failed to save mission to {filename}")
            return False
    
    def load_mission(self, filename: str) -> bool:
        """Load mission from file"""
        print(f"\n📂 Loading mission from {filename}...")
        
        if self.mission.load_mission_from_file(filename):
            info = self.mission.get_mission_info()
            print(f"✅ Mission loaded: {info['waypoint_count']} waypoints")
            return True
        else:
            print(f"❌ Failed to load mission from {filename}")
            return False
    
    def monitor_mission_execution(self):
        """Monitor mission execution in real-time"""
        print("\n📡 Starting mission execution monitoring...")
        print("Press Ctrl+C to stop monitoring")
        print("=" * 80)
        
        try:
            last_waypoint = -1
            start_time = time.time()
            
            while True:
                # Get navigation status
                nav_status = self.telemetry.get_nav_status()
                gps = self.telemetry.get_gps()
                attitude = self.telemetry.get_attitude()
                
                current_wp = nav_status.get('waypoint_number', 0)
                nav_state = nav_status.get('nav_state', 'UNKNOWN')
                
                # Check for waypoint progress
                if current_wp != last_waypoint:
                    elapsed = time.time() - start_time
                    print(f"\n🎯 Reached waypoint {current_wp} after {elapsed:.1f}s")
                    last_waypoint = current_wp
                
                # Display current status
                print(f"\r"
                      f"WP: {current_wp:2d} | "
                      f"State: {nav_state:12s} | "
                      f"Pos: {gps.get('lat', 0):9.6f},{gps.get('lon', 0):10.6f} | "
                      f"Alt: {gps.get('alt', 0):5.1f}m | "
                      f"Heading: {attitude.get('yaw', 0):5.1f}°",
                      end='', flush=True)
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Mission monitoring stopped")

def main():
    """Main mission planning demonstration"""
    
    SERIAL_PORT = '/dev/ttyUSB0'
    
    print("🗺️  MSPKit Mission Planning Example")
    print("=" * 50)
    print("This example requires an iNav flight controller")
    print()
    
    try:
        planner = MissionPlanner(SERIAL_PORT)
        
        while True:
            print("\n🎯 Mission Planning Menu:")
            print("1. Create simple waypoint mission")
            print("2. Create survey mission")
            print("3. Create search pattern mission")
            print("4. Validate current mission")
            print("5. Upload mission to FC")
            print("6. Download mission from FC")
            print("7. Save mission to file")
            print("8. Load mission from file")
            print("9. Monitor mission execution")
            print("10. Show mission info")
            print("11. Exit")
            
            choice = input("\nSelect option (1-11): ").strip()
            
            if choice == '1':
                planner.create_simple_waypoint_mission()
                
            elif choice == '2':
                planner.create_survey_mission()
                
            elif choice == '3':
                planner.create_search_pattern_mission()
                
            elif choice == '4':
                planner.validate_mission()
                
            elif choice == '5':
                planner.upload_mission()
                
            elif choice == '6':
                planner.download_mission()
                
            elif choice == '7':
                filename = input("Enter filename (e.g., mission.json): ").strip()
                if filename:
                    planner.save_mission(filename)
                    
            elif choice == '8':
                filename = input("Enter filename: ").strip()
                if filename:
                    planner.load_mission(filename)
                    
            elif choice == '9':
                planner.monitor_mission_execution()
                
            elif choice == '10':
                info = planner.mission.get_mission_info()
                print(f"\n📊 Current Mission Info:")
                for key, value in info.items():
                    print(f"   {key}: {value}")
                    
            elif choice == '11':
                print("👋 Exiting mission planner")
                break
                
            else:
                print("❌ Invalid option")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
