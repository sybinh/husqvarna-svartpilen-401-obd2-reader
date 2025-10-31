/**
 * @file can_interface.h
 * @brief CAN Interface Layer for MCP2515 Controller
 * @details Provides CAN communication interface using MCP2515 CAN controller via SPI
 * @author OBD2 Reader Project
 * @date 2024
 */

#ifndef CAN_INTERFACE_H
#define CAN_INTERFACE_H

#include "common_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* CAN frame structure */
typedef struct {
    uint32_t id;                    /* CAN ID */
    uint8_t length;                 /* Data length (0-8) */
    uint8_t data[8];                /* Data bytes */
    bool extended;                  /* Extended frame flag */
    bool remote;                    /* Remote frame flag */
} CAN_Frame_t;

/* Hardware pin configuration for MCP2515 */
typedef struct {
    uint8_t mcp2515_cs;             /* MCP2515 CS pin */
    uint8_t mcp2515_int;            /* MCP2515 INT pin */
    uint8_t spi_mosi;               /* SPI MOSI pin */
    uint8_t spi_miso;               /* SPI MISO pin */
    uint8_t spi_sck;                /* SPI SCK pin */
    uint8_t status_led;             /* Status LED pin */
} HardwarePins_t;

/* CAN configuration */
typedef struct {
    uint8_t rx_pin;                 /* CAN RX pin */
    uint8_t tx_pin;                 /* CAN TX pin */
    uint32_t baudrate;              /* CAN baudrate */
} CAN_Config_t;

/* CAN Interface Functions */
bool CAN_InitMCP2515(const HardwarePins_t* pins);
bool CAN_Reset(void);
bool CAN_SendFrame(const CAN_Frame_t* frame);
bool CAN_ReceiveFrame(CAN_Frame_t* frame);
bool CAN_Available(void);
bool CAN_SetFilter(uint32_t filter_id, uint32_t mask_id);

/* Generic CAN Interface (for compatibility) */
Status_t CAN_Init(const CAN_Config_t* config);
Status_t CAN_DeInit(void);

/* OBD2 specific functions */
Status_t CAN_SendOBD2Request(uint8_t pid);
Status_t CAN_ReceiveOBD2Response(uint8_t pid, uint8_t* data, uint8_t* length, uint32_t timeout_ms);

#ifdef __cplusplus
}
#endif

#endif /* CAN_INTERFACE_H */
