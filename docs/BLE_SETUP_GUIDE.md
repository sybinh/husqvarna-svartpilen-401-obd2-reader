# Bluetooth Low Energy (BLE) Setup Guide

## Tổng quan

Project đã được nâng cấp để hỗ trợ **Bluetooth Low Energy (BLE)** thay vì Serial USB. Điều này cho phép:

✅ **Không cần dây USB** - ESP32 gắn trực tiếp trên xe  
✅ **Tiết kiệm điện** hơn WiFi  
✅ **Kết nối nhanh** và ổn định  
✅ **Khoảng cách** ~10-100m tùy môi trường  

## 🔧 Cài đặt Firmware ESP32

### 1. Yêu cầu
- ESP32 DevKit V1
- PlatformIO IDE
- USB cable để upload firmware

### 2. Build và Upload

```bash
cd firmware
pio run --target upload
pio device monitor
```

### 3. Kiểm tra

Khi ESP32 khởi động, bạn sẽ thấy:

```
========================================
Husqvarna Svartpilen 401 OBD2 Reader v2.0
BLE + WiFi Edition
Professional Layered Architecture
========================================
✓ BLE service initialized successfully
  Device is now discoverable as: Svartpilen401_OBD2
  Desktop app can connect via Bluetooth
```

## 💻 Cài đặt Desktop App

### 1. Cài đặt Python dependencies

**Windows:**
```powershell
cd desktop_monitor
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd desktop_monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Yêu cầu hệ thống

**Windows 10/11:**
- Bluetooth adapter hỗ trợ BLE (Bluetooth 4.0+)
- Driver Bluetooth đã cài đặt

**Linux:**
```bash
sudo apt install bluez
sudo systemctl start bluetooth
```

**macOS:**
- Built-in Bluetooth đã hỗ trợ BLE

### 3. Chạy ứng dụng

```bash
python main.py
```

## 📱 Sử dụng BLE Connection

### 1. Mở Desktop App

![BLE Connection](../docs/images/ble_connection.png)

### 2. Chọn BLE Mode

- Source: `BLE (Bluetooth)`
- Click `Scan` để tìm devices

### 3. Kết nối

- Chọn device `★ Svartpilen401_OBD2`
- Click `Connect`
- Chờ status: `● Connected` (màu xanh)

### 4. Xem dữ liệu real-time

Dashboard sẽ hiển thị:
- RPM
- Speed (km/h)
- Coolant Temperature (°C)
- Throttle Position (%)

## 🔧 Cấu hình BLE

### ESP32 Firmware

Trong `firmware/src/main.cpp`:

```cpp
// Enable/Disable BLE
#define ENABLE_BLE true  // Set to false to disable BLE

// BLE Device Name
#define BLE_DEVICE_NAME "Svartpilen401_OBD2"
```

### Service UUIDs

Trong `firmware/include/ble_service.h`:

```cpp
#define BLE_SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define BLE_CHAR_DATA_UUID      "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define BLE_CHAR_STATUS_UUID    "beb5483e-36e1-4688-b7f5-ea07361b26a9"
```

**Lưu ý:** UUIDs phải giống nhau giữa firmware và desktop app!

## 🚀 Dual Mode: BLE + WiFi

ESP32 chạy **song song** cả BLE và WiFi:

### BLE Mode
- **Desktop App** kết nối qua Bluetooth
- Tốc độ: 200ms/update
- Không cần WiFi router

### WiFi Mode
- **Web Browser** truy cập qua HTTP
- URL: `http://[ESP32_IP_ADDRESS]`
- Tốc độ: 1s/update
- Cần WiFi credentials trong code

## ⚠️ Troubleshooting

### Desktop App không tìm thấy BLE device

1. **Kiểm tra Bluetooth adapter:**
   ```bash
   # Windows PowerShell
   Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth"}
   ```

2. **Kiểm tra bleak library:**
   ```bash
   pip install --upgrade bleak
   ```

3. **ESP32 đã khởi động BLE?**
   - Mở Serial Monitor
   - Xem dòng: `✓ BLE service initialized successfully`

### Kết nối bị disconnect ngay

1. **Kiểm tra MTU size** - Firmware mặc định: 517 bytes
2. **Giảm update rate** - Sửa `BLE_SEND_INTERVAL` trong main.cpp
3. **Khoảng cách** - Giữ PC gần ESP32 (<10m)

### BLE support not available

Desktop app hiển thị: `BLE not available`

**Giải pháp:**
```bash
pip install bleak
```

Nếu vẫn lỗi trên Linux:
```bash
sudo apt install python3-dev libdbus-1-dev
pip install bleak
```

## 📊 So sánh Serial vs BLE

| Feature | Serial USB | BLE |
|---------|-----------|-----|
| Khoảng cách | 1-5m (dây USB) | 10-100m |
| Tiện lợi | ⚠️ Cần dây | ✅ Không dây |
| Tốc độ | 115200 baud | ~1 Mbps |
| Latency | ~50ms | ~100-200ms |
| Điện năng | Cao hơn | Thấp (BLE) |
| Setup | Đơn giản | Cần scan device |

## 🔐 Bảo mật

**Lưu ý:** BLE connection hiện tại **không có mã hóa**.

Để thêm security:
1. Implement BLE pairing
2. Add PIN code authentication
3. Sử dụng encrypted characteristics

Xem: [ESP32 BLE Security Guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/ble-security.html)

## 📚 Tài liệu tham khảo

- [ESP32 BLE Arduino](https://github.com/nkolban/ESP32_BLE_Arduino)
- [Bleak Python Library](https://github.com/hbldh/bleak)
- [Bluetooth Core Specification](https://www.bluetooth.com/specifications/specs/)

## 🆘 Hỗ trợ

Nếu gặp vấn đề, mở issue trên GitHub với:
- Log từ Serial Monitor (ESP32)
- Log từ Desktop App
- Hệ điều hành và phiên bản Bluetooth
