#!/bin/bash
# AI-RecoverOps Universal Installer
# Works on Linux, macOS, and Windows (via WSL/Git Bash)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/ai-recoverops/ai-recoverops"
INSTALL_DIR="$HOME/.ai-recoverops"
BIN_DIR="$HOME/.local/bin"
VERSION="1.0.0"

# Functions
print_banner() {
    echo -e "${CYAN}"
    echo "=============================================="
    echo "🚀 AI-RecoverOps Universal Installer v$VERSION"
    echo "   DevOps Automation Platform"
    echo "=============================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.8+ is required but not found"
        echo "Please install Python from https://python.org"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is required but not found"
        echo "Please install pip3"
        exit 1
    fi
    
    # Check git (optional)
    if command -v git &> /dev/null; then
        print_success "Git found"
        HAS_GIT=true
    else
        print_warning "Git not found - will use alternative installation method"
        HAS_GIT=false
    fi
    
    # Check Node.js (optional for dashboard)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
        HAS_NODE=true
    else
        print_warning "Node.js not found - dashboard features will be limited"
        HAS_NODE=false
    fi
}

install_aiops() {
    print_step "Installing AI-RecoverOps..."
    
    # Create directories
    mkdir -p "$BIN_DIR"
    mkdir -p "$INSTALL_DIR"
    
    # Install via pip
    if pip3 install ai-recoverops; then
        print_success "AI-RecoverOps installed via pip"
    else
        print_warning "pip install failed, trying alternative method..."
        
        # Alternative: clone and install
        if [ "$HAS_GIT" = true ]; then
            cd "$INSTALL_DIR"
            git clone "$REPO_URL" .
            pip3 install -e .
            print_success "AI-RecoverOps installed from source"
        else
            print_error "Installation failed - please install git or use pip directly"
            exit 1
        fi
    fi
}

setup_shell_integration() {
    print_step "Setting up shell integration..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    case "$SHELL_NAME" in
        bash)
            SHELL_RC="$HOME/.bashrc"
            ;;
        zsh)
            SHELL_RC="$HOME/.zshrc"
            ;;
        fish)
            SHELL_RC="$HOME/.config/fish/config.fish"
            ;;
        *)
            SHELL_RC="$HOME/.profile"
            ;;
    esac
    
    # Add to PATH if not already there
    if ! echo "$PATH" | grep -q "$BIN_DIR"; then
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
        print_success "Added $BIN_DIR to PATH in $SHELL_RC"
    fi
    
    # Add completion (if supported)
    if command -v aiops &> /dev/null; then
        case "$SHELL_NAME" in
            bash)
                echo 'eval "$(_AIOPS_COMPLETE=bash_source aiops)"' >> "$SHELL_RC"
                ;;
            zsh)
                echo 'eval "$(_AIOPS_COMPLETE=zsh_source aiops)"' >> "$SHELL_RC"
                ;;
        esac
        print_success "Shell completion configured"
    fi
}

create_desktop_entry() {
    print_step "Creating desktop integration..."
    
    # Create .desktop file (Linux)
    if [ -d "$HOME/.local/share/applications" ]; then
        cat > "$HOME/.local/share/applications/ai-recoverops.desktop" << EOF
[Desktop Entry]
Name=AI-RecoverOps
Comment=Universal DevOps Automation Platform
Exec=aiops dashboard
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=Development;System;
EOF
        print_success "Desktop entry created"
    fi
}

install_dashboard() {
    if [ "$HAS_NODE" = true ]; then
        print_step "Installing dashboard dependencies..."
        
        # Check if dashboard directory exists
        DASHBOARD_DIR="$INSTALL_DIR/dashboard"
        if [ -d "$DASHBOARD_DIR" ]; then
            cd "$DASHBOARD_DIR"
            if npm install; then
                print_success "Dashboard dependencies installed"
            else
                print_warning "Dashboard installation failed - dashboard features will be limited"
            fi
        else
            print_warning "Dashboard source not found - using API-only mode"
        fi
    fi
}

verify_installation() {
    print_step "Verifying installation..."
    
    # Test aiops command
    if command -v aiops &> /dev/null; then
        VERSION_OUTPUT=$(aiops version 2>/dev/null || echo "unknown")
        print_success "aiops command available: $VERSION_OUTPUT"
    else
        print_error "aiops command not found in PATH"
        echo "Try running: export PATH=\"$BIN_DIR:\$PATH\""
        exit 1
    fi
    
    # Test Python import
    if python3 -c "import ai_recoverops; print('✅ Python module import successful')" 2>/dev/null; then
        print_success "Python module import successful"
    else
        print_warning "Python module import failed - some features may not work"
    fi
}

show_next_steps() {
    echo
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo
    echo -e "${CYAN}Next steps:${NC}"
    echo "1. Restart your terminal or run: source $SHELL_RC"
    echo "2. Initialize a new project: ${YELLOW}aiops init my-project${NC}"
    echo "3. Configure your infrastructure: ${YELLOW}vim aiops.yml${NC}"
    echo "4. Start monitoring: ${YELLOW}aiops deploy${NC}"
    echo
    echo -e "${CYAN}Quick start:${NC}"
    echo "  ${YELLOW}aiops init my-web-app${NC}     # Initialize project"
    echo "  ${YELLOW}aiops scan${NC}                # Scan infrastructure"
    echo "  ${YELLOW}aiops deploy${NC}              # Deploy monitoring"
    echo "  ${YELLOW}aiops status${NC}              # Check status"
    echo
    echo -e "${CYAN}Documentation:${NC}"
    echo "  📖 User Guide: https://docs.ai-recoverops.com"
    echo "  🚀 Examples: https://github.com/ai-recoverops/examples"
    echo "  💬 Community: https://discord.gg/ai-recoverops"
    echo
    echo -e "${CYAN}Access Points (after deployment):${NC}"
    echo "  📊 Dashboard: http://localhost:3000"
    echo "  🔧 API: http://localhost:8000"
    echo "  📖 API Docs: http://localhost:8000/docs"
}

# Main installation flow
main() {
    print_banner
    
    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root is not recommended"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    check_requirements
    install_aiops
    setup_shell_integration
    create_desktop_entry
    install_dashboard
    verify_installation
    show_next_steps
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "AI-RecoverOps Universal Installer"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h          Show this help message"
        echo "  --uninstall         Uninstall AI-RecoverOps"
        echo "  --update            Update to latest version"
        echo "  --dev               Install development version"
        echo
        exit 0
        ;;
    --uninstall)
        print_step "Uninstalling AI-RecoverOps..."
        pip3 uninstall -y ai-recoverops
        rm -rf "$INSTALL_DIR"
        rm -f "$HOME/.local/share/applications/ai-recoverops.desktop"
        print_success "AI-RecoverOps uninstalled"
        exit 0
        ;;
    --update)
        print_step "Updating AI-RecoverOps..."
        pip3 install --upgrade ai-recoverops
        print_success "AI-RecoverOps updated"
        exit 0
        ;;
    --dev)
        print_step "Installing development version..."
        pip3 install --upgrade git+https://github.com/ai-recoverops/ai-recoverops.git
        print_success "Development version installed"
        exit 0
        ;;
    "")
        # No arguments, run main installation
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac