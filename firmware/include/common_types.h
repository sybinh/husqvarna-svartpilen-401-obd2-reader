/**
 * @file common_types.h
 * @brief Common data types and definitions for Husqvarna Svartpilen 401 OBD2 Reader
 * @version 1.0
 * @date 2025-10-30
 */

#ifndef COMMON_TYPES_H
#define COMMON_TYPES_H

#include <stdint.h>
#include <stdbool.h>

/* Return status types */
typedef enum {
    STATUS_OK = 0,
    STATUS_ERROR = 1,
    STATUS_TIMEOUT = 2,
    STATUS_INVALID_PARAM = 3,
    STATUS_NOT_INITIALIZED = 4,
    STATUS_BUSY = 5
} Status_t;

/* OBD2 PIDs for Husqvarna Svartpilen 401 */
typedef enum {
    PID_ENGINE_RPM = 0x0C,
    PID_VEHICLE_SPEED = 0x0D,
    PID_ENGINE_COOLANT_TEMP = 0x05,
    PID_THROTTLE_POSITION = 0x11,
    PID_FUEL_LEVEL = 0x2F,
    PID_ENGINE_RUNTIME = 0x1F,
    PID_FUEL_TRIM_BANK1 = 0x06,
    PID_INTAKE_MANIFOLD_PRESSURE = 0x0B
} OBD2_PID_t;

/* Vehicle data structure */
typedef struct {
    uint16_t rpm;                   /* Engine RPM */
    uint8_t speed;                  /* Vehicle speed in km/h */
    int8_t coolantTemp;             /* Coolant temperature in C */
    uint8_t throttlePosition;       /* Throttle position 0-100% */
    uint8_t fuelLevel;              /* Fuel level 0-100% */
    uint32_t engineRuntime;         /* Engine runtime in seconds */
    bool engineRunning;             /* Engine status */
    bool dataValid;                 /* Data validity flag */
    uint32_t lastUpdate;            /* Last update timestamp */
} VehicleData_t;

/* System states */
typedef enum {
    SYSTEM_STATE_INIT = 0,
    SYSTEM_STATE_IDLE = 1,
    SYSTEM_STATE_CONNECTING = 2,
    SYSTEM_STATE_CONNECTED = 3,
    SYSTEM_STATE_READING_DATA = 4,
    SYSTEM_STATE_ERROR = 5
} SystemState_t;

/* Callback function types */
typedef void (*DataUpdateCallback_t)(const VehicleData_t* data);

/* Constants */
#define CAN_TIMEOUT_MS              100
#define OBD2_REQUEST_TIMEOUT_MS     500

#endif /* COMMON_TYPES_H */
