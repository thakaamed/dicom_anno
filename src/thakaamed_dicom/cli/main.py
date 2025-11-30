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
"""Main CLI entry point for THAKAAMED DICOM Anonymizer."""


import click

from thakaamed_dicom import __version__
from thakaamed_dicom.cli.console import console, show_banner


@click.group(invoke_without_command=True)
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
    """THAKAAMED DICOM Anonymizer - Professional medical imaging de-identification

    \b
    Supporting Saudi Vision 2030 Healthcare Transformation

    \b
    Available presets:
      • sfda_safe_harbor    - Maximum privacy (HIPAA Safe Harbor)
      • research            - Balanced for research (date shifting)
      • full_anonymization  - Complete de-identification

    \b
    Quick start:
      thakaamed-dicom presets              # List available presets
      thakaamed-dicom validate -p sfda_safe_harbor  # Validate a preset
      thakaamed-dicom anonymize -i ./in -o ./out -p sfda_safe_harbor
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
from thakaamed_dicom.cli.commands.anonymize import anonymize  # noqa: E402
from thakaamed_dicom.cli.commands.presets import presets  # noqa: E402
from thakaamed_dicom.cli.commands.report import report  # noqa: E402
from thakaamed_dicom.cli.commands.validate import validate  # noqa: E402
from thakaamed_dicom.cli.commands.version import version  # noqa: E402

main.add_command(version)
main.add_command(presets)
main.add_command(validate)
main.add_command(anonymize)
main.add_command(report)


if __name__ == "__main__":
    main()
