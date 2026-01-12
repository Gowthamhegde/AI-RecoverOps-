# AI-RecoverOps Universal Installer for Windows
# PowerShell script for easy installation

param(
    [switch]$Help,
    [switch]$Uninstall,
    [switch]$Update,
    [switch]$Dev
)

# Configuration
$RepoUrl = "https://github.com/ai-recoverops/ai-recoverops"
$Version = "1.0.0"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Step($Message) {
    Write-ColorOutput Blue "[STEP] $Message"
}

function Write-Success($Message) {
    Write-ColorOutput Green "[SUCCESS] $Message"
}

function Write-Warning($Message) {
    Write-ColorOutput Yellow "[WARNING] $Message"
}

function Write-Error($Message) {
    Write-ColorOutput Red "[ERROR] $Message"
}

function Print-Banner {
    Write-ColorOutput Cyan @"
==============================================
🚀 AI-RecoverOps Universal Installer v$Version
   DevOps Automation Platform
==============================================
"@
}

function Check-Requirements {
    Write-Step "Checking system requirements..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Success "Python found: $pythonVersion"
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Error "Python 3.8+ is required but not found"
        Write-Output "Please install Python from https://python.org"
        Write-Output "Make sure to check 'Add Python to PATH' during installation"
        exit 1
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>$null
        if ($pipVersion) {
            Write-Success "pip found"
        } else {
            throw "pip not found"
        }
    } catch {
        Write-Error "pip is required but not found"
        Write-Output "Please reinstall Python with pip included"
        exit 1
    }
    
    # Check git (optional)
    try {
        $gitVersion = git --version 2>$null
        if ($gitVersion) {
            Write-Success "Git found: $gitVersion"
            $script:HasGit = $true
        } else {
            throw "Git not found"
        }
    } catch {
        Write-Warning "Git not found - will use alternative installation method"
        $script:HasGit = $false
    }
    
    # Check Node.js (optional)
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-Success "Node.js found: $nodeVersion"
            $script:HasNode = $true
        } else {
            throw "Node.js not found"
        }
    } catch {
        Write-Warning "Node.js not found - dashboard features will be limited"
        $script:HasNode = $false
    }
    
    # Check if running as Administrator
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if ($isAdmin) {
        Write-Warning "Running as Administrator - this may cause permission issues"
        $response = Read-Host "Continue anyway? (y/N)"
        if ($response -notmatch '^[Yy]$') {
            exit 1
        }
    }
}

function Install-AIOps {
    Write-Step "Installing AI-RecoverOps..."
    
    try {
        # Try pip install first
        $result = pip install ai-recoverops 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "AI-RecoverOps installed via pip"
        } else {
            throw "pip install failed"
        }
    } catch {
        Write-Warning "pip install failed, trying alternative method..."
        
        if ($script:HasGit) {
            # Clone and install from source
            $installDir = "$env:USERPROFILE\.ai-recoverops"
            
            if (Test-Path $installDir) {
                Remove-Item -Recurse -Force $installDir
            }
            
            git clone $RepoUrl $installDir
            Set-Location $installDir
            pip install -e .
            Write-Success "AI-RecoverOps installed from source"
        } else {
            Write-Error "Installation failed - please install git or use pip directly"
            exit 1
        }
    }
}

function Setup-Environment {
    Write-Step "Setting up environment..."
    
    # Add Python Scripts to PATH if not already there
    $pythonScripts = python -c "import site; print(site.USER_BASE + '\\Scripts')" 2>$null
    
    if ($pythonScripts -and (Test-Path $pythonScripts)) {
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        
        if ($currentPath -notlike "*$pythonScripts*") {
            $newPath = "$currentPath;$pythonScripts"
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            Write-Success "Added Python Scripts to PATH"
            
            # Update current session PATH
            $env:PATH += ";$pythonScripts"
        }
    }
}

function Create-Shortcuts {
    Write-Step "Creating shortcuts..."
    
    try {
        # Create desktop shortcut
        $desktopPath = [Environment]::GetFolderPath("Desktop")
        $shortcutPath = "$desktopPath\AI-RecoverOps.lnk"
        
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-Command aiops dashboard"
        $shortcut.WorkingDirectory = $env:USERPROFILE
        $shortcut.Description = "AI-RecoverOps Dashboard"
        $shortcut.Save()
        
        Write-Success "Desktop shortcut created"
    } catch {
        Write-Warning "Could not create desktop shortcut: $_"
    }
    
    try {
        # Create Start Menu shortcut
        $startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
        $startShortcutPath = "$startMenuPath\AI-RecoverOps.lnk"
        
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($startShortcutPath)
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-Command aiops dashboard"
        $shortcut.WorkingDirectory = $env:USERPROFILE
        $shortcut.Description = "AI-RecoverOps Dashboard"
        $shortcut.Save()
        
        Write-Success "Start Menu shortcut created"
    } catch {
        Write-Warning "Could not create Start Menu shortcut: $_"
    }
}

