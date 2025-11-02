# ========================================
# Setup Script for Windows
# ESP32 WROOM - OBD2 Reader Project
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ESP32 WROOM OBD2 Reader - Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Check PlatformIO installation
Write-Host ""
Write-Host "[2/5] Checking PlatformIO..." -ForegroundColor Yellow
try {
    $pioVersion = pio --version 2>&1
    Write-Host "  ✓ PlatformIO found: $pioVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ PlatformIO not found!" -ForegroundColor Red
    Write-Host "  Installing PlatformIO..." -ForegroundColor Yellow
    pip install platformio
    Write-Host "  ✓ PlatformIO installed" -ForegroundColor Green
}

# Check Bluetooth adapter
Write-Host ""
Write-Host "[3/5] Checking Bluetooth adapter..." -ForegroundColor Yellow
$bluetooth = Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth"} | Select-Object -First 1
if ($bluetooth) {
    Write-Host "  ✓ Bluetooth adapter found: $($bluetooth.FriendlyName)" -ForegroundColor Green
    Write-Host "    Status: $($bluetooth.Status)" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠ No Bluetooth adapter found" -ForegroundColor Yellow
    Write-Host "    BLE features will not work without Bluetooth 4.0+" -ForegroundColor Yellow
}

# Setup Desktop App
Write-Host ""
Write-Host "[4/5] Setting up Desktop Application..." -ForegroundColor Yellow
Push-Location desktop_monitor

# Create virtual environment
if (Test-Path "venv") {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
} else {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

# Activate and install requirements
Write-Host "  Installing Python packages..." -ForegroundColor Cyan
& .\venv\Scripts\activate.ps1
pip install -r requirements.txt --quiet
Write-Host "  ✓ Python packages installed" -ForegroundColor Green

Pop-Location

# Check COM ports
Write-Host ""
Write-Host "[5/5] Checking COM ports..." -ForegroundColor Yellow
$comPorts = [System.IO.Ports.SerialPort]::getportnames()
if ($comPorts.Count -gt 0) {
    Write-Host "  ✓ Available COM ports:" -ForegroundColor Green
    foreach ($port in $comPorts) {
        Write-Host "    - $port" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ⚠ No COM ports found" -ForegroundColor Yellow
    Write-Host "    Connect ESP32 via USB to see COM port" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Connect ESP32 WROOM via USB" -ForegroundColor White
Write-Host "  2. Build firmware:     cd firmware; pio run" -ForegroundColor White
Write-Host "  3. Upload firmware:    pio run --target upload" -ForegroundColor White
Write-Host "  4. Monitor serial:     pio device monitor" -ForegroundColor White
Write-Host "  5. Run desktop app:    cd desktop_monitor; python main.py" -ForegroundColor White
Write-Host ""
Write-Host "📖 For detailed guide, see: QUICKSTART_BLE.md" -ForegroundColor Cyan
Write-Host ""
