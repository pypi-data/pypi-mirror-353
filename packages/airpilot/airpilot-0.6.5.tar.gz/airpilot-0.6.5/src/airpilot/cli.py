#!/usr/bin/env python3
"""
AirPilot CLI - Universal Intelligence Control

Command-line interface for initializing and managing .air directories
and AirPilot global intelligence control.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

from .license import LicenseManager, require_license

console = Console()

# Read version from package metadata
def _get_version() -> str:
    """Get version from installed package metadata."""
    try:
        from importlib.metadata import version
        return version("airpilot")
    except ImportError:
        # Fallback for Python < 3.8
        try:
            from importlib_metadata import version
            return version("airpilot")
        except ImportError:
            return "0.6.4"  # Fallback version
    except Exception:
        return "0.6.4"  # Fallback version

__version__ = _get_version()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version number')
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """AirPilot - Universal Intelligence Control

    Where .git gives us version control, .air gives us intelligence control.
    """
    if version:
        console.print(Panel(
            f"[bold]AirPilot CLI[/bold]\n"
            f"Version: [green]{__version__}[/green]\n"
            f"Universal Intelligence Control",
            title="Version Information",
            border_style="blue"
        ))
        return

    if ctx.invoked_subcommand is None:
        console.print(Panel(
            Text.from_markup(
                "[bold blue]AirPilot[/bold blue] - Universal Intelligence Control\n\n"
                "Where [cyan].git[/cyan] gives us version control, [cyan].air[/cyan] gives us intelligence control.\n\n"
                "Commands:\n"
                "  [bold]air init[/bold]              Initialize current directory\n"
                "  [bold]air init <project>[/bold]    Create new project with .air\n"
                "  [bold]air init --global[/bold]     Initialize system-level intelligence\n"
                "  [bold]air license[/bold]           Manage AirPilot license\n"
                "  [bold]air license help[/bold]      Complete licensing instructions\n"
                "  [bold]air sync[/bold]              Premium: Real-time vendor sync\n\n"
                "For premium features, run [dim]air license help[/dim] to get started.\n"
                "Run [dim]air <command> --help[/dim] for more information."
            ),
            title="AirPilot",
            border_style="blue"
        ))


@cli.command()
@click.argument('project_name', required=False)
@click.option('--global', 'global_init', is_flag=True,
              help='Initialize system-level intelligence control')
@click.option('--force', is_flag=True,
              help='Overwrite existing .air directory (with backup)')
def init(project_name: Optional[str], global_init: bool, force: bool) -> None:
    """Initialize .air intelligence control

    PROJECT_NAME    Create new project directory with .air (optional)
    """
    try:
        if global_init:
            init_global_intelligence()
        elif project_name:
            init_new_project(project_name, force)
        else:
            init_current_directory(force)
    except KeyboardInterrupt:
        console.print(Panel(
            "[yellow]Operation cancelled by user[/yellow]",
            title="Cancelled",
            border_style="yellow"
        ))
        sys.exit(1)
    except Exception as e:
        console.print(Panel(
            f"[red]Error: {e}[/red]",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)


def init_global_intelligence() -> None:
    """Initialize system-level intelligence control at ~/.airpilot/ and ~/.air/"""
    home = Path.home()
    airpilot_dir = home / ".airpilot"
    air_dir = home / ".air"

    console.print(Panel(
        "[bold]Initializing System-Level Intelligence Control[/bold]\n\n"
        f"Creating:\n"
        f"• {airpilot_dir} (AirPilot configuration)\n"
        f"• {air_dir} (.air standard implementation)",
        title="Global Intelligence",
        border_style="green"
    ))

    # Check for existing directories
    existing = []
    if airpilot_dir.exists():
        existing.append(str(airpilot_dir))
    if air_dir.exists():
        existing.append(str(air_dir))

    if existing:
        console.print(Panel(
            f"[yellow]Found existing directories:[/yellow]\n"
            f"• {chr(10).join(existing)}\n\n"
            f"[bold]Continue and merge with existing?[/bold]",
            title="Existing Directories Found",
            border_style="yellow"
        ))
        if not Confirm.ask("Continue and merge with existing?"):
            console.print(Panel(
                "[yellow]Operation cancelled[/yellow]",
                title="Cancelled",
                border_style="yellow"
            ))
            return

    # Create AirPilot configuration
    create_airpilot_config(airpilot_dir)

    # Create .air standard implementation
    create_air_standard(air_dir)

    console.print(Panel(
        f"[green]SUCCESS: System-level intelligence control initialized![/green]\n\n"
        f"[bold]Next steps:[/bold]\n"
        f"• Configure your preferences in [cyan]{airpilot_dir}/config.json[/cyan]\n"
        f"• Add global rules and prompts to [cyan]{air_dir}/[/cyan]\n"
        f"• Run [cyan]air init[/cyan] in project directories to inherit from global",
        title="Global Intelligence Control Initialized",
        border_style="green"
    ))


def init_current_directory(force: bool) -> None:
    """Initialize .air in current directory"""
    current_dir = Path.cwd()

    console.print(Panel(
        f"[bold]Initializing Intelligence Control[/bold]\n\n"
        f"Directory: {current_dir}",
        title="Project Intelligence",
        border_style="blue"
    ))

    # Check for existing .air directory
    air_dir = current_dir / ".air"
    if air_dir.exists() and not force:
        if detect_air_standard(air_dir):
            console.print(Panel(
                "[yellow]Found existing .air standard directory[/yellow]\n\n"
                "[bold]Merge with existing .air directory?[/bold]",
                title="Existing .air Directory Found",
                border_style="yellow"
            ))
            if not Confirm.ask("Merge with existing .air directory?"):
                console.print(Panel(
                    "[yellow]Operation cancelled[/yellow]",
                    title="Cancelled",
                    border_style="yellow"
                ))
                return
        else:
            backup_path = backup_existing_air(air_dir)
            console.print(Panel(
                f"[yellow]Found non-standard .air directory[/yellow]\n\n"
                f"[bold]Backup location:[/bold]\n"
                f"[blue]{backup_path}[/blue]",
                title="Directory Backed Up",
                border_style="blue"
            ))

    # Initialize or check Git
    init_git_if_needed(current_dir)

    # Backup existing AI vendor directories
    backup_ai_vendors(current_dir)

    # Create .air standard structure
    create_air_standard(air_dir, is_project=True)

    # Create .airpilot project config
    create_airpilot_project_config(current_dir)

    console.print(Panel(
        "[green]SUCCESS: Project intelligence control initialized![/green]\n\n"
        "[bold]Next steps:[/bold]\n"
        "• Add project rules to [cyan].air/rules/[/cyan]\n"
        "• Configure vendors in [cyan].airpilot[/cyan]\n"
        "• Install AirPilot VSCode extension for automatic sync",
        title="Project Intelligence Control Initialized",
        border_style="green"
    ))


def init_new_project(project_name: str, force: bool) -> None:
    """Create new project directory with .air intelligence control"""
    project_dir = Path.cwd() / project_name

    console.print(Panel(
        f"[bold]Creating New Project with Intelligence Control[/bold]\n\n"
        f"Project: {project_name}\n"
        f"Location: {project_dir}",
        title="New Project",
        border_style="green"
    ))

    # Check if directory already exists
    if project_dir.exists() and not force:
        console.print(Panel(
            f"[red]Directory '{project_name}' already exists[/red]\n\n"
            f"[bold]Continue with existing directory?[/bold]",
            title="Directory Exists",
            border_style="red"
        ))
        if not Confirm.ask("Continue with existing directory?"):
            console.print(Panel(
                "[yellow]Operation cancelled[/yellow]",
                title="Cancelled",
                border_style="yellow"
            ))
            return

    # Create project directory
    project_dir.mkdir(exist_ok=True)

    # Change to project directory
    os.chdir(project_dir)

    # Initialize the project
    init_current_directory(force)

    console.print(Panel(
        f"[green]SUCCESS: New project '{project_name}' created successfully![/green]\n\n"
        f"[bold]Project location:[/bold]\n"
        f"[cyan]{project_dir}[/cyan]",
        title="Project Created",
        border_style="green"
    ))


def create_airpilot_config(airpilot_dir: Path) -> None:
    """Create AirPilot configuration directory"""
    airpilot_dir.mkdir(exist_ok=True)

    # config.json
    config = {
        "version": "0.0.1",
        "user": {
            "name": "",
            "email": "",
            "preferences": {
                "default_domain": "software",
                "auto_backup": True,
                "sync_on_change": True
            }
        },
        "global_air_path": str(Path.home() / ".air"),
        "created": "2025-01-06"
    }

    config_file = airpilot_dir / "config.json"
    if not config_file.exists():
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    # README.md
    readme_content = """# AirPilot User Configuration

