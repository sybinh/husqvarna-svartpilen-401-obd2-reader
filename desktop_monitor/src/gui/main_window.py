#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window for OBD2 Monitor
Professional PyQt6 GUI for monitoring vehicle data
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QGroupBox, QGridLayout, QComboBox, QPushButton, 
    QStatusBar, QTextEdit, QSplitter, QTabWidget, QMenuBar,
    QMessageBox, QApplication
)
from PyQt6.QtCore import QTimer, Qt, pyqtSlot
from PyQt6.QtGui import QFont, QAction, QIcon
from PyQt6.QtCore import QSettings

from ..data.models import VehicleData, ConnectionConfig, AppSettings
from ..data.handler import DataHandler, FileDataHandler
from ..utils.logger import setup_logging
from .styles import DARK_THEME

logger = logging.getLogger(__name__)

class OBD2MonitorMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize logging
        setup_logging()
        
        # Application state
        self.settings = QSettings()
        self.app_settings = AppSettings()
        self.current_data = VehicleData()
        
        # Data handlers
        self.serial_handler: DataHandler = None
        self.file_handler: FileDataHandler = None
        
        # UI components
        self.setup_ui()
        self.setup_menu()
        self.setup_data_handlers()
        self.setup_timers()
        self.load_settings()
        
        logger.info("OBD2 Monitor started")
        
    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Husqvarna Svartpilen 401 OBD2 Monitor")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Apply dark theme
        self.setStyleSheet(DARK_THEME)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Connection controls
        connection_group = self.create_connection_controls()
        main_layout.addWidget(connection_group)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Dashboard tab
        dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(dashboard_tab, "Dashboard")
        
        # Raw data tab
        raw_data_tab = self.create_raw_data_tab()
        self.tab_widget.addTab(raw_data_tab, "Raw Data")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Please connect to data source")
        
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        simulator_action = QAction("Start &Simulator", self)
        simulator_action.triggered.connect(self.start_simulator)
        tools_menu.addAction(simulator_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_connection_controls(self):
        """Create connection control panel"""
        group = QGroupBox("Connection")
        layout = QHBoxLayout(group)
        
        # Source selection
        layout.addWidget(QLabel("Source:"))
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Serial Port", "File Monitor"])
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        layout.addWidget(self.source_combo)
        
        # Port/File selection
        layout.addWidget(QLabel("Port/File:"))
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        layout.addWidget(self.port_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        layout.addStretch()
        
        # Initialize port list
        self.refresh_ports()
        
        return group
        
    def create_dashboard_tab(self):
        """Create main dashboard tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Vehicle data panel
        vehicle_panel = self.create_vehicle_data_panel()
        
        # System info panel
        system_panel = self.create_system_info_panel()
        
        # Add to splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(vehicle_panel)
        splitter.addWidget(system_panel)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
        return widget
        
    def create_vehicle_data_panel(self):
        """Create vehicle data display panel"""
        group = QGroupBox("Vehicle Data")
        layout = QVBoxLayout(group)
        
        # Engine data grid
        engine_group = QGroupBox("Engine Parameters")
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
        engine_layout.addWidget(QLabel("°C"), 2, 2)
        
        # Throttle Position
        engine_layout.addWidget(QLabel("Throttle:"), 3, 0)
        self.throttle_value = QLabel("0")
        self.throttle_value.setProperty("class", "value-label")
        engine_layout.addWidget(self.throttle_value, 3, 1)
        engine_layout.addWidget(QLabel("%"), 3, 2)
        
        layout.addWidget(engine_group)
        layout.addStretch()
        
        return group
        
    def create_system_info_panel(self):
        """Create system information panel"""
        group = QGroupBox("System Information")
        layout = QVBoxLayout(group)
        
        # System status grid
        status_group = QGroupBox("Status")
        status_layout = QGridLayout(status_group)
        
        status_layout.addWidget(QLabel("State:"), 0, 0)
        self.system_state = QLabel("UNKNOWN")
        status_layout.addWidget(self.system_state, 0, 1)
        
        status_layout.addWidget(QLabel("WiFi:"), 1, 0)
        self.wifi_status = QLabel("Disconnected")
        status_layout.addWidget(self.wifi_status, 1, 1)
        
        status_layout.addWidget(QLabel("Signal:"), 2, 0)
        self.wifi_signal = QLabel("0 dBm")
        status_layout.addWidget(self.wifi_signal, 2, 1)
        
        status_layout.addWidget(QLabel("Last Update:"), 3, 0)
        self.last_update = QLabel("Never")
        status_layout.addWidget(self.last_update, 3, 1)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        return group
        
    def create_raw_data_tab(self):
        """Create raw data display tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_raw_data)
        controls_layout.addWidget(clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Raw data display
        self.raw_data_text = QTextEdit()
        self.raw_data_text.setFont(QFont("Consolas", 9))
        self.raw_data_text.setReadOnly(True)
        layout.addWidget(self.raw_data_text)
        
        return widget
        
    def setup_data_handlers(self):
        """Setup data handlers"""
        config = ConnectionConfig()
        self.serial_handler = DataHandler(config)
        self.serial_handler.data_received.connect(self.on_data_received)
        self.serial_handler.connection_status_changed.connect(self.on_connection_status_changed)
        self.serial_handler.error_occurred.connect(self.on_error_occurred)
        
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(self.app_settings.update_interval)
        
    def refresh_ports(self):
        """Refresh available ports/files"""
        self.port_combo.clear()
        
        if self.source_combo.currentText() == "Serial Port":
            ports = self.serial_handler.get_available_ports()
            for port in ports:
                display_text = f"{port['device']} - {port['description']}"
                self.port_combo.addItem(display_text, port['device'])
        else:
            # File monitor mode
            self.port_combo.addItem("obd2_data.json", "obd2_data.json")
            
    def on_source_changed(self, source: str):
        """Handle source type change"""
        self.refresh_ports()
        
    def toggle_connection(self):
        """Toggle connection to data source"""
        if self.connect_btn.text() == "Connect":
            self.connect_to_source()
        else:
            self.disconnect_from_source()
            
    def connect_to_source(self):
        """Connect to selected data source"""
        if self.source_combo.currentText() == "Serial Port":
            if self.port_combo.count() > 0:
                port = self.port_combo.currentData()
                if port:
                    self.serial_handler.connect_serial(port)
        else:
            # File monitor
            file_path = self.port_combo.currentData()
            if file_path:
                self.file_handler = FileDataHandler(file_path)
                self.file_handler.data_received.connect(self.on_data_received)
                self.file_handler.error_occurred.connect(self.on_error_occurred)
                self.file_handler.start_monitoring()
                self.on_connection_status_changed(True, f"Monitoring {file_path}")
                
    def disconnect_from_source(self):
        """Disconnect from data source"""
        if self.serial_handler:
            self.serial_handler.disconnect()
            
        if self.file_handler:
            self.file_handler.stop_monitoring()
            self.file_handler = None
            self.on_connection_status_changed(False, "Disconnected")
            
    @pyqtSlot(VehicleData)
    def on_data_received(self, data: VehicleData):
        """Handle received vehicle data"""
        self.current_data = data
        
        # Add to raw data log
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {data.to_dict()}\n"
        self.raw_data_text.append(log_entry)
        
        # Keep log size manageable
        if self.raw_data_text.document().blockCount() > 1000:
            cursor = self.raw_data_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 100)
            cursor.removeSelectedText()
            
    @pyqtSlot(bool, str)
    def on_connection_status_changed(self, connected: bool, message: str):
        """Handle connection status changes"""
        self.status_bar.showMessage(message)
        
        if connected:
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet("background-color: #f44336;")
        else:
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet("background-color: #4CAF50;")
            
    @pyqtSlot(str)
    def on_error_occurred(self, error_message: str):
        """Handle error messages"""
        logger.error(error_message)
        self.status_bar.showMessage(f"Error: {error_message}")
        
    def update_display(self):
        """Update display with current data"""
        # Update vehicle data
        self.rpm_value.setText(str(self.current_data.rpm))
        self.speed_value.setText(str(self.current_data.speed))
        self.coolant_value.setText(str(self.current_data.coolant_temp))
        self.throttle_value.setText(str(self.current_data.throttle_position))
        
        # Update system info
        self.system_state.setText(self.current_data.system_state.value)
        
        wifi_text = "Connected" if self.current_data.wifi_connected else "Disconnected"
        self.wifi_status.setText(wifi_text)
        self.wifi_signal.setText(f"{self.current_data.wifi_rssi} dBm")
        
        # Update timestamp
        if self.current_data.timestamp > 0:
            dt = datetime.fromtimestamp(self.current_data.timestamp)
            self.last_update.setText(dt.strftime("%H:%M:%S"))
            
    def clear_raw_data(self):
        """Clear raw data log"""
        self.raw_data_text.clear()
        
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet")
        
    def start_simulator(self):
        """Start data simulator"""
        # TODO: Implement simulator launcher
        QMessageBox.information(self, "Simulator", "Simulator launcher not implemented yet")
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h3>Husqvarna Svartpilen 401 OBD2 Monitor</h3>
        <p>Version 1.0.0</p>
        <p>A comprehensive OBD2 monitoring system for motorcycle enthusiasts.</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Real-time vehicle data monitoring</li>
        <li>Professional GUI interface</li>
        <li>Serial and file data sources</li>
        <li>Extensible architecture</li>
        </ul>
        <p>Made with ?? for the Husqvarna community</p>
        """
        QMessageBox.about(self, "About", about_text)
        
    def load_settings(self):
        """Load application settings"""
        # TODO: Load settings from QSettings
        pass
        
    def save_settings(self):
        """Save application settings"""
        # TODO: Save settings to QSettings
        pass
        
    def closeEvent(self, event):
        """Handle application close"""
        self.disconnect_from_source()
        self.save_settings()
        event.accept()
        logger.info("OBD2 Monitor closed")