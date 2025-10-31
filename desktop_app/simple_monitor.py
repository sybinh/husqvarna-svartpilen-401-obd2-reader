#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple OBD2 Monitor - File-based version
Reads OBD2 data from JSON file for testing without serial ports
"""

import sys
import json
import time
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QGroupBox, QGridLayout,
                             QPushButton, QStatusBar, QTextEdit, QSplitter)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

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

class SimpleOBD2Monitor(QMainWindow):
    """Simple OBD2 monitor reading from JSON file"""
    
    def __init__(self, data_file="obd2_data.json"):
        super().__init__()
        self.data_file = data_file
        self.vehicle_data = VehicleData()
        self.last_modified = 0
        
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Husqvarna Svartpilen 401 OBD2 Monitor (Simple)")
        self.setGeometry(100, 100, 800, 600)
        
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
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Info panel
        info_group = QGroupBox("Data Source")
        info_layout = QHBoxLayout(info_group)
        info_layout.addWidget(QLabel(f"Reading from: {self.data_file}"))
        
        self.refresh_btn = QPushButton("Force Refresh")
        self.refresh_btn.clicked.connect(self.read_data_file)
        info_layout.addWidget(self.refresh_btn)
        
        main_layout.addWidget(info_group)
        
        # Data display
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Vehicle data
        vehicle_panel = self.create_vehicle_data_panel()
        splitter.addWidget(vehicle_panel)
        
        # Right panel - System info
        system_panel = self.create_system_info_panel()
        splitter.addWidget(system_panel)
        
        splitter.setSizes([500, 300])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Reading from {self.data_file}")
        
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
        
        # Raw Data Display
        data_group = QGroupBox("Raw Data")
        data_layout = QVBoxLayout(data_group)
        
        self.data_text = QTextEdit()
        self.data_text.setMaximumHeight(200)
        self.data_text.setFont(QFont("Consolas", 8))
        self.data_text.setReadOnly(True)
        data_layout.addWidget(self.data_text)
        
        layout.addWidget(data_group)
        
        return widget
        
    def setup_timer(self):
        """Setup update timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_data_file)
        self.update_timer.start(500)  # Check every 500ms
        
    def check_data_file(self):
        """Check if data file has been updated"""
        try:
            if os.path.exists(self.data_file):
                modified = os.path.getmtime(self.data_file)
                if modified > self.last_modified:
                    self.last_modified = modified
                    self.read_data_file()
            else:
                self.status_bar.showMessage(f"Waiting for {self.data_file}...")
        except Exception as e:
            self.status_bar.showMessage(f"Error checking file: {e}")
            
    def read_data_file(self):
        """Read data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                # Update vehicle data
                self.vehicle_data.timestamp = data.get('timestamp', 0)
                self.vehicle_data.rpm = data.get('rpm', 0)
                self.vehicle_data.speed = data.get('speed', 0)
                self.vehicle_data.coolant_temp = data.get('coolant_temp', 0)
                self.vehicle_data.throttle_position = data.get('throttle_position', 0)
                self.vehicle_data.system_state = data.get('system_state', 'UNKNOWN')
                self.vehicle_data.wifi_connected = data.get('wifi_connected', False)
                self.vehicle_data.wifi_rssi = data.get('wifi_rssi', 0)
                
                # Update display
                self.update_display()
                
                # Update raw data display
                self.data_text.clear()
                self.data_text.append(json.dumps(data, indent=2))
                
                # Update status
                self.status_bar.showMessage(f"Data updated: {datetime.now().strftime('%H:%M:%S')}")
                
        except Exception as e:
            self.status_bar.showMessage(f"Error reading file: {e}")
            
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
            dt = datetime.fromtimestamp(self.vehicle_data.timestamp)
            self.last_update.setText(dt.strftime("%H:%M:%S"))

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Svartpilen 401 OBD2 Monitor (Simple)")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = SimpleOBD2Monitor()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()