This directory contains your personal AirPilot configuration and preferences.

## Files

- `config.json` - Your personal AirPilot settings and preferences
- (More configuration files may be added in future versions)

## Configuration

Edit `config.json` to customize:
- User information
- Default domain preferences
- Backup and sync behavior
- Global .air directory location

## Global Intelligence

Your global intelligence patterns are stored in `~/.air/` following the .air standard.
"""

    readme_file = airpilot_dir / "README.md"
    if not readme_file.exists():
        with open(readme_file, 'w') as f:
            f.write(readme_content)


def create_air_standard(air_dir: Path, is_project: bool = False) -> None:
    """Create complete .air standard directory structure with scaffolding"""
    console.print(Panel(
        f"[blue]Creating .air standard structure...[/blue]\n\n"
        f"[bold]Location:[/bold] [cyan]{air_dir}[/cyan]",
        title="Initializing Intelligence Control",
        border_style="blue"
    ))

    air_dir.mkdir(exist_ok=True)

    # Create .airpilot configuration file
    create_air_config_file(air_dir, is_project)

    # Create main README
    create_air_readme(air_dir, is_project)

    # Create top-level directories and files
    create_global_rules(air_dir)
    create_global_prompts(air_dir)
    create_global_workflows(air_dir)
    create_global_frameworks(air_dir)
    create_global_tools(air_dir)

    # Create domains structure
    create_domains_structure(air_dir)

    # Project-specific additions
    if is_project:
        create_project_context(air_dir)


def create_air_config_file(air_dir: Path, is_project: bool) -> None:
    """Create .airpilot configuration file for .air directory"""
    config = {
        "enabled": True,
        "source": "rules/",
        "sourceIsDirectory": True,
        "indexFileName": "index.md",
        "defaultFormat": "markdown",
        "autoSync": True,
        "showStatus": True,
        "vendors": {
            "claude": {"enabled": True, "path": ".claude/", "format": "markdown", "isDirectory": True},
            "copilot": {"enabled": True, "path": ".github/copilot-instructions/", "format": "markdown", "isDirectory": True}
        } if is_project else {}
    }

    airpilot_file = air_dir / ".airpilot"
    if not airpilot_file.exists():
        with open(airpilot_file, 'w') as f:
            json.dump(config, f, indent=2)


def create_air_readme(air_dir: Path, is_project: bool) -> None:
    """Create main README for .air directory"""
    scope = "Project" if is_project else "Global"
    readme_content = f"""# {scope} Intelligence Control

