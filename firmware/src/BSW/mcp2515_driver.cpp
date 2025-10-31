/**
 * @file mcp2515_driver.cpp
 * @brief MCP2515 CAN Controller Driver Implementation
 * @details Implements MCP2515 CAN controller driver for ESP32 via SPI interface
 * @author OBD2 Reader Project
 * @date 2024
 */

#include "hal_interface.h"
#include "can_interface.h"
#include "common_types.h"
#include <CAN.h>
#include <SPI.h>

// Static variables for hardware pins
static HardwarePins_t g_pins;

/**
 * @brief Initialize MCP2515 CAN controller
 * @param pins Hardware pin configuration
 * @return true if initialization successful, false otherwise
 */
bool CAN_InitMCP2515(const HardwarePins_t* pins) {
    if (pins == nullptr) {
        return false;
    }
    
    // Validate pin numbers (ESP32 has GPIO 0-39)
    if (pins->mcp2515_cs > 39 || pins->mcp2515_int > 39 || 
        pins->spi_mosi > 39 || pins->spi_miso > 39 || pins->spi_sck > 39) {
        return false;
    }
    
    // Store pin configuration
    g_pins = *pins;
    
    // Initialize SPI with custom pins
    SPI.begin(pins->spi_sck, pins->spi_miso, pins->spi_mosi, pins->mcp2515_cs);
    
    // Set MCP2515 pins (CS and INT)
    CAN.setPins(pins->mcp2515_cs, pins->mcp2515_int);
    
    // Initialize CAN at 500kbps (OBD2 standard)
    if (!CAN.begin(500E3)) {
        return false;
    }
    
    return true;
}

/**
 * @brief Send CAN frame
 * @param frame Pointer to CAN frame to send
 * @return true if sent successfully, false otherwise
 */
bool CAN_SendFrame(const CAN_Frame_t* frame) {
    if (frame == nullptr) {
        return false;
    }
    
    // Set packet ID and RTR flag
    CAN.beginPacket(frame->id, frame->length, frame->remote);
    
    // Send data bytes
    for (uint8_t i = 0; i < frame->length; i++) {
        CAN.write(frame->data[i]);
    }
    
    // End packet transmission
    return CAN.endPacket() == 1;
}

/**
 * @brief Receive CAN frame
 * @param frame Pointer to buffer for received frame
 * @return true if frame received, false otherwise
 */
bool CAN_ReceiveFrame(CAN_Frame_t* frame) {
    if (frame == nullptr) {
        return false;
    }
    
    // Check if packet available
    int packetSize = CAN.parsePacket();
    if (packetSize <= 0) {
        return false;
    }
    
    // Get packet information
    frame->id = CAN.packetId();
    frame->length = packetSize;
    frame->remote = CAN.packetRtr();
    frame->extended = CAN.packetExtended();
    
    // Read data bytes
    for (int i = 0; i < packetSize && i < 8; i++) {
        frame->data[i] = CAN.read();
    }
    
    return true;
}

/**
 * @brief Check if CAN frame is available
 * @return true if frame is available to read
 */
bool CAN_Available(void) {
    return CAN.parsePacket() > 0;
}

/**
 * @brief Set CAN filter for OBD2 responses
 * @param filter_id CAN ID to filter for
 * @param mask_id Mask for filtering
 * @return true if filter set successfully
 */
bool CAN_SetFilter(uint32_t filter_id, uint32_t mask_id) {
    // MCP2515 library handles filtering internally
    // This is a placeholder for advanced filtering if needed
    return true;
}

/**
 * @brief Reset MCP2515 controller
 * @return true if reset successful
 */
bool CAN_Reset(void) {
    // Stop current CAN operation
    CAN.end();
    
    // Stop SPI if needed
    SPI.end();
    
    // Reinitialize with stored pins
    return CAN_InitMCP2515(&g_pins);
}

/**
 * @brief Generic CAN initialization (compatibility wrapper)
 * @param config CAN configuration
 * @return STATUS_OK if successful
 */
Status_t CAN_Init(const CAN_Config_t* config) {
    // For now, ignore the config and use default MCP2515 pins
    // In a real implementation, you might want to map these properly
    if (CAN_InitMCP2515(&g_pins)) {
        return STATUS_OK;
    }
    return STATUS_ERROR;
}

/**
 * @brief Send OBD2 request
 * @param pid Parameter ID to request
 * @return STATUS_OK if successful
 */
Status_t CAN_SendOBD2Request(uint8_t pid) {
    CAN_Frame_t frame;
    frame.id = 0x7DF;  // OBD2 functional addressing
    frame.length = 8;
    frame.extended = false;
    frame.remote = false;
    
    // OBD2 request format: [Length, Mode, PID, padding...]
    frame.data[0] = 0x02;    // Length
    frame.data[1] = 0x01;    // Mode 01 (current data)
    frame.data[2] = pid;     // Parameter ID
    frame.data[3] = 0x00;    // Padding
    frame.data[4] = 0x00;
    frame.data[5] = 0x00;
    frame.data[6] = 0x00;
    frame.data[7] = 0x00;
    
    if (CAN_SendFrame(&frame)) {
        return STATUS_OK;
    }
    return STATUS_ERROR;
}

/**
 * @brief Receive OBD2 response
 * @param pid Expected parameter ID
 * @param data Buffer for response data
 * @param length Pointer to length variable
 * @param timeout_ms Timeout in milliseconds
 * @return STATUS_OK if successful
 */
Status_t CAN_ReceiveOBD2Response(uint8_t pid, uint8_t* data, uint8_t* length, uint32_t timeout_ms) {
    if (data == nullptr || length == nullptr) {
        return STATUS_INVALID_PARAM;
    }
    
    uint32_t start_time = millis();
    CAN_Frame_t frame;
    
    while ((millis() - start_time) < timeout_ms) {
        if (CAN_ReceiveFrame(&frame)) {
            // Check if this is an OBD2 response (ID range 0x7E8-0x7EF)
            if (frame.id >= 0x7E8 && frame.id <= 0x7EF) {
                // Check if response matches requested PID
                if (frame.length >= 3 && frame.data[1] == 0x41 && frame.data[2] == pid) {
                    // Extract data (skip length, mode, and PID bytes)
                    *length = frame.length - 3;
                    for (uint8_t i = 0; i < *length && i < 5; i++) {  // Max 5 bytes of data
                        data[i] = frame.data[3 + i];
                    }
                    return STATUS_OK;
                }
            }
        }
        delay(1);  // Small delay to prevent busy waiting
    }
    
    return STATUS_TIMEOUT;
}