#!/bin/bash
# Script to commit BLE implementation changes

echo "📝 Committing BLE implementation..."

git add .
git commit -m "feat: Add Bluetooth Low Energy (BLE) support for wireless communication

✨ Features:
- ESP32 BLE GATT server for wireless data transmission
- Desktop app BLE client with device scanner
- Support for dual mode: BLE + WiFi/HTTP
- Async BLE communication using bleak library
- Auto-advertising and reconnection
- BLE device scanner in GUI with RSSI display

🔧 Changes:
- Added ble_service.h and ble_service.cpp for ESP32
- Updated main.cpp with BLE initialization and data sending
- Created ble_handler.py for Python BLE client
- Updated handler.py to support Serial, BLE, and File modes
- Enhanced GUI with BLE scanner and connection status
- Added bleak to requirements.txt

📚 Documentation:
- Added BLE_SETUP_GUIDE.md with detailed setup instructions
- Updated README.md with BLE features
- Created BLE_IMPLEMENTATION_SUMMARY.md

🎯 Benefits:
- No USB cable needed - ESP32 mounts on motorcycle
- ~10-100m wireless range
- Lower power consumption than WiFi
- Real-time data updates (200ms)

Version: 2.0 - BLE Edition"

echo "✅ Committed successfully!"
echo ""
echo "To push to GitHub:"
echo "git push origin main"
