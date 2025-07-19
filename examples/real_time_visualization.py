#!/usr/bin/env python3
"""
Real-time Data Visualization Example

This example demonstrates real-time visualization of flight controller data:
- Attitude (roll, pitch, yaw) visualization
- GPS tracking on a map
- Battery monitoring
- Sensor data graphs

Requires matplotlib and optionally folium for map visualization.
"""

import time
import math
import threading
from collections import deque
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mspkit import connect, FlightController, Telemetry

# Optional imports
try:
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    print("⚠️  folium not installed - GPS map visualization disabled")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️  numpy not installed - some visualizations may be limited")

class RealTimeVisualizer:
    """Real-time data visualization for flight controller telemetry"""
    
    def __init__(self, serial_port: str, fc_type: FlightController):
        self.conn = connect(serial_port, fc_type=fc_type)
        self.telemetry = Telemetry(self.conn)
        
        # Data storage
        self.max_samples = 500  # 50 seconds at 10Hz
        self.data = {
            'time': deque(maxlen=self.max_samples),
            'roll': deque(maxlen=self.max_samples),
            'pitch': deque(maxlen=self.max_samples),
            'yaw': deque(maxlen=self.max_samples),
            'altitude': deque(maxlen=self.max_samples),
            'battery_voltage': deque(maxlen=self.max_samples),
            'battery_current': deque(maxlen=self.max_samples),
            'gps_lat': deque(maxlen=self.max_samples),
            'gps_lon': deque(maxlen=self.max_samples),
            'satellites': deque(maxlen=self.max_samples),
        }
        
        # Threading
        self.running = False
        self.data_thread = None
        self.start_time = time.time()
        
        print(f"✅ Connected to {fc_type.name} flight controller")
    
    def start_data_collection(self):
        """Start background data collection thread"""
        self.running = True
        self.data_thread = threading.Thread(target=self._collect_data)
        self.data_thread.daemon = True
        self.data_thread.start()
        print("📊 Data collection started")
    
    def stop_data_collection(self):
        """Stop data collection"""
        self.running = False
        if self.data_thread:
            self.data_thread.join()
        print("🛑 Data collection stopped")
    
    def _collect_data(self):
        """Background data collection loop"""
        while self.running:
            try:
                current_time = time.time() - self.start_time
                
                # Get telemetry data
                attitude = self.telemetry.get_attitude()
                gps = self.telemetry.get_gps()
                battery = self.telemetry.get_battery()
                
                # Store data
                self.data['time'].append(current_time)
                self.data['roll'].append(attitude.get('roll', 0))
                self.data['pitch'].append(attitude.get('pitch', 0))
                self.data['yaw'].append(attitude.get('yaw', 0))
                self.data['altitude'].append(gps.get('alt', 0))
                self.data['battery_voltage'].append(battery.get('voltage', 0))
                self.data['battery_current'].append(battery.get('current', 0))
                self.data['gps_lat'].append(gps.get('lat', 0))
                self.data['gps_lon'].append(gps.get('lon', 0))
                self.data['satellites'].append(gps.get('num_sat', 0))
                
                time.sleep(0.1)  # 10Hz data collection
                
            except Exception as e:
                print(f"⚠️  Data collection error: {e}")
                time.sleep(1)
    
    def create_attitude_visualization(self):
        """Create real-time attitude visualization"""
        print("🎯 Starting attitude visualization...")
        
        # Set up the plot
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Real-time Flight Controller Data', fontsize=16)
        
        # Configure subplots
        ax1.set_title('Attitude (Roll, Pitch, Yaw)')
        ax1.set_ylabel('Degrees')
        ax1.set_xlabel('Time (s)')
        ax1.grid(True)
        ax1.set_ylim(-180, 180)
        
        ax2.set_title('Altitude')
        ax2.set_ylabel('Meters')
        ax2.set_xlabel('Time (s)')
        ax2.grid(True)
        
        ax3.set_title('Battery Voltage')
        ax3.set_ylabel('Volts')
        ax3.set_xlabel('Time (s)')
        ax3.grid(True)
        ax3.set_ylim(10, 17)  # Typical 4S LiPo range
        
        ax4.set_title('GPS Satellites')
        ax4.set_ylabel('Count')
        ax4.set_xlabel('Time (s)')
        ax4.grid(True)
        ax4.set_ylim(0, 20)
        
        # Initialize empty lines
        line_roll, = ax1.plot([], [], 'r-', label='Roll', linewidth=2)
        line_pitch, = ax1.plot([], [], 'g-', label='Pitch', linewidth=2)
        line_yaw, = ax1.plot([], [], 'b-', label='Yaw', linewidth=2)
        ax1.legend()
        
        line_alt, = ax2.plot([], [], 'purple', linewidth=2)
        line_voltage, = ax3.plot([], [], 'orange', linewidth=2)
        line_sats, = ax4.plot([], [], 'brown', linewidth=2, marker='o', markersize=3)
        
        def animate(frame):
            """Animation update function"""
            if not self.data['time']:
                return line_roll, line_pitch, line_yaw, line_alt, line_voltage, line_sats
            
            # Convert deques to lists for plotting
            times = list(self.data['time'])
            rolls = list(self.data['roll'])
            pitches = list(self.data['pitch'])
            yaws = list(self.data['yaw'])
            altitudes = list(self.data['altitude'])
            voltages = list(self.data['battery_voltage'])
            satellites = list(self.data['satellites'])
            
            # Update attitude plot
            line_roll.set_data(times, rolls)
            line_pitch.set_data(times, pitches)
            line_yaw.set_data(times, yaws)
            
            # Update other plots
            line_alt.set_data(times, altitudes)
            line_voltage.set_data(times, voltages)
            line_sats.set_data(times, satellites)
            
            # Auto-scale x-axis
            if times:
                for ax in [ax1, ax2, ax3, ax4]:
                    ax.set_xlim(max(0, times[-1] - 30), times[-1] + 1)  # Show last 30 seconds
            
            # Auto-scale altitude
            if altitudes:
                alt_min, alt_max = min(altitudes), max(altitudes)
                margin = max(10, (alt_max - alt_min) * 0.1)
                ax2.set_ylim(alt_min - margin, alt_max + margin)
            
            return line_roll, line_pitch, line_yaw, line_alt, line_voltage, line_sats
        
        # Start animation
        ani = animation.FuncAnimation(fig, animate, interval=100, blit=True)
        plt.tight_layout()
        plt.show()
        
        return ani
    
    def create_artificial_horizon(self):
        """Create an artificial horizon display"""
        print("🛩️  Starting artificial horizon...")
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        fig.suptitle('Artificial Horizon', fontsize=16)
        
        # Remove default polar plot elements
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 90)
        ax.set_yticks([30, 60, 90])
        ax.set_yticklabels(['30°', '60°', '90°'])
        ax.grid(True)
        
        def animate_horizon(frame):
            """Update artificial horizon"""
            ax.clear()
            ax.set_theta_zero_location('N')
            ax.set_theta_direction(-1)
            ax.set_ylim(0, 90)
            
            if self.data['roll'] and self.data['pitch']:
                roll = self.data['roll'][-1]
                pitch = self.data['pitch'][-1]
                yaw = self.data['yaw'][-1]
                
                # Draw horizon line
                horizon_angles = np.linspace(0, 2*np.pi, 100)
                horizon_radius = np.full_like(horizon_angles, 90 - abs(pitch))
                
                # Color based on pitch (blue for sky, brown for ground)
                color = 'skyblue' if pitch >= 0 else 'brown'
                ax.fill_between(horizon_angles, 0, horizon_radius, alpha=0.3, color=color)
                
                # Aircraft symbol (fixed in center)
                ax.plot([0, np.pi], [45, 45], 'k-', linewidth=3, label='Horizon')
                ax.plot([np.pi/2, 3*np.pi/2], [45, 45], 'r-', linewidth=5, label='Aircraft')
                
                # Add attitude text
                ax.text(0, 100, f'Roll: {roll:.1f}°\nPitch: {pitch:.1f}°\nYaw: {yaw:.1f}°',
                       transform=ax.transData, ha='center', va='bottom',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            return ax,
        
        ani = animation.FuncAnimation(fig, animate_horizon, interval=100)
        plt.show()
        
        return ani
    
    def create_gps_map(self) -> str:
        """Create GPS track map (if folium is available)"""
        if not HAS_FOLIUM:
            print("❌ folium not available for GPS mapping")
            return ""
        
        print("🗺️  Creating GPS track map...")
        
        # Get GPS coordinates
        lats = [lat for lat in self.data['gps_lat'] if lat != 0]
        lons = [lon for lon in self.data['gps_lon'] if lon != 0]
        
        if not lats or not lons:
            print("⚠️  No GPS data available")
            return ""
        
        # Create map centered on track
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=15)
        
        # Add GPS track
        gps_points = list(zip(lats, lons))
        folium.PolyLine(gps_points, color='red', weight=3, opacity=0.8).add_to(m)
        
        # Add start and end markers
        if len(gps_points) > 0:
            folium.Marker(gps_points[0], popup='Start', 
                         icon=folium.Icon(color='green')).add_to(m)
            folium.Marker(gps_points[-1], popup='Current', 
                         icon=folium.Icon(color='red')).add_to(m)
        
        # Save map
        map_file = 'gps_track.html'
        m.save(map_file)
        print(f"✅ GPS map saved to {map_file}")
        
        return map_file
    
    def create_battery_gauge(self):
        """Create battery status gauge"""
        print("🔋 Starting battery monitoring...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        fig.suptitle('Battery Status', fontsize=16)
        
        def animate_battery(frame):
            """Update battery display"""
            ax1.clear()
            ax2.clear()
            
            if self.data['battery_voltage'] and self.data['battery_current']:
                voltage = self.data['battery_voltage'][-1]
                current = self.data['battery_current'][-1]
                
                # Voltage gauge
                ax1.set_title('Battery Voltage')
                ax1.set_xlim(-1, 1)
                ax1.set_ylim(-1, 1)
                
                # Calculate voltage percentage (assuming 4S LiPo: 12.8V-16.8V)
                voltage_percent = max(0, min(100, (voltage - 12.8) / (16.8 - 12.8) * 100))
                
                # Draw voltage arc
                angles = np.linspace(np.pi, 0, 100)
                radius = 0.8
                
                # Background arc
                ax1.plot(radius * np.cos(angles), radius * np.sin(angles), 'lightgray', linewidth=10)
                
                # Voltage arc
                voltage_angles = angles[:int(voltage_percent)]
                color = 'green' if voltage_percent > 50 else 'orange' if voltage_percent > 25 else 'red'
                ax1.plot(radius * np.cos(voltage_angles), radius * np.sin(voltage_angles), 
                        color, linewidth=10)
                
                # Voltage text
                ax1.text(0, -0.3, f'{voltage:.2f}V\n{voltage_percent:.0f}%', 
                        ha='center', va='center', fontsize=14, weight='bold')
                
                ax1.set_aspect('equal')
                ax1.axis('off')
                
                # Current graph
                ax2.set_title('Battery Current')
                if len(self.data['time']) > 1:
                    times = list(self.data['time'])
                    currents = list(self.data['battery_current'])
                    ax2.plot(times, currents, 'blue', linewidth=2)
                    ax2.set_xlim(max(0, times[-1] - 30), times[-1] + 1)
                    ax2.set_ylabel('Current (A)')
                    ax2.set_xlabel('Time (s)')
                    ax2.grid(True)
                
                # Current value
                ax2.text(0.02, 0.98, f'Current: {current:.2f}A', 
                        transform=ax2.transAxes, va='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            return ax1, ax2
        
        ani = animation.FuncAnimation(fig, animate_battery, interval=500)
        plt.tight_layout()
        plt.show()
        
        return ani

def main():
    """Main visualization demonstration"""
    
    SERIAL_PORT = '/dev/ttyUSB0'
    FC_TYPE = FlightController.INAV
    
    print("📊 MSPKit Real-time Visualization Example")
    print("=" * 50)
    print("This example provides real-time visualization of flight data")
    print()
    
    try:
        visualizer = RealTimeVisualizer(SERIAL_PORT, FC_TYPE)
        visualizer.start_data_collection()
        
        # Let some data collect
        print("📊 Collecting initial data...")
        time.sleep(2)
        
        while True:
            print("\n📊 Visualization Menu:")
            print("1. Attitude and telemetry graphs")
            print("2. Artificial horizon")
            print("3. Battery status gauge")
            print("4. Create GPS track map")
            print("5. Show current status")
            print("6. Exit")
            
            choice = input("\nSelect visualization (1-6): ").strip()
            
            if choice == '1':
                print("📈 Opening attitude visualization...")
                print("Close the plot window to return to menu")
                visualizer.create_attitude_visualization()
                
            elif choice == '2':
                print("🛩️  Opening artificial horizon...")
                print("Close the plot window to return to menu")
                visualizer.create_artificial_horizon()
                
            elif choice == '3':
                print("🔋 Opening battery monitor...")
                print("Close the plot window to return to menu")
                visualizer.create_battery_gauge()
                
            elif choice == '4':
                map_file = visualizer.create_gps_map()
                if map_file:
                    print(f"🗺️  Open {map_file} in a web browser to view the GPS track")
                
            elif choice == '5':
                # Show current status
                if visualizer.data['time']:
                    print(f"\n📊 Current Status:")
                    print(f"   Data points: {len(visualizer.data['time'])}")
                    print(f"   Runtime: {visualizer.data['time'][-1]:.1f}s")
                    print(f"   Roll: {visualizer.data['roll'][-1]:.1f}°")
                    print(f"   Pitch: {visualizer.data['pitch'][-1]:.1f}°")
                    print(f"   Yaw: {visualizer.data['yaw'][-1]:.1f}°")
                    print(f"   Altitude: {visualizer.data['altitude'][-1]:.1f}m")
                    print(f"   Battery: {visualizer.data['battery_voltage'][-1]:.2f}V")
                    print(f"   GPS Sats: {visualizer.data['satellites'][-1]}")
                else:
                    print("⚠️  No data collected yet")
                
            elif choice == '6':
                print("👋 Exiting visualization")
                break
                
            else:
                print("❌ Invalid option")
    
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'visualizer' in locals():
            visualizer.stop_data_collection()

if __name__ == "__main__":
    main()
