#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 OBD2 Data Simulator
Simulates ESP32 sending OBD2 data via Serial/BLE for testing GUI
"""

import json
import time
import random
import sys

class OBD2Simulator:
    """Simulates ESP32 OBD2 data output"""
    
    def __init__(self):
        self.rpm = 0
        self.speed = 0
        self.coolant_temp = 20
        self.throttle = 0
        self.engine_running = False
        self.timestamp = 0
        
    def generate_idle_data(self):
        """Generate data for idle engine"""
        self.rpm = random.randint(800, 1200)
        self.speed = 0
        self.coolant_temp = random.randint(70, 85)
        self.throttle = 0
        self.engine_running = True
        
    def generate_driving_data(self):
        """Generate data for driving"""
        # Simulate acceleration/deceleration
        rpm_target = random.randint(2000, 6500)
        speed_target = random.randint(20, 120)
        throttle_target = random.randint(10, 80)
        
        # Smooth transitions
        self.rpm = int(self.rpm * 0.7 + rpm_target * 0.3)
        self.speed = int(self.speed * 0.8 + speed_target * 0.2)
        self.throttle = int(self.throttle * 0.6 + throttle_target * 0.4)
        
        # Coolant temp increases slowly
        if self.coolant_temp < 95:
            self.coolant_temp += random.uniform(0.1, 0.5)
            
        self.engine_running = True
        
    def generate_stopped_data(self):
        """Generate data for stopped engine"""
        self.rpm = 0
        self.speed = 0
        self.throttle = 0
        self.engine_running = False
        # Coolant cools down slowly
        if self.coolant_temp > 25:
            self.coolant_temp -= random.uniform(0.2, 0.5)
            
    def get_json_data(self):
        """Generate JSON data like ESP32 sends"""
        data = {
            "timestamp": int(time.time() * 1000),
            "rpm": max(0, int(self.rpm)),
            "speed": max(0, int(self.speed)),
            "coolant_temp": int(self.coolant_temp),
            "throttle_position": max(0, min(100, int(self.throttle))),
            "system_state": "CONNECTED" if self.engine_running else "IDLE",
            "wifi_connected": True,
            "wifi_rssi": random.randint(-80, -40)
        }
        return json.dumps(data)
    
    def print_startup_banner(self):
        """Print ESP32 startup banner"""
        print("========================================")
        print("Husqvarna Svartpilen 401 OBD2 Reader v2.0")
        print("BLE + WiFi Edition")
        print("Professional Layered Architecture")
        print("========================================")
        print("✓ BLE service initialized successfully")
        print("  Device is now discoverable as: Svartpilen401_OBD2")
        print("  Desktop app can connect via Bluetooth")
        print("MCP2515 CAN controller initialized")
        print("✓ OBD2 handler initialized")
        print("WiFi connected!")
        print("IP address: 192.168.1.100")
        print("System initialization complete!")
        print("========================================")
        print("")
        print("Starting OBD2 data simulation...")
        print("Mode: Auto-cycling (stopped → idle → driving)")
        print("")
        
def main():
    """Main simulator loop"""
    sim = OBD2Simulator()
    sim.print_startup_banner()
    
    mode_cycle = ["stopped", "idle", "driving"]
    current_mode = 0
    mode_duration = 0
    mode_change_interval = 10  # seconds per mode
    
    update_interval = 1.0  # 1 second
    last_update = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # Update mode cycling
            mode_duration += current_time - last_update
            if mode_duration >= mode_change_interval:
                current_mode = (current_mode + 1) % len(mode_cycle)
                mode_duration = 0
                mode_name = mode_cycle[current_mode]
                print(f"\n=== Mode changed to: {mode_name.upper()} ===\n")
            
            # Generate data based on current mode
            mode = mode_cycle[current_mode]
            if mode == "stopped":
                sim.generate_stopped_data()
            elif mode == "idle":
                sim.generate_idle_data()
            elif mode == "driving":
                sim.generate_driving_data()
            
            # Output JSON data (like ESP32 does)
            json_data = sim.get_json_data()
            print(json_data)
            sys.stdout.flush()  # Force flush for real-time output
            
            last_update = current_time
            time.sleep(update_interval)
            
    except KeyboardInterrupt:
        print("\n\nSimulator stopped by user")
        print("========================================")
        sys.exit(0)

if __name__ == "__main__":
    print("ESP32 OBD2 Data Simulator")
    print("Simulates real ESP32 Serial/BLE output")
    print("Press Ctrl+C to stop\n")
    main()