function Install-Dashboard {
    if ($script:HasNode) {
        Write-Step "Installing dashboard dependencies..."
        
        $dashboardDir = "$env:USERPROFILE\.ai-recoverops\dashboard"
        if (Test-Path $dashboardDir) {
            Set-Location $dashboardDir
            try {
                npm install
                Write-Success "Dashboard dependencies installed"
            } catch {
                Write-Warning "Dashboard installation failed - dashboard features will be limited"
            }
        } else {
            Write-Warning "Dashboard source not found - using API-only mode"
        }
    }
}

function Verify-Installation {
    Write-Step "Verifying installation..."
    
    # Refresh PATH for current session
    $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")
    
    # Test aiops command
    try {
        $versionOutput = aiops version 2>$null
        if ($versionOutput) {
            Write-Success "aiops command available"
        } else {
            throw "aiops command not found"
        }
    } catch {
        Write-Error "aiops command not found in PATH"
        Write-Output "Try restarting your terminal or running: refreshenv"
        exit 1
    }
    
    # Test Python import
    try {
        python -c "import ai_recoverops; print('✅ Python module import successful')" 2>$null
        Write-Success "Python module import successful"
    } catch {
        Write-Warning "Python module import failed - some features may not work"
    }
}

function Show-NextSteps {
    Write-Output ""
    Write-ColorOutput Green "🎉 Installation completed successfully!"
    Write-Output ""
    Write-ColorOutput Cyan "Next steps:"
    Write-Output "1. Restart your terminal or run: refreshenv"
    Write-Output "2. Initialize a new project: aiops init my-project"
    Write-Output "3. Configure your infrastructure: notepad aiops.yml"
    Write-Output "4. Start monitoring: aiops deploy"
    Write-Output ""
    Write-ColorOutput Cyan "Quick start:"
    Write-Output "  aiops init my-web-app     # Initialize project"
    Write-Output "  aiops scan                # Scan infrastructure"
    Write-Output "  aiops deploy              # Deploy monitoring"
    Write-Output "  aiops status              # Check status"
    Write-Output ""
    Write-ColorOutput Cyan "Documentation:"
    Write-Output "  📖 User Guide: https://docs.ai-recoverops.com"
    Write-Output "  🚀 Examples: https://github.com/ai-recoverops/examples"
    Write-Output "  💬 Community: https://discord.gg/ai-recoverops"
    Write-Output ""
    Write-ColorOutput Cyan "Access Points (after deployment):"
    Write-Output "  📊 Dashboard: http://localhost:3000"
    Write-Output "  🔧 API: http://localhost:8000"
    Write-Output "  📖 API Docs: http://localhost:8000/docs"
}

function Uninstall-AIOps {
    Write-Step "Uninstalling AI-RecoverOps..."
    
    try {
        pip uninstall -y ai-recoverops
        
        # Remove shortcuts
        $desktopShortcut = "$([Environment]::GetFolderPath('Desktop'))\AI-RecoverOps.lnk"
        $startMenuShortcut = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\AI-RecoverOps.lnk"
        
        if (Test-Path $desktopShortcut) {
            Remove-Item $desktopShortcut
        }
        
        if (Test-Path $startMenuShortcut) {
            Remove-Item $startMenuShortcut
        }
        
        # Remove installation directory
        $installDir = "$env:USERPROFILE\.ai-recoverops"
        if (Test-Path $installDir) {
            Remove-Item -Recurse -Force $installDir
        }
        
        Write-Success "AI-RecoverOps uninstalled"
    } catch {
        Write-Error "Uninstallation failed: $_"
        exit 1
    }
}

function Update-AIOps {
    Write-Step "Updating AI-RecoverOps..."
    
    try {
        pip install --upgrade ai-recoverops
        Write-Success "AI-RecoverOps updated"
    } catch {
        Write-Error "Update failed: $_"
        exit 1
    }
}

function Install-DevVersion {
    Write-Step "Installing development version..."
    
    try {
        pip install --upgrade git+https://github.com/ai-recoverops/ai-recoverops.git
        Write-Success "Development version installed"
    } catch {
        Write-Error "Development installation failed: $_"
        exit 1
    }
}

# Main execution
if ($Help) {
    Write-Output "AI-RecoverOps Universal Installer for Windows"
    Write-Output ""
    Write-Output "Usage: .\install.ps1 [options]"
    Write-Output ""
    Write-Output "Options:"
    Write-Output "  -Help           Show this help message"
    Write-Output "  -Uninstall      Uninstall AI-RecoverOps"
    Write-Output "  -Update         Update to latest version"
    Write-Output "  -Dev            Install development version"
    Write-Output ""
    exit 0
}

if ($Uninstall) {
    Uninstall-AIOps
    exit 0
}

if ($Update) {
    Update-AIOps
    exit 0
}

if ($Dev) {
    Install-DevVersion
    exit 0
}

# Main installation
Print-Banner
Check-Requirements
Install-AIOps
Setup-Environment
Create-Shortcuts
Install-Dashboard
Verify-Installation
Show-NextSteps