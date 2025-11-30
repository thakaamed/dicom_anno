# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Main CLI entry point for DICOM Anonymizer."""

import click

from dicom_anonymizer import __version__
from dicom_anonymizer.cli.console import console, show_banner


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="dicom-anonym")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.pass_context
def main(ctx: click.Context, config: str | None, verbose: bool) -> None:
    """DICOM Anonymizer - Professional medical imaging de-identification

    \b
    Supporting Saudi Vision 2030 Healthcare Transformation

    \b
    Available presets:
      • sfda_safe_harbor    - Maximum privacy (HIPAA Safe Harbor)
      • research            - Balanced for research (date shifting)
      • full_anonymization  - Complete de-identification

    \b
    Quick start:
      dicom-anonym presets              # List available presets
      dicom-anonym validate -p sfda_safe_harbor  # Validate a preset
      dicom-anonym anonymize -i ./in -o ./out -p sfda_safe_harbor
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose
    ctx.obj["console"] = console

    # If no command provided, show banner and help
    if ctx.invoked_subcommand is None:
        show_banner(__version__)
        click.echo(ctx.get_help())


# Import and register subcommands (must be after main() definition)
from dicom_anonymizer.cli.commands.anonymize import anonymize  # noqa: E402
from dicom_anonymizer.cli.commands.presets import presets  # noqa: E402
from dicom_anonymizer.cli.commands.report import report  # noqa: E402
from dicom_anonymizer.cli.commands.validate import validate  # noqa: E402
from dicom_anonymizer.cli.commands.version import version  # noqa: E402

main.add_command(version)
main.add_command(presets)
main.add_command(validate)
main.add_command(anonymize)
main.add_command(report)


if __name__ == "__main__":
    main()
