/**
 * @file main.cpp
 * @brief Main application for Husqvarna Svartpilen 401 OBD2 Reader
 * @version 2.0
 * @date 2025-10-31
 * 
 * Architecture: Layered Architecture
 * - BSW Layer: Hardware abstraction, drivers, communication (BLE + WiFi)
 * - Application Layer: OBD2 handling, web server, data management
 * 
 * Updates v2.0:
 * - Added BLE (Bluetooth Low Energy) support for wireless communication
 * - Desktop app can connect via BLE instead of Serial USB
 * - Dual mode: BLE for desktop + HTTP for web monitoring
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include "common_types.h"
#include "hal_interface.h"
#include "can_interface.h"
#include "obd2_handler.h"
#include "ble_service.h"

// System Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// BLE Configuration
#define ENABLE_BLE true  // Set to false to disable BLE

// Hardware Pins Configuration for MCP2515
static const HardwarePins_t hardware_pins = {
    .mcp2515_cs = 4,                /* MCP2515 CS pin */
    .mcp2515_int = 2,               /* MCP2515 INT pin */
    .spi_mosi = 21,                 /* SPI MOSI pin (SI) */
    .spi_miso = 19,                 /* SPI MISO pin */
    .spi_sck = 18,                  /* SPI SCK pin */
    .status_led = 25                /* Status LED pin */
};

// Global Variables
WebServer server(80);
SystemState_t current_state = SYSTEM_STATE_INIT;
VehicleData_t last_vehicle_data = {0};

// Function Prototypes
void system_init(void);
void vehicle_data_callback(const VehicleData_t* data);
void system_task(void);
void handleRoot(void);
void handleData(void);

// Function declarations
void system_init(void);
void system_task(void);
void vehicle_data_callback(VehicleData_t* data);
void output_vehicle_data_json(void);

void setup() {
    Serial.begin(115200);
    Serial.println("========================================");
    Serial.println("Husqvarna Svartpilen 401 OBD2 Reader v2.0");
    Serial.println("BLE + WiFi Edition");
    Serial.println("Professional Layered Architecture");
    Serial.println("========================================");
    
    system_init();
    
    Serial.println("System initialization complete!");
    Serial.println("========================================");
}

void loop() {
    static unsigned long last_json_output = 0;
    static unsigned long last_ble_send = 0;
    const unsigned long JSON_OUTPUT_INTERVAL = 1000; // Output every 1 second
    const unsigned long BLE_SEND_INTERVAL = 200;     // BLE update every 200ms
    
    unsigned long current_time = millis();
    
    // Handle web server
    server.handleClient();
    
    // Run system tasks
    system_task();
    
    // Update BLE connection status
    BLE_UpdateStatus();
    
    // Send data via BLE if connected
    if (ENABLE_BLE && BLE_IsConnected()) {
        if (current_time - last_ble_send >= BLE_SEND_INTERVAL) {
            BLE_SendVehicleData(&last_vehicle_data);
            last_ble_send = current_time;
        }
    }
    
    // Output JSON data to Serial for debugging
    if (current_time - last_json_output >= JSON_OUTPUT_INTERVAL) {
        output_vehicle_data_json();
        last_json_output = current_time;
    }
    
    delay(10);
}

// Pin definitions for easy access
#define STATUS_LED hardware_pins.status_led

