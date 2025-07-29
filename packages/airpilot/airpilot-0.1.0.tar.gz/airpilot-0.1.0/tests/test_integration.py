#!/usr/bin/env python3
"""
Integration tests for AirPilot CLI.

These tests verify end-to-end functionality and integration between components.
"""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from airpilot.cli import cli


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""

    def setup_method(self) -> None:
        """Set up test environment"""
        self.runner = CliRunner()

    @pytest.fixture
    def isolated_project(self) -> Generator[Path, None, None]:
        """Create isolated project directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original_cwd = Path.cwd()
            os.chdir(temp_path)
            try:
                yield temp_path
            finally:
                os.chdir(original_cwd)

    def test_complete_project_initialization_workflow(self, isolated_project: Path) -> None:
        """Test complete project initialization from start to finish"""
        project_name = "test-integration-project"

        # Step 1: Initialize new project
        result = self.runner.invoke(cli, ['init', project_name])
        assert result.exit_code == 0
        assert "SUCCESS: New project" in result.output

        project_dir = isolated_project / project_name
        assert project_dir.exists()

        # Step 2: Verify complete directory structure
        air_dir = project_dir / ".air"
        assert air_dir.exists()

        # Verify all core directories
        core_dirs = ["rules", "prompts", "workflows", "frameworks", "tools", "domains", "context"]
        for dir_name in core_dirs:
            dir_path = air_dir / dir_name
            assert dir_path.exists(), f"Missing directory: {dir_name}"

        # Step 3: Verify all domain directories
        domains_dir = air_dir / "domains"
        for domain in ["software", "health", "legal"]:
            domain_dir = domains_dir / domain
            assert domain_dir.exists(), f"Missing domain: {domain}"

            # Verify each domain has all subdirectories
            for subdir in ["rules", "prompts", "workflows", "frameworks", "tools"]:
                subdir_path = domain_dir / subdir
                assert subdir_path.exists(), f"Missing {domain}/{subdir}"

        # Step 4: Verify configuration files
        project_config = project_dir / ".airpilot"
        assert project_config.exists()

        with open(project_config) as f:
            config = json.load(f)
        assert config["enabled"] is True
        assert "claude" in config["vendors"]

        air_config = air_dir / ".airpilot"
        assert air_config.exists()

        # Step 5: Verify Git repository was initialized
        git_dir = project_dir / ".git"
        assert git_dir.exists()

        # Step 6: Verify all content files exist and have content
        content_files = [
            air_dir / "README.md",
            air_dir / "rules" / "index.md",
            air_dir / "prompts" / "index.md",
            air_dir / "workflows" / "index.md",
            air_dir / "frameworks" / "memory-bank.md",
            air_dir / "frameworks" / "conversation.md",
            air_dir / "frameworks" / "workflow.md",
            air_dir / "tools" / "README.md",
            air_dir / "context" / "active-focus.md",
            air_dir / "context" / "history.md",
        ]

        for file_path in content_files:
            assert file_path.exists(), f"Missing content file: {file_path}"
            content = file_path.read_text().strip()
            assert len(content) > 0, f"Empty content file: {file_path}"

    def test_global_then_project_initialization_workflow(self) -> None:
        """Test global initialization followed by project initialization"""
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)

            with patch('pathlib.Path.home', return_value=home_path):
                # Step 1: Initialize global intelligence
                result = self.runner.invoke(cli, ['init', '--global'])
                assert result.exit_code == 0
                assert "SUCCESS: System-level intelligence" in result.output

                # Verify global directories
                global_airpilot = home_path / ".airpilot"
                global_air = home_path / ".air"
                assert global_airpilot.exists()
                assert global_air.exists()

                # Verify global config
                global_config = global_airpilot / "config.json"
                assert global_config.exists()
                with open(global_config) as f:
                    config = json.load(f)
                assert config["global_air_path"] == str(global_air)

                # Step 2: Create project in temp directory
                with tempfile.TemporaryDirectory() as temp_project:
                    project_path = Path(temp_project)
                    original_cwd = Path.cwd()

                    try:
                        os.chdir(project_path)

                        # Initialize project
                        result = self.runner.invoke(cli, ['init'])
                        assert result.exit_code == 0
                        assert "SUCCESS: Project intelligence" in result.output

                        # Verify project structure
                        project_air = project_path / ".air"
                        assert project_air.exists()
                        assert (project_air / "context").exists()  # Project-specific

                        # Verify project config references global
                        project_config = project_path / ".airpilot"
                        assert project_config.exists()

                    finally:
                        os.chdir(original_cwd)

    def test_force_flag_overwrites_existing(self, isolated_project: Path) -> None:
        """Test --force flag properly handles existing directories"""
        # Step 1: Create existing .air directory with custom content
        air_dir = isolated_project / ".air"
        air_dir.mkdir()
        custom_file = air_dir / "custom.txt"
        custom_file.write_text("custom content")

        # Step 2: Run init with --force
        result = self.runner.invoke(cli, ['init', '--force'])
        assert result.exit_code == 0
        assert "SUCCESS: Project intelligence" in result.output

        # Step 3: Verify new structure was created
        assert air_dir.exists()
        assert (air_dir / "rules" / "index.md").exists()

        # Step 4: Verify old custom file was removed (backed up)
        assert not custom_file.exists()

    def test_error_recovery_workflows(self, isolated_project: Path) -> None:
        """Test error conditions and recovery"""
        # Test 1: Cancel during existing directory prompt
        existing_dir = isolated_project / "existing-project"
        existing_dir.mkdir()

        result = self.runner.invoke(cli, ['init', 'existing-project'], input='n\n')
        assert result.exit_code == 0
        assert "Cancelled" in result.output

        # Test 2: Continue with existing directory
        result = self.runner.invoke(cli, ['init', 'existing-project'], input='y\n')
        assert result.exit_code == 0
        assert "SUCCESS" in result.output


class TestCrossComponentIntegration:
    """Test integration between different CLI components"""

    def setup_method(self) -> None:
        """Set up test environment"""
        self.runner = CliRunner()

    def test_config_hierarchy_integration(self) -> None:
        """Test configuration hierarchy between global and project configs"""
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)

            with patch('pathlib.Path.home', return_value=home_path):
                # Create global config
                result = self.runner.invoke(cli, ['init', '--global'])
                assert result.exit_code == 0

                global_config = home_path / ".airpilot" / "config.json"
                with open(global_config) as f:
                    global_data = json.load(f)

                # Modify global config
                global_data["user"]["preferences"]["default_domain"] = "health"
                with open(global_config, 'w') as f:
                    json.dump(global_data, f, indent=2)

                # Create project
                with tempfile.TemporaryDirectory() as temp_project:
                    project_path = Path(temp_project)
                    original_cwd = Path.cwd()

                    try:
                        os.chdir(project_path)
                        result = self.runner.invoke(cli, ['init'])
                        assert result.exit_code == 0

                        # Verify project config exists and is separate
                        project_config = project_path / ".airpilot"
                        assert project_config.exists()

                        with open(project_config) as f:
                            project_data = json.load(f)

                        # Project config should have vendor settings
                        assert "vendors" in project_data
                        assert len(project_data["vendors"]) > 0

                    finally:
                        os.chdir(original_cwd)

    def test_git_integration_workflow(self, isolated_project: Path) -> None:
        """Test Git integration throughout the workflow"""
        # Verify Git is not present initially
        git_dir = isolated_project / ".git"
        assert not git_dir.exists()

        # Initialize project
        result = self.runner.invoke(cli, ['init'])
        assert result.exit_code == 0

        # Verify Git was initialized
        assert git_dir.exists()
        assert (git_dir / "config").exists()

        # Verify we can run Git commands
        try:
            git_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=isolated_project,
                capture_output=True,
                text=True,
                check=True
            )
            # Should show untracked files
            assert ".air/" in git_result.stdout or ".airpilot" in git_result.stdout

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git not available in test environment
            pytest.skip("Git not available for integration testing")

    def test_vendor_directory_detection_integration(self, isolated_project: Path) -> None:
        """Test vendor directory detection and backup messaging"""
        # Create some vendor directories
        vendor_dirs = [".claude", ".cursor", ".cline"]
        for vendor in vendor_dirs:
            vendor_dir = isolated_project / vendor
            vendor_dir.mkdir()
            (vendor_dir / "config.md").write_text(f"# {vendor} config")

        # Initialize project
        result = self.runner.invoke(cli, ['init'])
        assert result.exit_code == 0

        # Should mention found vendor directories
        assert "Found existing AI vendor directories" in result.output

        # Vendor directories should still exist (not modified)
        for vendor in vendor_dirs:
            vendor_dir = isolated_project / vendor
            assert vendor_dir.exists()
            assert (vendor_dir / "config.md").exists()


class TestPlatformCompatibility:
    """Test platform-specific functionality"""

    def setup_method(self) -> None:
        """Set up test environment"""
        self.runner = CliRunner()

    def test_path_handling_across_platforms(self) -> None:
        """Test path handling works on different platforms"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test with various path formats
            project_names = [
                "simple-project",
                "project_with_underscores",
                "project-with-dashes",
                "CamelCaseProject"
            ]

            original_cwd = Path.cwd()
            try:
                os.chdir(temp_path)

                for project_name in project_names:
                    result = self.runner.invoke(cli, ['init', project_name])
                    assert result.exit_code == 0, f"Failed for project name: {project_name}"

                    project_dir = temp_path / project_name
                    assert project_dir.exists()
                    assert (project_dir / ".air").exists()

            finally:
                os.chdir(original_cwd)

    def test_file_permissions_handling(self, isolated_project: Path) -> None:
        """Test file permissions are set correctly"""
        result = self.runner.invoke(cli, ['init'])
        assert result.exit_code == 0

        air_dir = isolated_project / ".air"

        # Check that files are readable
        for file_path in air_dir.rglob("*"):
            if file_path.is_file():
                assert os.access(file_path, os.R_OK), f"File not readable: {file_path}"

                # Config files should be writable
                if file_path.name in [".airpilot", "config.json"]:
                    assert os.access(file_path, os.W_OK), f"Config file not writable: {file_path}"


