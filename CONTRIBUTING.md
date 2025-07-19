# Contributing to MSPKit

Thank you for your interest in contributing to MSPKit! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and constructive in all interactions.

## Getting Started

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/mspkit.git
   cd mspkit
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```

5. Run tests to ensure everything works:
   ```bash
   pytest
   ```

### Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards below

3. Add or update tests as needed

4. Run the test suite:
   ```bash
   pytest
   ```

5. Run code formatting and linting:
   ```bash
   black mspkit/
   isort mspkit/
   flake8 mspkit/
   mypy mspkit/
   ```

6. Commit your changes with a clear commit message:
   ```bash
   git commit -m "Add feature: your clear description"
   ```

7. Push to your fork and submit a pull request

## Coding Standards

### Python Style
- Follow PEP 8 style guidelines
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 88 characters (Black default)

### Type Hints
- Use type hints for all new code
- Existing code should be gradually updated with type hints
- Use mypy for type checking

### Documentation
- Write clear docstrings for all public functions and classes
- Use Google-style docstrings
- Update README.md if adding new features
- Add examples for new functionality

### Testing
- Write unit tests for all new functionality
- Maintain or improve test coverage
- Test edge cases and error conditions
- Use pytest for testing

## Pull Request Guidelines

### Before Submitting
- Ensure all tests pass
- Update documentation as needed
- Add changelog entry for significant changes
- Rebase your branch on the latest main branch

### PR Description
- Clearly describe what the PR does
- Reference any related issues
- Include screenshots for UI changes
- List any breaking changes

### Review Process
- All PRs require at least one review
- Address reviewer feedback promptly
- Keep PRs focused and reasonably sized
- Be open to suggestions and improvements

## Types of Contributions

### Bug Reports
- Use the GitHub issue template
- Include minimal reproduction code
- Specify your environment (OS, Python version, etc.)
- Include relevant error messages and logs

### Feature Requests
- Describe the use case clearly
- Explain why the feature would be valuable
- Consider if it fits the project scope
- Be open to alternative solutions

### Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

### Documentation
- README improvements
- Code comments and docstrings
- Example code and tutorials
- Wiki pages

## Architecture Guidelines

### Core Principles
- **Safety First**: All flight control code must include safety checks
- **Compatibility**: Support both MSP v1 and v2 protocols
- **Simplicity**: Keep the API intuitive and easy to use
- **Reliability**: Handle errors gracefully and provide meaningful feedback

### Code Organization
- `mspkit/core.py`: Core connection and MSP protocol handling
- `mspkit/telemetry.py`: Telemetry data access
- `mspkit/control.py`: Flight control functionality
- `mspkit/mission.py`: Mission planning (iNav)
- `mspkit/config.py`: Configuration management
- `mspkit/sensors.py`: Sensor management and calibration

### Adding New Features

#### New MSP Commands
1. Add command constants to `msp_constants.py`
2. Implement the command in the appropriate module
3. Add comprehensive error handling
4. Write unit tests
5. Update documentation

#### New Flight Controller Support
1. Test compatibility with existing code
2. Add any required protocol variations
3. Update compatibility matrix in README
4. Add integration tests

## Testing

### Test Categories
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Hardware Tests**: Test with actual flight controllers (when available)
- **Safety Tests**: Verify safety mechanisms work correctly

### Test Requirements
- Tests must pass on all supported Python versions
- Include both positive and negative test cases
- Mock hardware interactions appropriately
- Test error conditions and edge cases

## Security

### Reporting Security Issues
- DO NOT open public issues for security vulnerabilities
- Email security concerns privately to the maintainers
- Include detailed information about the vulnerability
- Allow time for investigation and fixes before disclosure

### Security Considerations
- Flight control code has safety implications
- Validate all user inputs
- Implement timeouts and fail-safes
- Audit dependencies regularly

## Release Process

### Version Numbering
- Follow Semantic Versioning (semver.org)
- Major version: Breaking changes
- Minor version: New features (backward compatible)
- Patch version: Bug fixes

### Release Checklist
1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create GitHub release
5. Publish to PyPI
6. Update documentation

## Questions and Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community support
- **Documentation**: Check the wiki and README first

## Recognition

Contributors will be acknowledged in:
- `CONTRIBUTORS.md` file
- GitHub releases
- Project documentation

Thank you for contributing to MSPKit and helping make drone development more accessible!
