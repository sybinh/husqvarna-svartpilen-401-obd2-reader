# Windows Setup Guide - ESP32 WROOM

## ✅ Xác nhận Hardware

### ESP32 WROOM Specifications
- **Chip**: ESP32-D0WDQ6 (dual-core)
- **Flash**: 4MB
- **SRAM**: 520KB
- **Bluetooth**: Classic + BLE 4.2
- **WiFi**: 802.11 b/g/n
- **GPIO**: 30 pins available

✅ **Code đã được tối ưu cho ESP32 WROOM**

## 🔧 Yêu cầu trên Windows

### 1. Cài đặt Driver USB-to-Serial

**ESP32 WROOM sử dụng chip:**
- CP2102 (phổ biến nhất)
- CH340
- FTDI

#### Download Driver:
- **CP2102**: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- **CH340**: http://www.wch.cn/downloads/CH341SER_EXE.html

#### Kiểm tra Driver:
```powershell
# Mở Device Manager
devmgmt.msc

# Hoặc check COM port
[System.IO.Ports.SerialPort]::getportnames()
```

Nếu thấy "COM3", "COM4", etc. → Driver đã OK ✅

### 2. Cài đặt Python 3.8+

```powershell
# Download từ python.org hoặc dùng winget
winget install Python.Python.3.11

# Verify
python --version
# Should show: Python 3.11.x
```

### 3. Cài đặt PlatformIO

```powershell
# Install via pip
pip install platformio

# Verify
pio --version
```

### 4. Cài đặt Git (nếu chưa có)

```powershell
winget install Git.Git

# Verify
git --version
```

## 🚀 Quick Setup (3 phút)

### Option 1: Automatic Setup

```powershell
# Chạy script tự động
.\setup_windows.ps1
```

### Option 2: Manual Setup

```powershell
# 1. Setup Desktop App
cd desktop_monitor
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Build Firmware
cd ..\firmware
pio run

# 3. Upload to ESP32
pio run --target upload

# 4. Monitor Serial
pio device monitor
```

## 🔌 Kết nối ESP32 WROOM với PC

### 1. Connect USB Cable
- Cắm ESP32 vào cổng USB của PC
- Windows sẽ tự nhận diện (nếu driver đã cài)

### 2. Xác định COM Port

```powershell
# PowerShell
Get-WmiObject Win32_SerialPort | Select-Object Name,DeviceID

# Output example:
# Name                         DeviceID
# ----                         --------
# USB-SERIAL CH340 (COM3)      COM3
```

### 3. Upload Firmware

```powershell
cd firmware

# Auto-detect port
pio run --target upload

# Hoặc chỉ định port cụ thể
pio run --target upload --upload-port COM3
```

## 📡 Windows Bluetooth Setup

### 1. Kiểm tra Bluetooth Adapter

```powershell
# Check Bluetooth
Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth"}

# Should show Bluetooth adapter với Status = OK
```

### 2. Enable Bluetooth

```
Settings → Bluetooth & devices → Turn ON
```

### 3. Install BLE Library

```powershell
cd desktop_monitor
.\venv\Scripts\activate
pip install bleak
```

### 4. Test BLE Scan

```powershell
python -c "from bleak import BleakScanner; import asyncio; print(asyncio.run(BleakScanner.discover()))"
```

## ⚙️ ESP32 WROOM Pin Configuration

### Mặc định trong code:

```cpp
// MCP2515 CAN Controller
.mcp2515_cs   = GPIO 5   // Chip Select
.mcp2515_int  = GPIO 2   // Interrupt
.spi_mosi     = GPIO 23  // MOSI
.spi_miso     = GPIO 19  // MISO
.spi_sck      = GPIO 18  // SCK

// Status LED
.status_led   = GPIO 25

// OLED Display (Optional)
// SDA = GPIO 21
// SCL = GPIO 22
```

✅ **Các pin này tương thích 100% với ESP32 WROOM**

## 🐛 Troubleshooting Windows

### 1. COM Port không xuất hiện

**Nguyên nhân:**
- Driver chưa cài
- USB cable bị lỗi (chỉ charge không có data)
- ESP32 lỗi hardware

**Giải pháp:**
```powershell
# Reinstall driver
# Thử USB cable khác
# Thử USB port khác trên PC
# Press BOOT button khi upload
```

### 2. Permission Denied khi upload

```powershell
# Close Serial Monitor nếu đang mở
# Close Arduino IDE/other tools using COM port

# Force close port
taskkill /F /IM "python.exe"
```

### 3. Bluetooth không hoạt động

```powershell
# Restart Bluetooth service
Restart-Service bthserv

# Check Bluetooth Support Service
Get-Service bthserv
```

### 4. Upload lỗi "Timed out waiting for packet header"

**Giải pháp:**
1. Press và giữ **BOOT** button trên ESP32
2. Click **Upload** trong PlatformIO
3. Khi thấy "Connecting...", thả BOOT button
4. Upload sẽ bắt đầu

### 5. Serial Monitor không hiển thị gì

```powershell
# Check baudrate
pio device monitor --baud 115200

# Check correct port
pio device monitor --port COM3
```

## 📊 Performance trên Windows

### BLE Performance:
- **Latency**: ~150-200ms
- **Range**: 10-50m (tùy môi trường)
- **Throughput**: ~1 Mbps
- **Update rate**: 200ms (configurable)

### Serial Performance:
- **Baudrate**: 115200 bps
- **Latency**: ~50ms
- **Reliable**: ✅ Very stable

## 🔥 Windows Firewall

Nếu WiFi mode không kết nối được:

```powershell
# Allow Python through firewall
New-NetFirewallRule -DisplayName "Python" -Direction Inbound -Program "C:\Python311\python.exe" -Action Allow
```

## 🎯 Recommended Windows Settings

### 1. Power Plan
```
Control Panel → Power Options → High Performance
```

### 2. USB Selective Suspend
```
Power Options → Change plan settings → 
Change advanced power settings → 
USB settings → USB selective suspend setting → Disabled
```

### 3. Bluetooth Power
```
Device Manager → Bluetooth → 
Properties → Power Management → 
Uncheck "Allow computer to turn off this device"
```

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] PlatformIO installed  
- [ ] USB Driver installed (CP2102/CH340)
- [ ] Bluetooth adapter working
- [ ] COM port visible
- [ ] Desktop app dependencies installed
- [ ] Firmware compiled successfully
- [ ] Firmware uploaded to ESP32
- [ ] Serial monitor shows output
- [ ] BLE scanner finds device

## 📚 Tài liệu thêm

- **ESP32 WROOM Datasheet**: https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf
- **PlatformIO ESP32**: https://docs.platformio.org/en/latest/boards/espressif32/esp32dev.html
- **Windows Bluetooth**: https://docs.microsoft.com/en-us/windows/uwp/devices-sensors/bluetooth

## 🆘 Support

Nếu gặp vấn đề:
1. Check Serial Monitor output: `pio device monitor`
2. Check Windows Event Viewer: `eventvwr.msc`
3. Open GitHub Issue với:
   - Windows version
   - COM port info
   - Serial Monitor log
   - Error message

---

**✅ ESP32 WROOM + Windows 10/11 = Fully Supported!**