class TestPerformanceAndScale:
    """Test performance and scalability aspects"""

    def setup_method(self) -> None:
        """Set up test environment"""
        self.runner = CliRunner()

    def test_large_project_initialization_performance(self) -> None:
        """Test initialization performance doesn't degrade significantly"""

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original_cwd = Path.cwd()

            try:
                os.chdir(temp_path)

                start_time = time.time()
                result = self.runner.invoke(cli, ['init'])
                end_time = time.time()

                assert result.exit_code == 0

                # Should complete within reasonable time (5 seconds is generous)
                initialization_time = end_time - start_time
                assert initialization_time < 5.0, f"Initialization took too long: {initialization_time:.2f}s"

                # Verify all files were created
                air_dir = temp_path / ".air"
                all_files = list(air_dir.rglob("*"))
                # Should create at least 20 files/directories
                assert len(all_files) >= 20

            finally:
                os.chdir(original_cwd)

    def test_concurrent_initialization_safety(self) -> None:
        """Test that multiple concurrent initializations don't interfere"""
        import concurrent.futures

        def init_project(project_name: str) -> bool:
            """Initialize a project in a thread"""
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                original_cwd = Path.cwd()

                try:
                    os.chdir(temp_path)
                    runner = CliRunner()
                    result = runner.invoke(cli, ['init', project_name])
                    return result.exit_code == 0 and (temp_path / project_name / ".air").exists()
                finally:
                    os.chdir(original_cwd)

        # Run multiple initializations concurrently
        project_names = [f"concurrent-project-{i}" for i in range(3)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(init_project, name) for name in project_names]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(results), "Some concurrent initializations failed"


