# -*- coding: utf-8 -*-
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
"""PDF report builder with THAKAAMED branding."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, HRFlowable

from thakaamed_dicom.reports.models import ReportData

# ============================================================================
# THAKAAMED Brand Colors - Purple/Lavender Palette with Gold Accents
# ============================================================================
BRAND_PURPLE_DARK = colors.HexColor("#2D1B4E")    # Deep purple (headers, primary)
BRAND_PURPLE = colors.HexColor("#4A3069")          # Medium purple
BRAND_PURPLE_LIGHT = colors.HexColor("#E8E0F0")   # Light lavender (backgrounds)
BRAND_LAVENDER = colors.HexColor("#9B8BB8")        # Lavender accent
BRAND_GOLD = colors.HexColor("#C9A227")            # Gold accent (was green)
BRAND_GOLD_BRIGHT = colors.HexColor("#D4AF37")    # Bright gold
BRAND_GOLD_LIGHT = colors.HexColor("#F5E6B3")     # Light gold
BRAND_WHITE = colors.HexColor("#FFFFFF")
BRAND_GRAY = colors.HexColor("#6B7280")
BRAND_GRAY_LIGHT = colors.HexColor("#F3F4F6")
BRAND_TEXT_DARK = colors.HexColor("#1F1635")      # Dark purple for text
BRAND_GREEN_SAUDI = colors.HexColor("#006C35")    # Saudi green (Vision 2030 only)

# Legacy aliases for compatibility
BRAND_PRIMARY = BRAND_PURPLE_DARK
BRAND_LIGHT = BRAND_PURPLE_LIGHT
BRAND_TEAL = BRAND_PURPLE_DARK
BRAND_TEAL_DARK = BRAND_PURPLE_DARK
BRAND_TEAL_LIGHT = BRAND_PURPLE_LIGHT
BRAND_NAVY = BRAND_TEXT_DARK


class NumberedCanvas(canvas.Canvas):
    """Custom canvas for page numbering (Page X of Y)."""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(7.5 * inch, 0.5 * inch, f"Page {self._pageNumber} of {page_count}")


class PDFReportBuilder:
    """Build branded PDF anonymization report."""

    def __init__(self):
        self.styles = self._create_styles()
        self.logo_path = self._get_logo_path()

    def _get_logo_path(self) -> Path | None:
        """Get path to logo using importlib.resources (works when installed)."""
        try:
            from importlib.resources import files

            assets = files("dicom_anonymizer.reports.assets")
            logo_file = assets.joinpath("logo.png")
            # For Python 3.9+, convert Traversable to Path
            return Path(str(logo_file))
        except Exception:
            return None

    def _create_styles(self):
        """Create custom paragraph styles with THAKAAMED purple/lavender branding."""
        styles = getSampleStyleSheet()

        # Main report title - Dark purple
        styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=styles["Heading1"],
                fontSize=28,
                textColor=BRAND_PURPLE_DARK,
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName="Helvetica-Bold",
            )
        )
        
        # Subtitle under title - Gold
        styles.add(
            ParagraphStyle(
                name="ReportSubtitle",
                parent=styles["Normal"],
                fontSize=12,
                textColor=BRAND_GOLD,
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName="Helvetica-Bold",
            )
        )

        # Section headers - Dark purple with gold accent
        styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=BRAND_PURPLE_DARK,
                spaceBefore=20,
                spaceAfter=12,
                fontName="Helvetica-Bold",
                borderWidth=0,
                borderPadding=0,
                leftIndent=0,
            )
        )

        # Metadata subtitle
        styles.add(
            ParagraphStyle(
                name="Subtitle",
                parent=styles["Normal"],
                fontSize=10,
                textColor=BRAND_LAVENDER,
                alignment=TA_CENTER,
                spaceAfter=3,
            )
        )
        
        # Body text (custom - renamed to avoid conflict with built-in BodyText)
        styles.add(
            ParagraphStyle(
                name="THKBodyText",
                parent=styles["Normal"],
                fontSize=10,
                textColor=BRAND_TEXT_DARK,
                leading=14,
            )
        )

        # Table cell style
        styles.add(
            ParagraphStyle(
                name="TableCell",
                parent=styles["Normal"],
                fontSize=8,
                leading=10,
                textColor=BRAND_TEXT_DARK,
            )
        )
        
        # Footer style
        styles.add(
            ParagraphStyle(
                name="Footer",
                parent=styles["Normal"],
                fontSize=9,
                textColor=BRAND_LAVENDER,
                alignment=TA_CENTER,
            )
        )
        
        # Vision 2030 style - Keep Saudi green for this
        styles.add(
            ParagraphStyle(
                name="Vision2030",
                parent=styles["Normal"],
                fontSize=10,
                textColor=BRAND_GREEN_SAUDI,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        return styles

    def build(self, report_data: ReportData, output_path: Path) -> Path:
        """
        Generate PDF report.

        Args:
            report_data: Complete report data
            output_path: Path for output file

        Returns:
            Path to generated file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=1 * inch,
            bottomMargin=0.75 * inch,
        )

        story = []

        # Build content
        self._add_header(story, report_data)
        self._add_executive_summary(story, report_data)
        self._add_statistics_table(story, report_data)
        self._add_preset_config(story, report_data)
        self._add_file_manifest(story, report_data)
        self._add_compliance_statement(story, report_data)
        self._add_signature(story, report_data)

        # Build PDF with custom canvas for page numbering
        doc.build(
            story,
            onFirstPage=self._add_page_decorations,
            onLaterPages=self._add_page_decorations,
            canvasmaker=NumberedCanvas,
        )

        return output_path

    def _add_page_decorations(self, canvas_obj, doc):
        """Add THAKAAMED branded header/footer decorations to each page."""
        canvas_obj.saveState()
        
        page_width = letter[0]
        page_height = letter[1]

        # ========== HEADER ==========
        # Top dark purple banner stripe
        canvas_obj.setFillColor(BRAND_PURPLE_DARK)
        canvas_obj.rect(0, page_height - 0.4 * inch, page_width, 0.4 * inch, fill=1, stroke=0)
        
        # Gold accent line under purple
        canvas_obj.setStrokeColor(BRAND_GOLD_BRIGHT)
        canvas_obj.setLineWidth(3)
        canvas_obj.line(0, page_height - 0.4 * inch, page_width, page_height - 0.4 * inch)
        
        # Header text on purple banner
        canvas_obj.setFillColor(BRAND_GOLD)
        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.drawString(0.75 * inch, page_height - 0.28 * inch, "THAKAAMED")
        
        canvas_obj.setFillColor(BRAND_WHITE)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawRightString(page_width - 0.75 * inch, page_height - 0.28 * inch, 
                                   "DICOM Anonymization Report")

        # ========== FOOTER ==========
        # Gold accent line
        canvas_obj.setStrokeColor(BRAND_GOLD)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(0.75 * inch, 0.8 * inch, page_width - 0.75 * inch, 0.8 * inch)
        
        # Footer text - left side
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.setFillColor(BRAND_PURPLE_DARK)
        canvas_obj.drawString(0.75 * inch, 0.6 * inch, "THAKAAMED AI")
        
        # Footer text - center (Vision 2030)
        canvas_obj.setFillColor(BRAND_GREEN_SAUDI)
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.drawCentredString(page_width / 2, 0.6 * inch, "Vision 2030 Healthcare Transformation")
        
        # Footer text - right side
        canvas_obj.setFillColor(BRAND_LAVENDER)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawRightString(page_width - 0.75 * inch, 0.6 * inch, "CONFIDENTIAL")
        
        # Bottom dark purple stripe
        canvas_obj.setFillColor(BRAND_PURPLE_DARK)
        canvas_obj.rect(0, 0, page_width, 0.3 * inch, fill=1, stroke=0)
        
        # Website in footer stripe (gold text)
        canvas_obj.setFillColor(BRAND_GOLD)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawCentredString(page_width / 2, 0.12 * inch, "https://thakaamed.ai | contact@thakaamed.com")

        canvas_obj.restoreState()

    def _add_header(self, story, report_data: ReportData):
        """Add THAKAAMED branded report header with logo."""
        story.append(Spacer(1, 0.3 * inch))
        
        # Logo (if exists) - preserve aspect ratio
        logo_path = self.logo_path
        if logo_path:
            try:
                # Load image to get actual dimensions
                from PIL import Image as PILImage
                with PILImage.open(str(logo_path)) as img:
                    orig_width, orig_height = img.size
                
                # Set max width and calculate proportional height
                max_width = 2.2 * inch
                aspect_ratio = orig_height / orig_width
                calculated_height = max_width * aspect_ratio
                
                # Cap height if too tall
                max_height = 1.2 * inch
                if calculated_height > max_height:
                    calculated_height = max_height
                    max_width = max_height / aspect_ratio
                
                logo = Image(str(logo_path), width=max_width, height=calculated_height, mask="auto")
                logo.hAlign = "CENTER"
                story.append(logo)
                story.append(Spacer(1, 0.25 * inch))
            except Exception:
                # Fallback: Text-based THAKAAMED header
                story.append(Paragraph(
                    "<font color='#2D1B4E' size='24'><b>THAKAAMED</b></font>",
                    self.styles["ReportTitle"]
                ))
                story.append(Spacer(1, 0.1 * inch))

        # Main Title
        story.append(Paragraph("DICOM ANONYMIZATION REPORT", self.styles["ReportTitle"]))
        
        # Subtitle with gold accent
        story.append(Paragraph(
            "De-identification Audit Trail",
            self.styles["ReportSubtitle"]
        ))
        
        # Decorative line
        story.append(HRFlowable(
            width="80%", 
            thickness=2, 
            color=BRAND_GOLD, 
            spaceBefore=10, 
            spaceAfter=15,
            hAlign='CENTER'
        ))

        # Metadata in a clean box
        metadata_data = [
            ["Generated", report_data.generated_at.strftime('%Y-%m-%d %H:%M:%S')],
            ["Preset", report_data.preset_name],
            ["Compliance", ', '.join(report_data.compliance_standards)],
        ]
        
        metadata_table = Table(metadata_data, colWidths=[1.5 * inch, 4.5 * inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), BRAND_TEAL),
            ('TEXTCOLOR', (1, 0), (1, -1), BRAND_NAVY),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        metadata_table.hAlign = 'CENTER'
        story.append(metadata_table)
        story.append(Spacer(1, 0.4 * inch))

    def _add_executive_summary(self, story, report_data: ReportData):
        """Add THAKAAMED branded executive summary section."""
        story.append(Paragraph("📋 EXECUTIVE SUMMARY", self.styles["SectionHeader"]))
        story.append(HRFlowable(width="30%", thickness=2, color=BRAND_GOLD, spaceBefore=0, spaceAfter=10, hAlign='LEFT'))

        # Status determination
        if report_data.files_failed == 0:
            status = "✓ COMPLETE"
            status_color = BRAND_GOLD  # Gold for success
        else:
            status = "⚠ COMPLETED WITH ERRORS"
            status_color = colors.HexColor("#D97706")  # Amber

        # Summary in a styled box
        summary_data = [
            ["Files Processed", f"{report_data.files_processed:,}"],
            ["Studies Processed", f"{report_data.studies_processed:,}"],
            ["Series Processed", f"{report_data.series_processed:,}"],
            ["Processing Time", f"{report_data.processing_time_seconds:.1f} seconds"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), BRAND_TEAL),
            ('TEXTCOLOR', (1, 0), (1, -1), BRAND_NAVY),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, -1), BRAND_TEAL_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, BRAND_TEAL),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(summary_table)
        
        # Status badge
        story.append(Spacer(1, 0.15 * inch))
        status_style = ParagraphStyle(
            'StatusBadge',
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=status_color,
            fontName='Helvetica-Bold',
        )
        story.append(Paragraph(f"Status: {status}", status_style))
        story.append(Spacer(1, 0.3 * inch))

    def _add_statistics_table(self, story, report_data: ReportData):
        """Add THAKAAMED branded statistics table."""
        # Section header with gold underline
        story.append(Paragraph("📊 PROCESSING STATISTICS", self.styles["SectionHeader"]))
        story.append(HRFlowable(width="30%", thickness=2, color=BRAND_GOLD, spaceBefore=0, spaceAfter=10, hAlign='LEFT'))

        data = [
            ["Metric", "Count"],
            ["Tags Modified", f"{report_data.total_tags_modified:,}"],
            ["Tags Removed", f"{report_data.total_tags_removed:,}"],
            ["UIDs Remapped", f"{report_data.total_uids_remapped:,}"],
            ["Private Tags Removed", f"{report_data.total_private_tags_removed:,}"],
            ["Files Successful", f"{report_data.files_successful:,}"],
            ["Files Failed", f"{report_data.files_failed:,}"],
        ]

        table = Table(data, colWidths=[3.5 * inch, 2 * inch])
        table.setStyle(
            TableStyle(
                [
                    # Header row - THAKAAMED teal
                    ("BACKGROUND", (0, 0), (-1, 0), BRAND_TEAL),
                    ("TEXTCOLOR", (0, 0), (-1, 0), BRAND_WHITE),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    # Data rows
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("TEXTCOLOR", (0, 1), (-1, -1), BRAND_NAVY),
                    # Alternating row colors - teal tint
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_WHITE, BRAND_TEAL_LIGHT]),
                    # Border styling
                    ("LINEBELOW", (0, 0), (-1, 0), 2, BRAND_GOLD),
                    ("LINEBELOW", (0, -1), (-1, -1), 1, BRAND_TEAL),
                    ("LINEBEFORE", (0, 0), (0, -1), 1, BRAND_TEAL),
                    ("LINEAFTER", (-1, 0), (-1, -1), 1, BRAND_TEAL),
                    # Padding
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.4 * inch))

    def _add_preset_config(self, story, report_data: ReportData):
        """Add THAKAAMED branded preset configuration section."""
        story.append(Paragraph("⚙️ PRESET CONFIGURATION", self.styles["SectionHeader"]))
        story.append(HRFlowable(width="30%", thickness=2, color=BRAND_GOLD, spaceBefore=0, spaceAfter=10, hAlign='LEFT'))

        # Config details in a table
        config_data = [
            ["Profile", report_data.preset_name],
            ["Description", report_data.preset_description[:80] + "..." if len(report_data.preset_description) > 80 else report_data.preset_description],
            ["Date Handling", report_data.date_handling],
        ]
        
        config_table = Table(config_data, colWidths=[1.5 * inch, 5 * inch])
        config_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), BRAND_PURPLE_DARK),
            ('TEXTCOLOR', (1, 0), (1, -1), BRAND_TEXT_DARK),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(config_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # ============================================================
        # ACTION CODE LEGEND
        # ============================================================
        story.append(Paragraph(
            "<font color='#2D1B4E'><b>📖 DICOM De-identification Action Codes (DICOM PS3.15)</b></font>", 
            self.styles["Normal"]
        ))
        story.append(Spacer(1, 0.1 * inch))
        
        legend_data = [
            ["Code", "Action", "Description"],
            ["D", "Dummy", "Replace with a non-zero length dummy value (e.g., 'ANONYMIZED')"],
            ["Z", "Zero", "Replace with zero-length value or dummy value"],
            ["X", "Remove", "Remove the attribute completely from the dataset"],
            ["K", "Keep", "Keep the attribute unchanged (no modification)"],
            ["C", "Clean", "Replace with values of similar meaning that don't identify the patient"],
            ["U", "UID", "Replace with a new, consistently-mapped unique identifier (UID)"],
        ]
        
        legend_table = Table(legend_data, colWidths=[0.5 * inch, 0.8 * inch, 4.8 * inch])
        legend_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_PURPLE_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), BRAND_WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            # Data
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (0, -1), BRAND_GOLD),  # Code in gold
            ('TEXTCOLOR', (1, 1), (1, -1), BRAND_PURPLE_DARK),  # Action in purple
            ('TEXTCOLOR', (2, 1), (2, -1), BRAND_TEXT_DARK),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), BRAND_PURPLE_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, BRAND_PURPLE_DARK),
            ('LINEBELOW', (0, 0), (-1, 0), 2, BRAND_GOLD),
            ('GRID', (0, 1), (-1, -1), 0.5, BRAND_LAVENDER),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(legend_table)
        story.append(Spacer(1, 0.25 * inch))

        # ============================================================
        # ALL TAG RULES APPLIED
        # ============================================================
        if report_data.tag_rules_applied:
            story.append(Paragraph(
                "<font color='#2D1B4E'><b>📋 Complete Tag Rules Applied ({} rules)</b></font>".format(
                    len(report_data.tag_rules_applied)
                ), 
                self.styles["Normal"]
            ))
            story.append(Spacer(1, 0.1 * inch))

            # Create a table for ALL rules
            rules_data = [["Tag", "Description", "Action"]]
            for rule in report_data.tag_rules_applied:
                desc = rule.get("description", "-")
                action = rule.get("action", "?")
                tag = rule.get("tag", "")
                rules_data.append([tag, desc, action])

            rules_table = Table(rules_data, colWidths=[1.1 * inch, 4.1 * inch, 0.6 * inch])
            rules_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), BRAND_PURPLE_DARK),
                ('TEXTCOLOR', (0, 0), (-1, 0), BRAND_WHITE),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('LINEBELOW', (0, 0), (-1, 0), 2, BRAND_GOLD),
                # Data rows
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('TEXTCOLOR', (0, 1), (0, -1), BRAND_PURPLE),  # Tags in purple
                ('TEXTCOLOR', (1, 1), (1, -1), BRAND_TEXT_DARK),
                ('TEXTCOLOR', (2, 1), (2, -1), BRAND_GOLD),  # Actions in gold
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BRAND_WHITE, BRAND_PURPLE_LIGHT]),
                ('BOX', (0, 0), (-1, -1), 1, BRAND_PURPLE_DARK),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, BRAND_LAVENDER),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(rules_table)

        story.append(Spacer(1, 0.4 * inch))

    def _add_file_manifest(self, story, report_data: ReportData):
        """Add THAKAAMED branded file manifest table."""
        story.append(Paragraph("📁 FILE MANIFEST", self.styles["SectionHeader"]))
        story.append(HRFlowable(width="30%", thickness=2, color=BRAND_GOLD, spaceBefore=0, spaceAfter=10, hAlign='LEFT'))

        if not report_data.file_records:
            story.append(Paragraph("No file records available.", self.styles["Normal"]))
            story.append(Spacer(1, 0.3 * inch))
            return

        # Header row
        data = [["Original File", "Status", "Study UID (New)"]]

        # Add file records (limit to prevent huge PDFs)
        max_files = 50
        for record in report_data.file_records[:max_files]:
            status = "✓" if record.success else "✗"
            # Truncate paths for display
            orig_path = record.original_path
            if len(orig_path) > 35:
                orig_path = "..." + orig_path[-32:]

            uid_short = (
                record.study_uid_new[:30] + "..."
                if len(record.study_uid_new) > 30
                else record.study_uid_new
            )

            data.append(
                [
                    Paragraph(orig_path, self.styles["TableCell"]),
                    status,
                    Paragraph(uid_short, self.styles["TableCell"]),
                ]
            )

        if len(report_data.file_records) > max_files:
            data.append(
                [
                    f"... and {len(report_data.file_records) - max_files} more files",
                    "",
                    "",
                ]
            )

        table = Table(data, colWidths=[2.5 * inch, 0.5 * inch, 3.1 * inch])
        table.setStyle(
            TableStyle(
                [
                    # Header
                    ("BACKGROUND", (0, 0), (-1, 0), BRAND_TEAL),
                    ("TEXTCOLOR", (0, 0), (-1, 0), BRAND_WHITE),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("LINEBELOW", (0, 0), (-1, 0), 2, BRAND_GOLD),
                    # Data
                    ("ALIGN", (1, 0), (1, -1), "CENTER"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 7),
                    ("TEXTCOLOR", (0, 1), (-1, -1), BRAND_NAVY),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_WHITE, BRAND_TEAL_LIGHT]),
                    # Borders
                    ("BOX", (0, 0), (-1, -1), 1, BRAND_TEAL),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.5, BRAND_GRAY_LIGHT),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.4 * inch))

    def _add_compliance_statement(self, story, report_data: ReportData):
        """Add THAKAAMED branded compliance statement."""
        story.append(Paragraph("🔒 COMPLIANCE STATEMENT", self.styles["SectionHeader"]))
        story.append(HRFlowable(width="30%", thickness=2, color=BRAND_GOLD, spaceBefore=0, spaceAfter=10, hAlign='LEFT'))

        # Compliance box with teal border
        compliance_items = [
            ["Standard", "Description"],
            ["DICOM PS3.15", "Basic Application Level Confidentiality Profile"],
            ["HIPAA Safe Harbor", "45 CFR 164.514(b)(2) De-identification Method"],
            ["Saudi PDPL", "Personal Data Protection Law Requirements"],
        ]
        
        compliance_table = Table(compliance_items, colWidths=[1.8 * inch, 4.3 * inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_TEAL),
            ('TEXTCOLOR', (0, 0), (-1, 0), BRAND_WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), BRAND_NAVY),
            ('BACKGROUND', (0, 1), (-1, -1), BRAND_TEAL_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, BRAND_TEAL),
            ('LINEBELOW', (0, 0), (-1, 0), 2, BRAND_GOLD),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(compliance_table)
        story.append(Spacer(1, 0.15 * inch))

        compliance_text = """
        <font color="#1A365D">The de-identification process has modified or removed all patient identifying
        information as specified in the selected preset configuration. Original UIDs have
        been replaced with new, consistent identifiers to maintain referential integrity
        while preventing re-identification.</font>
        """
        story.append(Paragraph(compliance_text, self.styles["Normal"]))
        story.append(Spacer(1, 0.4 * inch))

    def _add_signature(self, story, report_data: ReportData):
        """Add THAKAAMED branded digital signature section."""
        story.append(Paragraph("🔐 DIGITAL SIGNATURE", self.styles["SectionHeader"]))
        story.append(HRFlowable(width="30%", thickness=2, color=BRAND_GOLD, spaceBefore=0, spaceAfter=10, hAlign='LEFT'))

        hash_display = report_data.report_hash[:32] + "..." if report_data.report_hash else "N/A"
        
        sig_data = [
            ["Report Hash (SHA-256)", hash_display],
            ["Generated by", f"THAKAAMED DICOM Anonymizer v{report_data.generator_version}"],
            ["Report ID", report_data.report_id],
        ]
        
        sig_table = Table(sig_data, colWidths=[2 * inch, 4.5 * inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), BRAND_TEAL),
            ('TEXTCOLOR', (1, 0), (1, -1), BRAND_NAVY),
            ('BACKGROUND', (0, 0), (-1, -1), BRAND_GRAY_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, BRAND_TEAL),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(sig_table)
        
        # Vision 2030 closing
        story.append(Spacer(1, 0.5 * inch))
        story.append(HRFlowable(width="100%", thickness=2, color=BRAND_GOLD, spaceBefore=0, spaceAfter=15, hAlign='CENTER'))
        
        # Final branded footer - Purple theme
        story.append(Paragraph(
            "<font color='#2D1B4E' size='14'><b>THAKAAMED AI</b></font>",
            ParagraphStyle('BrandFooter', alignment=TA_CENTER)
        ))
        story.append(Paragraph(
            "<font color='#9B8BB8' size='9'>Enterprise Healthcare Solutions</font>",
            ParagraphStyle('BrandFooterSub', alignment=TA_CENTER)
        ))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(
            "<font color='#006C35' size='10'><b>Supporting Saudi Vision 2030 Healthcare Transformation</b></font>",
            ParagraphStyle('Vision2030Footer', alignment=TA_CENTER)
        ))
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph(
            "<font color='#C9A227' size='9'><b>Made with ♥ in Riyadh</b></font>",
            ParagraphStyle('MadeWithLove', alignment=TA_CENTER)
        ))
        story.append(Spacer(1, 0.05 * inch))
        story.append(Paragraph(
            "<font color='#9B8BB8' size='8'>https://thakaamed.ai | contact@thakaamed.com</font>",
            ParagraphStyle('ContactInfo', alignment=TA_CENTER)
        ))
