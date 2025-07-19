#!/usr/bin/env python3
"""
Flight Control Example

This example demonstrates safe flight control operations including:
- Arming/disarming procedures
- RC override for manual control
- Flight mode changes
- Emergency procedures

⚠️  SAFETY WARNING: Only run this with propellers removed or in a simulator!
"""

import time
import logging
from mspkit import connect, FlightController, Control, Telemetry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeFlightController:
    """Safe wrapper for flight control operations"""
    
    def __init__(self, serial_port: str, fc_type: FlightController):
        self.conn = connect(serial_port, fc_type=fc_type)
        self.control = Control(self.conn)
        self.telemetry = Telemetry(self.conn)
        self.armed = False
        
    def safety_check(self) -> bool:
        """Perform pre-flight safety checks"""
        print("🔍 Performing safety checks...")
        
        try:
            # Check connection
            status = self.telemetry.get_status()
            if not status:
                print("❌ Cannot communicate with flight controller")
                return False
            
            # Check if already armed
            if status.get('armed', False):
                print("⚠️  Flight controller is already ARMED!")
                response = input("Continue anyway? (yes/no): ")
                if response.lower() != 'yes':
                    return False
            
            # Check battery voltage
            battery = self.telemetry.get_battery()
            voltage = battery.get('voltage', 0)
            if voltage < 10.5:  # Typical 3S minimum
                print(f"⚠️  Low battery voltage: {voltage:.2f}V")
                response = input("Continue anyway? (yes/no): ")
                if response.lower() != 'yes':
                    return False
            
            # Check GPS if using GPS modes
            gps = self.telemetry.get_gps()
            satellites = gps.get('num_sat', 0)
            if satellites < 6:
                print(f"⚠️  Low GPS satellite count: {satellites}")
                print("GPS-dependent modes may not work properly")
            
            print("✅ Safety checks passed")
            return True
            
        except Exception as e:
            print(f"❌ Safety check failed: {e}")
            return False
    
    def arm_aircraft(self) -> bool:
        """Safely arm the aircraft"""
        if not self.safety_check():
            return False
        
        print("🔧 Attempting to arm aircraft...")
        
        # Ensure throttle is low
        self.control.set_rc_override(throttle=1000)
        time.sleep(0.5)
        
        # Arm the aircraft
        if self.control.arm():
            print("✅ Aircraft ARMED successfully")
            self.armed = True
            return True
        else:
            print("❌ Failed to arm aircraft")
            print("Check:")
            print("- Throttle is at minimum")
            print("- All sensors are calibrated")
            print("- No failsafe conditions active")
            return False
    
    def disarm_aircraft(self) -> bool:
        """Safely disarm the aircraft"""
        print("🔧 Disarming aircraft...")
        
        # Cut throttle first
        self.control.set_rc_override(throttle=1000)
        time.sleep(0.2)
        
        if self.control.disarm():
            print("✅ Aircraft DISARMED successfully")
            self.armed = False
            return True
        else:
            print("❌ Failed to disarm aircraft")
            return False
    
    def controlled_hover_test(self, duration: int = 10):
        """Perform a controlled hover test"""
        if not self.armed:
            print("❌ Aircraft must be armed first")
            return False
        
        print(f"🚁 Starting {duration}s hover test...")
        print("   Throttle will gradually increase to hover point")
        
        hover_throttle = 1500  # Approximate hover point
        steps = 20
        throttle_increment = (hover_throttle - 1000) // steps
        
        try:
            # Gradually increase throttle
            for step in range(steps):
                current_throttle = 1000 + (throttle_increment * step)
                self.control.set_rc_override(throttle=current_throttle)
                
                # Monitor telemetry
                attitude = self.telemetry.get_attitude()
                print(f"   Step {step+1}/{steps}: Throttle={current_throttle}, "
                      f"Alt={attitude.get('alt', 0):.1f}m")
                
                time.sleep(0.5)
            
            # Maintain hover
            print(f"🏃 Maintaining hover for {duration} seconds...")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Monitor attitude and make small corrections
                attitude = self.telemetry.get_attitude()
                roll = attitude.get('roll', 0)
                pitch = attitude.get('pitch', 0)
                
                # Simple stabilization (very basic)
                roll_correction = max(-200, min(200, -roll * 10))
                pitch_correction = max(-200, min(200, -pitch * 10))
                
                self.control.set_rc_override(
                    throttle=hover_throttle,
                    roll=1500 + int(roll_correction),
                    pitch=1500 + int(pitch_correction),
                    yaw=1500
                )
                
                remaining = duration - (time.time() - start_time)
                print(f"\r   Hovering... {remaining:.1f}s remaining", end='', flush=True)
                time.sleep(0.1)
            
            print("\n✅ Hover test completed")
            
        except KeyboardInterrupt:
            print("\n🛑 Hover test interrupted by user")
        except Exception as e:
            print(f"\n❌ Hover test error: {e}")
        finally:
            # Always cut throttle
            self.control.set_rc_override(throttle=1000)
            time.sleep(0.5)
    
    def emergency_stop(self):
        """Emergency stop procedure"""
        print("🚨 EMERGENCY STOP ACTIVATED!")
        
        # Immediate throttle cut
        self.control.set_rc_override(throttle=1000)
        
        # Clear RC overrides
        self.control.clear_rc_override()
        
        # Disarm
        self.disarm_aircraft()
        
        print("✅ Emergency stop completed")

