#!/usr/bin/env python3
"""
MSPKit SDK - Installation Test

This script tests the basic functionality of the MSPKit SDK installation
without requiring a physical flight controller connection.
"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import mspkit
        print(f"✅ Main module imported (version {mspkit.__version__})")
    except Exception as e:
        print(f"❌ Failed to import main module: {e}")
        return False
    
    try:
        from mspkit import (
            ConnectionManager, FlightController, MSPException,
            Telemetry, Control, Config, Mission, Waypoint, Sensors,
            MSPCommands, FlightModes, connect, get_flight_data
        )
        print("✅ All classes and functions imported successfully")
    except Exception as e:
        print(f"❌ Failed to import components: {e}")
        return False
    
    return True

def test_enums_and_constants():
    """Test enum and constant definitions"""
    print("\nTesting enums and constants...")
    
    try:
        from mspkit import FlightController, MSPCommands, FlightModes, PWM_VALUES
        
        # Test FlightController enum
        assert FlightController.INAV == 1
        assert FlightController.BETAFLIGHT == 2
        print("✅ FlightController enum working")
        
        # Test MSP commands
        assert MSPCommands.MSP_ATTITUDE == 108
        assert MSPCommands.MSP_STATUS == 101
        print("✅ MSP commands defined correctly")
        
        # Test PWM values
        assert PWM_VALUES['MIN'] == 1000
        assert PWM_VALUES['MAX'] == 2000
        print("✅ PWM constants defined correctly")
        
    except Exception as e:
        print(f"❌ Enum/constant test failed: {e}")
        return False
    
    return True

def test_class_instantiation():
    """Test that classes can be instantiated (without connection)"""
    print("\nTesting class instantiation...")
    
    try:
        from mspkit import Waypoint, FlightController
        
        # Test Waypoint class
        wp = Waypoint(47.6062, -122.3321, 50.0)
        assert wp.lat == 47.6062
        assert wp.lon == -122.3321
        assert wp.alt == 50.0
        print("✅ Waypoint class working")
        
        # Test waypoint serialization
        wp_dict = wp.to_dict()
        wp2 = Waypoint.from_dict(wp_dict)
        assert wp2.lat == wp.lat
        print("✅ Waypoint serialization working")
        
    except Exception as e:
        print(f"❌ Class instantiation test failed: {e}")
        return False
    
    return True

def test_mission_planning():
    """Test mission planning functionality (without FC connection)"""
    print("\nTesting mission planning...")
    
    try:
        from mspkit import Mission, Waypoint, FlightController
        
        # Create a mock connection object
        class MockConnection:
            def __init__(self):
                self.fc_type = FlightController.INAV
        
        mock_conn = MockConnection()
        mission = Mission(mock_conn)
        
        # Test adding waypoints
        success = mission.add_waypoint(47.6062, -122.3321, 50.0)
        assert success
        assert mission.get_waypoint_count() == 1
        print("✅ Waypoint addition working")
        
        # Test mission creation
        waypoints = [
            (47.6062, -122.3321, 50),
            (47.6072, -122.3331, 60),
            (47.6082, -122.3341, 50),
        ]
        success = mission.create_simple_mission(waypoints)
        assert success
        assert mission.get_waypoint_count() > 3  # Includes RTH waypoint
        print("✅ Mission creation working")
        
        # Test mission info
        info = mission.get_mission_info()
        assert info['waypoint_count'] > 0
        print("✅ Mission info working")
        
    except Exception as e:
        print(f"❌ Mission planning test failed: {e}")
        return False
    
    return True

def test_convenience_functions():
    """Test convenience functions"""
    print("\nTesting convenience functions...")
    
    try:
        from mspkit import connect, FlightController
        
        # Test that connect function exists and handles invalid ports gracefully
        try:
            # This should fail but not crash
            conn = connect('/invalid/port', fc_type=FlightController.INAV)
            print("⚠️  Invalid port connection didn't fail as expected")
        except:
            print("✅ Connect function handles invalid ports properly")
        
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
        return False
    
    return True

def test_logging():
    """Test logging configuration"""
    print("\nTesting logging...")
    
    try:
        import logging
        from mspkit.core import logger as core_logger
        
        # Test that loggers are configured
        assert core_logger.name == 'mspkit.core'
        print("✅ Logging configuration working")
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚁 MSPKit SDK - Installation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_enums_and_constants,
        test_class_instantiation,
        test_mission_planning,
        test_convenience_functions,
        test_logging,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! MSPKit SDK is ready to use.")
        print("\nNext steps:")
        print("1. Connect your flight controller via USB")
        print("2. Run: python examples/comprehensive_demo.py")
        print("3. Check the documentation in README.md")
        return 0
    else:
        print("❌ Some tests failed. Please check your installation.")
        print("Try: pip install --upgrade mspkit")
        return 1

if __name__ == "__main__":
    sys.exit(main())
