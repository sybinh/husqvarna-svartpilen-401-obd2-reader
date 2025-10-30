/**
 * @file obd2_handler.cpp
 * @brief OBD2 protocol handler - Application layer
 * @version 1.0
 * @date 2025-10-30
 */

#include <Arduino.h>
#include "obd2_handler.h"
#include "can_interface.h"

static VehicleData_t vehicle_data = {0};
static bool obd2_initialized = false;
static DataUpdateCallback_t data_callback = nullptr;

Status_t OBD2_Init(const OBD2_Config_t* config) {
    if (config == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    CAN_Config_t can_config;
    can_config.rx_pin = config->can_rx_pin;
    can_config.tx_pin = config->can_tx_pin;
    can_config.baudrate = config->can_baudrate;
    
    Status_t status = CAN_Init(&can_config);
    if (status != STATUS_OK) {
        return status;
    }
    
    vehicle_data.dataValid = false;
    vehicle_data.engineRunning = false;
    vehicle_data.lastUpdate = 0;
    
    obd2_initialized = true;
    return STATUS_OK;
}

Status_t OBD2_RegisterCallback(DataUpdateCallback_t callback) {
    if (callback == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    data_callback = callback;
    return STATUS_OK;
}

Status_t OBD2_ReadAllData(void) {
    if (!obd2_initialized) {
        return STATUS_NOT_INITIALIZED;
    }
    
    Status_t overall_status = STATUS_OK;
    
    if (OBD2_ReadRPM(&vehicle_data.rpm) != STATUS_OK) {
        overall_status = STATUS_ERROR;
    }
    
    delay(10);
    
    if (OBD2_ReadSpeed(&vehicle_data.speed) != STATUS_OK) {
        overall_status = STATUS_ERROR;
    }
    
    delay(10);
    
    if (OBD2_ReadCoolantTemp(&vehicle_data.coolantTemp) != STATUS_OK) {
        overall_status = STATUS_ERROR;
    }
    
    delay(10);
    
    if (OBD2_ReadThrottlePosition(&vehicle_data.throttlePosition) != STATUS_OK) {
        overall_status = STATUS_ERROR;
    }
    
    vehicle_data.engineRunning = (vehicle_data.rpm > 0);
    vehicle_data.lastUpdate = millis();
    
    if (overall_status == STATUS_OK || vehicle_data.rpm > 0) {
        vehicle_data.dataValid = true;
        
        if (data_callback != nullptr) {
            data_callback(&vehicle_data);
        }
    }
    
    return overall_status;
}

Status_t OBD2_ReadRPM(uint16_t* rpm) {
    if (!obd2_initialized || rpm == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    Status_t status = CAN_SendOBD2Request(PID_ENGINE_RPM);
    if (status != STATUS_OK) {
        return status;
    }
    
    uint8_t data[5];
    uint8_t length;
    status = CAN_ReceiveOBD2Response(PID_ENGINE_RPM, data, &length, OBD2_REQUEST_TIMEOUT_MS);
    
    if (status == STATUS_OK && length >= 2) {
        *rpm = ((uint16_t)data[0] * 256 + data[1]) / 4;
    } else {
        *rpm = 0;
    }
    
    return status;
}

Status_t OBD2_ReadSpeed(uint8_t* speed) {
    if (!obd2_initialized || speed == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    Status_t status = CAN_SendOBD2Request(PID_VEHICLE_SPEED);
    if (status != STATUS_OK) {
        return status;
    }
    
    uint8_t data[5];
    uint8_t length;
    status = CAN_ReceiveOBD2Response(PID_VEHICLE_SPEED, data, &length, OBD2_REQUEST_TIMEOUT_MS);
    
    if (status == STATUS_OK && length >= 1) {
        *speed = data[0];
    } else {
        *speed = 0;
    }
    
    return status;
}

Status_t OBD2_ReadCoolantTemp(int8_t* temp) {
    if (!obd2_initialized || temp == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    Status_t status = CAN_SendOBD2Request(PID_ENGINE_COOLANT_TEMP);
    if (status != STATUS_OK) {
        return status;
    }
    
    uint8_t data[5];
    uint8_t length;
    status = CAN_ReceiveOBD2Response(PID_ENGINE_COOLANT_TEMP, data, &length, OBD2_REQUEST_TIMEOUT_MS);
    
    if (status == STATUS_OK && length >= 1) {
        *temp = (int8_t)data[0] - 40;
    } else {
        *temp = -40;
    }
    
    return status;
}

Status_t OBD2_ReadThrottlePosition(uint8_t* throttle) {
    if (!obd2_initialized || throttle == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    Status_t status = CAN_SendOBD2Request(PID_THROTTLE_POSITION);
    if (status != STATUS_OK) {
        return status;
    }
    
    uint8_t data[5];
    uint8_t length;
    status = CAN_ReceiveOBD2Response(PID_THROTTLE_POSITION, data, &length, OBD2_REQUEST_TIMEOUT_MS);
    
    if (status == STATUS_OK && length >= 1) {
        *throttle = (data[0] * 100) / 255;
    } else {
        *throttle = 0;
    }
    
    return status;
}

const VehicleData_t* OBD2_GetVehicleData(void) {
    return &vehicle_data;
}
