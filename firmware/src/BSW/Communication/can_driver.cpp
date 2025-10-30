/**
 * @file can_driver.cpp
 * @brief CAN bus driver implementation for ESP32
 * @version 1.0
 * @date 2025-10-30
 */

#include <Arduino.h>
#include <CAN.h>
#include "can_interface.h"

static bool can_initialized = false;

Status_t CAN_Init(const CAN_Config_t* config) {
    if (config == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    CAN.setPins(config->rx_pin, config->tx_pin);
    
    if (!CAN.begin(config->baudrate)) {
        return STATUS_ERROR;
    }
    
    can_initialized = true;
    return STATUS_OK;
}

Status_t CAN_DeInit(void) {
    if (!can_initialized) {
        return STATUS_NOT_INITIALIZED;
    }
    
    CAN.end();
    can_initialized = false;
    return STATUS_OK;
}

Status_t CAN_SendFrame(const CAN_Frame_t* frame) {
    if (!can_initialized || frame == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    if (frame->length > 8) {
        return STATUS_INVALID_PARAM;
    }
    
    if (frame->extended) {
        CAN.beginExtendedPacket(frame->id);
    } else {
        CAN.beginPacket(frame->id);
    }
    
    for (uint8_t i = 0; i < frame->length; i++) {
        CAN.write(frame->data[i]);
    }
    
    if (!CAN.endPacket()) {
        return STATUS_ERROR;
    }
    
    return STATUS_OK;
}

Status_t CAN_ReceiveFrame(CAN_Frame_t* frame, uint32_t timeout_ms) {
    if (!can_initialized || frame == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    uint32_t start_time = millis();
    
    while (millis() - start_time < timeout_ms) {
        int packet_size = CAN.parsePacket();
        
        if (packet_size > 0) {
            frame->id = CAN.packetId();
            frame->extended = CAN.packetExtended();
            frame->remote = CAN.packetRtr();
            frame->length = packet_size;
            
            for (int i = 0; i < packet_size && i < 8; i++) {
                frame->data[i] = CAN.read();
            }
            
            return STATUS_OK;
        }
        
        delay(1);
    }
    
    return STATUS_TIMEOUT;
}

bool CAN_IsFrameAvailable(void) {
    if (!can_initialized) {
        return false;
    }
    
    return CAN.parsePacket() > 0;
}

Status_t CAN_SendOBD2Request(uint8_t pid) {
    if (!can_initialized) {
        return STATUS_NOT_INITIALIZED;
    }
    
    CAN_Frame_t frame;
    frame.id = 0x7DF;
    frame.length = 8;
    frame.extended = false;
    frame.remote = false;
    
    frame.data[0] = 0x02;
    frame.data[1] = 0x01;
    frame.data[2] = pid;
    frame.data[3] = 0x00;
    frame.data[4] = 0x00;
    frame.data[5] = 0x00;
    frame.data[6] = 0x00;
    frame.data[7] = 0x00;
    
    return CAN_SendFrame(&frame);
}

Status_t CAN_ReceiveOBD2Response(uint8_t pid, uint8_t* data, uint8_t* length, uint32_t timeout_ms) {
    if (!can_initialized || data == nullptr || length == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    CAN_Frame_t frame;
    Status_t status = CAN_ReceiveFrame(&frame, timeout_ms);
    
    if (status != STATUS_OK) {
        return status;
    }
    
    if (frame.id < 0x7E8 || frame.id > 0x7EF) {
        return STATUS_ERROR;
    }
    
    if (frame.length < 3) {
        return STATUS_ERROR;
    }
    
    uint8_t frame_length = frame.data[0];
    uint8_t service = frame.data[1];
    uint8_t response_pid = frame.data[2];
    
    if (service != 0x41 || response_pid != pid) {
        return STATUS_ERROR;
    }
    
    *length = frame_length - 2;
    for (uint8_t i = 0; i < *length && i < 5; i++) {
        data[i] = frame.data[3 + i];
    }
    
    return STATUS_OK;
}
