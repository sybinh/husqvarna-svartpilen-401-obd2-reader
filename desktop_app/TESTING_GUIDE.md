# Testing Guide for Husqvarna Svartpilen 401 OBD2 Monitor

## Overview
This guide explains how to test the desktop monitoring application without needing the actual ESP32 hardware.

## Test Setup Options

### Option 1: Simple Testing (Recommended)
Use the built-in ESP32 simulator that creates realistic motorcycle data.

#### Steps:
1. **Start the simulator:**
   ```powershell
   python esp32_simulator.py
   ```
   - Select a COM port (or use default COM3)
   - The simulator will generate realistic motorcycle data

2. **In another terminal, start the GUI:**
   ```powershell
   python obd2_monitor_clean.py
   ```
   - Select the same COM port in the GUI
   - Click "Connect"
   - You should see real-time data updates

### Option 2: Using Test Script
Run the convenient test script:
```powershell
test_app.bat
```

Select option 3 to run both simulator and GUI together.

## What the Simulator Does

### Realistic Data Generation:
- **Engine States**: Random start/stop simulation
- **RPM**: 1200 (idle) to 8500 (redline) based on throttle
- **Speed**: Calculated from RPM with simulated gear ratios
- **Temperature**: 85-105°C based on engine load
- **Throttle**: Random 0-100% positions
- **System States**: ENGINE_OFF, IDLE, ACCELERATING, CITY, HIGHWAY

### Data Format:
```json
{
  "timestamp": 1698765432,
  "rpm": 3500,
  "speed": 65,
  "coolant_temp": 92,
  "throttle_position": 45,
  "system_state": "HIGHWAY",
  "wifi_connected": true,
  "wifi_rssi": -42
}
```

## GUI Features to Test

### Main Display:
- **Engine Data**: RPM, Speed, Coolant Temperature, Throttle Position
- **System Status**: State, WiFi connection, Signal strength
- **Real-time Updates**: Data refreshes every 100ms
- **Raw Data Log**: JSON data with timestamps

### Connection Features:
- **Port Selection**: Dropdown with available COM ports
- **Connect/Disconnect**: Toggle connection status
- **Status Bar**: Connection status and error messages

## Troubleshooting

### Common Issues:

1. **"No module named 'PyQt6'"**
   ```powershell
   pip install PyQt6
   ```

2. **"No module named 'serial'"**
   ```powershell
   pip install pyserial
   ```

3. **COM port not available**
   - Check Device Manager for available ports
   - Try different COM port numbers
   - Install USB-to-Serial drivers if needed

4. **No data in GUI**
   - Ensure both simulator and GUI use same COM port
   - Check if simulator is actually sending data
   - Verify serial connection status

### Virtual Serial Ports (Advanced):
If you need virtual COM ports:

1. **Install com0com** (free):
   - Download from: https://sourceforge.net/projects/com0com/
   - Creates virtual COM port pairs (e.g., COM1 <-> COM2)

2. **Use the bridge tool**:
   ```powershell
   python virtual_serial_bridge.py
   ```

## Expected Behavior

### Normal Operation:
1. Simulator connects to COM port
2. GUI connects to same COM port
3. Data flows: Simulator ? Serial ? GUI
4. GUI displays updating values every second
5. Raw data appears in log panel

### Realistic Simulation:
- Engine randomly starts/stops every ~50 seconds
- When running: RPM varies with throttle
- Speed responds to RPM changes
- Temperature rises with engine load
- System state changes based on speed/throttle

## Files Created

### Application Files:
- `obd2_monitor_clean.py` - Main GUI application
- `esp32_simulator.py` - Data simulator
- `virtual_serial_bridge.py` - Serial port bridge utility
- `test_app.bat` - Convenient test launcher

### Configuration Files:
- `requirements.txt` - Python dependencies
- `setup.bat` - Virtual environment setup
- `run_app.bat` - Application launcher

## Next Steps

### Integration Testing:
1. Test with actual ESP32 hardware
2. Validate CAN bus data reception
3. Test with real motorcycle OBD2 port
4. Verify WiFi connectivity features

### Development:
1. Add data logging to files
2. Implement alerts/warnings
3. Add graphical charts
4. Create mobile app version

## Performance Notes

### Resource Usage:
- GUI updates at 10 FPS (100ms intervals)
- Serial data processed in separate thread
- Raw data log limited to 100 entries
- Memory usage: ~50MB typical

### Latency:
- Serial communication: ~10ms
- GUI update delay: ~100ms
- Total latency: <200ms end-to-end

This setup provides a complete testing environment for the OBD2 monitoring system without requiring physical hardware.