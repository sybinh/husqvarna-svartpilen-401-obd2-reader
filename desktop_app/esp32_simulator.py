#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 OBD2 Data Simulator
Simulates ESP32 sending OBD2 data via serial port for testing desktop application
"""

import json
import time
import random
import threading
from datetime import datetime
import serial.tools.list_ports

class ESP32Simulator:
    def __init__(self, port="COM3", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        
        # Simulation parameters
        self.rpm = 800  # Idle RPM
        self.speed = 0
        self.coolant_temp = 85  # Normal operating temp
        self.throttle_position = 0
        self.engine_running = False
        self.wifi_connected = True
        self.wifi_rssi = -45
        
        # Realistic ranges for Husqvarna Svartpilen 401
        self.rpm_idle = 1200
        self.rpm_max = 8500
        self.temp_min = 85
        self.temp_max = 105
        
    def connect(self):
        """Connect to virtual serial port"""
        try:
            print(f"Connecting to {self.port}...")
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            print("Available ports:")
            ports = serial.tools.list_ports.comports()
            for port in ports:
                print(f"  {port.device} - {port.description}")
            return False
            
    def disconnect(self):
        """Disconnect from serial port"""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Disconnected")
            
    def simulate_realistic_data(self):
        """Simulate realistic motorcycle data"""
        timestamp = int(time.time())
        
        # Simulate engine behavior
        if random.random() < 0.02:  # 2% chance to start/stop engine
            self.engine_running = not self.engine_running
            if self.engine_running:
                print("Engine started!")
            else:
                print("Engine stopped!")
        
        if self.engine_running:
            # Engine is running - simulate riding
            if random.random() < 0.1:  # 10% chance to change throttle
                self.throttle_position = random.randint(0, 100)
            
            # RPM based on throttle
            if self.throttle_position > 0:
                target_rpm = self.rpm_idle + (self.throttle_position / 100) * (self.rpm_max - self.rpm_idle)
                self.rpm += (target_rpm - self.rpm) * 0.1  # Smooth transition
            else:
                self.rpm += (self.rpm_idle - self.rpm) * 0.1
                
            # Speed based on RPM (simplified)
            if self.rpm > self.rpm_idle:
                gear_ratio = random.choice([0.8, 1.0, 1.2, 1.4, 1.6, 2.0])  # Simulate gear changes
                self.speed = max(0, (self.rpm - self.rpm_idle) / 100 * gear_ratio)
            else:
                self.speed *= 0.95  # Deceleration
                
            # Temperature increases with RPM
            target_temp = self.temp_min + (self.rpm - self.rpm_idle) / (self.rpm_max - self.rpm_idle) * (self.temp_max - self.temp_min)
            self.coolant_temp += (target_temp - self.coolant_temp) * 0.05
            
        else:
            # Engine off
            self.rpm = 0
            self.speed *= 0.9  # Coasting
            self.throttle_position = 0
            self.coolant_temp += (20 - self.coolant_temp) * 0.01  # Cool down to ambient
        
        # Add some noise
        self.rpm += random.randint(-50, 50)
        self.speed += random.uniform(-2, 2)
        self.coolant_temp += random.uniform(-1, 1)
        
        # Clamp values
        self.rpm = max(0, int(self.rpm))
        self.speed = max(0, int(self.speed))
        self.coolant_temp = max(20, min(120, int(self.coolant_temp)))
        self.throttle_position = max(0, min(100, self.throttle_position))
        
        # WiFi signal variation
        self.wifi_rssi = random.randint(-60, -30)
        
        # Determine system state
        if self.engine_running:
            if self.speed > 50:
                system_state = "HIGHWAY"
            elif self.speed > 20:
                system_state = "CITY"
            elif self.throttle_position > 0:
                system_state = "ACCELERATING"
            else:
                system_state = "IDLE"
        else:
            system_state = "ENGINE_OFF"
            
        return {
            "timestamp": timestamp,
            "rpm": self.rpm,
            "speed": self.speed,
            "coolant_temp": self.coolant_temp,
            "throttle_position": self.throttle_position,
            "system_state": system_state,
            "wifi_connected": self.wifi_connected,
            "wifi_rssi": self.wifi_rssi
        }
        
    def send_data(self, data):
        """Send JSON data via serial"""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                json_str = json.dumps(data) + "\n"
                self.serial_conn.write(json_str.encode('utf-8'))
                return True
            except Exception as e:
                print(f"Error sending data: {e}")
                return False
        return False
        
    def run_simulation(self, interval=1.0):
        """Run the simulation loop"""
        self.running = True
        print("Starting simulation...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                # Generate and send data
                data = self.simulate_realistic_data()
                
                if self.send_data(data):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] RPM:{data['rpm']} Speed:{data['speed']}km/h "
                          f"Temp:{data['coolant_temp']}C Throttle:{data['throttle_position']}% "
                          f"State:{data['system_state']}")
                else:
                    print("Failed to send data")
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
        except Exception as e:
            print(f"Simulation error: {e}")
        finally:
            self.disconnect()

def list_available_ports():
    """List all available serial ports"""
    print("Available serial ports:")
    ports = serial.tools.list_ports.comports()
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    return ports

def main():
    """Main entry point"""
    print("=== ESP32 OBD2 Data Simulator ===")
    print("This tool simulates ESP32 sending OBD2 data for testing the desktop app")
    print()
    
    # List available ports
    ports = list_available_ports()
    
    if not ports:
        print("No serial ports found!")
        return
        
    # Port selection
    print()
    try:
        choice = input("Select port number (or press Enter for COM3): ").strip()
        
        if choice == "":
            port = "COM3"
        else:
            port_index = int(choice) - 1
            if 0 <= port_index < len(ports):
                port = ports[port_index].device
            else:
                print("Invalid selection, using COM3")
                port = "COM3"
    except:
        port = "COM3"
        
    print(f"Using port: {port}")
    
    # Create and run simulator
    simulator = ESP32Simulator(port=port)
    
    if simulator.connect():
        print()
        print("Simulation scenarios:")
        print("- Engine will randomly start/stop")
        print("- Throttle position changes randomly")
        print("- RPM, Speed, Temperature respond realistically")
        print("- Data sent every 1 second")
        print()
        
        simulator.run_simulation()
    else:
        print("Failed to connect to serial port")

if __name__ == "__main__":
    main()