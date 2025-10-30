/**
 * @file obd2_handler.h
 * @brief OBD2 protocol handler interface
 * @version 1.0
 * @date 2025-10-30
 */

#ifndef OBD2_HANDLER_H
#define OBD2_HANDLER_H

#include "common_types.h"

/* OBD2 Configuration */
typedef struct {
    uint8_t can_rx_pin;             /* CAN RX pin */
    uint8_t can_tx_pin;             /* CAN TX pin */
    uint32_t can_baudrate;          /* CAN baudrate */
    uint32_t update_interval_ms;    /* Data update interval */
} OBD2_Config_t;

/* OBD2 Interface Functions */
Status_t OBD2_Init(const OBD2_Config_t* config);
Status_t OBD2_RegisterCallback(DataUpdateCallback_t callback);
Status_t OBD2_ReadAllData(void);
Status_t OBD2_ReadRPM(uint16_t* rpm);
Status_t OBD2_ReadSpeed(uint8_t* speed);
Status_t OBD2_ReadCoolantTemp(int8_t* temp);
Status_t OBD2_ReadThrottlePosition(uint8_t* throttle);
const VehicleData_t* OBD2_GetVehicleData(void);

#endif /* OBD2_HANDLER_H */
