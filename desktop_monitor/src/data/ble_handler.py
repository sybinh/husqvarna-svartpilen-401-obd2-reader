#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLE Handler for OBD2 Monitor
Handles Bluetooth Low Energy communication with ESP32
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List
from PyQt6.QtCore import QObject, pyqtSignal, QThread

try:
    from bleak import BleakClient, BleakScanner
    from bleak.backends.characteristic import BleakGATTCharacteristic
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

from .models import VehicleData

logger = logging.getLogger(__name__)

# BLE Service UUIDs (must match ESP32 firmware)
BLE_SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
BLE_CHAR_DATA_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
BLE_CHAR_STATUS_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a9"

# Device name to look for
BLE_DEVICE_NAME = "Svartpilen401_OBD2"


class BLEHandler(QObject):
    """Handles BLE communication with ESP32"""
    
    # Signals
    data_received = pyqtSignal(VehicleData)
    connection_status_changed = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str)
    devices_discovered = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.client: Optional[BleakClient] = None
        self.connected = False
        self.running = False
        self.device_address: Optional[str] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[QThread] = None
        
        if not BLEAK_AVAILABLE:
            logger.error("Bleak library not available. Install with: pip install bleak")
            
    def is_available(self) -> bool:
        """Check if BLE is available"""
        return BLEAK_AVAILABLE
    
    async def scan_devices(self, timeout: float = 5.0) -> List[Dict]:
        """Scan for BLE devices
        
        Args:
            timeout: Scan timeout in seconds
            
        Returns:
            List of discovered devices with name, address, and RSSI
        """
        if not BLEAK_AVAILABLE:
            logger.error("Bleak library not available!")
            return []
            
        logger.info(f"Starting BLE scan (timeout: {timeout}s)...")
        logger.info("Make sure Bluetooth is enabled on your PC!")
        logger.info("TIP: Wait a few seconds after disconnect for ESP32 to restart advertising")
        devices = []
        
        try:
            # Force fresh scan by not using cache
            discovered = await BleakScanner.discover(timeout=timeout, return_adv=True)
            
            logger.info(f"Scan complete. Found {len(discovered)} devices total")
            
            for address, (device, adv_data) in discovered.items():
                device_info = {
                    'name': device.name or 'Unknown',
                    'address': device.address,
                    'rssi': adv_data.rssi if hasattr(adv_data, 'rssi') else 0
                }
                devices.append(device_info)
                
                # Log all devices but highlight ESP32
                if 'Svartpilen' in device_info['name'] or 'OBD2' in device_info['name']:
                    logger.info(f"  ★ {device_info['name']} | {device_info['address']} | RSSI: {device_info['rssi']} dBm")
                else:
                    logger.info(f"  - {device_info['name']} | {device_info['address']} | RSSI: {device_info['rssi']} dBm")
                
        except Exception as e:
            logger.error(f"BLE scan error: {e}")
            logger.exception("Full traceback:")
            
        logger.info(f"Returning {len(devices)} devices to GUI")
        return devices
    
    def scan_devices_sync(self, timeout: float = 5.0):
        """Synchronous wrapper for scanning devices - runs in separate thread for Windows"""
        if not BLEAK_AVAILABLE:
            self.error_occurred.emit("BLE not available. Install bleak library.")
            return
            
        import threading
        
        def scan_thread():
            try:
                # Create new event loop for this thread (Windows compatible)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # For Windows, ensure we use ProactorEventLoop
                import sys
                if sys.platform == 'win32':
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                devices = loop.run_until_complete(self.scan_devices(timeout))
                loop.close()
                
                self.devices_discovered.emit(devices)
                
            except Exception as e:
                error_msg = f"Failed to scan devices: {str(e)}"
                logger.error(error_msg)
                logger.exception("Scan thread error:")
                self.error_occurred.emit(error_msg)
        
        # Run scan in separate thread
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
    
    async def connect_async(self, address: str) -> bool:
        """Connect to BLE device asynchronously
        
        Args:
            address: BLE device address (MAC address)
            
        Returns:
            True if connection successful
        """
        if not BLEAK_AVAILABLE:
            return False
            
        try:
            logger.info(f"Connecting to BLE device: {address}")
            
            # Create client with disconnect callback
            self.client = BleakClient(
                address,
                disconnected_callback=self._handle_disconnect
            )
            await self.client.connect()
            
            if self.client.is_connected:
                self.connected = True
                self.device_address = address
                
                # Subscribe to data characteristic
                await self.client.start_notify(
                    BLE_CHAR_DATA_UUID,
                    self._data_notification_handler
                )
                
                # Subscribe to status characteristic
                await self.client.start_notify(
                    BLE_CHAR_STATUS_UUID,
                    self._status_notification_handler
                )
                
                logger.info(f"Connected to {address}")
                self.connection_status_changed.emit(True, f"Connected to {address}")
                
                return True
            else:
                logger.error("Connection failed")
                return False
                
        except Exception as e:
            error_msg = f"Failed to connect: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    async def disconnect_async(self):
        """Disconnect from BLE device"""
        try:
            if self.client:
                if self.client.is_connected:
                    try:
                        # Unsubscribe from notifications first
                        await self.client.stop_notify(BLE_CHAR_DATA_UUID)
                        await self.client.stop_notify(BLE_CHAR_STATUS_UUID)
                    except Exception as e:
                        logger.warning(f"Error stopping notifications: {e}")
                    
                    try:
                        # Disconnect from device
                        await self.client.disconnect()
                        logger.info("Disconnected from BLE device")
                    except Exception as e:
                        logger.warning(f"Error during disconnect: {e}")
                
                # Force cleanup by destroying client object completely
                # This helps Windows BLE send proper disconnect packet
                try:
                    del self.client
                except:
                    pass
                self.client = None
                
                # Give Windows time to send disconnect packet
                await asyncio.sleep(0.5)
                    
        except Exception as e:
            logger.error(f"Error in disconnect_async: {e}")
                
        self.connected = False
        self.connection_status_changed.emit(False, "Disconnected")
    
    def connect(self, address: str):
        """Connect to BLE device (synchronous wrapper) - runs in separate thread for Windows"""
        if not BLEAK_AVAILABLE:
            self.error_occurred.emit("BLE not available. Install bleak library.")
            return
        
        import threading
        
        def connect_thread():
            try:
                # Create new event loop for this thread (Windows compatible)
                import sys
                if sys.platform == 'win32':
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.loop = loop
                
                success = loop.run_until_complete(self.connect_async(address))
                
                if success:
                    # Keep event loop running for notifications
                    self.running = True
                    loop.run_until_complete(self._keep_alive())
                    
            except Exception as e:
                error_msg = f"Connection error: {str(e)}"
                logger.error(error_msg)
                logger.exception("Connect thread error:")
                self.error_occurred.emit(error_msg)
            finally:
                if loop and not loop.is_closed():
                    loop.close()
        
        # Run connect in separate thread
        self.thread = threading.Thread(target=connect_thread, daemon=True)
        self.thread.start()
    
    def disconnect(self):
        """Disconnect from BLE device (synchronous wrapper)"""
        logger.info("Disconnecting from BLE device...")
        
        # Signal thread to stop
        self.running = False
        
        # If we have an active client in a running loop, schedule disconnect
        if self.client and self.loop and not self.loop.is_closed():
            try:
                # Schedule the disconnect in the loop
                future = asyncio.run_coroutine_threadsafe(self.disconnect_async(), self.loop)
                # Wait for it to complete with timeout
                future.result(timeout=3.0)
            except Exception as e:
                logger.warning(f"Error during async disconnect: {e}")
        
        # Give the keep_alive loop time to exit gracefully
        import time
        time.sleep(0.5)
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            
        # Clean up
        self.client = None
        self.loop = None
        self.connected = False
        
        logger.info("BLE disconnected successfully")
        self.connection_status_changed.emit(False, "Disconnected")
    
    def _handle_disconnect(self, client):
        """Callback when BLE device disconnects"""
        logger.warning("BLE device disconnected (callback)")
        self.connected = False
        self.running = False
        self.connection_status_changed.emit(False, "Device disconnected")
    
    async def _keep_alive(self):
        """Keep the event loop alive for notifications"""
        while self.running and self.client and self.client.is_connected:
            await asyncio.sleep(0.1)
    
    def _data_notification_handler(
        self,
        characteristic: BleakGATTCharacteristic,
        data: bytearray
    ):
        """Handle data notifications from ESP32"""
        try:
            json_str = data.decode('utf-8')
            json_data = json.loads(json_str)
            
            vehicle_data = VehicleData.from_dict(json_data)
            
            if vehicle_data.is_valid():
                self.data_received.emit(vehicle_data)
            else:
                logger.warning(f"Invalid data received: {json_data}")
                
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse BLE data: {e}")
    
    def _status_notification_handler(
        self,
        characteristic: BleakGATTCharacteristic,
        data: bytearray
    ):
        """Handle status notifications from ESP32"""
        try:
            json_str = data.decode('utf-8')
            json_data = json.loads(json_str)
            
            logger.debug(f"Status update: {json_data}")
            
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse status data: {e}")


class BLEWorker(QObject):
    """Worker for running BLE operations in a separate thread"""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, handler: BLEHandler, address: str):
        super().__init__()
        self.handler = handler
        self.address = address
    
    def run(self):
        """Run BLE connection in thread"""
        try:
            self.handler.connect(self.address)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
