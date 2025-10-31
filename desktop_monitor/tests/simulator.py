#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Data Simulator for OBD2 Monitor
Generates realistic motorcycle data for testing
"""

import json
import time
import random
import threading
from datetime import datetime
from pathlib import Path

class OBD2Simulator:
    """Simulates OBD2 data for testing"""
    
    def __init__(self, output_file="obd2_data.json"):
        self.output_file = Path(output_file)
        self.running = False
        
        # Simulation state
        self.rpm = 800
        self.speed = 0
        self.coolant_temp = 85
        self.throttle_position = 0
        self.engine_running = False
        self.wifi_connected = True
        self.wifi_rssi = -45
        
        # Realistic ranges for Husqvarna Svartpilen 401
        self.rpm_idle = 1200
        self.rpm_max = 8500
        self.temp_min = 85
        self.temp_max = 105
        
    def generate_realistic_data(self):
        """Generate realistic motorcycle data"""
        timestamp = int(time.time())
        
        # Simulate engine behavior
        if random.random() < 0.02:  # 2% chance to start/stop engine
            self.engine_running = not self.engine_running
            print(f"Engine {'started' if self.engine_running else 'stopped'}!")
        
        if self.engine_running:
            # Engine is running - simulate riding
            if random.random() < 0.1:  # 10% chance to change throttle
                self.throttle_position = random.randint(0, 100)
            
            # RPM based on throttle
            if self.throttle_position > 0:
                target_rpm = self.rpm_idle + (self.throttle_position / 100) * (self.rpm_max - self.rpm_idle)
                self.rpm += (target_rpm - self.rpm) * 0.1
            else:
                self.rpm += (self.rpm_idle - self.rpm) * 0.1
                
            # Speed based on RPM (simplified gear simulation)
            if self.rpm > self.rpm_idle:
                gear_ratio = random.choice([0.8, 1.0, 1.2, 1.4, 1.6, 2.0])
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
            self.coolant_temp += (20 - self.coolant_temp) * 0.01  # Cool down
        
        # Add realistic noise
        self.rpm += random.randint(-50, 50)
        self.speed += random.uniform(-2, 2)
        self.coolant_temp += random.uniform(-1, 1)
        
        # Clamp values to realistic ranges
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
    
    def save_data(self, data):
        """Save data to JSON file"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def run_simulation(self, interval=1.0):
        """Run the simulation loop"""
        self.running = True
        print("=== OBD2 Data Simulator Started ===")
        print(f"Writing to: {self.output_file.absolute()}")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while self.running:
                # Generate and save data
                data = self.generate_realistic_data()
                
                if self.save_data(data):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] RPM:{data['rpm']} Speed:{data['speed']}km/h "
                          f"Temp:{data['coolant_temp']}C Throttle:{data['throttle_position']}% "
                          f"State:{data['system_state']}")
                else:
                    print("Failed to save data")
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
        except Exception as e:
            print(f"Simulation error: {e}")
        finally:
            self.running = False
            print("Simulator stopped")

def main():
    """Main entry point"""
    print("Husqvarna Svartpilen 401 OBD2 Data Simulator")
    print("=" * 50)
    
    # Check if running from tests directory
    output_file = "obd2_data.json"
    if Path.cwd().name == "tests":
        output_file = "../obd2_data.json"
    
    simulator = OBD2Simulator(output_file)
    simulator.run_simulation()

if __name__ == "__main__":
    main()