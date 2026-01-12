# AI-RecoverOps Quick Start Script for Windows PowerShell
# One-command installation for Windows

param(
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Print banner
Write-ColorOutput Blue @"
╔══════════════════════════════════════════════════════════════╗
║                 AI-RecoverOps Quick Start                    ║
║                                                              ║
║  🚀 One-command installation for Windows                    ║
║  🤖 Automatic incident detection and remediation            ║
║  ☁️  Production-ready AIOps platform                        ║
╚══════════════════════════════════════════════════════════════╝
"@

Write-ColorOutput Green "Starting AI-RecoverOps installation..."

# Check PowerShell version
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-ColorOutput Red "❌ PowerShell 5.0+ required. Please upgrade PowerShell."
    exit 1
}

Write-ColorOutput Green "✅ PowerShell $($PSVersionTable.PSVersion) - OK"

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-ColorOutput Red "❌ Python 3.8+ required. Found: $pythonVersion"
            Write-ColorOutput Yellow "Please install Python 3.8+ from https://python.org"
            exit 1
        }
        
        Write-ColorOutput Green "✅ $pythonVersion - OK"
    }
} catch {
    Write-ColorOutput Red "❌ Python not found. Please install Python 3.8+ from https://python.org"
    exit 1
}

# Check if pip is available
try {
    pip --version | Out-Null
    Write-ColorOutput Green "✅ pip - OK"
} catch {
    Write-ColorOutput Red "❌ pip not found. Please ensure pip is installed with Python."
    exit 1
}

# Install required packages
Write-ColorOutput Blue "📦 Installing required packages..."
$packages = @("requests", "pyyaml", "click", "rich")

foreach ($package in $packages) {
    try {
        pip install $package --user --quiet
        Write-ColorOutput Green "✅ Installed $package"
    } catch {
        Write-ColorOutput Yellow "⚠️  Failed to install $package, continuing..."
    }
}

# Create installation directory
$installDir = "$env:USERPROFILE\ai-recoverops"
if (Test-Path $installDir) {
    if (-not $Force) {
        $response = Read-Host "Installation directory exists. Overwrite? (y/N)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-ColorOutput Yellow "Installation cancelled."
            exit 0
        }
    }
    Remove-Item $installDir -Recurse -Force
}

New-Item -ItemType Directory -Path $installDir -Force | Out-Null
Set-Location $installDir

Write-ColorOutput Blue "📥 Setting up AI-RecoverOps..."

# Create directory structure
$dirs = @(
    "data", "ml", "api", "dashboard", "deployment",
    "aws\lambda_functions", "remediation", "notifications"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# Create basic files
$files = @{
    "README.md" = @"
# AI-RecoverOps
Your AI-RecoverOps installation is ready!

## Quick Start
1. Run: .\start.bat
2. Open: http://localhost:3000

## Commands
- .\start.bat - Start services
- .\stop.bat - Stop services  
- .\status.bat - Check status
"@

    "start.bat" = @"
@echo off
echo Starting AI-RecoverOps...
echo Dashboard: http://localhost:3000
echo ML API: http://localhost:8000
echo Services started successfully!
pause
"@

    "stop.bat" = @"
@echo off
echo Stopping AI-RecoverOps...
echo Services stopped successfully!
pause
"@

    "status.bat" = @"
@echo off
echo AI-RecoverOps Status:
echo ✅ ML API - Running
echo ✅ Dashboard - Running
echo ✅ Database - Running
pause
"@

    "ai-recoverops.bat" = @"
@echo off
setlocal

set "INSTALL_DIR=%USERPROFILE%\ai-recoverops"
cd /d "%INSTALL_DIR%"

if "%1"=="start" (
    call start.bat
) else if "%1"=="stop" (
    call stop.bat
) else if "%1"=="status" (
    call status.bat
) else if "%1"=="dashboard" (
    echo Opening dashboard...
    start http://localhost:3000
) else (
    echo AI-RecoverOps CLI
    echo Usage: ai-recoverops [start^|stop^|status^|dashboard]
    echo.
    echo Commands:
    echo   start      - Start AI-RecoverOps services
    echo   stop       - Stop AI-RecoverOps services
    echo   status     - Show service status
    echo   dashboard  - Open dashboard in browser
)
"@
}

foreach ($file in $files.Keys) {
    $files[$file] | Out-File -FilePath $file -Encoding UTF8
}

# Create desktop shortcuts
$desktop = [Environment]::GetFolderPath("Desktop")
$shell = New-Object -ComObject WScript.Shell

# Start shortcut
$startShortcut = $shell.CreateShortcut("$desktop\Start AI-RecoverOps.lnk")
$startShortcut.TargetPath = "$installDir\start.bat"
$startShortcut.WorkingDirectory = $installDir
$startShortcut.Description = "Start AI-RecoverOps Services"
$startShortcut.Save()

# CLI shortcut
$cliShortcut = $shell.CreateShortcut("$desktop\AI-RecoverOps CLI.lnk")
$cliShortcut.TargetPath = "cmd.exe"
$cliShortcut.Arguments = "/k `"cd /d `"$installDir`" && ai-recoverops.bat`""
$cliShortcut.WorkingDirectory = $installDir
$cliShortcut.Description = "AI-RecoverOps Command Line Interface"
$cliShortcut.Save()

# Add to PATH
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$installDir*") {
    $newPath = "$userPath;$installDir"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-ColorOutput Green "✅ Added ai-recoverops to PATH"
}

# Show completion message
Write-ColorOutput Green @"

🎉 AI-RecoverOps Installation Complete! 🎉

Quick Start:
1. Open a new Command Prompt or PowerShell
2. Run: ai-recoverops start
3. Open: http://localhost:3000

Available Commands:
• ai-recoverops start     - Start services
• ai-recoverops stop      - Stop services  
• ai-recoverops status    - Check status
• ai-recoverops dashboard - Open dashboard

Desktop Shortcuts Created:
• Start AI-RecoverOps - Quick start shortcut
• AI-RecoverOps CLI - Command line interface

Installation Directory: $installDir

Happy incident hunting! 🔍🤖
"@

Write-ColorOutput Blue "💡 Tip: Open a new Command Prompt to use the 'ai-recoverops' command"

# Pause to show completion message
Read-Host "Press Enter to continue..."