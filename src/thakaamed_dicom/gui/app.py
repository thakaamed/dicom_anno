# ============================================================================
#  THAKAAMED DICOM Anonymizer
#  Copyright (c) 2025 THAKAAMED AI. All rights reserved.
#
#  https://thakaamed.com | Enterprise Healthcare Solutions
#
#  LICENSE: CC BY-NC-ND 4.0 (Non-Commercial)
#  This software is for RESEARCH AND EDUCATIONAL PURPOSES ONLY.
#  For commercial licensing: licensing@thakaamed.com
#
#  See LICENSE file for full terms. | Built for Saudi Vision 2030
# ============================================================================
"""Simplified folder-based GUI for THAKAAMED DICOM Anonymizer."""

import subprocess
import sys
from pathlib import Path

from nicegui import app, ui

from thakaamed_dicom import __version__
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor
from thakaamed_dicom.gui.components import PRESETS
from thakaamed_dicom.gui.styles import APP_CSS
from thakaamed_dicom.reports.generator import ReportGenerator
from thakaamed_dicom.reports.models import ReportFormat

# Fixed folder paths
INPUT_FOLDER = Path.home() / "DICOM_Input"
OUTPUT_FOLDER = Path.home() / "DICOM_Anonymized"


def ensure_folders():
    """Create input and output folders if they don't exist."""
    INPUT_FOLDER.mkdir(exist_ok=True)
    OUTPUT_FOLDER.mkdir(exist_ok=True)


def scan_dicom_files(folder: Path) -> list[Path]:
    """Scan folder for DICOM files."""
    dicom_files = []
    dicom_extensions = {".dcm", ".dicom", ".dic", ".ima"}
    
    if not folder.exists():
        return dicom_files
    
    for file_path in folder.rglob("*"):
        if file_path.is_file():
            # Check extension
            if file_path.suffix.lower() in dicom_extensions:
                dicom_files.append(file_path)
            # Also include files without extension (common for DICOM)
            elif not file_path.suffix and file_path.name not in {".", "..", ".DS_Store"}:
                dicom_files.append(file_path)
    
    return sorted(dicom_files)


def open_folder_in_finder(folder: Path):
    """Open folder in Finder (macOS)."""
    folder.mkdir(exist_ok=True)
    if sys.platform == "darwin":
        subprocess.run(["open", str(folder)])
    elif sys.platform == "win32":
        subprocess.run(["explorer", str(folder)])
    else:
        subprocess.run(["xdg-open", str(folder)])


