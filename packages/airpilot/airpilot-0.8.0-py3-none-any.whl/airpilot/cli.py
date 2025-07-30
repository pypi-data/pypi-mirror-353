#!/usr/bin/env python3
"""
AirPilot CLI - Universal Intelligence Control

Command-line interface for initializing and managing .air directories
and AirPilot global intelligence control.
"""

import sys
from typing import Optional

import click

from .commands.init import init
from .commands.license import license
from .commands.sync import sync
from .ui.panels import show_error_panel, show_main_help_panel, show_version_panel
from .utils.version import get_version

__version__ = get_version()


class AirPilotGroup(click.Group):
    """Custom Click Group that handles unknown commands with Panel UI"""

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """Override to handle unknown commands with Panel UI"""
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv

        # Command not found - show beautiful error panel
        show_error_panel(
            f"Unknown command '[yellow]{cmd_name}[/yellow]'\n\n"
            f"[bold]Available commands:[/bold]\n"
            f"• [cyan]air init[/cyan] - Initialize intelligence control\n"
            f"• [cyan]air license[/cyan] - Manage AirPilot license\n"
            f"• [cyan]air sync[/cyan] - Premium: Real-time vendor sync\n\n"
            f"Run [dim]air --help[/dim] for more information.",
            title="Command Not Found"
        )
        sys.exit(1)


@click.group(cls=AirPilotGroup, invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version number')
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """AirPilot - Universal Intelligence Control

    Where .git gives us version control, .air gives us intelligence control.
    """
    if version:
        show_version_panel()
        return

    if ctx.invoked_subcommand is None:
        show_main_help_panel()


# Register commands
cli.add_command(init)
cli.add_command(license)
cli.add_command(sync)


def main() -> None:
    """Main entry point for the CLI"""
    # Support both 'airpilot' and 'air' commands
    if len(sys.argv) > 0:
        if sys.argv[0].endswith('air'):
            # Called as 'air' - all good
            pass
        elif sys.argv[0].endswith('airpilot'):
            # Called as 'airpilot' - also good
            pass

    cli()


if __name__ == '__main__':
    main()
