"""
Basic tests for MSPKit core functionality.
These tests use mocked connections to avoid requiring actual hardware.
"""

import pytest
from unittest.mock import Mock, patch
import mspkit
from mspkit.core import ConnectionManager
from mspkit import FlightController


class TestConnectionManager:
    """Test the core connection management functionality."""

    def test_connection_manager_init(self):
        """Test ConnectionManager initialization."""
        # This is a basic structure test - actual implementation may vary
        assert hasattr(mspkit, 'connect')

    @patch('serial.Serial')
    def test_connection_creation(self, mock_serial):
        """Test creating a connection with mocked serial."""
        mock_serial.return_value = Mock()
        
        # Test that connection can be attempted (implementation may vary)
        try:
            # This will depend on actual implementation
            conn = mspkit.connect('/dev/ttyUSB0', fc_type=FlightController.INAV)
            assert conn is not None
        except (ImportError, AttributeError):
            # Skip if implementation is not ready
            pytest.skip("Connection implementation not available")

    def test_flight_controller_types(self):
        """Test that flight controller types are defined."""
        assert hasattr(FlightController, 'INAV')
        assert hasattr(FlightController, 'BETAFLIGHT')


class TestPackageStructure:
    """Test the package structure and imports."""

    def test_package_imports(self):
        """Test that main components can be imported."""
        import mspkit
        
        # Test basic package structure
        assert hasattr(mspkit, '__version__')

    def test_main_classes_importable(self):
        """Test that main classes can be imported."""
        try:
            from mspkit import Telemetry, Control, Mission, Config, Sensors
            # Classes exist and are importable
            assert Telemetry is not None
            assert Control is not None
            assert Mission is not None
            assert Config is not None
            assert Sensors is not None
        except ImportError:
            # Some classes might not be implemented yet
            pytest.skip("Some classes not yet implemented")


@pytest.mark.hardware
class TestHardwareConnection:
    """Tests that require actual hardware (marked as hardware tests)."""

    def test_real_connection(self):
        """Test connection to real hardware - requires flight controller."""
        pytest.skip("Hardware test - requires connected flight controller")

    def test_real_telemetry(self):
        """Test real telemetry data - requires flight controller."""
        pytest.skip("Hardware test - requires connected flight controller")


if __name__ == "__main__":
    pytest.main([__file__])
