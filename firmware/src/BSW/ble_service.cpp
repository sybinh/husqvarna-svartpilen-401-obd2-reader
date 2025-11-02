/**
 * @file ble_service.cpp
 * @brief BLE Service implementation for OBD2 data transmission
 * @version 1.0
 * @date 2025-10-31
 */

#include "ble_service.h"
#include <ArduinoJson.h>

// Global instance
OBD2BLEService* g_bleService = nullptr;

// ============================================================================
// BLE Connection Callbacks Implementation
// ============================================================================

void BLEConnectionCallbacks::onConnect(BLEServer* pServer) {
    Serial.println("BLE: Client connected");
    // Re-set callbacks after each connection to ensure reliability
    pServer->setCallbacks(new BLEConnectionCallbacks());
    if (g_bleService) {
        // Directly update connection status instead of relying on getConnectedCount()
        g_bleService->deviceConnected = true;
        g_bleService->oldDeviceConnected = true;
        // Reset activity time on new connection
        g_bleService->lastActivityTime = millis();
        Serial.println("BLE: Device connected event");
    }
}

void BLEConnectionCallbacks::onDisconnect(BLEServer* pServer) {
    Serial.println("BLE: Client disconnected");
    if (g_bleService) {
        // Directly update connection status
        g_bleService->deviceConnected = false;
        g_bleService->oldDeviceConnected = false;
        Serial.println("BLE: Device disconnected event");
    }
    // Auto restart advertising with longer delay for stability
    delay(1000); // Increased from 500ms to 1000ms
    pServer->getAdvertising()->start();
    Serial.println("BLE: Advertising restarted");
}

// ============================================================================
// OBD2BLEService Implementation
// ============================================================================

OBD2BLEService::OBD2BLEService() 
    : pServer(nullptr),
      pService(nullptr),
      pDataCharacteristic(nullptr),
      pStatusCharacteristic(nullptr),
      pCallbacks(nullptr),
      deviceConnected(false),
      oldDeviceConnected(false),
      lastDataSend(0),
      lastActivityTime(0) {
}

OBD2BLEService::~OBD2BLEService() {
    if (pCallbacks) {
        delete pCallbacks;
    }
}

Status_t OBD2BLEService::init(const BLEConfig_t* config) {
    if (!config) {
        Serial.println("BLE: Invalid configuration");
        return STATUS_ERROR;
    }
    
    Serial.println("BLE: Initializing BLE service...");
    
    // Initialize BLE Device
    BLEDevice::init(config->device_name);
    
    // Set MTU size for larger data packets
    BLEDevice::setMTU(config->mtu_size);
    
    // Create BLE Server
    pServer = BLEDevice::createServer();
    if (!pServer) {
        Serial.println("BLE: Failed to create server");
        return STATUS_ERROR;
    }
    
    // Set connection callbacks
    pCallbacks = new BLEConnectionCallbacks();
    pServer->setCallbacks(pCallbacks);
    
    // Create BLE Service
    pService = pServer->createService(BLE_SERVICE_UUID);
    if (!pService) {
        Serial.println("BLE: Failed to create service");
        return STATUS_ERROR;
    }
    
    // Setup characteristics
    setupCharacteristics();
    
    // Start the service
    pService->start();
    
    // Start advertising
    if (config->auto_advertise) {
        startAdvertising();
    }
    
    Serial.println("BLE: Service initialized successfully");
    Serial.printf("BLE: Device name: %s\n", config->device_name);
    Serial.printf("BLE: MTU size: %d\n", config->mtu_size);
    
    return STATUS_OK;
}

