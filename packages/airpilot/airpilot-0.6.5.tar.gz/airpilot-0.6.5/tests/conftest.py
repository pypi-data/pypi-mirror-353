#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for AirPilot CLI tests.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator, List

import pytest


@pytest.fixture(scope="session")
def original_cwd() -> Path:
    """Preserve original working directory for the entire test session"""
    return Path.cwd()


@pytest.fixture
def isolated_filesystem() -> Generator[Path, None, None]:
    """
    Create an isolated filesystem for testing.

    This fixture creates a temporary directory, changes to it for the test,
    and then restores the original working directory after the test completes.
    """
    original_cwd = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        os.chdir(temp_path)

        try:
            yield temp_path
        finally:
            os.chdir(original_cwd)


@pytest.fixture
def mock_home_directory() -> Generator[Path, None, None]:
    """
    Create a temporary directory to serve as a mock home directory.

    This fixture creates a temporary directory that can be used as a mock
    home directory for testing global installations without affecting
    the real user home directory.
    """
    with tempfile.TemporaryDirectory() as temp_home:
        yield Path(temp_home)


@pytest.fixture
def sample_git_repo(isolated_filesystem: Path) -> Generator[Path, None, None]:
    """
    Create a sample Git repository for testing Git-related functionality.

    Args:
        isolated_filesystem: Isolated filesystem fixture

    Yields:
        Path: Path to the Git repository directory
    """
    repo_dir = isolated_filesystem / "sample-repo"
    repo_dir.mkdir()

    # Initialize Git repository
    try:
        subprocess.run(
            ["git", "init"],
            cwd=repo_dir,
            check=True,
            capture_output=True
        )

        # Configure git user for tests
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_dir,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_dir,
            check=True,
            capture_output=True
        )

        yield repo_dir

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git not available, skip tests that require it
        pytest.skip("Git not available for testing")


@pytest.fixture
def sample_air_directory(isolated_filesystem: Path) -> Generator[Path, None, None]:
    """
    Create a sample .air directory structure for testing.

    Args:
        isolated_filesystem: Isolated filesystem fixture

    Yields:
        Path: Path to the .air directory
    """
    air_dir = isolated_filesystem / ".air"
    air_dir.mkdir()

    # Create basic structure
    (air_dir / "rules").mkdir()
    (air_dir / "rules" / "index.md").write_text("# Test Rules\n\nTest content")

    (air_dir / "prompts").mkdir()
    (air_dir / "prompts" / "index.md").write_text("# Test Prompts\n\nTest content")

    yield air_dir


@pytest.fixture
def sample_vendor_directories(isolated_filesystem: Path) -> Generator[List[str], None, None]:
    """
    Create sample AI vendor directories for testing backup functionality.

    Args:
        isolated_filesystem: Isolated filesystem fixture

    Yields:
        list: List of vendor directory names that were created
    """
    vendors = [".claude", ".cursor", ".cline", ".clinerules"]

    for vendor in vendors:
        vendor_dir = isolated_filesystem / vendor
        vendor_dir.mkdir()

        # Add some sample content
        if vendor == ".github":
            copilot_dir = vendor_dir / "copilot-instructions"
            copilot_dir.mkdir(parents=True)
            (copilot_dir / "instructions.md").write_text("# Copilot Instructions")
        else:
            (vendor_dir / "config.md").write_text(f"# {vendor} Configuration")

    yield vendors


# Test data constants
TEST_PROJECT_NAMES = [
    "simple-project",
    "project-with-dashes",
    "project_with_underscores",
    "CamelCaseProject",
    "project123"
]

INVALID_PROJECT_NAMES = [
    "",
    " ",
    "project with spaces",
    "project/with/slashes",
    "project\\with\\backslashes",
    "project:with:colons"
]

SAMPLE_CONFIG_DATA = {
    "version": "0.0.1",
    "user": {
        "name": "Test User",
        "email": "test@example.com",
        "preferences": {
            "default_domain": "software",
            "auto_backup": True,
            "sync_on_change": True
        }
    },
    "global_air_path": "/test/path/.air",
    "created": "2025-01-06"
}
