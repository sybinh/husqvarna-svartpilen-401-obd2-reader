#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Handler for OBD2 Monitor
Handles data communication and processing
"""

import json
import threading
import time
import logging
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

from .models import VehicleData, ConnectionConfig

logger = logging.getLogger(__name__)

class DataHandler(QObject):
    """Handles data communication from various sources"""
    
    # Signals
    data_received = pyqtSignal(VehicleData)
    connection_status_changed = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config: ConnectionConfig):
        super().__init__()
        self.config = config
        self.serial_connection: Optional[serial.Serial] = None
        self.running = False
        self.read_thread: Optional[threading.Thread] = None
        
    def get_available_ports(self) -> list:
        """Get list of available serial ports"""
        if not SERIAL_AVAILABLE:
            return []
            
        ports = []
        try:
            for port in serial.tools.list_ports.comports():
                ports.append({
                    'device': port.device,
                    'description': port.description,
                    'hwid': port.hwid
                })
        except Exception as e:
            logger.error(f"Error getting ports: {e}")
            
        return ports
    
    def connect_serial(self, port: str) -> bool:
        """Connect to serial port"""
        if not SERIAL_AVAILABLE:
            self.error_occurred.emit("Serial library not available")
            return False
            
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.disconnect()
                
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=self.config.baudrate,
                timeout=self.config.timeout
            )
            
            self.running = True
            self.read_thread = threading.Thread(target=self._read_serial_data, daemon=True)
            self.read_thread.start()
            
            self.connection_status_changed.emit(True, f"Connected to {port}")
            logger.info(f"Connected to serial port {port}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to connect to {port}: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return False
    
    def disconnect(self):
        """Disconnect from data source"""
        self.running = False
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)
            
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                logger.info("Serial connection closed")
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
                
        self.connection_status_changed.emit(False, "Disconnected")
    
    def _read_serial_data(self):
        """Read data from serial port in separate thread"""
        buffer = ""
        
        while self.running and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting:
                    data = self.serial_connection.read(
                        self.serial_connection.in_waiting
                    ).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Process complete JSON objects
                    while '{' in buffer and '}' in buffer:
                        start = buffer.find('{')
                        end = buffer.find('}', start) + 1
                        
                        if start != -1 and end > start:
                            json_str = buffer[start:end]
                            buffer = buffer[end:]
                            
                            try:
                                json_data = json.loads(json_str)
                                vehicle_data = VehicleData.from_dict(json_data)
                                
                                if vehicle_data.is_valid():
                                    self.data_received.emit(vehicle_data)
                                else:
                                    logger.warning(f"Invalid data received: {json_data}")
                                    
                            except (json.JSONDecodeError, ValueError) as e:
                                logger.warning(f"Failed to parse JSON: {e}")
                        else:
                            break
                            
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                if self.running:
                    error_msg = f"Serial read error: {str(e)}"
                    self.error_occurred.emit(error_msg)
                    logger.error(error_msg)
                break

class FileDataHandler(QObject):
    """Handles data from file source (for testing)"""
    
    data_received = pyqtSignal(VehicleData)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.last_modified = 0
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self):
        """Start monitoring file for changes"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_file, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Started monitoring file: {self.file_path}")
        
    def stop_monitoring(self):
        """Stop monitoring file"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        logger.info("Stopped file monitoring")
        
    def _monitor_file(self):
        """Monitor file for changes"""
        import os
        
        while self.running:
            try:
                if os.path.exists(self.file_path):
                    modified = os.path.getmtime(self.file_path)
                    if modified > self.last_modified:
                        self.last_modified = modified
                        self._read_file_data()
                        
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                error_msg = f"File monitoring error: {str(e)}"
                self.error_occurred.emit(error_msg)
                logger.error(error_msg)
                break
                
    def _read_file_data(self):
        """Read data from file"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                vehicle_data = VehicleData.from_dict(data)
                
                if vehicle_data.is_valid():
                    self.data_received.emit(vehicle_data)
                else:
                    logger.warning(f"Invalid data in file: {data}")
                    
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)