def main():
    """Main flight control demonstration"""
    
    SERIAL_PORT = '/dev/ttyUSB0'
    FC_TYPE = FlightController.INAV
    
    print("🚁 MSPKit Flight Control Example")
    print("=" * 50)
    print("⚠️  SAFETY WARNING:")
    print("   - Remove propellers before testing")
    print("   - Ensure aircraft is secure")
    print("   - Have emergency stop ready")
    print("   - Only run in safe environment")
    print()
    
    response = input("Are you ready to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Exiting for safety")
        return
    
    try:
        # Initialize flight controller
        print(f"\n📡 Connecting to {FC_TYPE.name} on {SERIAL_PORT}...")
        flight_controller = SafeFlightController(SERIAL_PORT, FC_TYPE)
        print("✅ Connected successfully!")
        
        while True:
            print("\n🎮 Flight Control Menu:")
            print("1. Arm aircraft")
            print("2. Disarm aircraft")
            print("3. Hover test (10 seconds)")
            print("4. Emergency stop")
            print("5. Monitor telemetry")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                flight_controller.arm_aircraft()
                
            elif choice == '2':
                flight_controller.disarm_aircraft()
                
            elif choice == '3':
                if flight_controller.armed:
                    flight_controller.controlled_hover_test()
                else:
                    print("❌ Aircraft must be armed first")
                    
            elif choice == '4':
                flight_controller.emergency_stop()
                
            elif choice == '5':
                print("📊 Monitoring telemetry (Press Ctrl+C to stop)...")
                try:
                    while True:
                        status = flight_controller.telemetry.get_status()
                        attitude = flight_controller.telemetry.get_attitude()
                        battery = flight_controller.telemetry.get_battery()
                        
                        print(f"\r{'ARMED' if status.get('armed') else 'DISARMED'} | "
                              f"Roll: {attitude.get('roll', 0):6.1f}° | "
                              f"Pitch: {attitude.get('pitch', 0):6.1f}° | "
                              f"Battery: {battery.get('voltage', 0):4.2f}V", 
                              end='', flush=True)
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\n📊 Telemetry monitoring stopped")
                    
            elif choice == '6':
                print("👋 Exiting flight control")
                if flight_controller.armed:
                    print("🔧 Disarming aircraft before exit...")
                    flight_controller.disarm_aircraft()
                break
                
            else:
                print("❌ Invalid option")
    
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted")
        if 'flight_controller' in locals() and flight_controller.armed:
            flight_controller.emergency_stop()
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'flight_controller' in locals() and flight_controller.armed:
            flight_controller.emergency_stop()

if __name__ == "__main__":
    main()
