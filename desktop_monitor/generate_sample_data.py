#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate sample OBD2 data file for testing GUI
Creates a CSV file with realistic vehicle data
"""

import csv
import random
import time
from datetime import datetime

def generate_sample_data(num_samples=300):
    """Generate sample OBD2 data spanning multiple driving scenarios"""
    
    data = []
    timestamp = int(time.time() * 1000)
    
    # Scenario 1: Engine off/stopped (0-50 samples)
    for i in range(50):
        data.append({
            'timestamp': timestamp + (i * 1000),
            'rpm': 0,
            'speed': 0,
            'coolant_temp': 25 + i * 0.5,  # Slowly heating up
            'throttle_position': 0,
            'system_state': 'STOPPED',
            'wifi_connected': True,
            'wifi_rssi': -55
        })
    
    # Scenario 2: Idle (51-100 samples)
    for i in range(50):
        data.append({
            'timestamp': timestamp + ((50 + i) * 1000),
            'rpm': 900 + random.randint(-100, 100),  # Idle fluctuation
            'speed': 0,
            'coolant_temp': 50 + i * 0.7,  # Warming up
            'throttle_position': 0,
            'system_state': 'IDLE',
            'wifi_connected': True,
            'wifi_rssi': -50
        })
    
    # Scenario 3: City driving (101-200 samples)
    for i in range(100):
        # Simulate stop-and-go traffic
        phase = i % 20
        if phase < 5:  # Accelerating
            rpm = 1500 + phase * 500
            speed = phase * 10
            throttle = phase * 15
        elif phase < 10:  # Cruising
            rpm = 3000 + random.randint(-200, 200)
            speed = 50 + random.randint(-5, 5)
            throttle = 35 + random.randint(-5, 5)
        elif phase < 13:  # Decelerating
            rpm = 2000 - (phase - 10) * 300
            speed = 50 - (phase - 10) * 15
            throttle = 20 - (phase - 10) * 5
        else:  # Stopped/idle at light
            rpm = 900 + random.randint(-50, 50)
            speed = 0
            throttle = 0
            
        data.append({
            'timestamp': timestamp + ((100 + i) * 1000),
            'rpm': max(900, rpm),
            'speed': max(0, speed),
            'coolant_temp': min(95, 85 + i * 0.1),  # Heating to operating temp
            'throttle_position': max(0, throttle),
            'system_state': 'CONNECTED',
            'wifi_connected': True,
            'wifi_rssi': -45 + random.randint(-5, 5)
        })
    
    # Scenario 4: Highway driving (201-300 samples)
    for i in range(100):
        # Smooth highway cruising with occasional speed changes
        if i % 30 < 20:  # Cruising
            rpm = 4500 + random.randint(-300, 300)
            speed = 90 + random.randint(-5, 5)
            throttle = 40 + random.randint(-5, 5)
        else:  # Overtaking
            rpm = 5500 + random.randint(-200, 200)
            speed = 110 + random.randint(-5, 5)
            throttle = 65 + random.randint(-5, 5)
            
        data.append({
            'timestamp': timestamp + ((200 + i) * 1000),
            'rpm': min(6500, rpm),
            'speed': min(120, speed),
            'coolant_temp': min(95, 90 + random.randint(-2, 2)),  # Stable temp
            'throttle_position': min(100, throttle),
            'system_state': 'CONNECTED',
            'wifi_connected': True,
            'wifi_rssi': -50 + random.randint(-10, 5)
        })
    
    return data

def save_to_csv(data, filename='sample_obd2_data.csv'):
    """Save data to CSV file"""
    
    fieldnames = ['timestamp', 'rpm', 'speed', 'coolant_temp', 'throttle_position', 
                  'system_state', 'wifi_connected', 'wifi_rssi']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✓ Generated {len(data)} samples")
    print(f"✓ Saved to: {filename}")
    print(f"\nData summary:")
    print(f"  - Duration: {len(data)} seconds (~{len(data)//60} minutes)")
    print(f"  - Scenarios: Stopped → Idle → City → Highway")
    print(f"  - Max RPM: {max(d['rpm'] for d in data)}")
    print(f"  - Max Speed: {max(d['speed'] for d in data)} km/h")
    print(f"  - Max Temp: {max(d['coolant_temp'] for d in data):.1f}°C")

def save_to_json(data, filename='sample_obd2_data.json'):
    """Save data to JSON file (alternative format)"""
    import json
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2)
    
    print(f"✓ Also saved JSON format: {filename}")

if __name__ == "__main__":
    print("=" * 60)
    print("OBD2 Sample Data Generator")
    print("=" * 60)
    print()
    
    # Generate data
    data = generate_sample_data(300)
    
    # Save to both formats
    save_to_csv(data, 'sample_obd2_data.csv')
    save_to_json(data, 'sample_obd2_data.json')
    
    print("\nYou can now test the GUI:")
    print("1. Run: test_gui.bat")
    print("2. Select 'File (CSV)' as source")
    print("3. Load: sample_obd2_data.csv")
    print()
