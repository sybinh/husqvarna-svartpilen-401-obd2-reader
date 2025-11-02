#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Models for OBD2 Monitor
Defines the data structures used throughout the application
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SystemState(Enum):
    """System operation states"""
    UNKNOWN = "UNKNOWN"
    ENGINE_OFF = "ENGINE_OFF"
    STOPPED = "STOPPED"  # Engine stopped/off
    IDLE = "IDLE"
    ACCELERATING = "ACCELERATING"
    CONNECTED = "CONNECTED"  # Normal running/connected
    CITY = "CITY"
    HIGHWAY = "HIGHWAY"
    COOLING = "COOLING"

@dataclass
class VehicleData:
    """Vehicle data structure"""
    timestamp: int = 0
    rpm: int = 0
    speed: int = 0
    coolant_temp: int = 0
    throttle_position: int = 0
    system_state: SystemState = SystemState.UNKNOWN
    wifi_connected: bool = False
    wifi_rssi: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VehicleData':
        """Create VehicleData from dictionary"""
        # Convert float to int for numeric fields
        return cls(
            timestamp=int(data.get('timestamp', 0)),
            rpm=int(data.get('rpm', 0)),
            speed=int(data.get('speed', 0)),
            coolant_temp=int(float(data.get('coolant_temp', 0))),
            throttle_position=int(data.get('throttle_position', 0)),
            system_state=SystemState(data.get('system_state', 'UNKNOWN')),
            wifi_connected=bool(data.get('wifi_connected', False)),
            wifi_rssi=int(data.get('wifi_rssi', 0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'rpm': self.rpm,
            'speed': self.speed,
            'coolant_temp': self.coolant_temp,
            'throttle_position': self.throttle_position,
            'system_state': self.system_state.value,
            'wifi_connected': self.wifi_connected,
            'wifi_rssi': self.wifi_rssi
        }
    
    def is_valid(self) -> bool:
        """Check if data is valid"""
        return (
            0 <= self.rpm <= 10000 and
            0 <= self.speed <= 300 and
            -40 <= self.coolant_temp <= 150 and
            0 <= self.throttle_position <= 100 and
            -100 <= self.wifi_rssi <= 0
        )

@dataclass
class ConnectionConfig:
    """Connection configuration"""
    serial_port: str = ""
    baudrate: int = 115200
    timeout: float = 1.0
    auto_reconnect: bool = True
    
@dataclass
class AppSettings:
    """Application settings"""
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    update_interval: int = 100  # milliseconds
    log_level: str = "INFO"
    theme: str = "dark"
    save_data: bool = False
    data_file: str = "obd2_data.log"