void system_init(void) {
    // Initialize GPIO for status LED
    HAL_GPIO_Init(hardware_pins.status_led, HAL_GPIO_MODE_OUTPUT);
    HAL_GPIO_Write(hardware_pins.status_led, GPIO_LEVEL_LOW);
    
    // Initialize BLE Service
    if (ENABLE_BLE) {
        Serial.println("Initializing BLE service...");
        BLEConfig_t ble_config = {
            .device_name = BLE_DEVICE_NAME,
            .auto_advertise = true,
            .mtu_size = 517  // Maximum MTU for better throughput
        };
        
        Status_t ble_status = BLE_Init(&ble_config);
        if (ble_status == STATUS_OK) {
            Serial.println("✓ BLE service initialized successfully");
            Serial.println("  Device is now discoverable as: " BLE_DEVICE_NAME);
            Serial.println("  Desktop app can connect via Bluetooth");
        } else {
            Serial.println("✗ BLE initialization failed");
        }
    }
    
    // Initialize MCP2515 CAN controller
    if (!CAN_InitMCP2515(&hardware_pins)) {
        Serial.println("Error: MCP2515 CAN initialization failed");
        current_state = SYSTEM_STATE_ERROR;
        return;
    }
    Serial.println("MCP2515 CAN controller initialized");
    
    // Initialize OBD2 handler
    OBD2_Config_t obd2_config;
    obd2_config.update_interval_ms = 100;
    
    Status_t status = OBD2_Init(&obd2_config);
    if (status == STATUS_OK) {
        Serial.println("OBD2 handler initialized");
        OBD2_RegisterCallback(vehicle_data_callback);
        current_state = SYSTEM_STATE_IDLE;
    } else {
        Serial.println("Error: OBD2 initialization failed");
        current_state = SYSTEM_STATE_ERROR;
        return;
    }
    
    // Initialize WiFi
    WiFi.begin(ssid, password);
    current_state = SYSTEM_STATE_CONNECTING;
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        HAL_GPIO_Toggle(STATUS_LED);
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        current_state = SYSTEM_STATE_CONNECTED;
    } else {
        Serial.println("\nWiFi connection failed, continuing without WiFi");
        current_state = SYSTEM_STATE_IDLE;
    }
    
    // Setup web server
    server.on("/", handleRoot);
    server.on("/data", handleData);
    server.begin();
    
    HAL_GPIO_Write(STATUS_LED, GPIO_LEVEL_HIGH);
}

void vehicle_data_callback(const VehicleData_t* data) {
    if (data != nullptr) {
        last_vehicle_data = *data;
        
        Serial.printf("RPM: %d, Speed: %d km/h, Temp: %dC, Throttle: %d%%\n",
                     data->rpm, data->speed, data->coolantTemp, data->throttlePosition);
    }
}

void system_task(void) {
    static uint32_t last_data_read = 0;
    static uint32_t last_led_blink = 0;
    static uint32_t last_ble_check = 0;
    static uint32_t debug_counter = 0;
    
    uint32_t current_time = millis();
    
    // Debug: Print every 5 seconds
    if (debug_counter++ % 250 == 0) {  // 250 * 20ms = 5s
        Serial.printf("DEBUG: time=%lu, last_ble_check=%lu, diff=%lu\n", 
                      current_time, last_ble_check, current_time - last_ble_check);
    }
    
    // Check BLE connection timeout every 2 seconds
    if (current_time - last_ble_check >= 2000) {
        Serial.println("MAIN: Calling BLE check..."); // DEBUG
        if (g_bleService) {
            g_bleService->checkConnectionTimeout();
        } else {
            Serial.println("MAIN: g_bleService is NULL!"); // DEBUG
        }
        last_ble_check = current_time;
    }
    
    // Read OBD2 data periodically
    if (current_time - last_data_read >= 200) {
        if (current_state != SYSTEM_STATE_ERROR) {
            Status_t status = OBD2_ReadAllData();
            
            if (status == STATUS_OK) {
                current_state = SYSTEM_STATE_CONNECTED;
            }
        }
        last_data_read = current_time;
    }
    
    // Blink status LED
    if (current_time - last_led_blink >= 1000) {
        HAL_GPIO_Toggle(STATUS_LED);
        last_led_blink = current_time;
    }
    
    // Handle error state
    if (current_state == SYSTEM_STATE_ERROR) {
        static uint32_t last_error_blink = 0;
        if (current_time - last_error_blink >= 200) {
            HAL_GPIO_Toggle(STATUS_LED);
            last_error_blink = current_time;
        }
    }
}

