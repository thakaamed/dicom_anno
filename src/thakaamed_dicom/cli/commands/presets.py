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
"""Presets listing command for THAKAAMED DICOM Anonymizer."""

import click

from thakaamed_dicom.cli.console import console, create_results_table, print_info
from thakaamed_dicom.config.loader import list_available_presets


@click.command()
def presets() -> None:
    """List available anonymization presets."""
    available_presets = list_available_presets()

    if not available_presets:
        print_info("No presets found.")
        return

    # Create table
    table = create_results_table(title="Available Anonymization Presets")
    table.add_column("Name", style="bold cyan", no_wrap=True)
    table.add_column("Filename", style="dim")
    table.add_column("Description", style="white")
    table.add_column("Location", style="dim")
    table.add_column("Compliance", style="green")

    for preset in available_presets:
        compliance_str = ", ".join(preset.get("compliance", [])[:2])
        if len(preset.get("compliance", [])) > 2:
            compliance_str += "..."

        table.add_row(
            preset["name"],
            preset["filename"],
            preset["description"][:50] + "..." if len(preset["description"]) > 50 else preset["description"],
            preset["location"],
            compliance_str or "-",
        )

    console.print()
    console.print(table)
    console.print()

    # Usage hint
    console.print(
        "[dim]Use 'thakaamed-dicom validate --preset <filename>' to validate a preset[/dim]"
    )
    console.print(
        "[dim]Use 'thakaamed-dicom anonymize --preset <filename>' to use a preset[/dim]"
    )
    console.print()
