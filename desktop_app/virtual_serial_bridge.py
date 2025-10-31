#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtual Serial Port for Testing
Creates a pair of connected virtual serial ports for testing
"""

import sys
import threading
import time
import queue

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("Please install pyserial: pip install pyserial")
    sys.exit(1)

class VirtualSerialBridge:
    """Bridge between two serial ports for testing"""
    
    def __init__(self, port1, port2, baudrate=115200):
        self.port1_name = port1
        self.port2_name = port2
        self.baudrate = baudrate
        
        self.port1 = None
        self.port2 = None
        self.running = False
        
        self.queue1to2 = queue.Queue()
        self.queue2to1 = queue.Queue()
        
    def connect(self):
        """Connect to both ports"""
        try:
            print(f"Opening {self.port1_name}...")
            self.port1 = serial.Serial(self.port1_name, self.baudrate, timeout=0.1)
            
            print(f"Opening {self.port2_name}...")
            self.port2 = serial.Serial(self.port2_name, self.baudrate, timeout=0.1)
            
            print("Both ports connected successfully!")
            return True
            
        except Exception as e:
            print(f"Error connecting: {e}")
            self.disconnect()
            return False
            
    def disconnect(self):
        """Disconnect from ports"""
        self.running = False
        
        if self.port1 and self.port1.is_open:
            self.port1.close()
            
        if self.port2 and self.port2.is_open:
            self.port2.close()
            
        print("Disconnected")
        
    def bridge_data(self):
        """Bridge data between ports"""
        self.running = True
        
        # Start reader threads
        thread1 = threading.Thread(target=self._read_port1, daemon=True)
        thread2 = threading.Thread(target=self._read_port2, daemon=True)
        
        thread1.start()
        thread2.start()
        
        print("Bridge started. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                # Forward data from port1 to port2
                try:
                    data = self.queue1to2.get(timeout=0.1)
                    if self.port2 and self.port2.is_open:
                        self.port2.write(data)
                        print(f"1->2: {len(data)} bytes")
                except queue.Empty:
                    pass
                    
                # Forward data from port2 to port1
                try:
                    data = self.queue2to1.get(timeout=0.1)
                    if self.port1 and self.port1.is_open:
                        self.port1.write(data)
                        print(f"2->1: {len(data)} bytes")
                except queue.Empty:
                    pass
                    
        except KeyboardInterrupt:
            print("\nStopping bridge...")
            
        self.disconnect()
        
    def _read_port1(self):
        """Read from port1 and queue for port2"""
        while self.running and self.port1 and self.port1.is_open:
            try:
                if self.port1.in_waiting:
                    data = self.port1.read(self.port1.in_waiting)
                    self.queue1to2.put(data)
            except:
                break
                
    def _read_port2(self):
        """Read from port2 and queue for port1"""
        while self.running and self.port2 and self.port2.is_open:
            try:
                if self.port2.in_waiting:
                    data = self.port2.read(self.port2.in_waiting)
                    self.queue2to1.put(data)
            except:
                break

def show_available_ports():
    """Show available serial ports"""
    print("Available serial ports:")
    ports = list_ports.comports()
    
    if not ports:
        print("  No ports found")
        return []
        
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
        
    return ports

def main():
    """Main entry point"""
    print("=== Virtual Serial Port Bridge ===")
    print("This tool bridges two serial ports for testing")
    print()
    
    # Show available ports
    ports = show_available_ports()
    
    print()
    print("For testing OBD2 monitor:")
    print("1. Use COM-COM bridge software like com0com")
    print("2. Or use USB-to-Serial adapters")
    print("3. Connect ESP32 Simulator to one port")
    print("4. Connect Desktop GUI to the other port")
    print()
    
    if len(ports) < 2:
        print("Need at least 2 serial ports for bridging")
        print("Consider using virtual serial port software:")
        print("- com0com (free): https://sourceforge.net/projects/com0com/")
        print("- Virtual Serial Port Driver (commercial)")
        return
        
    # Get port selection
    try:
        print("Select first port:")
        choice1 = int(input(f"Enter number (1-{len(ports)}): ")) - 1
        
        print("Select second port:")
        choice2 = int(input(f"Enter number (1-{len(ports)}): ")) - 1
        
        if not (0 <= choice1 < len(ports)) or not (0 <= choice2 < len(ports)):
            print("Invalid selection")
            return
            
        if choice1 == choice2:
            print("Cannot bridge a port to itself")
            return
            
        port1 = ports[choice1].device
        port2 = ports[choice2].device
        
        print(f"\nBridging {port1} <-> {port2}")
        
        # Create and run bridge
        bridge = VirtualSerialBridge(port1, port2)
        
        if bridge.connect():
            bridge.bridge_data()
            
    except (ValueError, KeyboardInterrupt):
        print("Cancelled")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()