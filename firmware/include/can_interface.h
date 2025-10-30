/**
 * @file can_interface.h
 * @brief CAN communication interface for OBD2
 * @version 1.0
 * @date 2025-10-30
 */

#ifndef CAN_INTERFACE_H
#define CAN_INTERFACE_H

#include "common_types.h"

/* CAN frame structure */
typedef struct {
    uint32_t id;                    /* CAN ID */
    uint8_t length;                 /* Data length (0-8) */
    uint8_t data[8];                /* Data bytes */
    bool extended;                  /* Extended frame flag */
    bool remote;                    /* Remote frame flag */
} CAN_Frame_t;

/* CAN configuration */
typedef struct {
    uint8_t rx_pin;                 /* CAN RX pin */
    uint8_t tx_pin;                 /* CAN TX pin */
    uint32_t baudrate;              /* CAN baudrate */
} CAN_Config_t;

/* CAN Interface Functions */
Status_t CAN_Init(const CAN_Config_t* config);
Status_t CAN_DeInit(void);
Status_t CAN_SendFrame(const CAN_Frame_t* frame);
Status_t CAN_ReceiveFrame(CAN_Frame_t* frame, uint32_t timeout_ms);
bool CAN_IsFrameAvailable(void);

/* OBD2 specific functions */
Status_t CAN_SendOBD2Request(uint8_t pid);
Status_t CAN_ReceiveOBD2Response(uint8_t pid, uint8_t* data, uint8_t* length, uint32_t timeout_ms);

#endif /* CAN_INTERFACE_H */
