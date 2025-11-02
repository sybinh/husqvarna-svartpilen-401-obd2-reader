# Husqvarna Svartpilen 401 OBD2 Reader

## 🚀 Version 2.0 - BLE Edition

A comprehensive OBD2 monitoring system designed specifically for the Husqvarna Svartpilen 401 motorcycle, featuring ESP32-based hardware with **Bluetooth Low Energy (BLE)** and a PyQt6 desktop application for real-time wireless vehicle data visualization.

Project đọc tín hiệu OBD2 từ xe Husqvarna Svartpilen 401 (2021) thông qua ESP32 với kết nối **BLE không dây**.

## ✨ What's New in v2.0

### 🔵 Bluetooth Low Energy Support
- **Wireless connection** via BLE - No USB cable needed!
- ESP32 mounts directly on motorcycle
- Desktop app connects wirelessly
- ~10-100m range depending on environment
- Lower power consumption than WiFi

### 🎯 Key Features

- **Real-time Data Monitoring**: Live display of engine parameters via BLE
- **ESP32-based Hardware**: Wireless data transmission via Bluetooth or WiFi
- **Desktop Application**: Professional PyQt6 GUI with dark theme and BLE scanner
- **Dual Mode**: BLE for desktop + HTTP for web browser monitoring
- **CAN Bus Interface**: MCP2515 controller for OBD2 communication
- **Motorcycle-specific**: Optimized for Husqvarna Svartpilen 401
- **Extensible Architecture**: Modular design for easy enhancement



```## Pin Connections

obd2_project/

├── firmware/                   # ESP32 firmware code### ESP32 to MCP2515 (SPI Interface)

│   ├── platformio.ini         # PlatformIO configuration| ESP32 Pin | MCP2515 Pin | Function |

│   ├── include/               # Header files|-----------|-------------|----------|

│   │   ├── can_interface.h    # CAN communication interface| GPIO 5    | CS          | Chip Select |

│   │   ├── common_types.h     # Common type definitions| GPIO 23   | SI (MOSI)   | Master Out Slave In |

│   │   ├── hal_interface.h    # Hardware abstraction layer| GPIO 19   | SO (MISO)   | Master In Slave Out |

│   │   ├── obd2_handler.h     # OBD2 protocol handler| GPIO 18   | SCK         | Serial Clock |

│   │   └── oled_driver.h      # OLED display driver| GPIO 2    | INT         | Interrupt |

│   └── src/                   # Source code| 3.3V      | VCC         | Power Supply |

│       ├── main.cpp           # Main application| GND       | GND         | Ground |

│       ├── Application/       # Application layer

│       │   └── OBD2/         # OBD2 specific code### Additional Components

│       └── BSW/              # Basic software| ESP32 Pin | Component | Function |

│           ├── mcp2515_driver.cpp  # CAN controller driver|-----------|-----------|----------|

│           └── HAL/          # Hardware abstraction| GPIO 25   | LED       | Status LED |

│| GPIO 21   | OLED      | SDA (I2C Data) |

├── desktop_monitor/           # Desktop monitoring application| GPIO 22   | OLED      | SCL (I2C Clock) |

│   ├── src/                  # Source code

│   │   ├── gui/             # GUI components### MCP2515 to OBD2 Port  

│   │   ├── data/            # Data handling modules| MCP2515 Pin | OBD2 Pin | Function |

│   │   └── utils/           # Utility functions|-------------|----------|----------|

│   ├── tests/               # Test files and simulators| CANH        | Pin 6    | CAN High |

│   ├── docs/                # Application documentation| CANL        | Pin 14   | CAN Low |

│   └── requirements.txt     # Python dependencies| GND         | Pin 4,5  | Ground |

│

├── docs/                     # Project documentation** Chi tiết đầy đủ về hardware xem file [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md)**

│   ├── hardware_setup.md    # Hardware setup guide

│   ├── firmware_guide.md    # Firmware development guide## Setup

│   └── api_reference.md     # API documentation

│1. Cài đặt PlatformIO IDE

└── README.md                # This file2. Clone project và mở trong VS Code  

```3. Build: `pio run`

4. Upload: `pio run --target upload`