This directory follows the universal .air standard for AI intelligence control.

> *Where .git gives us version control, .air gives us intelligence control.*

## The Five Core AI Management Primitives

### 1. Rules
AI behavior guidelines, coding standards, domain constraints

### 2. Prompts
Specific instructions and templates for AI interactions

### 3. Workflows
Process documentation, memory systems, project context

### 4. Frameworks
Project management patterns and organizational methodologies

### 5. Tools
Scripts, MCP configurations, automation, domain-specific utilities

## Structure

- `rules/` - {'Project-level' if is_project else 'Global'} rules across all domains
- `prompts/` - {'Project-level' if is_project else 'Global'} prompts across all domains
- `workflows/` - {'Project-level' if is_project else 'Global'} workflows across all domains
- `frameworks/` - {'Project-level' if is_project else 'Global'} framework definitions
- `tools/` - {'Project-level' if is_project else 'Global'} tools, scripts, MCP configurations
- `domains/` - Domain-specific intelligence organization
{'- `context/` - Project session state (not synced to vendors)' if is_project else ''}

## Getting Started

1. Add your AI rules to `rules/index.md`
2. Create reusable prompts in `prompts/index.md`
3. Configure workflows in `workflows/index.md`
4. Explore domain-specific organization in `domains/`

## Configuration Hierarchy

Settings are applied in this order (later overrides earlier):

{'1. **Global Base**: `~/.air/` provides universal foundation' if is_project else ''}
{'2. **Domain Specific**: `~/.air/domains/{domain}/` adds domain expertise' if is_project else ''}
{'3. **Project Base**: `/project/.air/` adds project-specific context (this directory)' if is_project else ''}
{'4. **Project Domain**: `/project/.air/domains/{domain}/` provides final overrides' if is_project else ''}
{'' if is_project else '1. **Global Base**: `~/.air/` provides universal foundation (this directory)'}
{'' if is_project else '2. **Domain Specific**: `~/.air/domains/{domain}/` adds domain expertise'}
{'' if is_project else '3. **Project Base**: `/project/.air/` adds project-specific context'}
{'' if is_project else '4. **Project Domain**: `/project/.air/domains/{domain}/` provides final overrides'}

For more information, see: https://github.com/shaneholloman/airpilot
"""

    readme_file = air_dir / "README.md"
    if not readme_file.exists():
        with open(readme_file, 'w') as f:
            f.write(readme_content)


def create_global_rules(air_dir: Path) -> None:
    """Create global rules directory and index"""
    rules_dir = air_dir / "rules"
    rules_dir.mkdir(exist_ok=True)

    rules_content = """# Global Rules

