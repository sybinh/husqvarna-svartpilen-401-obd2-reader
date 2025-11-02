/**
 * @file ble_service.h
 * @brief BLE Service for OBD2 data transmission
 * @version 1.0
 * @date 2025-10-31
 * 
 * Implements BLE GATT server for wireless data transmission
 * to desktop/mobile applications
 */

#ifndef BLE_SERVICE_H
#define BLE_SERVICE_H

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "common_types.h"

// BLE Service UUIDs
#define BLE_SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define BLE_CHAR_DATA_UUID      "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define BLE_CHAR_STATUS_UUID    "beb5483e-36e1-4688-b7f5-ea07361b26a9"

// BLE Device Name
#define BLE_DEVICE_NAME         "Svartpilen401_OBD2"

// BLE Configuration
typedef struct {
    const char* device_name;
    bool auto_advertise;
    uint16_t mtu_size;
} BLEConfig_t;

// BLE Connection Callbacks
class BLEConnectionCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer);
    void onDisconnect(BLEServer* pServer);
};

// BLE Service Class
class OBD2BLEService {
private:
    BLEServer* pServer;
    BLEService* pService;
    BLECharacteristic* pDataCharacteristic;
    BLECharacteristic* pStatusCharacteristic;
    BLEConnectionCallbacks* pCallbacks;
    
    uint32_t lastDataSend;
    
    void setupCharacteristics();
    String createDataJSON(const VehicleData_t* data);
    String createStatusJSON(SystemState_t state, bool wifiConnected, int8_t rssi);
    
public:
    // Public for callback access
    bool deviceConnected;
    bool oldDeviceConnected;
    uint32_t lastActivityTime;
    
    OBD2BLEService();
    ~OBD2BLEService();
    
    // Initialize BLE service
    Status_t init(const BLEConfig_t* config);
    
    // Send vehicle data via BLE
    Status_t sendVehicleData(const VehicleData_t* data);
    
    // Send system status via BLE
    Status_t sendSystemStatus(SystemState_t state, bool wifiConnected, int8_t rssi);
    
    // Check if device is connected
    bool isConnected() const { return deviceConnected; }
    
    // Start/Stop advertising
    void startAdvertising();
    void stopAdvertising();
    
    // Get connection status
    uint8_t getConnectedDevices() const;
    
    // Update connection status
    void updateConnectionStatus();
    
    // Check for connection timeout (Windows BLE doesn't send disconnect)
    void checkConnectionTimeout();
};

// Global BLE Service instance (declared in ble_service.cpp)
extern OBD2BLEService* g_bleService;

// Helper functions
Status_t BLE_Init(const BLEConfig_t* config);
Status_t BLE_SendVehicleData(const VehicleData_t* data);
Status_t BLE_SendSystemStatus(SystemState_t state, bool wifiConnected, int8_t rssi);
bool BLE_IsConnected();
void BLE_UpdateStatus();
void BLE_EnsureAdvertising(); // Ensure advertising is active when not connected

#endif // BLE_SERVICE_H
