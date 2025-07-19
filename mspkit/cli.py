#!/usr/bin/env python3
"""
MSPKit Command Line Interface

Provides easy command-line access to MSPKit functionality.
"""

import argparse
import json
import sys
import logging
from typing import Optional

from mspkit import connect, FlightController, Telemetry, Mission, Config

def setup_logging(verbose: bool):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def connect_to_fc(port: str, fc_type: str) -> Optional[object]:
    """Connect to flight controller"""
    try:
        fc_enum = FlightController.INAV if fc_type.upper() == 'INAV' else FlightController.BETAFLIGHT
        return connect(port, fc_type=fc_enum)
    except Exception as e:
        print(f"Failed to connect to {port}: {e}")
        return None

def cmd_info(args):
    """Get flight controller information"""
    conn = connect_to_fc(args.port, args.fc_type)
    if not conn:
        return 1
    
    telem = Telemetry(conn)
    info = telem.get_api_version()
    
    print(f"Flight Controller Info:")
    print(f"  Type: {args.fc_type}")
    print(f"  API Version: {info.get('version', 'Unknown')}")
    print(f"  MSP Version: {info.get('msp_version', 'Unknown')}")
    
    return 0

def cmd_telemetry(args):
    """Stream telemetry data"""
    conn = connect_to_fc(args.port, args.fc_type)
    if not conn:
        return 1
    
    telem = Telemetry(conn)
    
    try:
        import time
        while True:
            attitude = telem.get_attitude()
            gps = telem.get_gps()
            
            print(f"\rRoll: {attitude.get('roll', 0):6.1f}° | "
                  f"Pitch: {attitude.get('pitch', 0):6.1f}° | "
                  f"Yaw: {attitude.get('yaw', 0):6.1f}° | "
                  f"Alt: {gps.get('alt', 0):6.1f}m", end='')
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nTelemetry stopped")
        return 0

def cmd_mission_upload(args):
    """Upload mission from file"""
    conn = connect_to_fc(args.port, args.fc_type)
    if not conn:
        return 1
    
    mission = Mission(conn)
    
    if mission.load_mission_from_file(args.file):
        print(f"Loaded mission with {mission.get_waypoint_count()} waypoints")
        
        if mission.upload_mission():
            print("Mission uploaded successfully!")
            return 0
        else:
            print("Failed to upload mission")
            return 1
    else:
        print(f"Failed to load mission from {args.file}")
        return 1

def cmd_mission_download(args):
    """Download mission to file"""
    conn = connect_to_fc(args.port, args.fc_type)
    if not conn:
        return 1
    
    mission = Mission(conn)
    
    if mission.download_mission():
        if mission.save_mission_to_file(args.file):
            print(f"Mission saved to {args.file} ({mission.get_waypoint_count()} waypoints)")
            return 0
        else:
            print(f"Failed to save mission to {args.file}")
            return 1
    else:
        print("Failed to download mission")
        return 1

def cmd_config_backup(args):
    """Backup flight controller configuration"""
    conn = connect_to_fc(args.port, args.fc_type)
    if not conn:
        return 1
    
    config = Config(conn)
    
    if config.backup_config(args.file):
        print(f"Configuration backed up to {args.file}")
        return 0
    else:
        print("Failed to backup configuration")
        return 1

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MSPKit CLI - Command line interface for MSPKit SDK"
    )
    
    parser.add_argument(
        '-p', '--port',
        default='/dev/ttyUSB0',
        help='Serial port (default: /dev/ttyUSB0)'
    )
    
    parser.add_argument(
        '-t', '--fc-type',
        choices=['INAV', 'BETAFLIGHT'],
        default='INAV',
        help='Flight controller type (default: INAV)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Info command
    subparsers.add_parser('info', help='Get flight controller information')
    
    # Telemetry command
    subparsers.add_parser('telemetry', help='Stream telemetry data')
    
    # Mission commands
    mission_upload = subparsers.add_parser('mission-upload', help='Upload mission from file')
    mission_upload.add_argument('file', help='Mission file path')
    
    mission_download = subparsers.add_parser('mission-download', help='Download mission to file')
    mission_download.add_argument('file', help='Mission file path')
    
    # Config commands
    config_backup = subparsers.add_parser('config-backup', help='Backup configuration')
    config_backup.add_argument('file', help='Backup file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    setup_logging(args.verbose)
    
    # Route to appropriate command handler
    commands = {
        'info': cmd_info,
        'telemetry': cmd_telemetry,
        'mission-upload': cmd_mission_upload,
        'mission-download': cmd_mission_download,
        'config-backup': cmd_config_backup,
    }
    
    return commands[args.command](args)

if __name__ == '__main__':
    sys.exit(main())
