"""
Git operations for AirPilot CLI.
"""
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


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
