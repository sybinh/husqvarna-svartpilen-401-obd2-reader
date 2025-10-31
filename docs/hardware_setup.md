# Hardware Setup Guide

## Overview

This guide covers the hardware setup for the Husqvarna Svartpilen 401 OBD2 Reader project.

## Required Components

### Primary Hardware

- **ESP32 Development Board** (ESP32-DevKitC-32E recommended)
- **MCP2515 CAN Controller Module** with TJA1050 transceiver
- **12V to 5V/3.3V Power Converter** (optional, for permanent installation)
- **OBD2 Connector** (female) with wiring harness
- **Jumper Wires** and **Breadboard** (for prototyping)

### Optional Components

- **OLED Display** (128x64, SSD1306 controller)
- **Enclosure** for weather protection
- **LED Status Indicators**
- **Reset Button**

## Pin Connections

### ESP32 to MCP2515 CAN Controller

| MCP2515 Pin | ESP32 Pin | Function |
|-------------|-----------|----------|
| VCC         | 3.3V      | Power supply |
| GND         | GND       | Ground |
| CS          | GPIO 5    | Chip select |
| SO (MISO)   | GPIO 19   | SPI data out |
| SI (MOSI)   | GPIO 23   | SPI data in |
| SCK         | GPIO 18   | SPI clock |
| INT         | GPIO 2    | Interrupt |

### ESP32 to OLED Display (Optional)

| OLED Pin | ESP32 Pin | Function |
|----------|-----------|----------|
| VCC      | 3.3V      | Power supply |
| GND      | GND       | Ground |
| SDA      | GPIO 21   | I2C data |
| SCL      | GPIO 22   | I2C clock |

### OBD2 Connector Pinout

| Pin | Function | Wire Color |
|-----|----------|------------|
| 4   | Chassis Ground | Black |
| 5   | Signal Ground | Black |
| 6   | CAN High (CAN_H) | Yellow |
| 14  | CAN Low (CAN_L) | Green |
| 16  | +12V Battery | Red |

## Wiring Diagram

```
ESP32                    MCP2515                 OBD2 Connector
                                                      
3.3V ?????????????????? VCC                          
GND  ?????????????????? GND ?????????????????? Pin 4,5 (Ground)
GPIO 5 ??????????????? CS                           
GPIO 19 ?????????????? SO                           
GPIO 23 ?????????????? SI                           
GPIO 18 ?????????????? SCK                          
GPIO 2 ??????????????? INT                          
                       CAN_H ???????????????? Pin 6 (CAN High)
                       CAN_L ???????????????? Pin 14 (CAN Low)
```

## Assembly Instructions

### Step 1: Prepare the Breadboard

1. Insert ESP32 development board into breadboard
2. Insert MCP2515 module into breadboard
3. Ensure proper spacing between modules

### Step 2: Power Connections

1. Connect ESP32 3.3V to MCP2515 VCC
2. Connect ESP32 GND to MCP2515 GND
3. Connect breadboard power rails

### Step 3: SPI Connections

1. Connect GPIO 5 to MCP2515 CS pin
2. Connect GPIO 19 to MCP2515 SO (MISO)
3. Connect GPIO 23 to MCP2515 SI (MOSI)
4. Connect GPIO 18 to MCP2515 SCK
5. Connect GPIO 2 to MCP2515 INT

### Step 4: CAN Bus Connections

1. Prepare OBD2 connector wiring:
   - Strip wire ends (6mm recommended)
   - Use appropriate wire gauge (18-22 AWG)
2. Connect CAN_H from MCP2515 to OBD2 pin 6
3. Connect CAN_L from MCP2515 to OBD2 pin 14
4. Connect ground from ESP32/MCP2515 to OBD2 pins 4 and 5

### Step 5: Optional Components

**OLED Display:**
1. Connect VCC to ESP32 3.3V
2. Connect GND to ESP32 GND
3. Connect SDA to GPIO 21
4. Connect SCL to GPIO 22

**Status LEDs:**
- Power LED: Connect to 3.3V through 330? resistor
- Activity LED: Connect to GPIO 25 through 330? resistor

## Testing the Hardware

### Basic Connectivity Test

1. Power on the ESP32
2. Check LED indicators on MCP2515 module
3. Verify 3.3V output on ESP32
4. Test continuity of all connections

### CAN Bus Test

1. Connect to motorcycle's OBD2 port
2. Turn on motorcycle ignition (engine doesn't need to run)
3. Monitor serial output for CAN messages
4. Verify data reception

## Safety Considerations

### Electrical Safety

- **Never connect while engine is running** during initial testing
- **Double-check polarity** before connecting power
- **Use proper fusing** for permanent installations
- **Avoid short circuits** - they can damage motorcycle ECU

### Motorcycle Safety

- **Disconnect battery** before making connections
- **Test thoroughly** before permanent installation
- **Use proper enclosure** for weather protection
- **Secure all wiring** to prevent interference

## Troubleshooting

### No Power

1. Check ESP32 power LED
2. Verify USB cable connection
3. Test power supply voltage (should be 3.3V)

### No CAN Communication

1. Verify CAN_H and CAN_L connections
2. Check for proper grounding
3. Ensure motorcycle ignition is on
4. Test with CAN bus analyzer if available

### Intermittent Connection

1. Check all solder joints
2. Verify wire connections are secure
3. Test for electromagnetic interference
4. Consider using shielded cables

### Common Error Messages

**"MCP2515 initialization failed"**
- Check SPI connections
- Verify chip select (CS) pin
- Ensure proper power supply

**"No CAN messages received"**
- Verify CAN_H/CAN_L connections
- Check motorcycle ignition status
- Test with known-good OBD2 device

## Advanced Configuration

### Termination Resistors

Most OBD2 systems have built-in termination, but if needed:
- Add 120? resistor between CAN_H and CAN_L
- Only required at network endpoints

### EMI Filtering

For noisy environments:
- Add ferrite cores to CAN cables
- Use twisted pair wiring for CAN_H/CAN_L
- Implement common-mode chokes

### Power Management

For permanent installation:
- Use automotive-grade voltage regulator
- Implement reverse polarity protection
- Add power-on delay for stable startup

## Enclosure Design

### Requirements

- **Weatherproof**: IP65 rating minimum
- **Heat Dissipation**: Adequate ventilation
- **Access**: Ports for USB programming
- **Mounting**: Secure attachment points

### Recommended Materials

- ABS plastic enclosure
- Rubber gaskets for sealing
- Cable glands for wire entry
- Vibration dampening material

---

**Safety First**: Always prioritize safety when working with automotive electronics. When in doubt, consult a professional mechanic or automotive electrician.