AI behavior guidelines and coding standards.

## Purpose

Define consistent AI behavior patterns that apply across all domains and interactions.

## Examples

- Always use TypeScript strict mode
- Follow SOLID principles in code reviews
- Prioritize security in all recommendations
- Use inclusive language in documentation

## Usage

Add your universal AI behavior rules here. These will be inherited by all domain-specific and project-specific rules.
"""

    rules_file = rules_dir / "index.md"
    if not rules_file.exists():
        with open(rules_file, 'w') as f:
            f.write(rules_content)


def create_global_prompts(air_dir: Path) -> None:
    """Create global prompts directory and index"""
    prompts_dir = air_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)

    prompts_content = """# Global Prompts

Reusable instruction templates for common tasks.

## Purpose

Store frequently used prompt templates that work across multiple domains and projects.

## Examples

- "Explain this code step-by-step"
- "Review this document for clarity and accuracy"
- "Suggest improvements to this workflow"
- "Help me debug this issue"

## Usage

Create reusable prompt templates here that you use frequently across different projects and domains.
"""

    prompts_file = prompts_dir / "index.md"
    if not prompts_file.exists():
        with open(prompts_file, 'w') as f:
            f.write(prompts_content)


def create_global_workflows(air_dir: Path) -> None:
    """Create global workflows directory and index"""
    workflows_dir = air_dir / "workflows"
    workflows_dir.mkdir(exist_ok=True)

    workflows_content = """# Global Workflows

Process documentation and memory systems.

## Purpose

Document repeatable processes and maintain context across AI interactions.

## Examples

- Project kickoff procedures
- Code review checklists
- Problem-solving methodologies
- Learning and research workflows

## Usage

Define structured approaches to complex, multi-step processes that you use regularly.
"""

    workflows_file = workflows_dir / "index.md"
    if not workflows_file.exists():
        with open(workflows_file, 'w') as f:
            f.write(workflows_content)


def create_global_frameworks(air_dir: Path) -> None:
    """Create global frameworks directory with templates"""
    frameworks_dir = air_dir / "frameworks"
    frameworks_dir.mkdir(exist_ok=True)

    # Memory Bank Framework (Cline-style)
    memory_bank_content = """# Memory Bank Framework

Cline-style project context and progress tracking.

## Purpose

Maintain persistent project memory across AI sessions, tracking progress, decisions, and context.

## Structure

### Project Brief
- Project overview and objectives
- Key stakeholders and constraints
- Success criteria and milestones

### Active Context
- Current focus and priorities
- Recent decisions and rationale
- Immediate next steps

### Progress Tracking
- Completed milestones
- Blockers and challenges
- Lessons learned

## Usage

Use this framework to maintain continuity across AI interactions, ensuring context is preserved and progress is tracked systematically.
"""

    memory_bank_file = frameworks_dir / "memory-bank.md"
    if not memory_bank_file.exists():
        with open(memory_bank_file, 'w') as f:
            f.write(memory_bank_content)

    # Conversation Framework (Claude-style)
    conversation_content = """# Conversation Framework

Claude-style session history and knowledge base.

## Purpose

Maintain conversational context and build cumulative knowledge across AI interactions.

## Structure

### Session History
- Previous conversation summaries
- Key insights and discoveries
- Decision points and outcomes

### Knowledge Base
- Domain-specific learnings
- Best practices discovered
- Common patterns and solutions

### Context Threads
- Ongoing discussion topics
- Related concepts and connections
- Future exploration areas

## Usage

Use this framework to build conversational intelligence that improves over time and maintains rich context.
"""

    conversation_file = frameworks_dir / "conversation.md"
    if not conversation_file.exists():
        with open(conversation_file, 'w') as f:
            f.write(conversation_content)

    # Workflow Framework (Windsurf-style)
    workflow_content = """# Workflow Framework

Windsurf-style memories, tasks, and planning.

## Purpose

Organize work into structured workflows with memory, task management, and strategic planning.

## Structure

### Memories
- Important context and decisions
- Patterns and insights
- Historical reference points

### Tasks
- Current work items
- Priorities and dependencies
- Progress and status

### Planning
- Strategic objectives
- Resource allocation
- Timeline and milestones

## Usage

Use this framework for structured project management and strategic thinking with AI assistance.
"""

    workflow_file = frameworks_dir / "workflow.md"
    if not workflow_file.exists():
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)


def create_global_tools(air_dir: Path) -> None:
    """Create global tools directory"""
    tools_dir = air_dir / "tools"
    tools_dir.mkdir(exist_ok=True)

    tools_content = """# Global Tools

