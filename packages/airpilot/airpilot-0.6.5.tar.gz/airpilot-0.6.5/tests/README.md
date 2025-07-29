# Tests

Test directory for AirPilot CLI functionality.

## Purpose

This directory contains test cases and test artifacts for the AirPilot CLI implementation.

## Structure

- `test_*.py` - pytest test files
- `fixtures/` - Test data and sample configurations
- `temp/` - Temporary test outputs (gitignored)

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=airpilot

# Run specific test file
uv run pytest tests/test_cli.py
```

## Test Categories

### Unit Tests
- CLI command parsing
- Configuration handling
- Scaffolding logic

### Integration Tests  
- Full air init workflows
- File system operations
- Git integration

### End-to-End Tests
- Complete CLI scenarios
- Cross-platform compatibility
- Error handling