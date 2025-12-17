#!/bin/bash
# ============================================================================
#  THAKAAMED DICOM Anonymizer - Easy Installer for macOS
#  Copyright (c) 2025 THAKAAMED AI. All rights reserved.
#
#  https://thakaamed.ai | Enterprise Healthcare Solutions
#
#  This installer sets up everything needed to run the DICOM Anonymizer
#  on a Mac without requiring Xcode or technical knowledge.
#
#  Usage: curl -LsSf https://thakaamed.com/dicom/install.sh | bash
#  Or:    bash install.sh
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
APP_NAME="THAKAAMED DICOM Anonymizer"
INSTALL_DIR="$HOME/.thakaamed-dicom"
VENV_DIR="$INSTALL_DIR/venv"
LAUNCHER_NAME="THAKAAMED DICOM.command"
DESKTOP_PATH="$HOME/Desktop/$LAUNCHER_NAME"

# DICOM folders
DICOM_INPUT="$HOME/DICOM_Input"
DICOM_OUTPUT="$HOME/DICOM_Anonymized"

# Detect script directory (for local install) or use current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Print banner
print_banner() {
    echo ""
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                        ║"
    echo "║  ████████╗██╗  ██╗ █████╗ ██╗  ██╗ █████╗  █████╗    ███╗   ███╗       ║"
    echo "║  ╚══██╔══╝██║  ██║██╔══██╗██║ ██╔╝██╔══██╗██╔══██╗   ████╗ ████║       ║"
    echo "║     ██║   ███████║███████║█████╔╝ ███████║███████║   ██╔████╔██║       ║"
    echo "║     ██║   ██╔══██║██╔══██║██╔═██╗ ██╔══██║██╔══██║   ██║╚██╔╝██║       ║"
    echo "║     ██║   ██║  ██║██║  ██║██║  ██╗██║  ██║██║  ██║   ██║ ╚═╝ ██║       ║"
    echo "║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝     ╚═╝       ║"
    echo "║                                                                        ║"
    echo "║                    DICOM Anonymizer Installer                          ║"
    echo "║                Supporting Saudi Vision 2030 Healthcare                 ║"
    echo "║                                                                        ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Print step
print_step() {
    local step=$1
    local total=$2
    local message=$3
    echo -e "${CYAN}[$step/$total]${NC} $message"
}

# Print success
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Print error
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running on macOS
check_macos() {
    if [[ "$(uname)" != "Darwin" ]]; then
        print_error "This installer is for macOS only."
        print_warning "For other operating systems, please install manually:"
        echo "    pip install thakaamed-dicom"
        exit 1
    fi
}

# Check architecture
check_arch() {
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        echo -e "  ${CYAN}→${NC} Detected Apple Silicon (M1/M2/M3/M4)"
    else
        echo -e "  ${CYAN}→${NC} Detected Intel Mac"
    fi
}

# Install uv (fast Python package manager)
install_uv() {
    print_step 1 5 "Installing Python runtime..."
    
    if command -v uv &> /dev/null; then
        print_success "uv is already installed"
    else
        echo "  Downloading uv (fast Python package manager)..."
        curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null
        
        # Add uv to PATH for this session
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        
        if command -v uv &> /dev/null; then
            print_success "uv installed successfully"
        else
            print_error "Failed to install uv"
            exit 1
        fi
    fi
    
    check_arch
}

# Clear Python cache to prevent stale bytecode issues
clear_python_cache() {
    echo "  Clearing Python cache..."
    
    # Clear cache in project directory if it exists
    if [[ -d "$PROJECT_DIR/src" ]]; then
        find "$PROJECT_DIR/src" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find "$PROJECT_DIR/src" -type f -name "*.pyc" -delete 2>/dev/null || true
    fi
    
    # Clear cache in installed packages
    if [[ -d "$VENV_DIR" ]]; then
        find "$VENV_DIR" -type d -name "__pycache__" -path "*thakaamed*" -exec rm -rf {} + 2>/dev/null || true
    fi
    
    print_success "Python cache cleared"
}

# Create virtual environment and install package
install_package() {
    print_step 2 5 "Installing DICOM Anonymizer..."
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Ensure uv is in PATH
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    
    # Clear any existing cache first to prevent stale bytecode issues
    clear_python_cache
    
    # Check if we're running from the project directory
    if [[ -f "$PROJECT_DIR/pyproject.toml" ]]; then
        echo "  Installing from local project..."
        
        # Create venv with Python 3.11
        uv venv "$VENV_DIR" --python 3.11 2>/dev/null || uv venv "$VENV_DIR" --python 3.10
        
        # Install the package with force reinstall to ensure fresh install
        source "$VENV_DIR/bin/activate"
        uv pip install "$PROJECT_DIR" --force-reinstall --no-deps
        uv pip install "$PROJECT_DIR"  # Install deps normally
        deactivate
        
        print_success "Package installed from local source"
    else
        # Install from PyPI or URL (for hosted distribution)
        echo "  Creating Python environment..."
        uv venv "$VENV_DIR" --python 3.11 2>/dev/null || uv venv "$VENV_DIR" --python 3.10
        
        source "$VENV_DIR/bin/activate"
        
        # Try to install from a wheel if available in the same directory
        if ls "$SCRIPT_DIR"/*.whl 1> /dev/null 2>&1; then
            echo "  Installing from wheel..."
            uv pip install "$SCRIPT_DIR"/*.whl
        else
            print_warning "No local package found."
            echo "  Please ensure you have the package files or install manually."
            exit 1
        fi
        
        deactivate
        print_success "Package installed"
    fi
}

# Create DICOM folders
create_dicom_folders() {
    print_step 3 5 "Creating DICOM folders..."
    
    # Create input folder
    mkdir -p "$DICOM_INPUT"
    print_success "Input folder: $DICOM_INPUT"
    
    # Create output folder
    mkdir -p "$DICOM_OUTPUT"
    print_success "Output folder: $DICOM_OUTPUT"
}

# Create desktop launcher
create_launcher() {
    print_step 4 5 "Creating desktop launcher..."
    
    # Create the .command file
    cat > "$DESKTOP_PATH" << 'LAUNCHER_EOF'
#!/bin/bash
# THAKAAMED DICOM Anonymizer Launcher
# Double-click this file to start the application

# Configuration
INSTALL_DIR="$HOME/.thakaamed-dicom"
VENV_DIR="$INSTALL_DIR/venv"

# Ensure PATH includes common locations
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Clear terminal and show startup message
clear
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     🏥 THAKAAMED DICOM Anonymizer                         ║"
echo "║     Starting... please wait                               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
if [[ -f "$VENV_DIR/bin/activate" ]]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Error: Installation not found. Please reinstall."
    echo "Press any key to close..."
    read -n 1
    exit 1
fi

# Clear Python cache to prevent stale bytecode issues
# This ensures the latest code is always used
echo "Clearing cache..."
find "$INSTALL_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
# Also clear cache in editable install source if it exists
EDITABLE_PATH=$(python -c "import thakaamed_dicom; print(thakaamed_dicom.__file__)" 2>/dev/null | xargs dirname 2>/dev/null)
if [[ -n "$EDITABLE_PATH" && -d "$EDITABLE_PATH" ]]; then
    find "$EDITABLE_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
fi

# Launch the GUI
echo "Opening in your browser..."
echo ""
echo "📁 Input folder:  ~/DICOM_Input"
echo "📂 Output folder: ~/DICOM_Anonymized"
echo ""
echo "Press Ctrl+C to stop the application."
echo ""

thakaamed-dicom-gui

# Keep window open on error
if [[ $? -ne 0 ]]; then
    echo ""
    echo "Application closed with an error."
    echo "Press any key to close this window..."
    read -n 1
fi
LAUNCHER_EOF

    # Make it executable
    chmod +x "$DESKTOP_PATH"
    
    # Try to set a custom icon (optional, may fail silently)
    if [[ -f "$PROJECT_DIR/thakaamed_logos/thakaa_logo_1024.png" ]]; then
        ICON_DIR="$INSTALL_DIR/icons"
        mkdir -p "$ICON_DIR"
        sips -s format icns "$PROJECT_DIR/thakaamed_logos/thakaa_logo_1024.png" --out "$ICON_DIR/app.icns" 2>/dev/null || true
    fi
    
    print_success "Desktop launcher created"
}

# Launch the application
launch_app() {
    print_step 5 5 "Launching application..."
    
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ Installation Complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${BOLD}How to use:${NC}"
    echo ""
    echo -e "  ${CYAN}1.${NC} Put your DICOM files in:  ${PURPLE}~/DICOM_Input${NC}"
    echo -e "  ${CYAN}2.${NC} Open the web interface (see below)"
    echo -e "  ${CYAN}3.${NC} Select anonymization type"
    echo -e "  ${CYAN}4.${NC} Click ${GREEN}ANONYMIZE${NC}"
    echo -e "  ${CYAN}5.${NC} Find anonymized files in: ${PURPLE}~/DICOM_Anonymized${NC}"
    echo ""
    echo -e "  ${BOLD}To start the anonymizer:${NC}"
    echo -e "    • Double-click \"${PURPLE}THAKAAMED DICOM${NC}\" on your Desktop"
    echo ""
    echo -e "  ${BOLD}Or from Terminal:${NC}"
    echo -e "    • Run: ${CYAN}thakaamed-dicom-gui${NC}"
    echo ""
    echo -e "  ${PURPLE}Built for Saudi Vision 2030 Healthcare${NC}"
    echo -e "  ${CYAN}https://thakaamed.ai${NC}"
    echo ""
    
    # Ask if user wants to launch now
    read -p "  Launch the application now? [Y/n] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo ""
        echo "  Opening in your browser..."
        
        # Add venv to PATH and launch
        export PATH="$VENV_DIR/bin:$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        source "$VENV_DIR/bin/activate"
        
        # Open Finder to input folder so user can add files
        open "$DICOM_INPUT"
        
        # Open browser in background
        (sleep 2 && open "http://127.0.0.1:8080") &
        
        thakaamed-dicom-gui
    else
        echo ""
        echo -e "  ${CYAN}To launch later, double-click 'THAKAAMED DICOM' on your Desktop.${NC}"
        echo ""
    fi
}

# Main installation flow
main() {
    print_banner
    
    echo -e "${BOLD}Installing $APP_NAME...${NC}"
    echo ""
    
    check_macos
    install_uv
    install_package
    create_dicom_folders
    create_launcher
    launch_app
}

# Run main
main "$@"