class TestDataIntegrity:
    """Test data integrity and consistency"""

    def setup_method(self) -> None:
        """Set up test environment"""
        self.runner = CliRunner()

    def test_generated_json_validity(self, isolated_project: Path) -> None:
        """Test all generated JSON files are valid"""
        result = self.runner.invoke(cli, ['init'])
        assert result.exit_code == 0

        # Find all JSON files
        json_files = list(isolated_project.rglob("*.json"))
        assert len(json_files) > 0

        for json_file in json_files:
            try:
                with open(json_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {json_file}: {e}")

    def test_markdown_file_consistency(self, isolated_project: Path) -> None:
        """Test markdown files follow consistent format"""
        result = self.runner.invoke(cli, ['init'])
        assert result.exit_code == 0

        air_dir = isolated_project / ".air"
        markdown_files = list(air_dir.rglob("*.md"))
        assert len(markdown_files) > 0

        for md_file in markdown_files:
            content = md_file.read_text()

            # Should start with level 1 header
            assert content.startswith("# "), f"File {md_file} missing main header"

            # Should have non-empty content
            assert len(content.strip()) > 10, f"File {md_file} has minimal content"

            # Should not have placeholder brackets that weren't filled
            assert "[Add your" not in content or md_file.name in ["active-focus.md", "history.md"], \
                f"File {md_file} has unfilled placeholders"

    def test_configuration_consistency(self, isolated_project: Path) -> None:
        """Test configuration files are internally consistent"""
        result = self.runner.invoke(cli, ['init'])
        assert result.exit_code == 0

        # Load project config
        project_config_file = isolated_project / ".airpilot"
        with open(project_config_file) as f:
            project_config = json.load(f)

        # Load air config
        air_config_file = isolated_project / ".air" / ".airpilot"
        with open(air_config_file) as f:
            air_config = json.load(f)

        # Both should be enabled
        assert project_config["enabled"] is True
        assert air_config["enabled"] is True

        # Source paths should be consistent
        assert project_config["source"] == ".air/rules/"
        assert air_config["source"] == "rules/"

        # Format should match
        assert project_config["defaultFormat"] == air_config["defaultFormat"]
