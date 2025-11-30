# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Version command for THAKAAMED DICOM Anonymizer."""

import sys

import click

from dicom_anonymizer import __version__
from dicom_anonymizer.cli.console import console, create_branded_panel


@click.command()
def version() -> None:
    """Show version information and system details."""
    # Get dependency versions
    try:
        import pydicom

        pydicom_version = pydicom.__version__
    except ImportError:
        pydicom_version = "not installed"

    try:
        from importlib.metadata import version as get_version

        rich_version = get_version("rich")
    except Exception:
        rich_version = "not installed"

    try:
        import pydantic

        pydantic_version = pydantic.__version__
    except ImportError:
        pydantic_version = "not installed"

    # Build version info
    version_info = f"""
[bold]THAKAAMED DICOM Anonymizer[/bold] v{__version__}

[dim]Professional medical imaging de-identification[/dim]
[brand.gold]Supporting Saudi Vision 2030 Healthcare Transformation[/brand.gold]

[bold]System Information:[/bold]
  Python:   {sys.version.split()[0]}
  pydicom:  {pydicom_version}
  Rich:     {rich_version}
  Pydantic: {pydantic_version}

[dim]© 2024 THAKAAMED | Kingdom of Saudi Arabia[/dim]
"""

    panel = create_branded_panel(version_info.strip(), title="Version")
    console.print(panel)
