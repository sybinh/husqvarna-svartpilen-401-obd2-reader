#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Husqvarna Svartpilen 401 OBD2 Monitor Desktop Application
Real-time display of vehicle data from ESP32 via serial connection
"""

import sys
import json
import serial
import threading
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QGroupBox, QGridLayout,
                             QComboBox, QPushButton, QStatusBar, QTextEdit,
                             QSplitter, QFrame)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont, QPalette, QColor

@dataclass
class VehicleData:
    timestamp: int = 0
    rpm: int = 0
    speed: int = 0
    coolant_temp: int = 0
    throttle_position: int = 0
    system_state: str = "UNKNOWN"
    wifi_connected: bool = False
    wifi_rssi: int = 0

class SerialWorker(QObject):
    """Worker thread for serial communication"""
    data_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.serial_port: Optional[serial.Serial] = None
        self.running = False
        
    def connect_serial(self, port: str, baudrate: int = 115200):
        """Connect to serial port"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            self.running = True
            self.connection_status.emit(True, f"Connected to {port}")
            
            # Start reading thread
            self.read_thread = threading.Thread(target=self._read_serial, daemon=True)
            self.read_thread.start()
            
        except Exception as e:
            self.connection_status.emit(False, f"Error: {str(e)}")
            
    def disconnect_serial(self):
        """Disconnect from serial port"""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.connection_status.emit(False, "Disconnected")
        
    def _read_serial(self):
        """Read data from serial port in separate thread"""
        buffer = ""
        
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Look for complete JSON objects
                    while '{' in buffer and '}' in buffer:
                        start = buffer.find('{')
                        end = buffer.find('}', start) + 1
                        
                        if start != -1 and end > start:
                            json_str = buffer[start:end]
                            buffer = buffer[end:]
                            
                            try:
                                json_data = json.loads(json_str)
                                self.data_received.emit(json_data)
                            except json.JSONDecodeError:
                                pass  # Skip invalid JSON
                        else:
                            break
                            
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                if self.running:  # Only emit error if we're supposed to be running
                    self.connection_status.emit(False, f"Read error: {str(e)}")
                break

