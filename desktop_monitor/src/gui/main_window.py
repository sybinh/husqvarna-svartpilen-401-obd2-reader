#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window for OBD2 Monitor
Professional PyQt6 GUI for monitoring vehicle data
"""

import logging
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QGroupBox, QGridLayout, QComboBox, QPushButton, 
    QStatusBar, QTextEdit, QSplitter, QTabWidget, QMenuBar,
    QMessageBox, QApplication, QCheckBox
)
from PyQt6.QtCore import QTimer, Qt, pyqtSlot
from PyQt6.QtGui import QFont, QAction, QIcon, QTextCharFormat, QColor, QSyntaxHighlighter
from PyQt6.QtCore import QSettings, QRegularExpression

from ..data.models import VehicleData, ConnectionConfig, AppSettings
from ..data.handler import DataHandler, FileDataHandler
from ..utils.logger import setup_logging
from .styles import DARK_THEME

logger = logging.getLogger(__name__)


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define formats
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#569CD6"))  # Blue for keys
        self.key_format.setFontWeight(QFont.Weight.Bold)
        
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#CE9178"))  # Orange for strings
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#B5CEA8"))  # Green for numbers
        
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#569CD6"))  # Blue for booleans
        
        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("#808080"))  # Gray for null
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Highlight JSON keys
        key_pattern = QRegularExpression(r'"([^"]+)"\s*:')
        iterator = key_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.key_format)
        
        # Highlight strings
        string_pattern = QRegularExpression(r':\s*"([^"]*)"')
        iterator = string_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(1) - 1, match.capturedLength(1) + 2, self.string_format)
        
        # Highlight numbers
        number_pattern = QRegularExpression(r':\s*(-?\d+\.?\d*)')
        iterator = number_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(1), match.capturedLength(1), self.number_format)
        
        # Highlight booleans
        boolean_pattern = QRegularExpression(r'\b(true|false)\b')
        iterator = boolean_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.boolean_format)
        
        # Highlight null
        null_pattern = QRegularExpression(r'\bnull\b')
        iterator = null_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.null_format)

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
        
        # Raw data filters
        self.show_json = True
        self.show_can = True
        self.auto_scroll = True
        
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
        
        # Status bar (create early, before other widgets that might use it)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Initializing...")
        
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
        
        # Raw data tab (JSON formatted)
        raw_data_tab = self.create_raw_data_tab()
        self.tab_widget.addTab(raw_data_tab, "Raw Data (JSON)")
        
        # CAN Monitor tab
        can_monitor_tab = self.create_can_monitor_tab()
        self.tab_widget.addTab(can_monitor_tab, "CAN Monitor")
        
        main_layout.addWidget(self.tab_widget)
        
        # Update status bar
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
        self.source_combo.addItems(["BLE (Bluetooth)", "Serial Port", "File Monitor"])
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        layout.addWidget(self.source_combo)
        
        # Port/File/Device selection
        layout.addWidget(QLabel("Device:"))
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(300)
        layout.addWidget(self.port_combo)
        
        # Refresh/Scan button
        self.refresh_btn = QPushButton("Scan")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        # Connection status indicator
        self.connection_status_label = QLabel("● Disconnected")
        self.connection_status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        layout.addWidget(self.connection_status_label)
        
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
        engine_layout.addWidget(QLabel("�C"), 2, 2)
        
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
        """Create raw data display tab with JSON formatting"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Format toggle
        self.format_json_check = QCheckBox("Pretty Format")
        self.format_json_check.setChecked(True)
        controls_layout.addWidget(self.format_json_check)
        
        # Auto-scroll toggle
        self.auto_scroll_check = QCheckBox("Auto Scroll")
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.stateChanged.connect(self.on_auto_scroll_changed)
        controls_layout.addWidget(self.auto_scroll_check)
        
        # Clear button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_raw_data)
        controls_layout.addWidget(clear_btn)
        
        # Export button
        export_btn = QPushButton("Export to File")
        export_btn.clicked.connect(self.export_raw_data)
        controls_layout.addWidget(export_btn)
        
        controls_layout.addStretch()
        
        # Data count label
        self.raw_data_count_label = QLabel("Messages: 0")
        controls_layout.addWidget(self.raw_data_count_label)
        
        layout.addLayout(controls_layout)
        
        # Raw data display with syntax highlighting
        self.raw_data_text = QTextEdit()
        self.raw_data_text.setFont(QFont("Consolas", 10))
        self.raw_data_text.setReadOnly(True)
        self.raw_data_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Apply JSON syntax highlighter
        self.json_highlighter = JsonSyntaxHighlighter(self.raw_data_text.document())
        
        layout.addWidget(self.raw_data_text)
        
        # Message counter
        self.raw_data_count = 0
        
        return widget
        
    def create_can_monitor_tab(self):
        """Create CAN bus monitor tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Filter controls
        controls_layout.addWidget(QLabel("Filter PID:"))
        self.can_filter_combo = QComboBox()
        self.can_filter_combo.addItems([
            "All PIDs",
            "0x0C - Engine RPM",
            "0x0D - Vehicle Speed",
            "0x05 - Coolant Temp",
            "0x11 - Throttle Position",
            "0x0F - Intake Air Temp",
            "0x04 - Engine Load"
        ])
        self.can_filter_combo.currentTextChanged.connect(self.on_can_filter_changed)
        controls_layout.addWidget(self.can_filter_combo)
        
        # Show requests toggle
        self.show_requests_check = QCheckBox("Show Requests")
        self.show_requests_check.setChecked(True)
        controls_layout.addWidget(self.show_requests_check)
        
        # Show responses toggle
        self.show_responses_check = QCheckBox("Show Responses")
        self.show_responses_check.setChecked(True)
        controls_layout.addWidget(self.show_responses_check)
        
        # Clear button
        clear_can_btn = QPushButton("Clear")
        clear_can_btn.clicked.connect(self.clear_can_monitor)
        controls_layout.addWidget(clear_can_btn)
        
        controls_layout.addStretch()
        
        # Frame count
        self.can_frame_count_label = QLabel("Frames: 0")
        controls_layout.addWidget(self.can_frame_count_label)
        
        layout.addLayout(controls_layout)
        
        # CAN frames display
        self.can_monitor_text = QTextEdit()
        self.can_monitor_text.setFont(QFont("Consolas", 9))
        self.can_monitor_text.setReadOnly(True)
        self.can_monitor_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Add header
        header = "TIME          ID    DLC  DATA                            TYPE       DESCRIPTION\n"
        header += "=" * 100 + "\n"
        self.can_monitor_text.append(header)
        
        layout.addWidget(self.can_monitor_text)
        
        # Frame counter
        self.can_frame_count = 0
        
        return widget
        
    def setup_data_handlers(self):
        """Setup data handlers"""
        config = ConnectionConfig()
        self.serial_handler = DataHandler(config)
        self.serial_handler.data_received.connect(self.on_data_received)
        self.serial_handler.connection_status_changed.connect(self.on_connection_status_changed)
        self.serial_handler.error_occurred.connect(self.on_error_occurred)
        self.serial_handler.devices_discovered.connect(self.on_ble_devices_discovered)
        
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(self.app_settings.update_interval)
        
    def refresh_ports(self):
        """Refresh available ports/files/BLE devices"""
        self.port_combo.clear()
        source = self.source_combo.currentText()
        
        if source == "BLE (Bluetooth)":
            # Show scanning message
            self.port_combo.addItem("Scanning for BLE devices...", None)
            self.refresh_btn.setEnabled(False)
            self.status_bar.showMessage("Scanning for BLE devices (20s timeout - please wait after disconnect)...")
            
            # Start BLE scan with LONG timeout for Windows BLE cache issues
            if self.serial_handler and self.serial_handler.is_ble_available():
                self.serial_handler.scan_ble_devices(timeout=20.0)  # Increased from 10s to 20s
            else:
                self.port_combo.clear()
                self.port_combo.addItem("BLE not available (install bleak)", None)
                self.refresh_btn.setEnabled(True)
                self.status_bar.showMessage("BLE support not available")
                
        elif source == "Serial Port":
            ports = self.serial_handler.get_available_ports()
            if ports:
                for port in ports:
                    display_text = f"{port['device']} - {port['description']}"
                    self.port_combo.addItem(display_text, port['device'])
            else:
                self.port_combo.addItem("No serial ports found", None)
        else:
            # File monitor mode
            self.port_combo.addItem("obd2_data.json", "obd2_data.json")
            
    @pyqtSlot(list)
    def on_ble_devices_discovered(self, devices: list):
        """Handle BLE device discovery"""
        self.port_combo.clear()
        self.refresh_btn.setEnabled(True)
        
        if devices:
            for device in devices:
                # Highlight ESP32 devices
                name = device['name']
                address = device['address']
                rssi = device['rssi']
                
                if 'Svartpilen' in name or 'OBD2' in name or 'ESP32' in name:
                    display_text = f"★ {name} ({address}) RSSI: {rssi} dBm"
                else:
                    display_text = f"{name} ({address}) RSSI: {rssi} dBm"
                    
                self.port_combo.addItem(display_text, address)
                
            self.status_bar.showMessage(f"Found {len(devices)} BLE devices")
        else:
            self.port_combo.addItem("No BLE devices found", None)
            self.status_bar.showMessage("No BLE devices found. Try scanning again.")
            
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
        source = self.source_combo.currentText()
        
        if source == "BLE (Bluetooth)":
            # Connect via BLE
            if self.port_combo.count() > 0:
                address = self.port_combo.currentData()
                if address:
                    self.status_bar.showMessage(f"Connecting to BLE device {address}...")
                    self.serial_handler.connect_ble(address)
                else:
                    QMessageBox.warning(self, "No Device", "Please scan for BLE devices first")
                    
        elif source == "Serial Port":
            # Connect via Serial
            if self.port_combo.count() > 0:
                port = self.port_combo.currentData()
                if port:
                    self.serial_handler.connect_serial(port)
                else:
                    QMessageBox.warning(self, "No Port", "No serial port selected")
        else:
            # File monitor
            file_path = self.port_combo.currentData()
            if file_path:
                # Playback at 10x speed for faster testing
                self.file_handler = FileDataHandler(file_path, playback_speed=10.0)
                self.file_handler.data_received.connect(self.on_data_received)
                self.file_handler.error_occurred.connect(self.on_error_occurred)
                self.file_handler.start_monitoring()
                self.on_connection_status_changed(True, f"Monitoring {file_path} (10x speed)")
                
    def disconnect_from_source(self):
        """Disconnect from data source"""
        source = self.source_combo.currentText()
        
        if self.serial_handler:
            self.serial_handler.disconnect()
            
        if self.file_handler:
            self.file_handler.stop_monitoring()
            self.file_handler = None
            self.on_connection_status_changed(False, "Disconnected")
        
        # Show helpful message for BLE users
        if source == "BLE (Bluetooth)":
            self.status_bar.showMessage("Disconnected. Wait 3-5 seconds before scanning again for ESP32 to restart advertising.", 5000)
            
    @pyqtSlot(VehicleData)
    def on_data_received(self, data: VehicleData):
        """Handle received vehicle data"""
        self.current_data = data
        
        # Add to raw data log (JSON formatted)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Convert to dict and format as JSON
        data_dict = data.to_dict()
        
        if self.format_json_check.isChecked():
            # Pretty print JSON
            json_str = json.dumps(data_dict, indent=2)
            log_entry = f"[{timestamp}]\n{json_str}\n{'-'*80}\n"
        else:
            # Compact JSON
            json_str = json.dumps(data_dict)
            log_entry = f"[{timestamp}] {json_str}\n"
        
        self.raw_data_text.append(log_entry)
        self.raw_data_count += 1
        self.raw_data_count_label.setText(f"Messages: {self.raw_data_count}")
        
        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            scrollbar = self.raw_data_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        # Keep log size manageable (limit to 500 messages)
        if self.raw_data_text.document().blockCount() > 2000:
            cursor = self.raw_data_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 200)
            cursor.removeSelectedText()
            self.raw_data_count -= 50
        
        # Simulate CAN frames for demonstration
        # In real implementation, this would come from actual CAN bus monitoring
        self.add_simulated_can_frames(data)
            
    @pyqtSlot(bool, str)
    @pyqtSlot(bool, str)
    def on_connection_status_changed(self, connected: bool, message: str):
        """Handle connection status changes"""
        self.status_bar.showMessage(message)
        
        if connected:
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet("background-color: #f44336;")
            self.connection_status_label.setText("● Connected")
            self.connection_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet("background-color: #4CAF50;")
            self.connection_status_label.setText("● Disconnected")
            self.connection_status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            
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
            # Convert milliseconds to seconds for datetime
            timestamp_sec = self.current_data.timestamp / 1000.0
            dt = datetime.fromtimestamp(timestamp_sec)
            self.last_update.setText(dt.strftime("%H:%M:%S"))
            
    def clear_raw_data(self):
        """Clear raw data log"""
        self.raw_data_text.clear()
        self.raw_data_count = 0
        self.raw_data_count_label.setText("Messages: 0")
        
    def clear_can_monitor(self):
        """Clear CAN monitor log"""
        self.can_monitor_text.clear()
        # Re-add header
        header = "TIME          ID    DLC  DATA                            TYPE       DESCRIPTION\n"
        header += "=" * 100 + "\n"
        self.can_monitor_text.append(header)
        self.can_frame_count = 0
        self.can_frame_count_label.setText("Frames: 0")
        
    def on_auto_scroll_changed(self, state):
        """Handle auto-scroll toggle"""
        self.auto_scroll = (state == Qt.CheckState.Checked.value)
        
    def on_can_filter_changed(self, text):
        """Handle CAN filter change"""
        # Filter logic would be applied when adding CAN frames
        pass
        
    def export_raw_data(self):
        """Export raw data to file"""
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Raw Data", "", "Text Files (*.txt);;JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.raw_data_text.toPlainText())
                self.status_bar.showMessage(f"Exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
                
    def add_simulated_can_frames(self, data: VehicleData):
        """Add simulated CAN frames based on vehicle data
        In real implementation, this would capture actual CAN bus traffic"""
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Map of PID to description
        pid_descriptions = {
            "0C": "Engine RPM",
            "0D": "Vehicle Speed",
            "05": "Coolant Temperature",
            "11": "Throttle Position",
            "0F": "Intake Air Temp",
            "04": "Engine Load"
        }
        
        # Simulate request/response pairs for non-zero values
        frames = []
        
        if data.rpm > 0:
            # RPM request: 02 01 0C
            frames.append({
                "id": "7DF", "dlc": 8, 
                "data": "02 01 0C 00 00 00 00 00",
                "type": "REQUEST", "desc": "Query Engine RPM"
            })
            # RPM response: 04 41 0C [A] [B]
            rpm_a = (data.rpm * 4) >> 8
            rpm_b = (data.rpm * 4) & 0xFF
            frames.append({
                "id": "7E8", "dlc": 8,
                "data": f"04 41 0C {rpm_a:02X} {rpm_b:02X} 00 00 00",
                "type": "RESPONSE", "desc": f"Engine RPM = {data.rpm}"
            })
            
        if data.speed > 0:
            # Speed request
            frames.append({
                "id": "7DF", "dlc": 8,
                "data": "02 01 0D 00 00 00 00 00",
                "type": "REQUEST", "desc": "Query Vehicle Speed"
            })
            # Speed response
            frames.append({
                "id": "7E8", "dlc": 8,
                "data": f"03 41 0D {data.speed:02X} 00 00 00 00",
                "type": "RESPONSE", "desc": f"Speed = {data.speed} km/h"
            })
            
        if data.coolant_temp > -40:
            # Coolant temp request
            frames.append({
                "id": "7DF", "dlc": 8,
                "data": "02 01 05 00 00 00 00 00",
                "type": "REQUEST", "desc": "Query Coolant Temp"
            })
            # Coolant response (value + 40)
            temp_val = data.coolant_temp + 40
            frames.append({
                "id": "7E8", "dlc": 8,
                "data": f"03 41 05 {temp_val:02X} 00 00 00 00",
                "type": "RESPONSE", "desc": f"Coolant = {data.coolant_temp}°C"
            })
            
        if data.throttle_position > 0:
            # Throttle request
            frames.append({
                "id": "7DF", "dlc": 8,
                "data": "02 01 11 00 00 00 00 00",
                "type": "REQUEST", "desc": "Query Throttle Position"
            })
            # Throttle response (percentage * 255 / 100)
            throttle_val = int(data.throttle_position * 255 / 100)
            frames.append({
                "id": "7E8", "dlc": 8,
                "data": f"03 41 11 {throttle_val:02X} 00 00 00 00",
                "type": "RESPONSE", "desc": f"Throttle = {data.throttle_position}%"
            })
        
        # Add frames to CAN monitor
        for frame in frames:
            # Apply filters
            if not self.show_requests_check.isChecked() and frame["type"] == "REQUEST":
                continue
            if not self.show_responses_check.isChecked() and frame["type"] == "RESPONSE":
                continue
                
            # Format: TIME  ID  DLC  DATA  TYPE  DESC
            can_line = f"{timestamp}  {frame['id']}  {frame['dlc']}    {frame['data']}  {frame['type']:10} {frame['desc']}\n"
            
            # Color coding
            if frame['type'] == 'REQUEST':
                # Requests in cyan
                self.can_monitor_text.setTextColor(QColor("#00BCD4"))
            else:
                # Responses in green
                self.can_monitor_text.setTextColor(QColor("#4CAF50"))
                
            self.can_monitor_text.insertPlainText(can_line)
            self.can_monitor_text.setTextColor(QColor("#FFFFFF"))  # Reset to white
            
            self.can_frame_count += 1
        
        self.can_frame_count_label.setText(f"Frames: {self.can_frame_count}")
        
        # Auto-scroll CAN monitor
        scrollbar = self.can_monitor_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Keep CAN log manageable
        if self.can_monitor_text.document().blockCount() > 2000:
            cursor = self.can_monitor_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 200)
            cursor.removeSelectedText()
            self.can_frame_count -= 100
        
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