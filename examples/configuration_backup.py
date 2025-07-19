#!/usr/bin/env python3
"""
Configuration Management Example

This example demonstrates flight controller configuration management:
- Reading and displaying current configuration
- Modifying PID settings safely
- Backup and restore operations
- Feature toggles and settings

Useful for tuning and maintaining flight controller settings.
"""

import json
import time
import logging
from typing import Dict, Any, Optional
from mspkit import connect, FlightController, Config, Telemetry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigurationManager:
    """Comprehensive configuration management"""
    
    def __init__(self, serial_port: str, fc_type: FlightController):
        self.conn = connect(serial_port, fc_type=fc_type)
        self.config = Config(self.conn)
        self.telemetry = Telemetry(self.conn)
        self.fc_type = fc_type
        
        print(f"✅ Connected to {fc_type.name} flight controller")
    
    def display_current_config(self):
        """Display comprehensive current configuration"""
        print("\n📋 Current Configuration")
        print("=" * 60)
        
        try:
            # Basic info
            print("🔧 BASIC INFO:")
            api_info = self.telemetry.get_api_version()
            build_info = self.telemetry.get_build_info()
            
            print(f"   FC Type: {api_info.get('fc_variant', 'Unknown')}")
            print(f"   Version: {build_info.get('version', 'Unknown')}")
            print(f"   Build Date: {build_info.get('build_date', 'Unknown')}")
            print(f"   API Version: {api_info.get('version', 'Unknown')}")
            
            # PID settings
            print("\n🎛️  PID SETTINGS:")
            pid_config = self.config.get_pid_config()
            if pid_config:
                print(f"   Roll:  P={pid_config.get('roll_p', 0):3.0f}  I={pid_config.get('roll_i', 0):3.0f}  D={pid_config.get('roll_d', 0):3.0f}")
                print(f"   Pitch: P={pid_config.get('pitch_p', 0):3.0f}  I={pid_config.get('pitch_i', 0):3.0f}  D={pid_config.get('pitch_d', 0):3.0f}")
                print(f"   Yaw:   P={pid_config.get('yaw_p', 0):3.0f}  I={pid_config.get('yaw_i', 0):3.0f}  D={pid_config.get('yaw_d', 0):3.0f}")
            
            # RC settings
            print("\n📡 RC SETTINGS:")
            rc_tuning = self.config.get_rc_tuning()
            if rc_tuning:
                print(f"   RC Rate: {rc_tuning.get('rc_rate', 0):.2f}")
                print(f"   Expo: {rc_tuning.get('rc_expo', 0):.2f}")
                print(f"   Super Rate: {rc_tuning.get('super_rate', 0):.2f}")
                print(f"   Throttle Mid: {rc_tuning.get('throttle_mid', 0.5):.2f}")
                print(f"   Throttle Expo: {rc_tuning.get('throttle_expo', 0):.2f}")
            
            # Features
            print("\n⚙️  FEATURES:")
            features = self.config.get_features()
            if features:
                enabled_features = [name for name, enabled in features.items() if enabled]
                disabled_features = [name for name, enabled in features.items() if not enabled]
                
                print(f"   Enabled: {', '.join(enabled_features) if enabled_features else 'None'}")
                print(f"   Disabled: {', '.join(disabled_features[:5]) if disabled_features else 'None'}")
                if len(disabled_features) > 5:
                    print(f"            ... and {len(disabled_features) - 5} more")
            
            # Failsafe settings
            print("\n🛡️  FAILSAFE:")
            failsafe = self.config.get_failsafe_config()
            if failsafe:
                print(f"   Throttle: {failsafe.get('failsafe_throttle', 1000)}")
                print(f"   Delay: {failsafe.get('failsafe_delay', 0):.1f}s")
                print(f"   Off Delay: {failsafe.get('failsafe_off_delay', 0):.1f}s")
                print(f"   Kill Switch: {'Enabled' if failsafe.get('failsafe_kill_switch', False) else 'Disabled'}")
            
            # Motor configuration
            print("\n🚁 MOTORS:")
            motor_config = self.config.get_motor_config()
            if motor_config:
                print(f"   Min Throttle: {motor_config.get('min_throttle', 1000)}")
                print(f"   Max Throttle: {motor_config.get('max_throttle', 2000)}")
                print(f"   Min Command: {motor_config.get('min_command', 1000)}")
                print(f"   Motor Poles: {motor_config.get('motor_poles', 14)}")
            
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
    
    def backup_configuration(self, filename: Optional[str] = None) -> bool:
        """Create a complete backup of the configuration"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"fc_backup_{self.fc_type.name.lower()}_{timestamp}.json"
        
        print(f"\n💾 Creating configuration backup...")
        
        try:
            backup_data = {
                'timestamp': time.time(),
                'fc_type': self.fc_type.name,
                'metadata': {},
                'configuration': {}
            }
            
            # Get basic info
            api_info = self.telemetry.get_api_version()
            build_info = self.telemetry.get_build_info()
            
            backup_data['metadata'] = {
                'fc_variant': api_info.get('fc_variant', 'Unknown'),
                'version': build_info.get('version', 'Unknown'),
                'build_date': build_info.get('build_date', 'Unknown'),
                'api_version': api_info.get('version', 'Unknown')
            }
            
            # Collect all configuration sections
            print("   Reading PID configuration...")
            backup_data['configuration']['pid'] = self.config.get_pid_config()
            
            print("   Reading RC tuning...")
            backup_data['configuration']['rc_tuning'] = self.config.get_rc_tuning()
            
            print("   Reading features...")
            backup_data['configuration']['features'] = self.config.get_features()
            
            print("   Reading failsafe configuration...")
            backup_data['configuration']['failsafe'] = self.config.get_failsafe_config()
            
            print("   Reading motor configuration...")
            backup_data['configuration']['motor'] = self.config.get_motor_config()
            
            print("   Reading misc settings...")
            backup_data['configuration']['misc'] = self.config.get_misc_config()
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"✅ Configuration backed up to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def restore_configuration(self, filename: str) -> bool:
        """Restore configuration from backup file"""
        print(f"\n📂 Restoring configuration from {filename}...")
        
        try:
            # Load backup file
            with open(filename, 'r') as f:
                backup_data = json.load(f)
            
            # Verify compatibility
            backup_fc_type = backup_data.get('fc_type', 'Unknown')
            if backup_fc_type != self.fc_type.name:
                print(f"⚠️  FC type mismatch: backup={backup_fc_type}, current={self.fc_type.name}")
                response = input("Continue anyway? (yes/no): ")
                if response.lower() != 'yes':
                    return False
            
            config_data = backup_data.get('configuration', {})
            
            # Restore PID settings
            if 'pid' in config_data and config_data['pid']:
                print("   Restoring PID configuration...")
                if self.config.set_pid_config(config_data['pid']):
                    print("   ✅ PID configuration restored")
                else:
                    print("   ❌ PID configuration failed")
            
            # Restore RC tuning
            if 'rc_tuning' in config_data and config_data['rc_tuning']:
                print("   Restoring RC tuning...")
                if self.config.set_rc_tuning(config_data['rc_tuning']):
                    print("   ✅ RC tuning restored")
                else:
                    print("   ❌ RC tuning failed")
            
            # Restore features
            if 'features' in config_data and config_data['features']:
                print("   Restoring features...")
                if self.config.set_features(config_data['features']):
                    print("   ✅ Features restored")
                else:
                    print("   ❌ Features failed")
            
            # Save to EEPROM
            print("   Saving to EEPROM...")
            if self.config.save_config():
                print("✅ Configuration restore completed and saved")
                return True
            else:
                print("❌ Failed to save configuration to EEPROM")
                return False
                
        except FileNotFoundError:
            print(f"❌ Backup file {filename} not found")
            return False
        except json.JSONDecodeError:
            print(f"❌ Invalid backup file format")
            return False
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def tune_pid_interactive(self):
        """Interactive PID tuning"""
        print("\n🎛️  Interactive PID Tuning")
        print("⚠️  Make small changes and test carefully!")
        print()
        
        # Get current PID values
        current_pid = self.config.get_pid_config()
        if not current_pid:
            print("❌ Could not read current PID configuration")
            return
        
        print("Current PID values:")
        print(f"Roll:  P={current_pid.get('roll_p', 0):3.0f}  I={current_pid.get('roll_i', 0):3.0f}  D={current_pid.get('roll_d', 0):3.0f}")
        print(f"Pitch: P={current_pid.get('pitch_p', 0):3.0f}  I={current_pid.get('pitch_i', 0):3.0f}  D={current_pid.get('pitch_d', 0):3.0f}")
        print(f"Yaw:   P={current_pid.get('yaw_p', 0):3.0f}  I={current_pid.get('yaw_i', 0):3.0f}  D={current_pid.get('yaw_d', 0):3.0f}")
        print()
        
        # Create a copy for modification
        new_pid = current_pid.copy()
        
        while True:
            print("PID Tuning Options:")
            print("1. Adjust Roll P")
            print("2. Adjust Roll I") 
            print("3. Adjust Roll D")
            print("4. Adjust Pitch P")
            print("5. Adjust Pitch I")
            print("6. Adjust Pitch D")
            print("7. Adjust Yaw P")
            print("8. Adjust Yaw I")
            print("9. Adjust Yaw D")
            print("10. Apply changes")
            print("11. Reset to original")
            print("12. Exit without saving")
            
            choice = input("\nSelect option (1-12): ").strip()
            
            pid_map = {
                '1': 'roll_p', '2': 'roll_i', '3': 'roll_d',
                '4': 'pitch_p', '5': 'pitch_i', '6': 'pitch_d',
                '7': 'yaw_p', '8': 'yaw_i', '9': 'yaw_d'
            }
            
            if choice in pid_map:
                param = pid_map[choice]
                current_value = new_pid.get(param, 0)
                
                try:
                    new_value = float(input(f"Enter new value for {param} (current: {current_value}): "))
                    
                    # Basic validation
                    if 0 <= new_value <= 500:  # Reasonable PID limits
                        new_pid[param] = new_value
                        print(f"✅ {param} set to {new_value}")
                        
                        # Show updated values
                        print(f"Roll:  P={new_pid.get('roll_p', 0):3.0f}  I={new_pid.get('roll_i', 0):3.0f}  D={new_pid.get('roll_d', 0):3.0f}")
                        print(f"Pitch: P={new_pid.get('pitch_p', 0):3.0f}  I={new_pid.get('pitch_i', 0):3.0f}  D={new_pid.get('pitch_d', 0):3.0f}")
                        print(f"Yaw:   P={new_pid.get('yaw_p', 0):3.0f}  I={new_pid.get('yaw_i', 0):3.0f}  D={new_pid.get('yaw_d', 0):3.0f}")
                    else:
                        print("❌ Value out of range (0-500)")
                        
                except ValueError:
                    print("❌ Invalid number")
            
            elif choice == '10':
                print("🔧 Applying PID changes...")
                if self.config.set_pid_config(new_pid):
                    print("✅ PID values updated on flight controller")
                    
                    save = input("Save to EEPROM? (yes/no): ")
                    if save.lower() == 'yes':
                        if self.config.save_config():
                            print("✅ PID values saved to EEPROM")
                        else:
                            print("❌ Failed to save to EEPROM")
                    break
                else:
                    print("❌ Failed to update PID values")
            
            elif choice == '11':
                new_pid = current_pid.copy()
                print("🔄 Reset to original values")
            
            elif choice == '12':
                print("❌ Exiting without saving changes")
                break
            
            else:
                print("❌ Invalid option")
    
    def toggle_features(self):
        """Interactive feature toggle"""
        print("\n⚙️  Feature Management")
        
        features = self.config.get_features()
        if not features:
            print("❌ Could not read features")
            return
        
        print("Current features:")
        for i, (name, enabled) in enumerate(features.items(), 1):
            status = "✅ ENABLED " if enabled else "❌ DISABLED"
            print(f"{i:2d}. {name:20s} {status}")
        
        while True:
            try:
                choice = input("\nEnter feature number to toggle (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    break
                
                feature_num = int(choice) - 1
                feature_names = list(features.keys())
                
                if 0 <= feature_num < len(feature_names):
                    feature_name = feature_names[feature_num]
                    current_state = features[feature_name]
                    new_state = not current_state
                    
                    print(f"Toggle {feature_name}: {current_state} → {new_state}")
                    confirm = input("Confirm? (yes/no): ")
                    
                    if confirm.lower() == 'yes':
                        features[feature_name] = new_state
                        
                        if self.config.set_features(features):
                            print(f"✅ {feature_name} {'enabled' if new_state else 'disabled'}")
                            
                            save = input("Save to EEPROM? (yes/no): ")
                            if save.lower() == 'yes':
                                self.config.save_config()
                        else:
                            print(f"❌ Failed to toggle {feature_name}")
                            features[feature_name] = current_state  # Revert
                else:
                    print("❌ Invalid feature number")
                    
            except ValueError:
                print("❌ Invalid input")

def main():
    """Main configuration management demonstration"""
    
    SERIAL_PORT = '/dev/ttyUSB0'
    FC_TYPE = FlightController.INAV  # Change as needed
    
    print("⚙️  MSPKit Configuration Management Example")
    print("=" * 60)
    print("This example demonstrates flight controller configuration")
    print("backup, restore, and tuning capabilities.")
    print()
    
    try:
        config_manager = ConfigurationManager(SERIAL_PORT, FC_TYPE)
        
        while True:
            print("\n⚙️  Configuration Menu:")
            print("1. Display current configuration")
            print("2. Backup configuration to file")
            print("3. Restore configuration from file")
            print("4. Interactive PID tuning")
            print("5. Toggle features")
            print("6. Reset to defaults (with confirmation)")
            print("7. Exit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == '1':
                config_manager.display_current_config()
                
            elif choice == '2':
                filename = input("Enter backup filename (or press Enter for auto): ").strip()
                config_manager.backup_configuration(filename if filename else None)
                
            elif choice == '3':
                filename = input("Enter backup filename to restore: ").strip()
                if filename:
                    config_manager.restore_configuration(filename)
                
            elif choice == '4':
                config_manager.tune_pid_interactive()
                
            elif choice == '5':
                config_manager.toggle_features()
                
            elif choice == '6':
                print("⚠️  RESET TO DEFAULTS")
                print("This will erase ALL settings and return to factory defaults!")
                print("Make sure you have a backup!")
                print()
                
                confirm1 = input("Type 'RESET' to confirm: ")
                if confirm1 == 'RESET':
                    confirm2 = input("Are you absolutely sure? (yes/no): ")
                    if confirm2.lower() == 'yes':
                        print("🔧 Resetting to defaults...")
                        if config_manager.config.reset_config():
                            print("✅ Reset completed - flight controller will reboot")
                        else:
                            print("❌ Reset failed")
                    else:
                        print("❌ Reset cancelled")
                else:
                    print("❌ Reset cancelled")
                
            elif choice == '7':
                print("👋 Exiting configuration manager")
                break
                
            else:
                print("❌ Invalid option")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
