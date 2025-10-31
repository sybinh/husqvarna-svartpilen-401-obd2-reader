# Hardware Connection Guide

## Overview
This project uses MCP2515 CAN controller to interface between ESP32 and OBD2 port of Husqvarna Svartpilen 401 (2021).

## Connection Architecture
```
OBD2 Port (J1962) ? MCP2515 CAN Controller ? ESP32 (SPI) ? WiFi/Display
```

## Pin Connections

### ESP32 to MCP2515 (SPI Interface)
| ESP32 Pin | MCP2515 Pin | Function | Wire Color |
|-----------|-------------|----------|------------|
| GPIO 5    | CS          | Chip Select | Orange |
| GPIO 23   | SI (MOSI)   | Master Out Slave In | Blue |
| GPIO 19   | SO (MISO)   | Master In Slave Out | Green |
| GPIO 18   | SCK         | Serial Clock | Yellow |
| GPIO 2    | INT         | Interrupt | Purple |
| 3.3V      | VCC         | Power Supply | Red |
| GND       | GND         | Ground | Black |

### MCP2515 to OBD2 Connector
| MCP2515 Pin | OBD2 Pin | Function | Wire Color |
|-------------|----------|----------|------------|
| CANH        | Pin 6    | CAN High | White/Blue |
| CANL        | Pin 14   | CAN Low  | White/Green |
| GND         | Pin 4,5  | Ground   | Black |

### Additional ESP32 Connections
| ESP32 Pin | Component | Function |
|-----------|-----------|----------|
| GPIO 25   | LED       | Status LED |
| GPIO 21   | OLED      | SDA (I2C Data) |
| GPIO 22   | OLED      | SCL (I2C Clock) |
| GPIO 26   | Button 1  | User Input |
| GPIO 27   | Button 2  | User Input |

## Power Supply
- ESP32: 5V from USB or external power supply
- MCP2515: 3.3V from ESP32 regulator
- OBD2 provides 12V but not used (isolated via CAN bus)

## CAN Bus Specifications
- **Baud Rate**: 500 kbps (OBD2 standard)
- **Protocol**: ISO 15765-4 (CAN 2.0B)
- **Frame Format**: 11-bit identifier for OBD2
- **Termination**: 120? resistor on CAN bus (usually built into ECU)

## OBD2 Protocol Details
- **Request ID**: 0x7DF (broadcast) or 0x7E0-0x7E7 (specific ECU)
- **Response ID**: 0x7E8-0x7EF (ECU response)
- **Service Modes**: 
  - Mode 01: Live data
  - Mode 02: Freeze frame data
  - Mode 03: Diagnostic trouble codes
  - Mode 04: Clear trouble codes

## Assembly Notes
1. Use high-quality jumper wires for SPI connections
2. Keep CAN wires (CANH/CANL) twisted pair for noise immunity
3. Ensure proper grounding between all components
4. MCP2515 board should have 8MHz crystal oscillator
5. Use breadboard or PCB for stable connections
6. Add pull-up resistors (10k?) on CS and INT lines if needed

## Troubleshooting
- **CAN initialization fails**: Check SPI connections and crystal oscillator
- **No OBD2 response**: Verify CAN bus connections and baud rate
- **Random errors**: Check power supply stability and grounding
- **Communication timeout**: Ensure vehicle is running (ECU active)