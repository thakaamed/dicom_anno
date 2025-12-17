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
"""THAKAAMED brand styling for the web GUI."""

# Brand Colors - Dark Purple / Lavender Theme
BRAND_PRIMARY = "#4a1d6e"     # Deep purple
BRAND_ACCENT = "#7c3aed"      # Vibrant purple
BRAND_LAVENDER = "#c4b5fd"    # Soft lavender
BRAND_DARK = "#1e0a2e"        # Very dark purple for backgrounds
BRAND_LIGHT = "#f5f3ff"       # Light lavender tint
BRAND_CARD = "#faf8ff"        # Soft off-white with purple tint
BRAND_SUCCESS = "#22c55e"     # Green for buttons/success states

# Typography
FONT_HEADING = "'Outfit', 'Inter', system-ui, sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', system-ui, sans-serif"

# CSS for the application
APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --brand-primary: #4a1d6e;
    --brand-accent: #7c3aed;
    --brand-lavender: #c4b5fd;
    --brand-dark: #1e0a2e;
    --brand-light: #f5f3ff;
    --brand-card: #faf8ff;
    --brand-success: #22c55e;
    --brand-white: #ffffff;
}

body {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    background: linear-gradient(145deg, #0f051a 0%, var(--brand-dark) 30%, #2d1550 70%, #1e0a2e 100%);
    min-height: 100vh;
}

.app-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

.header-logo {
    width: 160px;
    height: auto;
    filter: drop-shadow(0 4px 20px rgba(124, 58, 237, 0.4));
}

.main-title {
    font-family: 'Outfit', system-ui, sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--brand-lavender) 0%, #e9d5ff 50%, #ffffff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    margin: 0;
    letter-spacing: -0.5px;
}

.subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 400;
    color: var(--brand-lavender);
    margin-top: 0.5rem;
    letter-spacing: 0.3px;
    opacity: 0.9;
}

.card {
    background: var(--brand-card);
    border-radius: 20px;
    box-shadow: 
        0 20px 60px rgba(74, 29, 110, 0.25),
        0 0 0 1px rgba(196, 181, 253, 0.1);
    padding: 2.5rem;
    margin-top: 2rem;
    backdrop-filter: blur(10px);
}

.upload-zone {
    border: 2px dashed var(--brand-accent);
    border-radius: 16px;
    background: linear-gradient(135deg, var(--brand-light) 0%, #ede9fe 100%);
    padding: 3rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.upload-zone:hover {
    border-color: var(--brand-primary);
    background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(124, 58, 237, 0.2);
}

.upload-zone.dragover {
    border-color: var(--brand-success);
    background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
    transform: scale(1.02);
}

.upload-icon {
    font-size: 4rem;
    color: var(--brand-accent);
    margin-bottom: 1rem;
}

.upload-text {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--brand-primary);
    margin-bottom: 0.5rem;
}

.upload-hint {
    font-size: 0.95rem;
    color: #6b7280;
}

.preset-selector {
    margin-top: 1.5rem;
}

.preset-option {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.preset-option:hover {
    border-color: var(--brand-accent);
    background: var(--brand-light);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.12);
}

.preset-option.selected {
    border-color: var(--brand-accent);
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.25);
}

.preset-title {
    font-weight: 700;
    color: var(--brand-primary);
    font-size: 1.1rem;
}

.preset-desc {
    font-size: 0.9rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

.anonymize-btn {
    background: linear-gradient(135deg, var(--brand-success) 0%, #16a34a 100%);
    color: white;
    font-family: 'Inter', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    padding: 1rem 3rem;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 6px 24px rgba(34, 197, 94, 0.35);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.anonymize-btn:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(34, 197, 94, 0.45);
    background: linear-gradient(135deg, #16a34a 0%, var(--brand-success) 100%);
}

.anonymize-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
    box-shadow: none;
}

.progress-section {
    margin-top: 1.5rem;
}

.file-list {
    max-height: 200px;
    overflow-y: auto;
    background: var(--brand-light);
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1rem;
    border: 1px solid #e5e7eb;
}

.file-item {
    display: flex;
    align-items: center;
    padding: 0.6rem;
    border-bottom: 1px solid #e5e7eb;
}

.file-item:last-child {
    border-bottom: none;
}

.file-icon {
    color: var(--brand-accent);
    margin-right: 0.75rem;
}

.file-name {
    flex: 1;
    font-size: 0.9rem;
    color: #374151;
    font-weight: 500;
}

.file-size {
    font-size: 0.8rem;
    color: #9ca3af;
}

.results-card {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 2px solid var(--brand-success);
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
}

.success-icon {
    font-size: 3rem;
    color: var(--brand-success);
}

.download-btn {
    background: linear-gradient(135deg, var(--brand-accent) 0%, var(--brand-primary) 100%);
    color: white;
    font-weight: 600;
    padding: 0.85rem 2.5rem;
    border-radius: 30px;
    border: none;
    cursor: pointer;
    transition: all 0.25s ease;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.3);
}

.download-btn:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4);
}

.footer {
    text-align: center;
    margin-top: 3rem;
    padding: 1.5rem;
    color: var(--brand-lavender);
    font-size: 0.9rem;
    opacity: 0.85;
}

.footer a {
    color: #e9d5ff;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
}

.footer a:hover {
    color: white;
    text-decoration: underline;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.stat-item {
    text-align: center;
    padding: 1.25rem;
    background: white;
    border-radius: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #f3f4f6;
}

.stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--brand-primary);
}

.stat-label {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 0.3rem;
    font-weight: 500;
}

/* Custom scrollbar for purple theme */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--brand-light);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: var(--brand-lavender);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--brand-accent);
}
"""
