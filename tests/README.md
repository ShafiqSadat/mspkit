# Tests for MSPKit

This directory contains the test suite for MSPKit.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mspkit

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v
```

## Test Structure

- `test_core.py` - Tests for core MSP protocol functionality
- `test_telemetry.py` - Tests for telemetry data access
- `test_control.py` - Tests for flight control features
- `test_mission.py` - Tests for mission planning
- `test_config.py` - Tests for configuration management
- `test_sensors.py` - Tests for sensor management
- `test_cli.py` - Tests for CLI tools

## Test Categories

### Unit Tests
Individual function and class testing with mocked dependencies.

### Integration Tests
Testing component interactions and protocol communication.

### Hardware Tests
Tests that require actual flight controller hardware (marked with `@pytest.mark.hardware`).

## Mocking

Hardware interactions are mocked using pytest fixtures to ensure tests can run without actual flight controller hardware.

## Running Hardware Tests

To run tests with actual hardware:

```bash
# Run only hardware tests (requires flight controller connected)
pytest -m hardware

# Skip hardware tests (default)
pytest -m "not hardware"
```
