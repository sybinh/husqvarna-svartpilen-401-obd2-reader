#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtual Serial Bridge for Testing
Creates virtual COM port pair for testing GUI without hardware
"""

import sys
import time
import subprocess
import json
import random

try:
    # For Windows testing - use named pipes or socket
    import socket
    import threading
    HAS_SOCKET = True
except ImportError:
    HAS_SOCKET = False

class VirtualSerialBridge:
    """Bridge simulator output to GUI via socket (simulates serial)"""
    
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.running = False
        
    def start_server(self):
        """Start TCP server (simulates serial port)"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = True
        
        print(f"Virtual Serial Bridge started on {self.host}:{self.port}")
        print("Waiting for GUI connection...")
        
        self.client_socket, addr = self.server_socket.accept()
        print(f"GUI connected from {addr}")
        return True
        
    def send_data(self, data):
        """Send data to connected GUI"""
        if self.client_socket:
            try:
                self.client_socket.send((data + '\n').encode('utf-8'))
                return True
            except:
                return False
        return False
        
    def close(self):
        """Close connections"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

def generate_test_data():
    """Generate test OBD2 data"""
    modes = ["idle", "driving", "stopped"]
    current_mode = random.choice(modes)
    
    if current_mode == "idle":
        data = {
            "timestamp": int(time.time() * 1000),
            "rpm": random.randint(800, 1200),
            "speed": 0,
            "coolant_temp": random.randint(70, 85),
            "throttle_position": 0,
            "system_state": "IDLE",
            "wifi_connected": True,
            "wifi_rssi": -50
        }
    elif current_mode == "driving":
        data = {
            "timestamp": int(time.time() * 1000),
            "rpm": random.randint(2000, 6500),
            "speed": random.randint(20, 120),
            "coolant_temp": random.randint(85, 95),
            "throttle_position": random.randint(20, 80),
            "system_state": "CONNECTED",
            "wifi_connected": True,
            "wifi_rssi": -45
        }
    else:  # stopped
        data = {
            "timestamp": int(time.time() * 1000),
            "rpm": 0,
            "speed": 0,
            "coolant_temp": random.randint(25, 60),
            "throttle_position": 0,
            "system_state": "IDLE",
            "wifi_connected": True,
            "wifi_rssi": -55
        }
    
    return json.dumps(data)

def main():
    """Main bridge function"""
    print("=" * 60)
    print("Virtual Serial Bridge - ESP32 OBD2 Simulator")
    print("=" * 60)
    print("\nThis simulates ESP32 Serial output for testing GUI\n")
    
    bridge = VirtualSerialBridge()
    
    try:
        if not bridge.start_server():
            print("Failed to start server")
            return
            
        print("\nSending simulated OBD2 data...")
        print("(Press Ctrl+C to stop)\n")
        
        # Send startup banner
        startup_lines = [
            "========================================",
            "Husqvarna Svartpilen 401 OBD2 Reader v2.0",
            "BLE + WiFi Edition",
            "========================================",
            "✓ BLE service initialized successfully",
            "✓ OBD2 handler initialized",
            "System initialization complete!",
            "========================================"
        ]
        
        for line in startup_lines:
            print(line)
            bridge.send_data(line)
            time.sleep(0.1)
            
        print("\nSending live data...\n")
        
        # Send data continuously
        count = 0
        while True:
            json_data = generate_test_data()
            
            if bridge.send_data(json_data):
                count += 1
                print(f"[{count}] Sent: {json_data}")
            else:
                print("Connection lost!")
                break
                
            time.sleep(1)  # 1 Hz update rate
            
    except KeyboardInterrupt:
        print("\n\nBridge stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        bridge.close()
        print("Bridge closed")

if __name__ == "__main__":
    if not HAS_SOCKET:
        print("Socket support not available!")
        sys.exit(1)
    main()
