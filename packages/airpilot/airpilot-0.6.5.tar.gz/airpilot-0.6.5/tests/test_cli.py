#!/usr/bin/env python3
"""
Unit tests for AirPilot CLI functionality.

Tests the core CLI commands and functions without mocking filesystem operations
to ensure real-world functionality.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from airpilot.cli import (
    backup_ai_vendors,
    backup_existing_air,
    cli,
    create_air_standard,
    create_airpilot_config,
    create_airpilot_project_config,
    detect_air_standard,
    init_git_if_needed,
)


class TestCLICommands:
    """Test CLI command functionality"""

    def setup_method(self) -> None:
        """Set up test environment for each test"""
        self.runner = CliRunner()

    def teardown_method(self) -> None:
        """Clean up after each test"""
        # Ensure we're back in original directory
        pass

    @pytest.fixture
    def temp_project_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for testing project operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original_cwd = Path.cwd()
            os.chdir(temp_path)
            # Store reference for cleanup if needed
            yield temp_path
            os.chdir(original_cwd)

    def test_cli_version(self) -> None:
        """Test --version flag returns version string"""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "AirPilot CLI v" in result.output
        assert "0.0.1" in result.output

    def test_cli_help(self) -> None:
        """Test default help output when no command given"""
        result = self.runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "AirPilot" in result.output
        assert "Universal Intelligence Control" in result.output
        assert "air init" in result.output

    def test_init_help(self) -> None:
        """Test init command help"""
        result = self.runner.invoke(cli, ['init', '--help'])
        assert result.exit_code == 0
        assert "Initialize .air intelligence control" in result.output
        assert "--global" in result.output
        assert "--force" in result.output

    def test_init_current_directory_basic(self, temp_project_dir: Path) -> None:
        """Test air init in current directory creates expected structure"""
        result = self.runner.invoke(cli, ['init'], input='y\n')

        assert result.exit_code == 0
        assert "SUCCESS: Project intelligence control initialized successfully!" in result.output

        # Verify .air directory structure
        air_dir = temp_project_dir / ".air"
        assert air_dir.exists()
        assert air_dir.is_dir()

        # Verify core directories
        assert (air_dir / "rules").exists()
        assert (air_dir / "prompts").exists()
        assert (air_dir / "workflows").exists()
        assert (air_dir / "frameworks").exists()
        assert (air_dir / "tools").exists()
        assert (air_dir / "domains").exists()
        assert (air_dir / "context").exists()

        # Verify configuration files
        assert (temp_project_dir / ".airpilot").exists()
        assert (air_dir / ".airpilot").exists()
        assert (air_dir / "README.md").exists()

    def test_init_new_project(self, temp_project_dir: Path) -> None:
        """Test air init <project> creates new project directory"""
        project_name = "test-new-project"
        result = self.runner.invoke(cli, ['init', project_name])

        assert result.exit_code == 0
        assert f"SUCCESS: New project '{project_name}' created successfully!" in result.output

        project_dir = temp_project_dir / project_name
        assert project_dir.exists()
        assert project_dir.is_dir()

        # Verify .air structure in new project
        air_dir = project_dir / ".air"
        assert air_dir.exists()
        assert (air_dir / "rules" / "index.md").exists()
        assert (air_dir / "context" / "active-focus.md").exists()
        assert (project_dir / ".airpilot").exists()

    def test_init_global_creates_home_directories(self) -> None:
        """Test air init --global creates directories in home folder"""
        with tempfile.TemporaryDirectory() as temp_home:
            home_path = Path(temp_home)

            with patch('pathlib.Path.home', return_value=home_path):
                result = self.runner.invoke(cli, ['init', '--global'])

                assert result.exit_code == 0
                assert "SUCCESS: System-level intelligence control initialized successfully!" in result.output

                # Verify global directories created
                airpilot_dir = home_path / ".airpilot"
                air_dir = home_path / ".air"

                assert airpilot_dir.exists()
                assert air_dir.exists()
                assert (airpilot_dir / "config.json").exists()
                assert (air_dir / "README.md").exists()

    def test_init_force_flag(self, temp_project_dir: Path) -> None:
        """Test --force flag overwrites existing .air directory"""
        # Create existing .air directory
        existing_air = temp_project_dir / ".air"
        existing_air.mkdir()
        (existing_air / "old_file.txt").write_text("old content")

        result = self.runner.invoke(cli, ['init', '--force'])

        assert result.exit_code == 0
        assert "SUCCESS: Project intelligence control initialized successfully!" in result.output

        # Verify new structure was created
        assert existing_air.exists()
        assert (existing_air / "rules" / "index.md").exists()
        # Old file should be gone (backed up)
        assert not (existing_air / "old_file.txt").exists()


class TestUtilityFunctions:
    """Test utility functions used by CLI commands"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_create_airpilot_config(self, temp_dir: Path) -> None:
        """Test AirPilot configuration creation"""
        airpilot_dir = temp_dir / ".airpilot"
        create_airpilot_config(airpilot_dir)

        assert airpilot_dir.exists()
        config_file = airpilot_dir / "config.json"
        readme_file = airpilot_dir / "README.md"

        assert config_file.exists()
        assert readme_file.exists()

        # Verify config content
        with open(config_file) as f:
            config = json.load(f)

        assert config["version"] == "0.0.1"
        assert "user" in config
        assert "preferences" in config["user"]
        assert config["user"]["preferences"]["default_domain"] == "software"

    def test_create_air_standard_project(self, temp_dir: Path) -> None:
        """Test .air standard creation for project"""
        air_dir = temp_dir / ".air"
        create_air_standard(air_dir, is_project=True)

        assert air_dir.exists()

        # Verify core directories
        core_dirs = ["rules", "prompts", "workflows", "frameworks", "tools", "domains"]
        for dir_name in core_dirs:
            assert (air_dir / dir_name).exists()

        # Verify project-specific context directory
        assert (air_dir / "context").exists()
        assert (air_dir / "context" / "active-focus.md").exists()
        assert (air_dir / "context" / "history.md").exists()

        # Verify domain structure
        domains_dir = air_dir / "domains"
        assert (domains_dir / "software").exists()
        assert (domains_dir / "health").exists()
        assert (domains_dir / "legal").exists()

        # Verify each domain has all subdirectories
        for domain in ["software", "health", "legal"]:
            domain_dir = domains_dir / domain
            for subdir in ["rules", "prompts", "workflows", "frameworks", "tools"]:
                assert (domain_dir / subdir).exists()

    def test_create_air_standard_global(self, temp_dir: Path) -> None:
        """Test .air standard creation for global installation"""
        air_dir = temp_dir / ".air"
        create_air_standard(air_dir, is_project=False)

        assert air_dir.exists()

        # Verify core directories exist
        core_dirs = ["rules", "prompts", "workflows", "frameworks", "tools", "domains"]
        for dir_name in core_dirs:
            assert (air_dir / dir_name).exists()

        # Verify context directory NOT created for global
        assert not (air_dir / "context").exists()

        # Verify README indicates global scope
        readme_content = (air_dir / "README.md").read_text()
        assert "Global Intelligence Control" in readme_content
        assert "Global Base" in readme_content

    def test_create_airpilot_project_config(self, temp_dir: Path) -> None:
        """Test project .airpilot configuration creation"""
        create_airpilot_project_config(temp_dir)

        config_file = temp_dir / ".airpilot"
        assert config_file.exists()

        with open(config_file) as f:
            config = json.load(f)

        assert config["enabled"] is True
        assert config["source"] == ".air/rules/"
        assert "vendors" in config
        assert "claude" in config["vendors"]
        assert "copilot" in config["vendors"]

    def test_detect_air_standard_positive(self, temp_dir: Path) -> None:
        """Test detection of standard .air directory"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()
        rules_dir = air_dir / "rules"
        rules_dir.mkdir()
        (rules_dir / "index.md").write_text("# Rules")

        assert detect_air_standard(air_dir) is True

    def test_detect_air_standard_negative(self, temp_dir: Path) -> None:
        """Test detection fails for non-standard .air directory"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()
        (air_dir / "random_file.txt").write_text("not standard")

        assert detect_air_standard(air_dir) is False

    def test_backup_existing_air(self, temp_dir: Path) -> None:
        """Test backup of existing .air directory"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()
        test_file = air_dir / "test.txt"
        test_content = "test content"
        test_file.write_text(test_content)

        backup_path = backup_existing_air(air_dir)

        # Original directory should be moved
        assert not air_dir.exists()
        assert backup_path.exists()
        assert backup_path.name.startswith(".air.backup.")

        # Content should be preserved
        backed_up_file = backup_path / "test.txt"
        assert backed_up_file.exists()
        assert backed_up_file.read_text() == test_content

    def test_backup_ai_vendors(self, temp_dir: Path) -> None:
        """Test detection and messaging for existing AI vendor directories"""
        # Create some vendor directories
        vendor_dirs = [".claude", ".cursor", ".cline"]
        for vendor in vendor_dirs:
            (temp_dir / vendor).mkdir()
            (temp_dir / vendor / "test.md").write_text("vendor config")

        # This function should run without error and detect the vendors
        # (It only prints messages, doesn't modify files)
        backup_ai_vendors(temp_dir)

        # Verify directories still exist (function only detects, doesn't backup)
        for vendor in vendor_dirs:
            assert (temp_dir / vendor).exists()

    def test_init_git_if_needed_new_repo(self, temp_dir: Path) -> None:
        """Test Git repository initialization in directory without Git"""
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_dir)
            init_git_if_needed(temp_dir)

            # Check if .git directory was created
            git_dir = temp_dir / ".git"
            assert git_dir.exists()
        finally:
            os.chdir(original_cwd)

    def test_init_git_if_needed_existing_repo(self, temp_dir: Path) -> None:
        """Test Git initialization skips existing repositories"""
        # Create existing .git directory
        git_dir = temp_dir / ".git"
        git_dir.mkdir()

        original_cwd = Path.cwd()
        try:
            os.chdir(temp_dir)
            init_git_if_needed(temp_dir)

            # .git should still exist and not be modified
            assert git_dir.exists()
        finally:
            os.chdir(original_cwd)


class TestContentGeneration:
    """Test generated content quality and correctness"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_rules_content_structure(self, temp_dir: Path) -> None:
        """Test generated rules content has proper structure"""
        air_dir = temp_dir / ".air"
        create_air_standard(air_dir, is_project=True)

        rules_file = air_dir / "rules" / "index.md"
        content = rules_file.read_text()

        assert "# Global Rules" in content
        assert "## Purpose" in content
        assert "## Examples" in content
        assert "## Usage" in content
        assert "TypeScript strict mode" in content

    def test_domain_structure_completeness(self, temp_dir: Path) -> None:
        """Test all domains have complete subdirectory structure"""
        air_dir = temp_dir / ".air"
        create_air_standard(air_dir, is_project=False)

        domains = ["software", "health", "legal"]
        subdirs = ["rules", "prompts", "workflows", "frameworks", "tools"]

        for domain in domains:
            domain_dir = air_dir / "domains" / domain
            assert domain_dir.exists()

            # Verify domain README
            domain_readme = domain_dir / "README.md"
            assert domain_readme.exists()
            content = domain_readme.read_text()
            assert f"# {domain.capitalize()} Domain" in content

            # Verify all subdirectories exist with content
            for subdir in subdirs:
                subdir_path = domain_dir / subdir
                assert subdir_path.exists()

                # Verify index/README file exists
                if subdir == "tools":
                    content_file = subdir_path / "README.md"
                else:
                    content_file = subdir_path / "index.md"

                assert content_file.exists()
                file_content = content_file.read_text()
                assert f"{domain.capitalize()} Domain" in file_content

    def test_framework_templates_exist(self, temp_dir: Path) -> None:
        """Test all framework templates are created with proper content"""
        air_dir = temp_dir / ".air"
        create_air_standard(air_dir, is_project=False)

        frameworks_dir = air_dir / "frameworks"
        expected_frameworks = ["memory-bank.md", "conversation.md", "workflow.md"]

        for framework in expected_frameworks:
            framework_file = frameworks_dir / framework
            assert framework_file.exists()

            content = framework_file.read_text()
            assert "# " in content  # Has heading
            assert "## Purpose" in content
            assert "## Structure" in content
            assert "## Usage" in content

    def test_project_context_files(self, temp_dir: Path) -> None:
        """Test project context files are created with proper templates"""
        air_dir = temp_dir / ".air"
        create_air_standard(air_dir, is_project=True)

        context_dir = air_dir / "context"

        # Test active-focus.md
        active_focus = context_dir / "active-focus.md"
        assert active_focus.exists()
        content = active_focus.read_text()
        assert "# Active Focus" in content
        assert "## Current Sprint" in content
        assert "### Primary Objectives" in content
        assert "## Recent Decisions" in content

        # Test history.md
        history = context_dir / "history.md"
        assert history.exists()
        content = history.read_text()
        assert "# Project Timeline and Decisions" in content
        assert "## Major Milestones" in content
        assert "## Decision Log" in content


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_keyboard_interrupt_handling(self) -> None:
        """Test CLI handles keyboard interrupt gracefully"""
        runner = CliRunner()

        # Simulate keyboard interrupt during user input
        result = runner.invoke(cli, ['init'], input='\x03')  # Ctrl+C

        # Should exit with code 1 and show cancellation message
        assert result.exit_code == 1

    def test_init_existing_project_directory(self) -> None:
        """Test init handles existing project directories"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = "existing-project"
            existing_project = temp_path / project_name
            existing_project.mkdir()

            original_cwd = Path.cwd()
            try:
                os.chdir(temp_path)

                # Test with existing directory, decline to continue
                result = runner.invoke(cli, ['init', project_name], input='n\n')
                assert result.exit_code == 0
                assert "Cancelled" in result.output

                # Test with existing directory, accept to continue
                result = runner.invoke(cli, ['init', project_name], input='y\n')
                assert result.exit_code == 0

            finally:
                os.chdir(original_cwd)

    def test_configuration_file_persistence(self) -> None:
        """Test configuration files are not overwritten if they exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            airpilot_dir = temp_path / ".airpilot"

            # Create existing config with custom content
            airpilot_dir.mkdir()
            config_file = airpilot_dir / "config.json"
            custom_config = {"custom": "value", "preserved": True}
            with open(config_file, 'w') as f:
                json.dump(custom_config, f)

            # Run create_airpilot_config again
            create_airpilot_config(airpilot_dir)

            # Verify custom config is preserved
            with open(config_file) as f:
                loaded_config = json.load(f)

            assert loaded_config["custom"] == "value"
            assert loaded_config["preserved"] is True
