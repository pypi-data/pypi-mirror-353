#!/usr/bin/env python3
"""
Tests for AirPilot CLI scaffolding functions.

These tests verify that the scaffolding functions create the correct
directory structure and file content for the .air standard.
"""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from airpilot.cli import (
    create_air_config_file,
    create_air_readme,
    create_domains_structure,
    create_global_frameworks,
    create_global_prompts,
    create_global_rules,
    create_global_tools,
    create_global_workflows,
    create_health_domain,
    create_legal_domain,
    create_project_context,
    create_software_domain,
)


class TestScaffoldingFunctions:
    """Test individual scaffolding functions"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_create_air_config_file_project(self, temp_dir: Path) -> None:
        """Test .airpilot config file creation for project"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_air_config_file(air_dir, is_project=True)

        config_file = air_dir / ".airpilot"
        assert config_file.exists()

        with open(config_file) as f:
            config = json.load(f)

        assert config["enabled"] is True
        assert config["source"] == "rules/"
        assert config["sourceIsDirectory"] is True
        assert config["defaultFormat"] == "markdown"
        assert "vendors" in config
        assert "claude" in config["vendors"]
        assert "copilot" in config["vendors"]

    def test_create_air_config_file_global(self, temp_dir: Path) -> None:
        """Test .airpilot config file creation for global"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_air_config_file(air_dir, is_project=False)

        config_file = air_dir / ".airpilot"
        assert config_file.exists()

        with open(config_file) as f:
            config = json.load(f)

        assert config["enabled"] is True
        assert config["vendors"] == {}  # No vendors for global config

    def test_create_air_readme_project(self, temp_dir: Path) -> None:
        """Test README creation for project .air directory"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_air_readme(air_dir, is_project=True)

        readme_file = air_dir / "README.md"
        assert readme_file.exists()

        content = readme_file.read_text()
        assert "# Project Intelligence Control" in content
        assert "Project-level" in content
        assert "context/" in content
        assert "Project session state" in content

    def test_create_air_readme_global(self, temp_dir: Path) -> None:
        """Test README creation for global .air directory"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_air_readme(air_dir, is_project=False)

        readme_file = air_dir / "README.md"
        assert readme_file.exists()

        content = readme_file.read_text()
        assert "# Global Intelligence Control" in content
        assert "Global" in content
        assert "context/" not in content

    def test_create_global_rules(self, temp_dir: Path) -> None:
        """Test global rules directory creation"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_global_rules(air_dir)

        rules_dir = air_dir / "rules"
        assert rules_dir.exists()

        index_file = rules_dir / "index.md"
        assert index_file.exists()

        content = index_file.read_text()
        assert "# Global Rules" in content
        assert "## Purpose" in content
        assert "TypeScript strict mode" in content
        assert "SOLID principles" in content

    def test_create_global_prompts(self, temp_dir: Path) -> None:
        """Test global prompts directory creation"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_global_prompts(air_dir)

        prompts_dir = air_dir / "prompts"
        assert prompts_dir.exists()

        index_file = prompts_dir / "index.md"
        assert index_file.exists()

        content = index_file.read_text()
        assert "# Global Prompts" in content
        assert "Explain this code" in content
        assert "Review this document" in content

    def test_create_global_workflows(self, temp_dir: Path) -> None:
        """Test global workflows directory creation"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_global_workflows(air_dir)

        workflows_dir = air_dir / "workflows"
        assert workflows_dir.exists()

        index_file = workflows_dir / "index.md"
        assert index_file.exists()

        content = index_file.read_text()
        assert "# Global Workflows" in content
        assert "Project kickoff" in content
        assert "Code review" in content

    def test_create_global_frameworks(self, temp_dir: Path) -> None:
        """Test global frameworks directory with all templates"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_global_frameworks(air_dir)

        frameworks_dir = air_dir / "frameworks"
        assert frameworks_dir.exists()

        # Test memory-bank framework
        memory_bank = frameworks_dir / "memory-bank.md"
        assert memory_bank.exists()
        content = memory_bank.read_text()
        assert "# Memory Bank Framework" in content
        assert "Cline-style" in content
        assert "Project Brief" in content
        assert "Active Context" in content

        # Test conversation framework
        conversation = frameworks_dir / "conversation.md"
        assert conversation.exists()
        content = conversation.read_text()
        assert "# Conversation Framework" in content
        assert "Claude-style" in content
        assert "Session History" in content

        # Test workflow framework
        workflow = frameworks_dir / "workflow.md"
        assert workflow.exists()
        content = workflow.read_text()
        assert "# Workflow Framework" in content
        assert "Windsurf-style" in content
        assert "Memories" in content
        assert "Tasks" in content

    def test_create_global_tools(self, temp_dir: Path) -> None:
        """Test global tools directory creation"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_global_tools(air_dir)

        tools_dir = air_dir / "tools"
        assert tools_dir.exists()

        readme_file = tools_dir / "README.md"
        assert readme_file.exists()

        content = readme_file.read_text()
        assert "# Global Tools" in content
        assert "MCP Configurations" in content
        assert "Automation scripts" in content

    def test_create_project_context(self, temp_dir: Path) -> None:
        """Test project context directory creation"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_project_context(air_dir)

        context_dir = air_dir / "context"
        assert context_dir.exists()

        # Test active-focus.md
        active_focus = context_dir / "active-focus.md"
        assert active_focus.exists()
        content = active_focus.read_text()
        assert "# Active Focus" in content
        assert "## Current Sprint" in content
        assert "### Primary Objectives" in content
        assert "## Recent Decisions" in content
        assert "## Next Steps" in content

        # Test history.md
        history = context_dir / "history.md"
        assert history.exists()
        content = history.read_text()
        assert "# Project Timeline and Decisions" in content
        assert "## Project Overview" in content
        assert "## Major Milestones" in content
        assert "## Decision Log" in content


class TestDomainScaffolding:
    """Test domain-specific scaffolding functions"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_create_domains_structure(self, temp_dir: Path) -> None:
        """Test complete domains structure creation"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_domains_structure(air_dir)

        domains_dir = air_dir / "domains"
        assert domains_dir.exists()

        # Verify domains README
        readme_file = domains_dir / "README.md"
        assert readme_file.exists()
        content = readme_file.read_text()
        assert "# Domains" in content
        assert "software/" in content
        assert "health/" in content
        assert "legal/" in content

        # Verify all three domains exist
        assert (domains_dir / "software").exists()
        assert (domains_dir / "health").exists()
        assert (domains_dir / "legal").exists()

    def test_create_software_domain(self, temp_dir: Path) -> None:
        """Test software domain creation"""
        domains_dir = temp_dir / "domains"
        domains_dir.mkdir()

        create_software_domain(domains_dir)

        software_dir = domains_dir / "software"
        assert software_dir.exists()

        # Verify domain README
        readme_file = software_dir / "README.md"
        assert readme_file.exists()
        content = readme_file.read_text()
        assert "# Software Domain" in content
        assert "Development, coding" in content
        assert "Code quality" in content
        assert "Architecture" in content

        # Verify all subdirectories
        subdirs = ["rules", "prompts", "workflows", "frameworks", "tools"]
        for subdir in subdirs:
            subdir_path = software_dir / subdir
            assert subdir_path.exists()

            # Verify content file
            if subdir == "tools":
                content_file = subdir_path / "README.md"
            else:
                content_file = subdir_path / "index.md"

            assert content_file.exists()
            content = content_file.read_text()
            assert "Software Domain" in content

    def test_create_health_domain(self, temp_dir: Path) -> None:
        """Test health domain creation"""
        domains_dir = temp_dir / "domains"
        domains_dir.mkdir()

        create_health_domain(domains_dir)

        health_dir = domains_dir / "health"
        assert health_dir.exists()

        # Verify domain README
        readme_file = health_dir / "README.md"
        assert readme_file.exists()
        content = readme_file.read_text()
        assert "# Health Domain" in content
        assert "Medical research" in content
        assert "wellness" in content
        assert "HIPAA compliance" in content

        # Verify subdirectory structure
        subdirs = ["rules", "prompts", "workflows", "frameworks", "tools"]
        for subdir in subdirs:
            subdir_path = health_dir / subdir
            assert subdir_path.exists()

    def test_create_legal_domain(self, temp_dir: Path) -> None:
        """Test legal domain creation"""
        domains_dir = temp_dir / "domains"
        domains_dir.mkdir()

        create_legal_domain(domains_dir)

        legal_dir = domains_dir / "legal"
        assert legal_dir.exists()

        # Verify domain README
        readme_file = legal_dir / "README.md"
        assert readme_file.exists()
        content = readme_file.read_text()
        assert "# Legal Domain" in content
        assert "Contracts" in content
        assert "compliance" in content
        assert "Contract review" in content
        assert "Risk assessment" in content

        # Verify subdirectory structure
        subdirs = ["rules", "prompts", "workflows", "frameworks", "tools"]
        for subdir in subdirs:
            subdir_path = legal_dir / subdir
            assert subdir_path.exists()


class TestContentQuality:
    """Test quality and consistency of generated content"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_all_markdown_files_have_headers(self, temp_dir: Path) -> None:
        """Test all generated markdown files have proper headers"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        # Create all structures
        create_global_rules(air_dir)
        create_global_prompts(air_dir)
        create_global_workflows(air_dir)
        create_global_frameworks(air_dir)
        create_global_tools(air_dir)
        create_domains_structure(air_dir)
        create_project_context(air_dir)

        # Find all markdown files
        markdown_files = list(air_dir.rglob("*.md"))
        assert len(markdown_files) > 0

        for md_file in markdown_files:
            content = md_file.read_text()
            # Every markdown file should start with a level 1 header
            assert content.startswith("# "), f"File {md_file} missing level 1 header"

    def test_consistent_domain_structure(self, temp_dir: Path) -> None:
        """Test all domains have identical structure"""
        domains_dir = temp_dir / "domains"
        domains_dir.mkdir()

        # Create all domains
        create_software_domain(domains_dir)
        create_health_domain(domains_dir)
        create_legal_domain(domains_dir)

        expected_subdirs = ["rules", "prompts", "workflows", "frameworks", "tools"]
        domains = ["software", "health", "legal"]

        for domain in domains:
            domain_dir = domains_dir / domain

            # Check all expected subdirectories exist
            for subdir in expected_subdirs:
                assert (domain_dir / subdir).exists(), f"Missing {subdir} in {domain}"

                # Check content file exists
                if subdir == "tools":
                    content_file = domain_dir / subdir / "README.md"
                else:
                    content_file = domain_dir / subdir / "index.md"

                assert content_file.exists(), f"Missing content file in {domain}/{subdir}"

    def test_no_empty_files_generated(self, temp_dir: Path) -> None:
        """Test no empty files are generated by scaffolding"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        # Create all structures
        create_global_rules(air_dir)
        create_global_prompts(air_dir)
        create_global_workflows(air_dir)
        create_global_frameworks(air_dir)
        create_global_tools(air_dir)
        create_domains_structure(air_dir)
        create_project_context(air_dir)
        create_air_readme(air_dir, is_project=True)
        create_air_config_file(air_dir, is_project=True)

        # Find all files
        all_files = [f for f in air_dir.rglob("*") if f.is_file()]

        for file_path in all_files:
            if file_path.suffix in [".md", ".json"]:
                content = file_path.read_text().strip()
                assert len(content) > 0, f"Empty file found: {file_path}"

    def test_framework_files_have_required_sections(self, temp_dir: Path) -> None:
        """Test framework files contain required sections"""
        air_dir = temp_dir / ".air"
        air_dir.mkdir()

        create_global_frameworks(air_dir)

        frameworks_dir = air_dir / "frameworks"
        framework_files = ["memory-bank.md", "conversation.md", "workflow.md"]

        required_sections = ["# ", "## Purpose", "## Structure", "## Usage"]

        for framework_file in framework_files:
            file_path = frameworks_dir / framework_file
            content = file_path.read_text()

            for section in required_sections:
                assert section in content, f"Missing section '{section}' in {framework_file}"

    def test_domain_readme_mentions_focus_areas(self, temp_dir: Path) -> None:
        """Test domain READMEs mention relevant focus areas"""
        domains_dir = temp_dir / "domains"
        domains_dir.mkdir()

        create_software_domain(domains_dir)
        create_health_domain(domains_dir)
        create_legal_domain(domains_dir)

        # Test software domain focus areas
        software_readme = domains_dir / "software" / "README.md"
        content = software_readme.read_text()
        assert "Code quality" in content
        assert "Architecture" in content

        # Test health domain focus areas
        health_readme = domains_dir / "health" / "README.md"
        content = health_readme.read_text()
        assert "Medical research" in content
        assert "HIPAA" in content

        # Test legal domain focus areas
        legal_readme = domains_dir / "legal" / "README.md"
        content = legal_readme.read_text()
        assert "Contract" in content
        assert "compliance" in content