Scripts, configurations, and automation utilities.

## Purpose

Store reusable tools, scripts, and configurations that enhance AI workflows across all domains.

## Types

### Scripts
- Automation scripts
- Utility functions
- Workflow helpers

### MCP Configurations
- Model Context Protocol setups
- Integration configurations
- Custom tool definitions

### Utilities
- Data processing tools
- File management scripts
- Development utilities

## Usage

Place executable tools and configurations here that you use across multiple projects and domains.
"""

    tools_file = tools_dir / "README.md"
    if not tools_file.exists():
        with open(tools_file, 'w') as f:
            f.write(tools_content)


def create_domains_structure(air_dir: Path) -> None:
    """Create domains structure with software, health, and legal domains"""
    domains_dir = air_dir / "domains"
    domains_dir.mkdir(exist_ok=True)

    # Domains README
    domains_readme = """# Domains

Domain-specific intelligence organization.

## Purpose

Organize AI intelligence by life and work domains, each containing the complete set of AI management primitives.

## Available Domains

- **software/** - Development, coding, technical work
- **health/** - Medical research, wellness, fitness
- **legal/** - Contracts, compliance, legal research

## Domain Structure

Each domain contains:
- `rules/` - Domain-specific AI behavior guidelines
- `prompts/` - Domain-specific instruction templates
- `workflows/` - Domain-specific process documentation
- `frameworks/` - Domain-specific organizational patterns
- `tools/` - Domain-specific scripts and configurations

## Adding Domains

Create new domain directories following the same structure for any area where you need specialized AI intelligence.
"""

    domains_readme_file = domains_dir / "README.md"
    if not domains_readme_file.exists():
        with open(domains_readme_file, 'w') as f:
            f.write(domains_readme)

    # Create each domain
    create_software_domain(domains_dir)
    create_health_domain(domains_dir)
    create_legal_domain(domains_dir)


def create_software_domain(domains_dir: Path) -> None:
    """Create software domain with complete structure"""
    software_dir = domains_dir / "software"
    software_dir.mkdir(exist_ok=True)

    # Software domain README
    software_readme = """# Software Domain

Development, coding, and technical work intelligence.

## Purpose

Specialized AI intelligence for software development, coding standards, technical documentation, and engineering workflows.

## Focus Areas

- Code quality and best practices
- Architecture and design patterns
- Development workflows and tooling
- Technical documentation
- Code review and debugging

## Structure

- `rules/` - Development AI behavior and coding standards
- `prompts/` - Development instruction templates
- `workflows/` - Development process documentation
- `frameworks/` - Development framework definitions
- `tools/` - Development scripts and configurations
"""

    software_readme_file = software_dir / "README.md"
    if not software_readme_file.exists():
        with open(software_readme_file, 'w') as f:
            f.write(software_readme)

    # Create software domain subdirectories
    create_domain_subdirectory(software_dir, "rules", "Development AI behavior and coding standards.")
    create_domain_subdirectory(software_dir, "prompts", "Development instruction templates.")
    create_domain_subdirectory(software_dir, "workflows", "Development process documentation.")
    create_domain_subdirectory(software_dir, "frameworks", "Development framework definitions.")
    create_domain_subdirectory(software_dir, "tools", "Development scripts and configurations.", is_tools=True)


def create_health_domain(domains_dir: Path) -> None:
    """Create health domain with complete structure"""
    health_dir = domains_dir / "health"
    health_dir.mkdir(exist_ok=True)

    # Health domain README
    health_readme = """# Health Domain

Medical research, wellness, and fitness intelligence.

## Purpose

Specialized AI intelligence for health-related activities, medical research, wellness planning, and fitness optimization.

## Focus Areas

- Medical research and literature review
- Wellness and preventive care
- Fitness and nutrition planning
- Health data analysis
- Privacy and HIPAA compliance

## Structure

- `rules/` - Medical AI behavior and privacy compliance
- `prompts/` - Medical instruction templates
- `workflows/` - Medical process documentation
- `frameworks/` - Medical framework definitions
- `tools/` - Medical scripts and configurations
"""

    health_readme_file = health_dir / "README.md"
    if not health_readme_file.exists():
        with open(health_readme_file, 'w') as f:
            f.write(health_readme)

    # Create health domain subdirectories
    create_domain_subdirectory(health_dir, "rules", "Medical AI behavior and privacy compliance.")
    create_domain_subdirectory(health_dir, "prompts", "Medical instruction templates.")
    create_domain_subdirectory(health_dir, "workflows", "Medical process documentation.")
    create_domain_subdirectory(health_dir, "frameworks", "Medical framework definitions.")
    create_domain_subdirectory(health_dir, "tools", "Medical scripts and configurations.", is_tools=True)


def create_legal_domain(domains_dir: Path) -> None:
    """Create legal domain with complete structure"""
    legal_dir = domains_dir / "legal"
    legal_dir.mkdir(exist_ok=True)

    # Legal domain README
    legal_readme = """# Legal Domain

Contracts, compliance, and legal research intelligence.

## Purpose

Specialized AI intelligence for legal work, contract analysis, compliance requirements, and legal research.

## Focus Areas

- Contract review and analysis
- Regulatory compliance
- Legal research and precedent
- Risk assessment
- Privacy and data protection

## Structure

- `rules/` - Legal AI behavior and compliance
- `prompts/` - Contract analysis and legal templates
- `workflows/` - Legal process documentation
- `frameworks/` - Legal framework definitions
- `tools/` - Legal scripts and configurations
"""

    legal_readme_file = legal_dir / "README.md"
    if not legal_readme_file.exists():
        with open(legal_readme_file, 'w') as f:
            f.write(legal_readme)

    # Create legal domain subdirectories
    create_domain_subdirectory(legal_dir, "rules", "Legal AI behavior and compliance.")
    create_domain_subdirectory(legal_dir, "prompts", "Contract analysis and legal templates.")
    create_domain_subdirectory(legal_dir, "workflows", "Legal process documentation.")
    create_domain_subdirectory(legal_dir, "frameworks", "Legal framework definitions.")
    create_domain_subdirectory(legal_dir, "tools", "Legal scripts and configurations.", is_tools=True)


def create_domain_subdirectory(domain_dir: Path, subdir_name: str, description: str, is_tools: bool = False) -> None:
    """Create a domain subdirectory with appropriate content"""
    subdir = domain_dir / subdir_name
    subdir.mkdir(exist_ok=True)

    # Capitalize first letter for title
    title = subdir_name.capitalize()
    domain_name = domain_dir.name.capitalize()

    content = f"""# {domain_name} Domain {title}

{description}

## Purpose

Domain-specific {subdir_name} for {domain_dir.name} intelligence and AI interactions.

## Usage

Add your {domain_dir.name}-specific {subdir_name} here to customize AI behavior for this domain.
"""

    filename = "README.md" if is_tools else "index.md"
    content_file = subdir / filename
    if not content_file.exists():
        with open(content_file, 'w') as f:
            f.write(content)


def create_project_context(air_dir: Path) -> None:
    """Create project-specific context directory"""
    context_dir = air_dir / "context"
    context_dir.mkdir(exist_ok=True)

    # Active focus file
    active_focus_content = """# Active Focus

Current work focus and priorities.

## Current Sprint

### Primary Objectives
- [Add your current primary objectives here]

### Secondary Goals
- [Add secondary goals here]

### Blockers
- [Add any current blockers here]

## Recent Decisions

### [Date] - Decision Title
- **Context**: Why this decision was needed
- **Decision**: What was decided
- **Impact**: How this affects the project

## Next Steps

### Immediate (This Week)
- [Add immediate next steps]

### Short Term (This Month)
- [Add short-term goals]

### Long Term (This Quarter)
- [Add long-term objectives]
"""

    active_focus_file = context_dir / "active-focus.md"
    if not active_focus_file.exists():
        with open(active_focus_file, 'w') as f:
            f.write(active_focus_content)

    # History file
    history_content = """# Project Timeline and Decisions

Project timeline and major decisions.

## Project Overview

### Started
- **Date**: [Project start date]
- **Objective**: [Main project objective]
- **Success Criteria**: [How success will be measured]

## Major Milestones

### [Date] - Milestone Name
- **Achievement**: What was accomplished
- **Impact**: How this moved the project forward
- **Lessons**: What was learned

## Decision Log

### [Date] - Decision Title
- **Context**: Situation requiring decision
- **Options**: Alternatives considered
- **Decision**: What was chosen and why
- **Outcome**: Results of the decision

## Key Learnings

### Technical
- [Technical insights gained]

### Process
- [Process improvements discovered]

### Team
- [Team collaboration learnings]
"""

    history_file = context_dir / "history.md"
    if not history_file.exists():
        with open(history_file, 'w') as f:
            f.write(history_content)


def create_airpilot_project_config(project_dir: Path) -> None:
    """Create .airpilot project configuration file"""
    config = {
        "enabled": True,
        "source": ".air/rules/",
        "sourceIsDirectory": True,
        "indexFileName": "index.md",
        "defaultFormat": "markdown",
        "autoSync": True,
        "showStatus": True,
        "vendors": {
            "claude": {"enabled": True, "path": ".claude/", "format": "markdown", "isDirectory": True},
            "copilot": {"enabled": True, "path": ".github/copilot-instructions/", "format": "markdown", "isDirectory": True}
        }
    }

    airpilot_file = project_dir / ".airpilot"
    if not airpilot_file.exists():
        with open(airpilot_file, 'w') as f:
            json.dump(config, f, indent=2)


def detect_air_standard(air_dir: Path) -> bool:
    """Detect if existing .air directory follows the standard"""
    # Check for standard structure indicators
    rules_index = air_dir / "rules" / "index.md"
    return rules_index.exists()


def backup_existing_air(air_dir: Path) -> Path:
    """Backup existing non-standard .air directory"""
    import time
    timestamp = int(time.time())
    backup_path = air_dir.parent / f".air.backup.{timestamp}"
    air_dir.rename(backup_path)
    return backup_path


def init_git_if_needed(project_dir: Path) -> None:
    """Initialize Git repository if not already present"""
    git_dir = project_dir / ".git"
    if not git_dir.exists():
        try:
            subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
            console.print(Panel(
                "[green]Git repository initialized successfully[/green]",
                title="Git Initialized",
                border_style="green"
            ))
        except subprocess.CalledProcessError:
            console.print(Panel(
                "[yellow]Could not initialize Git (git not available)[/yellow]",
                title="Git Warning",
                border_style="yellow"
            ))
        except FileNotFoundError:
            console.print(Panel(
                "[yellow]Git not found - skipping Git initialization[/yellow]",
                title="Git Warning",
                border_style="yellow"
            ))


def backup_ai_vendors(project_dir: Path) -> None:
    """Backup existing AI vendor directories"""
    vendor_dirs = [".claude", ".cursor", ".cline", ".clinerules", ".github/copilot-instructions"]
    found_vendors: List[str] = []

    for vendor in vendor_dirs:
        vendor_path = project_dir / vendor
        if vendor_path.exists():
            found_vendors.append(vendor)

    if found_vendors:
        console.print(Panel(
            f"[blue]Found existing AI vendor directories:[/blue]\n"
            f"• {chr(10).join([f'[cyan]{v}[/cyan]' for v in found_vendors])}\n\n"
            f"[bold]Note:[/bold] These will be backed up by AirPilot VSCode extension on first sync",
            title="AI Vendor Directories Detected",
            border_style="blue"
        ))


@cli.group(invoke_without_command=True)
@click.pass_context
def license(ctx: click.Context) -> None:
    """Manage AirPilot license"""
    if ctx.invoked_subcommand is None:
        license_manager = LicenseManager()
        info = license_manager.get_license_info()

        # Format installation date if available
        installed_info = ""
        if info.get("installed_at"):
            import time
            installed_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info["installed_at"]))
            installed_info = f"\n[bold]Installed:[/bold] {installed_date}"

        console.print(Panel(
            f"[bold]Plan:[/bold] {info['plan'].upper()}\n"
            f"[bold]Licensed:[/bold] {'Yes' if info['licensed'] else 'No'}\n"
            f"[bold]Features:[/bold] {', '.join(info['features'])}{installed_info}",
            title="AirPilot License Status",
            border_style="blue"
        ))

        if not info["licensed"]:
            console.print(Panel(
                "[bold]Premium Features Available:[/bold]\n"
                "• [blue]air sync[/blue] - Real-time vendor synchronization\n"
                "• [blue]air cloud[/blue] - Cloud backup and sync (coming soon)\n\n"
                "[bold]To get a license:[/bold]\n"
                "1. Email: shaneholloman@gmail.com\n"
                "2. Subject: AirPilot License Request\n"
                "3. Include your name and use case\n\n"
                "[bold]Once you have your key:[/bold]\n"
                "air license install <your-license-key>",
                title="Premium Features",
                border_style="cyan"
            ))


@license.command()
@click.argument('key')
def install(key: str) -> None:
    """Install a license key"""
    license_manager = LicenseManager()

    if license_manager.install_license(key):
        info = license_manager.get_license_info()
        console.print(Panel(
            f"[green]SUCCESS: License installed![/green]\n\n"
            f"[bold]Plan:[/bold] {info['plan'].upper()}\n"
            f"[bold]Features:[/bold] {', '.join(info['features'])}\n\n"
            f"You can now use premium features like [green]air sync[/green]",
            title="License Installation Complete",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[red]Invalid license key[/red]\n\n"
            "[bold]To get a license:[/bold]\n"
            "• Email: [blue]shaneholloman@gmail.com[/blue]\n"
            "• Subject: [green]AirPilot License Request[/green]\n"
            "• Include your name and use case\n\n"
            "[bold]Example format:[/bold]\n"
            "[yellow]airpilot-poc-XXXXXXXX-XXXXXXXX[/yellow]",
            title="License Installation Failed",
            border_style="red"
        ))


@license.command()
def remove() -> None:
    """Remove stored license and revert to free plan"""
    license_manager = LicenseManager()

    if Confirm.ask("Remove license and revert to free plan?"):
        if license_manager.remove_license():
            console.print(Panel(
                "[green]License removed successfully[/green]\n\n"
                "[bold]Status:[/bold] Reverted to free plan\n"
                "[bold]Available features:[/bold] init, init_global, init_project\n\n"
                "To reinstall a license, use: [green]air license install <key>[/green]",
                title="License Removed",
                border_style="yellow"
            ))
        else:
            console.print(Panel(
                "[red]Failed to remove license[/red]\n\n"
                "This may be due to file permissions or the license file being in use.\n\n"
                "For help, contact: [blue]shaneholloman@gmail.com[/blue]",
                title="License Removal Failed",
                border_style="red"
            ))


@license.command()
def status() -> None:
    """Show detailed license status"""
    license_manager = LicenseManager()
    info = license_manager.get_license_info()

    console.print(Panel(
        f"[bold]Plan:[/bold] {info['plan'].upper()}\n"
        f"[bold]Licensed:[/bold] {'Yes' if info['licensed'] else 'No'}\n"
        f"[bold]Features:[/bold] {', '.join(info['features'])}\n\n"
        f"[bold]Free Features:[/bold]\n"
        f"• air init - Initialize .air in current directory\n"
        f"• air init --global - Initialize system-level intelligence\n"
        f"• air init <project> - Create new project with .air\n\n"
        f"[bold]Premium Features:[/bold]\n"
        f"• air sync - Real-time vendor synchronization\n"
        f"• air cloud - Cloud backup and sync (coming soon)",
        title="AirPilot License Status",
        border_style="blue"
    ))


@license.command()
def help() -> None:
    """Show complete licensing instructions"""
    console.print(Panel(
        "[bold cyan]AirPilot Licensing Guide[/bold cyan]\n\n"

        "[bold]Step 1: Request a License[/bold]\n"
        "Email: [blue]shaneholloman@gmail.com[/blue]\n"
        "Subject: [green]AirPilot License Request[/green]\n\n"

        "Include in your email:\n"
        "• Your name and organization\n"
        "• Brief description of your use case\n"
        "• Mention this is for PoC testing\n\n"

        "[bold]Step 2: Install Your License[/bold]\n"
        "Once Shane sends you a license key:\n"
        "[green]air license install <your-license-key>[/green]\n\n"

        "[bold]Step 3: Verify Installation[/bold]\n"
        "[green]air license[/green]\n"
        "Should show Plan: POC, Licensed: Yes\n\n"

        "[bold]Step 4: Use Premium Features[/bold]\n"
        "[green]air sync[/green] - Real-time vendor synchronization\n\n"

        "[bold]Troubleshooting[/bold]\n"
        "• [green]air license status[/green] - Detailed license info\n"
        "• [green]air license remove[/green] - Remove current license\n"
        "• Contact: [blue]shaneholloman@gmail.com[/blue] for support\n\n"

        "[bold]Example License Key Format:[/bold]\n"
        "[yellow]airpilot-poc-XXXXXXXX-XXXXXXXX[/yellow]",
        title="Complete Licensing Instructions",
        border_style="cyan"
    ))


@cli.command()
@require_license("sync") 
def sync() -> None:
    """Premium: Real-time vendor synchronization

    Synchronizes .air directory with all configured AI vendor formats.
    Requires valid AirPilot license.
    """
    console.print(Panel(
        "[yellow]Starting real-time vendor synchronization...[/yellow]\n\n"
        "[green]SUCCESS: Sync feature activated![/green]\n\n"
        "[blue]This is a demo - full sync implementation coming soon[/blue]",
        title="Premium Sync Feature",
        border_style="green"
    ))


def main() -> None:
    """Main entry point for the CLI"""
    # Support both 'airpilot' and 'air' commands
    if len(sys.argv) > 0:
        if sys.argv[0].endswith('air'):
            # Called as 'air' command
            cli()
        else:
            # Called as 'airpilot' command
            cli()
    else:
        cli()


if __name__ == "__main__":
    main()
