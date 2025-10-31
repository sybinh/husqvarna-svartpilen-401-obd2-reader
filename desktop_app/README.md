# Husqvarna Svartpilen 401 OBD2 Monitor Desktop Application

PyQt6-based desktop application ?? monitor real-time OBD2 data t? ESP32 thông qua serial connection.

## Features

?? **Real-time Vehicle Data:**
- Engine RPM
- Vehicle Speed  
- Coolant Temperature
- Throttle Position

?? **System Information:**
- ESP32 system state
- WiFi connection status
- Signal strength (RSSI)
- Connection timestamp

?? **User Interface:**
- Dark theme optimized cho long-term viewing
- Real-time charts và gauges
- Raw data log v?i JSON formatting
- Serial port auto-detection

## Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
# Ch?y setup script
setup.bat

# Ch?y application  
run_app.bat
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run application
python obd2_monitor.py
```

## Requirements

- **Python 3.8+**
- **PyQt6** (GUI framework)
- **pyserial** (Serial communication)
- **ESP32** with OBD2 firmware running

## Usage

### 1. Hardware Setup
- Connect ESP32 v?i OBD2 port c?a xe Husqvarna Svartpilen 401
- Connect ESP32 v?i máy tính via USB cable
- ??m b?o ESP32 ?ang ch?y firmware v?i JSON serial output

### 2. Software Setup
- Ch?y `setup.bat` ?? install dependencies
- Ch?y `run_app.bat` ?? kh?i ??ng application

### 3. Connection
- Ch?n serial port c?a ESP32 t? dropdown (usually COM3, COM4, etc.)
- Click **Connect** ?? establish connection
- Data s? hi?n th? real-time khi ESP32 g?i JSON packets

### 4. Monitoring
- **Engine Data panel**: Hi?n th? RPM, speed, temperature, throttle
- **System Status panel**: Hi?n th? system state và WiFi info  
- **Raw Data Log**: Hi?n th? raw JSON data ?? debugging

## Data Format

ESP32 g?i JSON data qua serial v?i format:
```json
{
  "timestamp": 12345,
  "rpm": 3500,
  "speed": 80,
  "coolant_temp": 85,
  "throttle_position": 45,
  "system_state": "RUNNING",
  "wifi_connected": true,
  "wifi_rssi": -65
}
```

## Troubleshooting

### Serial Connection Issues
- **Port not found**: Check ESP32 USB cable và drivers
- **Permission denied**: Run as administrator ho?c check port permissions
- **No data received**: Verify ESP32 firmware và baud rate (115200)

### Application Issues  
- **PyQt6 import errors**: Run `setup.bat` ?? install dependencies
- **Python not found**: Install Python 3.8+ và add to PATH
- **Virtual environment issues**: Delete `venv` folder và run setup l?i

### Performance Issues
- **High CPU usage**: T?ng update interval trong code
- **Memory leak**: Restart application periodically
- **UI freezing**: Check serial data rate và buffer size

## Development

### Project Structure
```
desktop_app/
??? obd2_monitor.py      # Main application
??? requirements.txt     # Python dependencies  
??? setup.bat           # Windows setup script
??? run_app.bat         # Windows run script
??? README.md           # This file
```

### Customization
- **Update intervals**: Modify timer intervals trong `setup_timer()`
- **UI layout**: Customize widgets trong `init_ui()`
- **Data processing**: Modify `on_data_received()` function
- **Serial settings**: Change baud rate trong `connect_serial()`

### Adding Features
- **Data logging**: Add CSV export functionality
- **Charts**: Integrate matplotlib cho real-time plotting  
- **Alerts**: Add threshold-based warnings
- **Multiple connections**: Support multiple ESP32 devices

## License

MIT License - See project root for details

## Contributing

1. Fork repository
2. Create feature branch
3. Test v?i real ESP32 hardware
4. Submit pull request v?i screenshots

## Support

- **Hardware issues**: Check HARDWARE_GUIDE.md
- **Firmware issues**: Check firmware/README.md  
- **Software bugs**: Create GitHub issue v?i logs
- **Feature requests**: Discussion tab trên GitHub