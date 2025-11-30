# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Validate command for THAKAAMED DICOM Anonymizer."""

from pathlib import Path

import click

from dicom_anonymizer.cli.console import (
    console,
    create_results_table,
    print_error,
    print_info,
    print_success,
)
from dicom_anonymizer.config.loader import load_preset


@click.command()
@click.option(
    "--preset",
    "-p",
    type=str,
    help="Name of bundled preset to validate (e.g., sfda_safe_harbor)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to custom YAML configuration file",
)
def validate(preset: str | None, config: Path | None) -> None:
    """Validate configuration files.

    Validates preset configuration files to ensure they are properly
    formatted and contain valid settings.

    Examples:

        \b
        # Validate a bundled preset
        thakaamed-dicom validate --preset sfda_safe_harbor

        \b
        # Validate a custom configuration file
        thakaamed-dicom validate --config ./my_preset.yaml
    """
    if not preset and not config:
        print_error("Please specify either --preset or --config")
        raise click.UsageError("Must specify --preset or --config")

    target = preset or str(config)
    print_info(f"Validating: {target}")
    console.print()

    try:
        # Load and validate the preset
        preset_config = load_preset(target)

        # Display validation results
        print_success("Configuration is valid!")
        console.print()

        # Show preset details
        table = create_results_table(title="Preset Configuration")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Name", preset_config.name)
        table.add_row("Version", preset_config.version)
        table.add_row(
            "Description",
            preset_config.description[:60] + "..."
            if len(preset_config.description) > 60
            else preset_config.description,
        )
        table.add_row("Compliance", ", ".join(preset_config.compliance) or "-")
        table.add_row("Date Handling", preset_config.date_handling.value)
        table.add_row("Remove Private Tags", "Yes" if preset_config.remove_private_tags else "No")
        table.add_row("Tag Rules", str(len(preset_config.tag_rules)))

        # Profile options
        profile_options = []
        if preset_config.clean_pixel_data:
            profile_options.append("Clean Pixel Data")
        if preset_config.clean_visual_features:
            profile_options.append("Clean Visual Features")
        if preset_config.retain_longitudinal:
            profile_options.append("Retain Longitudinal")
        if preset_config.retain_patient_characteristics:
            profile_options.append("Retain Patient Characteristics")
        if preset_config.retain_device_identity:
            profile_options.append("Retain Device Identity")
        if preset_config.retain_institution_identity:
            profile_options.append("Retain Institution Identity")

        table.add_row(
            "Profile Options",
            ", ".join(profile_options) if profile_options else "None (Basic Profile)",
        )

        console.print(table)
        console.print()

        # Show sample tag rules
        if preset_config.tag_rules:
            console.print("[bold]Sample Tag Rules:[/bold]")
            rules_table = create_results_table(title=None)
            rules_table.add_column("Tag", style="cyan")
            rules_table.add_column("Action", style="yellow")
            rules_table.add_column("Description", style="dim")

            for rule in preset_config.tag_rules[:5]:
                rules_table.add_row(
                    rule.tag,
                    rule.action.value,
                    rule.description or "-",
                )

            if len(preset_config.tag_rules) > 5:
                rules_table.add_row(
                    "...",
                    "...",
                    f"and {len(preset_config.tag_rules) - 5} more rules",
                )

            console.print(rules_table)
            console.print()

    except FileNotFoundError as e:
        print_error(f"File not found: {e}")
        raise click.ClickException(str(e)) from e

    except ValueError as e:
        print_error(f"Validation failed: {e}")
        console.print()
        console.print(
            "[dim]Check the YAML syntax and ensure all required fields are present.[/dim]"
        )
        raise click.ClickException(str(e)) from e

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        raise click.ClickException(str(e)) from e