class OBD2Monitor(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.vehicle_data = VehicleData()
        self.serial_worker = SerialWorker()
        
        self.init_ui()
        self.setup_connections()
        self.setup_timer()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Husqvarna Svartpilen 401 OBD2 Monitor")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            .value-label {
                font-size: 24px;
                font-weight: bold;
                color: #00ff00;
            }
            .unit-label {
                font-size: 14px;
                color: #cccccc;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3b3b3b;
                color: white;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Connection controls
        connection_group = self.create_connection_controls()
        main_layout.addWidget(connection_group)
        
        # Data display
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Vehicle data
        vehicle_panel = self.create_vehicle_data_panel()
        splitter.addWidget(vehicle_panel)
        
        # Right panel - System info
        system_panel = self.create_system_info_panel()
        splitter.addWidget(system_panel)
        
        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Please connect to serial port")
        
    def create_connection_controls(self):
        """Create serial connection controls"""
        group = QGroupBox("Serial Connection")
        layout = QHBoxLayout(group)
        
        layout.addWidget(QLabel("Port:"))
        
        self.port_combo = QComboBox()
        self.refresh_ports()
        layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        layout.addStretch()
        
        return group
        
    def create_vehicle_data_panel(self):
        """Create vehicle data display panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Engine data
        engine_group = QGroupBox("Engine Data")
        engine_layout = QGridLayout(engine_group)
        
        # RPM
        engine_layout.addWidget(QLabel("RPM:"), 0, 0)
        self.rpm_value = QLabel("0")
        self.rpm_value.setProperty("class", "value-label")
        engine_layout.addWidget(self.rpm_value, 0, 1)
        engine_layout.addWidget(QLabel("RPM"), 0, 2)
        
        # Speed
        engine_layout.addWidget(QLabel("Speed:"), 1, 0)
        self.speed_value = QLabel("0")
        self.speed_value.setProperty("class", "value-label")
        engine_layout.addWidget(self.speed_value, 1, 1)
        engine_layout.addWidget(QLabel("km/h"), 1, 2)
        
        # Coolant Temperature
        engine_layout.addWidget(QLabel("Coolant Temp:"), 2, 0)
        self.coolant_value = QLabel("0")
        self.coolant_value.setProperty("class", "value-label")
        engine_layout.addWidget(self.coolant_value, 2, 1)
        engine_layout.addWidget(QLabel("deg C"), 2, 2)
        
        # Throttle Position
        engine_layout.addWidget(QLabel("Throttle:"), 3, 0)
        self.throttle_value = QLabel("0")
        self.throttle_value.setProperty("class", "value-label")
        engine_layout.addWidget(self.throttle_value, 3, 1)
        engine_layout.addWidget(QLabel("%"), 3, 2)
        
        layout.addWidget(engine_group)
        layout.addStretch()
        
        return widget
        
    def create_system_info_panel(self):
        """Create system information panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # System Status
        system_group = QGroupBox("System Status")
        system_layout = QGridLayout(system_group)
        
        system_layout.addWidget(QLabel("State:"), 0, 0)
        self.system_state = QLabel("UNKNOWN")
        system_layout.addWidget(self.system_state, 0, 1)
        
        system_layout.addWidget(QLabel("WiFi:"), 1, 0)
        self.wifi_status = QLabel("Disconnected")
        system_layout.addWidget(self.wifi_status, 1, 1)
        
        system_layout.addWidget(QLabel("Signal:"), 2, 0)
        self.wifi_signal = QLabel("0 dBm")
        system_layout.addWidget(self.wifi_signal, 2, 1)
        
        system_layout.addWidget(QLabel("Last Update:"), 3, 0)
        self.last_update = QLabel("Never")
        system_layout.addWidget(self.last_update, 3, 1)
        
        layout.addWidget(system_group)
        
        # Raw Data Log
        log_group = QGroupBox("Raw Data Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Consolas", 8))
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        return widget
        
    def setup_connections(self):
        """Setup signal connections"""
        self.serial_worker.data_received.connect(self.on_data_received)
        self.serial_worker.connection_status.connect(self.on_connection_status)
        
    def setup_timer(self):
        """Setup update timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # Update every 100ms
        
    def refresh_ports(self):
        """Refresh available serial ports"""
        import serial.tools.list_ports
        
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")
            
    def toggle_connection(self):
        """Toggle serial connection"""
        if self.connect_btn.text() == "Connect":
            port_text = self.port_combo.currentText()
            if port_text:
                port = port_text.split(" - ")[0]
                self.serial_worker.connect_serial(port)
        else:
            self.serial_worker.disconnect_serial()
            
    def on_data_received(self, data):
        """Handle received data from ESP32"""
        try:
            # Update vehicle data
            self.vehicle_data.timestamp = data.get('timestamp', 0)
            self.vehicle_data.rpm = data.get('rpm', 0)
            self.vehicle_data.speed = data.get('speed', 0)
            self.vehicle_data.coolant_temp = data.get('coolant_temp', 0)
            self.vehicle_data.throttle_position = data.get('throttle_position', 0)
            self.vehicle_data.system_state = data.get('system_state', 'UNKNOWN')
            self.vehicle_data.wifi_connected = data.get('wifi_connected', False)
            self.vehicle_data.wifi_rssi = data.get('wifi_rssi', 0)
            
            # Add to log
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] {json.dumps(data, indent=2)}")
            
            # Keep log size manageable
            if self.log_text.document().blockCount() > 100:
                cursor = self.log_text.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 20)
                cursor.removeSelectedText()
                
        except Exception as e:
            print(f"Error processing data: {e}")
            
    def on_connection_status(self, connected, message):
        """Handle connection status changes"""
        self.status_bar.showMessage(message)
        
        if connected:
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet("background-color: #f44336;")
        else:
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet("background-color: #4CAF50;")
            
    def update_display(self):
        """Update display with current data"""
        # Update values
        self.rpm_value.setText(str(self.vehicle_data.rpm))
        self.speed_value.setText(str(self.vehicle_data.speed))
        self.coolant_value.setText(str(self.vehicle_data.coolant_temp))
        self.throttle_value.setText(str(self.vehicle_data.throttle_position))
        
        # Update system info
        self.system_state.setText(self.vehicle_data.system_state)
        
        wifi_text = "Connected" if self.vehicle_data.wifi_connected else "Disconnected"
        self.wifi_status.setText(wifi_text)
        self.wifi_signal.setText(f"{self.vehicle_data.wifi_rssi} dBm")
        
        # Update timestamp
        if self.vehicle_data.timestamp > 0:
            self.last_update.setText(datetime.now().strftime("%H:%M:%S"))
            
    def closeEvent(self, event):
        """Handle application close"""
        self.serial_worker.disconnect_serial()
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Svartpilen 401 OBD2 Monitor")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = OBD2Monitor()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()