# ============================================================================
#  THAKAAMED DICOM Anonymizer
#  Copyright (c) 2024 THAKAAMED AI. All rights reserved.
#
#  https://thakaamed.com | Enterprise Healthcare Solutions
#
#  LICENSE: CC BY-NC-ND 4.0 (Non-Commercial)
#  This software is for RESEARCH AND EDUCATIONAL PURPOSES ONLY.
#  For commercial licensing: licensing@thakaamed.com
#
#  See LICENSE file for full terms. | Built for Saudi Vision 2030
# ============================================================================
"""Version command for THAKAAMED DICOM Anonymizer."""

import sys

import click

from thakaamed_dicom import __version__
from thakaamed_dicom.cli.console import console, create_branded_panel


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