## 🚀 Quick Start5. Monitor: `pio device monitor`



### Prerequisites## Configuration



- **Hardware**:### WiFi Settings

  - ESP32 development boardSửa trong `src/main.cpp`:

  - MCP2515 CAN controller module`cpp

  - OLED display (optional)const char* ssid = \"YOUR_WIFI_SSID\";

  - OBD2 connector and cablesconst char* password = \"YOUR_WIFI_PASSWORD\";

`

- **Software**:

  - PlatformIO IDE## Usage

  - Python 3.8+

  - Git1. Kết nối ESP32 với MCP2515 theo sơ đồ pin

2. Kết nối MCP2515 với OBD2 port của xe

### Hardware Setup3. ESP32 sẽ tự động kết nối WiFi

4. Truy cập web interface qua IP của ESP32

1. Connect MCP2515 to ESP32:

   ```## Supported OBD2 Parameters

   MCP2515    ESP32

   --------   ------ Engine RPM (PID 0x0C)

   VCC        3.3V- Vehicle Speed (PID 0x0D)

   GND        GND- Coolant Temperature (PID 0x05)  

   CS         GPIO 5- Throttle Position (PID 0x11)

   SO         GPIO 19

   SI         GPIO 23## License

   SCK        GPIO 18

   INT        GPIO 2MIT License

   ```

2. Connect to motorcycle's OBD2 port

### Firmware Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sybinh/husqvarna-svartpilen-401-obd2-reader.git
   cd husqvarna-svartpilen-401-obd2-reader
   ```

2. Open firmware project in PlatformIO IDE

3. Configure WiFi credentials in `main.cpp`

4. Build and upload to ESP32:
   ```bash
   pio run --target upload
   ```

### Desktop Application Setup

1. Navigate to desktop monitor directory:
   ```bash
   cd desktop_monitor
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python src/main.py
   ```

## 🔧 Development

### Firmware Development

The firmware is built using PlatformIO with the Arduino framework for ESP32. Key components:

- **CAN Interface**: Handles OBD2 communication via MCP2515
- **WiFi Module**: Transmits data to desktop application
- **OBD2 Handler**: Processes motorcycle-specific PIDs
- **HAL Layer**: Hardware abstraction for portability

### Desktop Application

Built with PyQt6, featuring:

- **Modular Architecture**: Separated GUI, data handling, and utilities
- **Real-time Updates**: Non-blocking serial communication
- **Dark Theme**: Professional appearance
- **Extensible Design**: Easy to add new features

## 📊 Monitored Parameters

| Parameter | Range | Unit | Description |
|-----------|-------|------|-------------|
| RPM | 0-8500 | RPM | Engine rotational speed |
| Speed | 0-200 | km/h | Vehicle speed |
| Coolant Temperature | 20-120 | °C | Engine coolant temperature |
| Throttle Position | 0-100 | % | Throttle opening percentage |
| System State | - | - | Current operation mode |

## 🧪 Testing

The project includes comprehensive testing tools:

- **Hardware Simulator**: Simulates ESP32 data output
- **GUI Test Suite**: Automated GUI testing
- **Data Validation**: Ensures data integrity
- **Performance Tests**: Monitors system performance

Run tests:
```bash
cd desktop_monitor
python -m pytest tests/
```

## 📚 Documentation

- [Hardware Setup Guide](docs/hardware_setup.md)
- [Firmware Development Guide](docs/firmware_guide.md)
- [Desktop Application Guide](desktop_monitor/docs/user_guide.md)
- [API Reference](docs/api_reference.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions
- **Email**: Contact the maintainer at [your-email@example.com]

## 🔮 Roadmap

- [ ] Mobile application (iOS/Android)
- [ ] Cloud data logging
- [ ] Advanced diagnostics
- [ ] Multiple motorcycle support
- [ ] Real-time alerts and notifications
- [ ] Data analytics and reporting

## ⚠️ Disclaimer

This project is for educational and research purposes. Always follow safety guidelines when working with automotive electronics. The authors are not responsible for any damage to vehicles or injury resulting from the use of this project.

---

**Made with ❤️ for the Husqvarna Svartpilen 401 community**