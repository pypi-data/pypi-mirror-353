# AirPilot CLI [![License: Elastic-2.0](https://img.shields.io/badge/License-Elastic-blue.svg)](https://github.com/shaneholloman/airpilot/blob/main/LICENSE.md) [![PyPI version](https://badge.fury.io/py/airpilot.svg)](https://badge.fury.io/py/airpilot)

![AirPilot Logo](https://raw.githubusercontent.com/shaneholloman/assets/main/airpilot/airpilot-office.png)

**AirPilot manages Universal Intelligence Control through the Air Standard, just as Git manages version control through its protocols.**

## Understanding the Framework

### 1. Universal Intelligence Control (UIC)

- The overarching domain/field of managing AI intelligence
- The "what" - the entire category of intelligence management
- Comparable to "version control" as a concept

### 2. Air Standard

- The technical specification - the `.air/` folder structure
- The "how" - the actual implementation format
- Comparable to Git's technical protocols

### 3. AirPilot

- The product/tool that manages the Air Standard
- The "who" - the agent that manages everything
- Comparable to Git the software

## The Ultimate Goal: Universal AI Standard

**Every repository uses `.git/` - Every AI project should use `.air/`**

Where `.git` gives us **version control**, `.air` gives us **intelligence control**.

AirPilot CLI introduces `.air` as the universal standard for AI assistant configuration, replacing vendor-specific chaos (`.claude/`, `.clinerules/`, `.cursor/rules/`) with one universal format that works across all platforms.

## Installation

### System-wide Installation

```bash
uv tool install airpilot
```

### Add to Project

```bash
uv add airpilot
```

## Quick Start

### Initialize Global Intelligence Control

Set up system-level AI intelligence patterns in your home directory:

```bash
air init --global
```

This creates:

- `~/.airpilot/` - Your personal AirPilot configuration
- `~/.air/` - Global AI intelligence patterns and rules

### Initialize Project Intelligence Control

Add AI intelligence control to your current project:

```bash
air init
```

This creates a complete `.air` directory structure with the universal standard.

### Create New Project with Intelligence Control

Start a new project with built-in AI intelligence:

```bash
air init my-new-project
```

This creates a new directory with Git repository and complete `.air` standard implementation.

## Commands

### Free Commands

- `air init` - Initialize .air in current directory
- `air init --global` - Initialize system-level intelligence control
- `air init <project>` - Create new project with .air standard
- `air --version` - Show version information
- `air --help` - Show help information

### Premium Commands (License Required)

- `air sync` - Real-time vendor synchronization
- `air license` - Manage your AirPilot license

### Coming Soon (Premium Features)

- `air teams` - Multi-user collaboration
- `air analytics` - Usage insights and patterns
- `air backup` - Cloud backup and restore
- `air enterprise` - SSO, audit logs, compliance

## Getting a License

To access premium features, you need a license key from Shane Holloman.

### Request Your License

**Email**: shaneholloman@gmail.com  
**Subject**: AirPilot License Request

Include:
- Your name and organization
- Brief description of your use case

### Install Your License

Once you receive your license key:

```bash
air license install YOUR-LICENSE-KEY-HERE
```

### Verify Installation

```bash
air license
```

For complete licensing instructions, see: [License Instructions](../docs/license-instructions.md)

## The .air Standard

AirPilot CLI implements the complete .air standard with six core AI management primitives:

### 1. Domains

Universal life domains that organize all AI intelligence (software, health, legal, cooking, etc.)

### 2. Rules

AI behavior guidelines, coding standards, domain constraints

### 3. Prompts

Specific instructions and templates for AI interactions

### 4. Workflows

Process documentation, memory systems, project context

### 5. Frameworks

Project management patterns and organizational methodologies

### 6. Tools

Scripts, MCP configurations, automation, domain-specific utilities

## Universal Domain Support

The .air standard includes comprehensive domain support to demonstrate universal applicability:

### Software Domain

- Development and coding standards
- Architecture and design patterns
- Code review and debugging workflows

### Health Domain

- Medical research and literature review
- Wellness and preventive care planning
- HIPAA compliance and privacy standards

### Legal Domain

- Contract review and analysis
- Regulatory compliance requirements
- Legal research and precedent tracking

## Two-Tier Intelligence Architecture

AirPilot CLI implements a sophisticated two-tier intelligence system:

### Global Intelligence (`~/.air/`)

- Universal patterns and rules that apply across all projects
- Domain-specific templates and frameworks
- Personal AI assistant preferences and workflows

### Project Intelligence (`./air/`)

- Project-specific context and requirements
- Local overrides and customizations
- Team collaboration and shared standards

### Configuration Hierarchy

Settings are applied in this order (later overrides earlier):

1. **Global Base**: `~/.air/` provides universal foundation
2. **Domain Specific**: `~/.air/domains/{domain}/` adds domain expertise
3. **Project Base**: `/project/.air/` adds project-specific context
4. **Project Domain**: `/project/.air/domains/{domain}/` provides final overrides

## VSCode Extension Integration

For a complete AI intelligence control experience, use AirPilot CLI alongside the [AirPilot VSCode Extension](https://github.com/shaneholloman/airpilot):

- **CLI**: Project scaffolding, global configuration, automation
- **VSCode Extension**: Real-time synchronization, visual management, vendor integration

The VSCode extension automatically detects `.air` directories created by the CLI and provides:

- Real-time file watching and synchronization
- Multi-vendor support (Claude, Cursor, Cline, GitHub Copilot, etc.)
- Visual rule management and editing
- Backup and migration tools

## Example: Getting Started

```bash
# 1. Set up global intelligence patterns
air init --global

# 2. Navigate to your project
cd my-project

# 3. Initialize project intelligence control
air init

# 4. Your project now has:
#    - .air/ directory with complete standard
#    - .airpilot configuration file
#    - Git repository (if not already present)
```

## Requirements

- Python 3.8+
- Git (optional, for automatic repository initialization)

## More Information

- **Main Project**: [AirPilot GitHub Repository](https://github.com/shaneholloman/airpilot)
- **VSCode Extension**: Available on the [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=shaneholloman.airpilot)
- **Documentation**: [Complete documentation and guides](https://github.com/shaneholloman/airpilot/tree/main/docs)
- **Issues**: [Report bugs and request features](https://github.com/shaneholloman/airpilot/issues)

---

**Universal Intelligence Control (UIC)** - *You I See*

AirPilot manages Universal Intelligence Control through the Air Standard, just as Git manages version control through its protocols.

## License

This project is licensed under the Elastic License 2.0 - see the [LICENSE](https://github.com/shaneholloman/airpilot/blob/main/LICENSE.md) file for details.
