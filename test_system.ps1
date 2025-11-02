# ========================================
# Test Script for ESP32 WROOM on Windows
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ESP32 WROOM System Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# Test 1: Python
Write-Host "[TEST 1] Python Installation" -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.([8-9]|\d{2,})") {
        Write-Host "  ✓ PASS: $pythonVersion" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ FAIL: Python 3.8+ required" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ FAIL: Python not found" -ForegroundColor Red
    $testsFailed++
}

# Test 2: PlatformIO
Write-Host ""
Write-Host "[TEST 2] PlatformIO Installation" -ForegroundColor Yellow
try {
    $pioVersion = pio --version 2>&1
    Write-Host "  ✓ PASS: $pioVersion" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "  ✗ FAIL: PlatformIO not found" -ForegroundColor Red
    $testsFailed++
}

# Test 3: Bluetooth
Write-Host ""
Write-Host "[TEST 3] Bluetooth Adapter" -ForegroundColor Yellow
$bluetooth = Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth" -and $_.Status -eq "OK"}
if ($bluetooth) {
    Write-Host "  ✓ PASS: Bluetooth adapter found" -ForegroundColor Green
    Write-Host "    Device: $($bluetooth.FriendlyName)" -ForegroundColor Cyan
    $testsPassed++
} else {
    Write-Host "  ✗ FAIL: No working Bluetooth adapter" -ForegroundColor Red
    $testsFailed++
}

# Test 4: COM Ports
Write-Host ""
Write-Host "[TEST 4] Serial COM Ports" -ForegroundColor Yellow
$comPorts = [System.IO.Ports.SerialPort]::getportnames()
if ($comPorts.Count -gt 0) {
    Write-Host "  ✓ PASS: COM ports available" -ForegroundColor Green
    foreach ($port in $comPorts) {
        Write-Host "    - $port" -ForegroundColor Cyan
    }
    $testsPassed++
} else {
    Write-Host "  ⚠ WARNING: No COM ports found" -ForegroundColor Yellow
    Write-Host "    Connect ESP32 via USB to see COM port" -ForegroundColor Gray
    # Not a failure, just warning
    $testsPassed++
}

# Test 5: Virtual Environment
Write-Host ""
Write-Host "[TEST 5] Desktop App Virtual Environment" -ForegroundColor Yellow
if (Test-Path "desktop_monitor\venv") {
    Write-Host "  ✓ PASS: Virtual environment exists" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "  ✗ FAIL: Virtual environment not found" -ForegroundColor Red
    Write-Host "    Run: cd desktop_monitor; python -m venv venv" -ForegroundColor Gray
    $testsFailed++
}

# Test 6: Python Packages
Write-Host ""
Write-Host "[TEST 6] Python Packages" -ForegroundColor Yellow
if (Test-Path "desktop_monitor\venv") {
    try {
        Push-Location desktop_monitor
        & .\venv\Scripts\python.exe -c "import PyQt6, serial, bleak" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ PASS: All required packages installed" -ForegroundColor Green
            $testsPassed++
        } else {
            Write-Host "  ✗ FAIL: Missing packages" -ForegroundColor Red
            Write-Host "    Run: pip install -r requirements.txt" -ForegroundColor Gray
            $testsFailed++
        }
        Pop-Location
    } catch {
        Write-Host "  ✗ FAIL: Cannot check packages" -ForegroundColor Red
        $testsFailed++
    }
} else {
    Write-Host "  ⊘ SKIP: No virtual environment" -ForegroundColor Gray
}

# Test 7: Firmware Files
Write-Host ""
Write-Host "[TEST 7] Firmware Source Files" -ForegroundColor Yellow
$requiredFiles = @(
    "firmware\src\main.cpp",
    "firmware\include\ble_service.h",
    "firmware\src\BSW\ble_service.cpp",
    "firmware\platformio.ini"
)
$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MISSING" -ForegroundColor Red
        $allFilesExist = $false
    }
}
if ($allFilesExist) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 8: USB Drivers
Write-Host ""
Write-Host "[TEST 8] USB-to-Serial Drivers" -ForegroundColor Yellow
$drivers = Get-WmiObject Win32_PnPSignedDriver | Where-Object {
    $_.DeviceName -match "CP210|CH340|FTDI|USB.*Serial"
}
if ($drivers) {
    Write-Host "  ✓ PASS: USB drivers found" -ForegroundColor Green
    foreach ($driver in $drivers | Select-Object -First 3) {
        Write-Host "    - $($driver.DeviceName)" -ForegroundColor Cyan
    }
    $testsPassed++
} else {
    Write-Host "  ⚠ WARNING: No USB-Serial drivers detected" -ForegroundColor Yellow
    Write-Host "    May need CP2102 or CH340 driver" -ForegroundColor Gray
    $testsPassed++  # Not critical
}

# Test 9: Disk Space
Write-Host ""
Write-Host "[TEST 9] Disk Space" -ForegroundColor Yellow
$drive = Get-PSDrive C
$freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
if ($freeSpaceGB -gt 1) {
    Write-Host "  ✓ PASS: $freeSpaceGB GB free" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "  ✗ FAIL: Low disk space ($freeSpaceGB GB)" -ForegroundColor Red
    $testsFailed++
}

# Test 10: Compile Test
Write-Host ""
Write-Host "[TEST 10] Firmware Compilation" -ForegroundColor Yellow
Write-Host "  Testing firmware build (this may take a minute)..." -ForegroundColor Gray
Push-Location firmware
try {
    $buildOutput = pio run 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ PASS: Firmware builds successfully" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ FAIL: Build errors detected" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ FAIL: Cannot build firmware" -ForegroundColor Red
    $testsFailed++
}
Pop-Location

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Results" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests Passed: " -NoNewline -ForegroundColor Yellow
Write-Host "$testsPassed" -ForegroundColor Green
Write-Host "Tests Failed: " -NoNewline -ForegroundColor Yellow
Write-Host "$testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "✓ All tests passed! System is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Connect ESP32 WROOM via USB" -ForegroundColor White
    Write-Host "  2. Upload firmware: cd firmware; pio run --target upload" -ForegroundColor White
    Write-Host "  3. Monitor output: pio device monitor" -ForegroundColor White
    Write-Host "  4. Run desktop app: cd desktop_monitor; python main.py" -ForegroundColor White
} else {
    Write-Host "⚠ Some tests failed. Please fix issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  - Install Python 3.8+: winget install Python.Python.3.11" -ForegroundColor White
    Write-Host "  - Install PlatformIO: pip install platformio" -ForegroundColor White
    Write-Host "  - Setup venv: cd desktop_monitor; python -m venv venv" -ForegroundColor White
    Write-Host "  - Install packages: .\venv\Scripts\activate; pip install -r requirements.txt" -ForegroundColor White
}

Write-Host ""
