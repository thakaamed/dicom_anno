# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""THAKAAMED branded console with Rich theming."""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

# THAKAAMED brand color constants
BRAND_PRIMARY = "#1b4d3e"  # Saudi green
BRAND_GOLD = "#ffd700"  # Gold accent
BRAND_LIGHT = "#e8f5e9"  # Light green

# THAKAAMED theme for console
THAKAAMED_THEME = Theme(
    {
        "brand.primary": BRAND_PRIMARY,
        "brand.gold": BRAND_GOLD,
        "brand.light": BRAND_LIGHT,
        "success": "bold green",
        "error": "bold red",
        "warning": "bold yellow",
        "info": "dim cyan",
        "header": f"bold white on {BRAND_PRIMARY}",
    }
)

# Module-level shared console instance
console = Console(theme=THAKAAMED_THEME)

# ASCII banner - CRITICAL: "THAKAA MED" with space between words
BANNER = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║  ████████╗██╗  ██╗ █████╗ ██╗  ██╗ █████╗  █████╗    ███╗   ███╗███████╗██████╗ ║
║  ╚══██╔══╝██║  ██║██╔══██╗██║ ██╔╝██╔══██╗██╔══██╗   ████╗ ████║██╔════╝██╔══██╗║
║     ██║   ███████║███████║█████╔╝ ███████║███████║   ██╔████╔██║█████╗  ██║  ██║║
║     ██║   ██╔══██║██╔══██║██╔═██╗ ██╔══██║██╔══██║   ██║╚██╔╝██║██╔══╝  ██║  ██║║
║     ██║   ██║  ██║██║  ██║██║  ██╗██║  ██║██║  ██║   ██║ ╚═╝ ██║███████╗██████╔╝║
║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝     ╚═╝╚══════╝╚═════╝ ║
║                          DICOM Anonymizer v{version:<24}                ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
"""


def show_banner(version: str = "1.0.0") -> None:
    """Display the THAKAAMED branded banner."""
    console.print(BANNER.format(version=version), style=BRAND_GOLD)


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[success]✓[/success] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[error]✗[/error] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]⚠[/warning] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[info]ℹ[/info] {message}")


def create_branded_panel(content: str, title: str | None = None) -> Panel:
    """Create a panel with THAKAAMED branding."""
    return Panel(
        content,
        title=title,
        border_style=BRAND_GOLD,
        box=box.ROUNDED,
    )


def create_results_table(title: str | None = "Results") -> Table:
    """Create a table with THAKAAMED branding."""
    return Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style=f"bold {BRAND_GOLD}",
    )
