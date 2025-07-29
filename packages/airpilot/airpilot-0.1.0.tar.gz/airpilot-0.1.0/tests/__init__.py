#!/usr/bin/env python3
"""
AirPilot CLI Test Suite

This package contains comprehensive tests for the AirPilot CLI functionality.

Test Structure:
- test_cli.py: Core CLI command functionality and utility functions
- test_scaffolding.py: Scaffolding functions and content generation
- test_integration.py: End-to-end workflows and integration tests
- conftest.py: Shared fixtures and test configuration

Test Categories:
- Unit Tests: Individual function testing with real filesystem operations
- Integration Tests: Complete workflow testing
- Content Quality Tests: Generated content validation
- Error Handling Tests: Edge cases and error recovery
- Performance Tests: Initialization timing and scalability
- Platform Compatibility Tests: Cross-platform functionality

Running Tests:
    # All tests
    uv run pytest

    # Specific test file
    uv run pytest tests/test_cli.py

    # With coverage
    uv run pytest --cov=airpilot

    # Verbose output
    uv run pytest -v

    # Stop on first failure
    uv run pytest -x

Test Philosophy:
These tests verify actual functionality without mocking filesystem operations
to ensure real-world reliability. Tests create temporary directories and
verify that the CLI produces the expected file structure and content.
"""
