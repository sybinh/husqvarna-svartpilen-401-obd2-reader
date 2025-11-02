#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Handler for OBD2 Monitor
Handles data communication and processing
Supports both Serial (USB) and BLE (Bluetooth) connections
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
from .ble_handler import BLEHandler, BLEAK_AVAILABLE

logger = logging.getLogger(__name__)

class DataHandler(QObject):
    """Handles data communication from various sources (Serial USB or BLE)"""
    
    # Signals
    data_received = pyqtSignal(VehicleData)
    connection_status_changed = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str)
    devices_discovered = pyqtSignal(list)  # For BLE device scanning
    
    def __init__(self, config: ConnectionConfig):
        super().__init__()
        self.config = config
        self.serial_connection: Optional[serial.Serial] = None
        self.ble_handler: Optional[BLEHandler] = None
        self.connection_type: str = "none"  # "serial", "ble", or "none"
        self.running = False
        self.read_thread: Optional[threading.Thread] = None
        
        # Initialize BLE handler if available
        if BLEAK_AVAILABLE:
            self.ble_handler = BLEHandler()
            # Connect BLE signals to DataHandler signals
            self.ble_handler.data_received.connect(self.data_received.emit)
            self.ble_handler.connection_status_changed.connect(self.connection_status_changed.emit)
            self.ble_handler.error_occurred.connect(self.error_occurred.emit)
            self.ble_handler.devices_discovered.connect(self.devices_discovered.emit)
            logger.info("BLE handler initialized")
        else:
            logger.warning("BLE support not available (install bleak)")
    
    def is_ble_available(self) -> bool:
        """Check if BLE is available"""
        return BLEAK_AVAILABLE and self.ble_handler is not None
    
    def scan_ble_devices(self, timeout: float = 5.0):
        """Scan for BLE devices
        
        Args:
            timeout: Scan timeout in seconds
        """
        if not self.is_ble_available():
            self.error_occurred.emit("BLE not available. Install: pip install bleak")
            return
            
        logger.info("Starting BLE device scan...")
        self.ble_handler.scan_devices_sync(timeout)
    
    def connect_ble(self, address: str) -> bool:
        """Connect to BLE device
        
        Args:
            address: BLE device MAC address
            
        Returns:
            True if connection initiated successfully
        """
        if not self.is_ble_available():
            self.error_occurred.emit("BLE not available")
            return False
            
        try:
            self.disconnect()  # Disconnect any existing connection
            
            logger.info(f"Connecting to BLE device: {address}")
            self.ble_handler.connect(address)
            self.connection_type = "ble"
            return True
            
        except Exception as e:
            error_msg = f"Failed to connect to BLE: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return False
        
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
        """Disconnect from data source (Serial or BLE)"""
        self.running = False
        
        # Disconnect Serial
        if self.connection_type == "serial":
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=2.0)
                
            if self.serial_connection and self.serial_connection.is_open:
                try:
                    self.serial_connection.close()
                    logger.info("Serial connection closed")
                except Exception as e:
                    logger.error(f"Error closing serial connection: {e}")
        
        # Disconnect BLE
        elif self.connection_type == "ble":
            if self.ble_handler:
                try:
                    self.ble_handler.disconnect()
                    logger.info("BLE connection closed")
                except Exception as e:
                    logger.error(f"Error closing BLE connection: {e}")
        
        self.connection_type = "none"
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
    """Handles data from file source (for testing) - replays data from JSON/CSV files"""
    
    data_received = pyqtSignal(VehicleData)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path: str, playback_speed: float = 1.0):
        super().__init__()
        self.file_path = file_path
        self.playback_speed = playback_speed  # 1.0 = real-time, 2.0 = 2x speed, etc.
        self.running = False
        self.playback_thread: Optional[threading.Thread] = None
        self.data_array = []
        self.current_index = 0
        
    def start_monitoring(self):
        """Start playing back file data"""
        # Load all data from file
        if not self._load_file_data():
            return
            
        self.running = True
        self.current_index = 0
        self.playback_thread = threading.Thread(target=self._playback_data, daemon=True)
        self.playback_thread.start()
        logger.info(f"Started playback of {len(self.data_array)} samples from: {self.file_path}")
        
    def stop_monitoring(self):
        """Stop playback"""
        self.running = False
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=2.0)
        logger.info("Stopped file playback")
        
    def _load_file_data(self):
        """Load all data from file (JSON or CSV)"""
        import os
        try:
            if not os.path.exists(self.file_path):
                error_msg = f"File not found: {self.file_path}"
                self.error_occurred.emit(error_msg)
                logger.error(error_msg)
                return False
                
            # Determine file type
            if self.file_path.endswith('.json'):
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    # Handle both single object and array of objects
                    if isinstance(data, list):
                        self.data_array = data
                    else:
                        self.data_array = [data]
                        
            elif self.file_path.endswith('.csv'):
                import csv
                with open(self.file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    self.data_array = [row for row in reader]
            else:
                error_msg = f"Unsupported file format: {self.file_path}"
                self.error_occurred.emit(error_msg)
                logger.error(error_msg)
                return False
                
            logger.info(f"Loaded {len(self.data_array)} samples from file")
            return True
            
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return False
            
    def _playback_data(self):
        """Playback data samples at specified speed"""
        while self.running and self.current_index < len(self.data_array):
            try:
                sample = self.data_array[self.current_index]
                
                # Convert to VehicleData
                vehicle_data = VehicleData.from_dict(sample)
                
                if vehicle_data.is_valid():
                    self.data_received.emit(vehicle_data)
                    logger.debug(f"Played sample {self.current_index + 1}/{len(self.data_array)}")
                else:
                    logger.warning(f"Invalid data at index {self.current_index}: {sample}")
                
                self.current_index += 1
                
                # Sleep for playback interval (1 second / speed)
                time.sleep(1.0 / self.playback_speed)
                
            except Exception as e:
                error_msg = f"Playback error at index {self.current_index}: {str(e)}"
                self.error_occurred.emit(error_msg)
                logger.error(error_msg)
                break
        
        # Loop back to start or stop
        if self.running and self.current_index >= len(self.data_array):
            logger.info("Playback finished, looping back to start")
            self.current_index = 0
            # Continue playback in a loop
            self._playback_data()