class DicomAnonymizerApp:
    """Main application state and UI."""

    def __init__(self):
        self.selected_preset: str = "sfda_safe_harbor"
        self.processing: bool = False
        self.dicom_files: list[Path] = []
        self.stats = None
        
        # UI elements
        self.file_count_label = None
        self.file_list_container = None
        self.progress_container = None
        self.results_container = None
        self.anonymize_btn = None
        self.progress_bar = None
        self.status_label = None
        self.preset_cards = {}
        
        # Ensure folders exist
        ensure_folders()
        
        # Initial scan
        self.dicom_files = scan_dicom_files(INPUT_FOLDER)

    def build_ui(self):
        """Build the main user interface."""
        # Add custom CSS
        ui.add_head_html(f"<style>{APP_CSS}</style>")
        
        with ui.column().classes("app-container w-full"):
            # Header
            self._build_header()
            
            # Main card
            with ui.card().classes("card"):
                # Step 1: Input folder info
                self._build_input_section()
                
                # Step 2: Preset selector
                self._build_preset_selector()
                
                # Anonymize button
                with ui.row().classes("w-full justify-center mt-8"):
                    self.anonymize_btn = ui.button(
                        "🔒 ANONYMIZE FILES",
                        on_click=self._process_files,
                    ).classes("anonymize-btn").props("no-caps")
                    self._update_button_state()
                
                # Progress section (hidden initially)
                self.progress_container = ui.column().classes("progress-section w-full")
                self.progress_container.set_visibility(False)
                with self.progress_container:
                    self.status_label = ui.label("Preparing...").classes("text-lg font-semibold text-gray-700")
                    self.progress_bar = ui.linear_progress(value=0).classes("w-full")
                
                # Results section (hidden initially)
                self.results_container = ui.column().classes("w-full")
                self.results_container.set_visibility(False)
            
            # Footer
            self._build_footer()

    def _build_header(self):
        """Build the header with logo and title."""
        with ui.row().classes("w-full items-center justify-center gap-6 mb-4"):
            # Try to load logo
            logo_path = Path(__file__).parent.parent / "reports" / "assets" / "logo.png"
            if logo_path.exists():
                ui.image(str(logo_path)).classes("header-logo")
            
            with ui.column().classes("items-center"):
                ui.html("<h1 class='main-title'>THAKAA MED</h1>", sanitize=False)
                ui.html("<p class='subtitle'>DICOM Anonymizer for Medical Research</p>", sanitize=False)
                ui.label(f"v{__version__}").classes("text-white/60 text-sm mt-1")

    def _build_input_section(self):
        """Build the input folder section."""
        # Section header
        with ui.row().classes("w-full items-center gap-2 mb-2"):
            ui.html("<span style='font-size: 1.5rem;'>📁</span>", sanitize=False)
            ui.label("Step 1: Place your DICOM files").classes("text-xl font-bold text-gray-800")
        
        # Info box
        with ui.card().classes("w-full bg-purple-50 border-l-4 border-purple-500 p-4 mb-4"):
            ui.label("Put your DICOM files in this folder:").classes("text-gray-700 mb-2")
            with ui.row().classes("items-center gap-2"):
                ui.label(str(INPUT_FOLDER)).classes("font-mono text-sm bg-white px-3 py-2 rounded border")
                ui.button(
                    "Open Folder",
                    on_click=lambda: open_folder_in_finder(INPUT_FOLDER),
                ).props("flat dense").classes("text-purple-600")
        
        # File count and refresh
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-3"):
                self.file_count_label = ui.label().classes("text-lg font-semibold")
                self._update_file_count()
            
            ui.button(
                "🔄 Refresh",
                on_click=self._refresh_files,
            ).props("flat dense").classes("text-purple-600")
        
        # File list (collapsible)
        with ui.expansion("Show files", icon="description").classes("w-full mt-2"):
            self.file_list_container = ui.column().classes("w-full max-h-48 overflow-y-auto")
            self._update_file_list()

    def _update_file_count(self):
        """Update the file count display."""
        count = len(self.dicom_files)
        if count == 0:
            self.file_count_label.text = "No DICOM files found"
            self.file_count_label.classes("text-lg font-semibold text-orange-600", remove="text-green-600 text-gray-700")
        elif count == 1:
            self.file_count_label.text = "1 DICOM file ready"
            self.file_count_label.classes("text-lg font-semibold text-green-600", remove="text-orange-600 text-gray-700")
        else:
            self.file_count_label.text = f"{count} DICOM files ready"
            self.file_count_label.classes("text-lg font-semibold text-green-600", remove="text-orange-600 text-gray-700")

    def _update_file_list(self):
        """Update the file list display."""
        self.file_list_container.clear()
        
        with self.file_list_container:
            if not self.dicom_files:
                ui.label("No files found. Add DICOM files to the input folder and click Refresh.").classes("text-gray-500 italic")
            else:
                for file_path in self.dicom_files[:50]:  # Show max 50 files
                    with ui.row().classes("items-center gap-2 py-1 border-b border-gray-100"):
                        ui.icon("description", size="sm").classes("text-purple-400")
                        ui.label(file_path.name).classes("text-sm text-gray-700")
                
                if len(self.dicom_files) > 50:
                    ui.label(f"... and {len(self.dicom_files) - 50} more files").classes("text-sm text-gray-500 italic mt-2")

    def _refresh_files(self):
        """Rescan the input folder."""
        self.dicom_files = scan_dicom_files(INPUT_FOLDER)
        self._update_file_count()
        self._update_file_list()
        self._update_button_state()
        ui.notify(f"Found {len(self.dicom_files)} DICOM files", type="info")

    def _build_preset_selector(self):
        """Build the preset selection section."""
        with ui.row().classes("w-full items-center gap-2 mt-6 mb-4"):
            ui.html("<span style='font-size: 1.5rem;'>🔐</span>", sanitize=False)
            ui.label("Step 2: Select Anonymization Level").classes("text-xl font-bold text-gray-800")
        
        with ui.row().classes("w-full gap-4 flex-wrap"):
            for preset in PRESETS:
                self._create_preset_card(preset)

    def _create_preset_card(self, preset):
        """Create a preset selection card."""
        is_selected = self.selected_preset == preset.id
        
        card = ui.card().classes(
            f"preset-option flex-1 min-w-64 cursor-pointer {'selected' if is_selected else ''}"
        )
        
        with card:
            with ui.row().classes("items-center gap-3"):
                ui.label(preset.icon).classes("text-2xl")
                with ui.column():
                    ui.label(preset.name).classes("preset-title")
                    ui.label(preset.description).classes("preset-desc")
        
        card.on("click", lambda p=preset.id, c=card: self._select_preset(p, c))
        self.preset_cards[preset.id] = card

    def _select_preset(self, preset_id: str, clicked_card):
        """Handle preset selection."""
        self.selected_preset = preset_id
        
        # Update all card styles
        for pid, card in self.preset_cards.items():
            if pid == preset_id:
                card.classes(add="selected")
            else:
                card.classes(remove="selected")
        
        preset_name = preset_id.replace("_", " ").title()
        ui.notify(f"Selected: {preset_name}", type="positive")

    def _update_button_state(self):
        """Update the anonymize button state."""
        if self.dicom_files and not self.processing:
            self.anonymize_btn.enable()
        else:
            self.anonymize_btn.disable()

    async def _process_files(self):
        """Process DICOM files from the input folder."""
        if not self.dicom_files:
            ui.notify("No DICOM files found. Add files to ~/DICOM_Input and click Refresh.", type="warning")
            return
        
        self.processing = True
        self.anonymize_btn.disable()
        self.progress_container.set_visibility(True)
        self.results_container.set_visibility(False)
        
        try:
            # Load preset
            self.status_label.text = "Loading preset configuration..."
            self.progress_bar.value = 0.05
            await ui.run_javascript("null")  # Force UI update
            
            preset_config = load_preset(self.selected_preset)
            
            # Create processor
            processor = DicomProcessor(preset=preset_config)
            
            # Process files
            total_files = len(self.dicom_files)
            self.status_label.text = f"Processing {total_files} file(s)..."
            self.progress_bar.value = 0.1
            await ui.run_javascript("null")
            
            def update_progress(completed: int, total: int):
                progress = 0.1 + (completed / max(total, 1)) * 0.7
                self.progress_bar.value = progress
                self.status_label.text = f"Processing file {completed}/{total}..."
            
            # Process directly from input folder to output folder
            self.stats = processor.process_directory(
                INPUT_FOLDER,
                OUTPUT_FOLDER,
                parallel=True,
                workers=4,
                progress_callback=update_progress,
            )
            
            # Generate reports
            self.status_label.text = "Generating reports..."
            self.progress_bar.value = 0.85
            await ui.run_javascript("null")
            
            report_dir = OUTPUT_FOLDER / "reports"
            report_dir.mkdir(exist_ok=True)
            
            generator = ReportGenerator()
            generator.generate(
                stats=self.stats,
                preset=preset_config,
                input_path=str(INPUT_FOLDER),
                output_path=str(OUTPUT_FOLDER),
                uid_mapping=processor.uid_mapper.export_mapping(),
                report_dir=report_dir,
                formats=[ReportFormat.PDF, ReportFormat.JSON],
            )
            
            self.progress_bar.value = 1.0
            self.status_label.text = "Complete!"
            
            # Show results
            self._show_results()
            
        except Exception as e:
            ui.notify(f"Error: {str(e)}", type="negative")
            self.status_label.text = f"Error: {str(e)}"
        finally:
            self.processing = False
            self._update_button_state()

    def _show_results(self):
        """Display the processing results."""
        self.results_container.set_visibility(True)
        self.results_container.clear()
        
        with self.results_container:
            with ui.card().classes("results-card w-full mt-4"):
                with ui.row().classes("items-center justify-center gap-4 mb-4"):
                    ui.html("<div class='success-icon'>✅</div>", sanitize=False)
                    ui.label("Anonymization Complete!").classes("text-2xl font-bold text-green-700")
                
                # Stats grid
                if self.stats:
                    with ui.row().classes("stats-grid w-full justify-center"):
                        self._create_stat("Files Processed", str(self.stats.files_processed))
                        self._create_stat("Successful", str(self.stats.files_successful))
                        self._create_stat("Tags Modified", f"{self.stats.total_tags_modified:,}")
                        self._create_stat("UIDs Remapped", f"{self.stats.total_uids_remapped:,}")
                
                # Output location
                ui.label("Anonymized files saved to:").classes("text-gray-700 mt-6 mb-2")
                with ui.row().classes("items-center gap-2"):
                    ui.label(str(OUTPUT_FOLDER)).classes("font-mono text-sm bg-white px-3 py-2 rounded border")
                    ui.button(
                        "Open Folder",
                        on_click=lambda: open_folder_in_finder(OUTPUT_FOLDER),
                    ).classes("download-btn").props("no-caps")
                
                # Process more button
                with ui.row().classes("w-full justify-center mt-6"):
                    ui.button(
                        "Process More Files",
                        on_click=self._reset,
                    ).props("flat").classes("text-gray-600")

    def _create_stat(self, label: str, value: str):
        """Create a stat display item."""
        with ui.column().classes("stat-item"):
            ui.label(value).classes("stat-value")
            ui.label(label).classes("stat-label")

    def _reset(self):
        """Reset the application for new files."""
        self.stats = None
        self.progress_container.set_visibility(False)
        self.results_container.set_visibility(False)
        self.progress_bar.value = 0
        self.status_label.text = "Preparing..."
        
        # Refresh file list
        self._refresh_files()
        
        ui.notify("Ready for new files", type="info")

    def _build_footer(self):
        """Build the footer."""
        ui.html("""
            <div class='footer'>
                <p>© 2025 <a href='https://thakaamed.ai' target='_blank'>THAKAAMED AI</a> • 
                Built for Saudi Vision 2030 Healthcare Transformation</p>
                <p style='margin-top: 0.5rem; font-size: 0.8rem;'>
                    For research and educational purposes only • 
                    <a href='mailto:licensing@thakaamed.ai'>Commercial licensing</a>
                </p>
            </div>
        """, sanitize=False)


