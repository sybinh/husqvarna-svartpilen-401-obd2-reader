# Husqvarna Svartpilen 401 OBD2 Reader

Project đọc tín hiệu OBD2 từ xe Husqvarna Svartpilen 401 (2021) thông qua ESP32.

## Tính năng

- Đọc dữ liệu OBD2 real-time từ xe máy
- Hiển thị RPM, tốc độ, nhiệt độ nước làm mát
- Web interface để monitor từ xa
- Kiến trúc layered chuyên nghiệp

## Hardware

- ESP32 DevKit
- CAN transceiver (SN65HVD230)
- OLED display (optional)

## Kết nối

| ESP32 Pin | Chức năng |
|-----------|-----------|
| GPIO 4    | CAN RX    |
| GPIO 5    | CAN TX    |
| GPIO 2    | Status LED|

## Setup

1. Cài đặt PlatformIO
2. Mở project trong VS Code
3. Cấu hình WiFi trong main.cpp
4. Build và upload: pio run --target upload

## Sử dụng

1. Kết nối ESP32 với OBD2 port của xe
2. Kết nối WiFi
3. Truy cập web interface qua IP của ESP32

## License

MIT License
