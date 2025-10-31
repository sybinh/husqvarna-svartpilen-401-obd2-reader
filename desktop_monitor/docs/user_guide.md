# Desktop Monitor User Guide

## Overview

The Desktop Monitor is a professional PyQt6 application for monitoring OBD2 data from the Husqvarna Svartpilen 401 motorcycle in real-time.

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (tested platform)

### Setup Steps

1. **Run the setup script:**
   ```cmd
   setup.bat
   ```
   This will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Configure the application

2. **Launch the application:**
   ```cmd
   run.bat
   ```

## Features

### Main Dashboard

- **Real-time Data Display**: Shows current RPM, speed, coolant temperature, and throttle position
- **System Status**: Displays engine state, WiFi connection, and signal strength
- **Professional GUI**: Dark theme with clear, readable displays

### Data Sources

The application supports two data sources:

1. **Serial Port**: Connect directly to ESP32 hardware
2. **File Monitor**: Read from JSON file (useful for testing)

### Raw Data View

- **Real-time Log**: Shows all incoming data with timestamps
- **JSON Format**: Raw data in structured format
- **Automatic Cleanup**: Maintains manageable log size

## Usage

### Connecting to Hardware

1. Select "Serial Port" from the source dropdown
2. Choose your COM port from the list
3. Click "Refresh" to update available ports
4. Click "Connect" to establish connection

### Testing with Simulator

1. Launch the application with `run.bat`
2. Choose option 3 "Run Both"
3. The simulator will generate test data
4. Select "File Monitor" and "obd2_data.json"
5. Click "Connect" to start monitoring

### Menu Options

- **File ? Settings**: Configure application preferences
- **Tools ? Start Simulator**: Launch test data generator
- **Help ? About**: Application information

## Data Format

The application expects JSON data in this format:

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

## Troubleshooting

### Common Issues

1. **PyQt6 Import Error**
   ```
   pip install PyQt6
   ```

2. **Serial Port Not Found**
   - Check Device Manager for COM ports
   - Install USB-to-Serial drivers
   - Try different USB ports

3. **No Data Received**
   - Verify correct COM port selection
   - Check baud rate (default: 115200)
   - Ensure ESP32 is transmitting data

### Debug Mode

Enable verbose logging by modifying `main.py`:

```python
setup_logging(level=logging.DEBUG)
```

## Architecture

### Module Structure

```
src/
??? gui/                # User interface components
?   ??? main_window.py  # Main application window
?   ??? styles.py       # GUI styling
??? data/               # Data handling
?   ??? models.py       # Data structures
?   ??? handler.py      # Communication handlers
??? utils/              # Utilities
    ??? logger.py       # Logging configuration
```

### Key Components

- **MainWindow**: Primary GUI interface
- **DataHandler**: Serial communication management
- **FileDataHandler**: File-based data source
- **VehicleData**: Data model for motorcycle parameters

## Customization

### Themes

Switch between dark and light themes in `styles.py`:

```python
# Use LIGHT_THEME instead of DARK_THEME
self.setStyleSheet(LIGHT_THEME)
```

### Update Intervals

Modify refresh rate in `main_window.py`:

```python
self.update_timer.start(50)  # 50ms = 20 FPS
```

### Data Validation

Customize value ranges in `models.py`:

```python
def is_valid(self) -> bool:
    return (
        0 <= self.rpm <= 10000 and
        0 <= self.speed <= 300 and
        # Add custom validation
    )
```

## Development

### Running Tests

```cmd
cd tests
python simulator.py
```

### Code Style

The project follows PEP 8 guidelines. Use these tools:

```cmd
pip install black flake8
black src/
flake8 src/
```

### Adding Features

1. Create new modules in appropriate packages
2. Update `__init__.py` files for imports
3. Add tests in `tests/` directory
4. Update documentation

## Performance

### Resource Usage

- **Memory**: ~50-100 MB typical
- **CPU**: <5% on modern systems
- **Update Rate**: 10 FPS (100ms intervals)

### Optimization Tips

- Increase update interval for lower CPU usage
- Limit raw data log size
- Use file monitoring for testing instead of serial

## Support

### Getting Help

1. Check this documentation
2. Review error messages in status bar
3. Enable debug logging
4. Check GitHub Issues

### Reporting Bugs

Include this information:

- Operating system version
- Python version
- Error messages
- Steps to reproduce
- Log files (if available)

---

**Version**: 1.0.0  
**Last Updated**: October 2025