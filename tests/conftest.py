"""
Pytest configuration and shared fixtures for MSPKit tests.
"""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_serial():
    """Provide a mocked serial connection."""
    mock = MagicMock()
    mock.write.return_value = None
    mock.read.return_value = b''
    mock.in_waiting = 0
    mock.is_open = True
    return mock


@pytest.fixture
def mock_connection():
    """Provide a mocked MSP connection."""
    mock = MagicMock()
    mock.is_connected = True
    mock.fc_type = "INAV"
    mock.msp_version = 2
    return mock


@pytest.fixture
def sample_telemetry_data():
    """Provide sample telemetry data for testing."""
    return {
        'attitude': {
            'roll': 5.2,
            'pitch': -2.1,
            'yaw': 180.5
        },
        'gps': {
            'latitude': 47.6062,
            'longitude': -122.3321,
            'altitude': 150,
            'fix_type': 'GPS_FIX_3D',
            'num_satellites': 8
        },
        'battery': {
            'voltage': 12.6,
            'current': 5.2,
            'consumed': 1200
        }
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "hardware: mark test as requiring actual hardware"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