def run_gui(host: str = "127.0.0.1", port: int = 8080, reload: bool = False):
    """Run the THAKAAMED DICOM Anonymizer GUI."""
    # Ensure folders exist
    ensure_folders()
    
    # Create app instance
    dicom_app = DicomAnonymizerApp()
    
    # Build UI
    @ui.page("/")
    def index():
        dicom_app.build_ui()
    
    # Run the app
    ui.run(
        host=host,
        port=port,
        title="THAKAAMED DICOM Anonymizer",
        favicon="🏥",
        reload=reload,
        show=True,
    )


def main():
    """Entry point for the GUI command."""
    # Parse simple arguments
    host = "127.0.0.1"
    port = 8080
    
    for i, arg in enumerate(sys.argv[1:]):
        if arg in ("--host", "-h") and i + 2 < len(sys.argv):
            host = sys.argv[i + 2]
        elif arg in ("--port", "-p") and i + 2 < len(sys.argv):
            port = int(sys.argv[i + 2])
    
    print(f"\n🏥 THAKAAMED DICOM Anonymizer")
    print(f"   Starting on http://{host}:{port}")
    print(f"")
    print(f"   📁 Input folder:  ~/DICOM_Input")
    print(f"   📂 Output folder: ~/DICOM_Anonymized")
    print(f"")
    print(f"   Press Ctrl+C to stop\n")
    
    run_gui(host=host, port=port)


if __name__ == "__main__":
    main()