void handleRoot() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Svartpilen 401 OBD2 Monitor</title>
    <meta http-equiv='refresh' content='2'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d); 
            color: #fff; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 107, 53, 0.1);
            border-radius: 10px;
            border: 2px solid #ff6b35;
        }
        .gauge { 
            display: inline-block; 
            margin: 15px; 
            text-align: center; 
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            min-width: 150px;
        }
        .gauge-value { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #ff6b35; 
            margin-bottom: 10px;
        }
        .gauge-label { 
            font-size: 1.2em; 
            color: #ccc;
        }
        .status { 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0; 
            text-align: center;
            font-size: 1.3em;
            font-weight: bold;
        }
        .running { 
            background: linear-gradient(135deg, #4CAF50, #45a049); 
        }
        .stopped { 
            background: linear-gradient(135deg, #f44336, #d32f2f); 
        }
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1> Husqvarna Svartpilen 401</h1>
            <h2>Professional OBD2 Diagnostics</h2>
            <p>Layered Architecture System</p>
        </div>
        
        <div class='status )";
  
    html += last_vehicle_data.engineRunning ? "running'> Engine: RUNNING" : "stopped'> Engine: STOPPED";
    html += R"('></div>
        
        <div style='text-align: center;'>
            <div class='gauge'>
                <div class='gauge-value'>)" + String(last_vehicle_data.rpm) + R"(</div>
                <div class='gauge-label'>Engine RPM</div>
            </div>
            <div class='gauge'>
                <div class='gauge-value'>)" + String(last_vehicle_data.speed) + R"(</div>
                <div class='gauge-label'>Speed (km/h)</div>
            </div>
            <div class='gauge'>
                <div class='gauge-value'>)" + String(last_vehicle_data.coolantTemp) + R"(</div>
                <div class='gauge-label'>Coolant (C)</div>
            </div>
            <div class='gauge'>
                <div class='gauge-value'>)" + String(last_vehicle_data.throttlePosition) + R"(</div>
                <div class='gauge-label'>Throttle (%)</div>
            </div>
        </div>
        
        <div style='text-align: center; margin-top: 30px; color: #888;'>
            <p>System State: )" + String(current_state) + R"(</p>
            <p>Last update: )" + String(millis() - last_vehicle_data.lastUpdate) + R"( ms ago</p>
            <p>Uptime: )" + String(millis() / 1000) + R"( seconds</p>
        </div>
    </div>
</body>
</html>)";
    
    server.send(200, "text/html", html);
}

void handleData() {
    String json = "{";
    json += "\"rpm\":" + String(last_vehicle_data.rpm) + ",";
    json += "\"speed\":" + String(last_vehicle_data.speed) + ",";
    json += "\"coolantTemp\":" + String(last_vehicle_data.coolantTemp) + ",";
    json += "\"throttlePosition\":" + String(last_vehicle_data.throttlePosition) + ",";
    json += "\"engineRunning\":" + String(last_vehicle_data.engineRunning ? "true" : "false") + ",";
    json += "\"dataValid\":" + String(last_vehicle_data.dataValid ? "true" : "false") + ",";
    json += "\"systemState\":" + String(current_state) + ",";
    json += "\"lastUpdate\":" + String(last_vehicle_data.lastUpdate) + ",";
    json += "\"uptime\":" + String(millis());
    json += "}";
    
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", json);
}

// JSON output for desktop application
void output_vehicle_data_json() {
    // Create JSON object
    Serial.println("{");
    Serial.printf("  \"timestamp\": %lu,\n", millis());
    Serial.printf("  \"rpm\": %d,\n", last_vehicle_data.rpm);
    Serial.printf("  \"speed\": %d,\n", last_vehicle_data.speed);
    Serial.printf("  \"coolant_temp\": %d,\n", last_vehicle_data.coolantTemp);
    Serial.printf("  \"throttle_position\": %d,\n", last_vehicle_data.throttlePosition);
    Serial.printf("  \"system_state\": \"%s\",\n", 
        (current_state == SYSTEM_STATE_CONNECTED) ? "CONNECTED" :
        (current_state == SYSTEM_STATE_IDLE) ? "IDLE" :
        (current_state == SYSTEM_STATE_ERROR) ? "ERROR" : 
        (current_state == SYSTEM_STATE_CONNECTING) ? "CONNECTING" : "UNKNOWN");
    Serial.printf("  \"wifi_connected\": %s,\n", WiFi.isConnected() ? "true" : "false");
    Serial.printf("  \"wifi_rssi\": %d\n", WiFi.RSSI());
    Serial.println("}");
}