void OBD2BLEService::setupCharacteristics() {
    // Data Characteristic (Vehicle Data)
    pDataCharacteristic = pService->createCharacteristic(
        BLE_CHAR_DATA_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pDataCharacteristic->addDescriptor(new BLE2902());
    
    // Status Characteristic (System Status)
    pStatusCharacteristic = pService->createCharacteristic(
        BLE_CHAR_STATUS_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pStatusCharacteristic->addDescriptor(new BLE2902());
    
    Serial.println("BLE: Characteristics configured");
}

void OBD2BLEService::startAdvertising() {
    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    
    pAdvertising->addServiceUUID(BLE_SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);  // iPhone connection issue fix
    pAdvertising->setMinPreferred(0x12);
    
    BLEDevice::startAdvertising();
    Serial.println("BLE: Advertising started");
}

void OBD2BLEService::stopAdvertising() {
    BLEDevice::stopAdvertising();
    Serial.println("BLE: Advertising stopped");
}

String OBD2BLEService::createDataJSON(const VehicleData_t* data) {
    StaticJsonDocument<256> doc;
    
    doc["timestamp"] = millis();
    doc["rpm"] = data->rpm;
    doc["speed"] = data->speed;
    doc["coolant_temp"] = data->coolantTemp;
    doc["throttle_position"] = data->throttlePosition;
    doc["engine_running"] = data->engineRunning;
    doc["data_valid"] = data->dataValid;
    
    String output;
    serializeJson(doc, output);
    return output;
}

String OBD2BLEService::createStatusJSON(SystemState_t state, bool wifiConnected, int8_t rssi) {
    StaticJsonDocument<128> doc;
    
    doc["timestamp"] = millis();
    doc["system_state"] = state;
    doc["wifi_connected"] = wifiConnected;
    doc["wifi_rssi"] = rssi;
    doc["ble_connected"] = deviceConnected;
    
    String output;
    serializeJson(doc, output);
    return output;
}

Status_t OBD2BLEService::sendVehicleData(const VehicleData_t* data) {
    if (!data) {
        return STATUS_ERROR;
    }
    
    if (!deviceConnected) {
        return STATUS_ERROR;  // No client connected
    }
    
    // Throttle data sending to avoid overwhelming BLE
    uint32_t now = millis();
    if (now - lastDataSend < 100) {  // Min 100ms between sends
        return STATUS_OK;
    }
    lastDataSend = now;
    lastActivityTime = now;  // Update activity timestamp
    
    // Create JSON string
    String jsonData = createDataJSON(data);
    
    // Send via BLE notification
    pDataCharacteristic->setValue(jsonData.c_str());
    pDataCharacteristic->notify();
    
    return STATUS_OK;
}

Status_t OBD2BLEService::sendSystemStatus(SystemState_t state, bool wifiConnected, int8_t rssi) {
    if (!deviceConnected) {
        return STATUS_ERROR;
    }
    
    // Create JSON string
    String jsonStatus = createStatusJSON(state, wifiConnected, rssi);
    
    // Send via BLE notification
    pStatusCharacteristic->setValue(jsonStatus.c_str());
    pStatusCharacteristic->notify();
    
    return STATUS_OK;
}

void OBD2BLEService::updateConnectionStatus() {
    bool newDeviceConnected = (pServer->getConnectedCount() > 0);
    
    // Handle connection state changes
    if (newDeviceConnected && !oldDeviceConnected) {
        Serial.println("BLE: Device connected event");
    }
    
    if (!newDeviceConnected && oldDeviceConnected) {
        Serial.println("BLE: Device disconnected event");
    }
    
    oldDeviceConnected = newDeviceConnected;
    deviceConnected = newDeviceConnected;
}

void OBD2BLEService::checkConnectionTimeout() {
    Serial.println("BLE: checkConnectionTimeout() CALLED"); // DEBUG
    
    // Only check if we think we're connected
    if (!deviceConnected) {
        Serial.println("BLE: Skipping check - not connected");
        return;
    }
    
    uint32_t now = millis();
    
    // Debug: Print connection check info
    uint8_t connectedCount = pServer->getConnectedCount();
    uint32_t timeSinceActivity = (lastActivityTime == 0) ? 0 : (now - lastActivityTime);
    uint32_t timeUntilTimeout = (timeSinceActivity > 10000) ? 0 : (10000 - timeSinceActivity);
    
    Serial.printf("BLE: Check - count=%d, idle=%lums, timeout_in=%lums\n", 
                  connectedCount, timeSinceActivity, timeUntilTimeout);
    
    // Initialize activity time on first check after connection
    if (lastActivityTime == 0) {
        lastActivityTime = now;
        Serial.println("BLE: Activity time initialized");
    }
    
    // Check for timeout
    if (now - lastActivityTime > 10000) {
        // No activity for 10+ seconds
        Serial.println("BLE: No activity for 10s, checking connection state...");
        
        if (connectedCount == 0) {
            // getConnectedCount says 0, definitely disconnected
            Serial.println("BLE: Connection timeout detected (count=0)");
        } else {
            // Count > 0 but no data - still assume disconnected (Windows bug)
            Serial.println("BLE: Connection timeout detected (no data but count>0, Windows BLE bug)");
        }
        
        Serial.println("BLE: Forcing disconnect and restart advertising");
        deviceConnected = false;
        oldDeviceConnected = false;
        lastActivityTime = 0;
        
        // Restart advertising
        delay(500);
        pServer->getAdvertising()->start();
        Serial.println("BLE: Advertising restarted after timeout");
    }
}

uint8_t OBD2BLEService::getConnectedDevices() const {
    if (pServer) {
        return pServer->getConnectedCount();
    }
    return 0;
}

// ============================================================================
// Global Helper Functions
// ============================================================================

Status_t BLE_Init(const BLEConfig_t* config) {
    if (!g_bleService) {
        g_bleService = new OBD2BLEService();
    }
    
    return g_bleService->init(config);
}

Status_t BLE_SendVehicleData(const VehicleData_t* data) {
    if (!g_bleService) {
        return STATUS_ERROR;
    }
    
    return g_bleService->sendVehicleData(data);
}

Status_t BLE_SendSystemStatus(SystemState_t state, bool wifiConnected, int8_t rssi) {
    if (!g_bleService) {
        return STATUS_ERROR;
    }
    
    return g_bleService->sendSystemStatus(state, wifiConnected, rssi);
}

bool BLE_IsConnected() {
    if (!g_bleService) {
        return false;
    }
    
    return g_bleService->isConnected();
}

void BLE_UpdateStatus() {
    if (g_bleService) {
        g_bleService->updateConnectionStatus();
    }
}

void BLE_EnsureAdvertising() {
    if (!g_bleService) return;
    
    // Force update connection status in case callback was missed
    g_bleService->updateConnectionStatus();
    
    if (!g_bleService->isConnected()) {
        Serial.println("BLE: Forcing advertising restart (not connected)");
        g_bleService->startAdvertising();
    }
}
