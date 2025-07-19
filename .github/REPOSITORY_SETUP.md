# MSPKit Repository Configuration

This file documents the recommended GitHub repository settings for the MSPKit project.

## Repository Settings

### General
- **Description**: "A comprehensive Python SDK for iNav and Betaflight flight controllers using MSP protocol"
- **Website**: https://github.com/ShafiqSadat/mspkit
- **Topics**: `python`, `drone`, `uav`, `inav`, `betaflight`, `msp`, `flight-controller`, `sdk`, `multiwii`, `cleanflight`
- **Include in the homepage**: ✅ README.md

### Features
- ✅ Wikis
- ✅ Issues
- ✅ Sponsorships
- ✅ Discussions
- ❌ Projects (enable if you plan to use project boards)

### Pull Requests
- ✅ Allow merge commits
- ✅ Allow squash merging (default)
- ❌ Allow rebase merging
- ✅ Always suggest updating pull request branches
- ✅ Automatically delete head branches

### Branch Protection Rules (for main branch)
- ✅ Require a pull request before merging
  - ✅ Require approvals (1 required)
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from CODEOWNERS
- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - Required status checks: `test (3.8)`, `test (3.9)`, `test (3.10)`, `test (3.11)`
- ✅ Require conversation resolution before merging
- ✅ Include administrators

### Security
- ✅ Enable vulnerability alerts
- ✅ Enable automated security updates
- ✅ Enable private vulnerability reporting

## Labels

The repository should include these labels for better issue organization:

### Type Labels
- `bug` (red) - Something isn't working
- `enhancement` (light blue) - New feature or request
- `documentation` (blue) - Improvements or additions to documentation
- `performance` (orange) - Performance improvements
- `refactoring` (yellow) - Code refactoring without functional changes

### Priority Labels
- `priority: critical` (dark red) - Critical issue that blocks major functionality
- `priority: high` (red) - High priority issue
- `priority: medium` (orange) - Medium priority issue
- `priority: low` (green) - Low priority issue

### Status Labels
- `needs-triage` (gray) - Needs initial review and categorization
- `needs-reproduction` (yellow) - Bug report needs reproduction steps
- `in-progress` (light blue) - Currently being worked on
- `blocked` (red) - Cannot proceed due to external dependencies
- `ready-for-review` (green) - Ready for code review

### Component Labels
- `component: core` - Core MSP protocol functionality
- `component: telemetry` - Telemetry data access
- `component: control` - Flight control features
- `component: mission` - Mission planning features
- `component: config` - Configuration management
- `component: sensors` - Sensor management
- `component: cli` - Command-line interface
- `component: examples` - Example code

### Special Labels
- `good first issue` (green) - Good for newcomers
- `help wanted` (green) - Extra attention is needed
- `breaking change` (red) - Will break existing functionality
- `duplicate` (gray) - This issue or pull request already exists
- `wontfix` (white) - This will not be worked on

## Milestones

Suggested milestones for organizing releases:

- `v0.2.1` - Bug fixes and minor improvements
- `v0.3.0` - New features and enhancements
- `v1.0.0` - Stable API release
- `Future` - Ideas for future consideration

## Repository Description Template

```
A comprehensive Python SDK for iNav and Betaflight flight controllers, providing a DroneKit-style interface using the MSP (MultiWii Serial Protocol) v1 and v2. Features safe flight control, real-time telemetry, mission planning, configuration management, and sensor calibration.
```
