/**
 * @file hal_interface.h
 * @brief Hardware Abstraction Layer interface definitions
 * @version 1.0
 * @date 2025-10-30
 */

#ifndef HAL_INTERFACE_H
#define HAL_INTERFACE_H

#include "common_types.h"

/* GPIO operations */
typedef enum {
    HAL_GPIO_MODE_INPUT = 0,
    HAL_GPIO_MODE_OUTPUT = 1,
    HAL_GPIO_MODE_INPUT_PULLUP = 2,
    HAL_GPIO_MODE_INPUT_PULLDOWN = 3
} GPIO_Mode_t;

typedef enum {
    GPIO_LEVEL_LOW = 0,
    GPIO_LEVEL_HIGH = 1
} GPIO_Level_t;

/* HAL GPIO Interface */
Status_t HAL_GPIO_Init(uint8_t pin, GPIO_Mode_t mode);
Status_t HAL_GPIO_Write(uint8_t pin, GPIO_Level_t level);
GPIO_Level_t HAL_GPIO_Read(uint8_t pin);
Status_t HAL_GPIO_Toggle(uint8_t pin);

/* HAL I2C Interface */
Status_t HAL_I2C_Init(uint8_t sda_pin, uint8_t scl_pin, uint32_t frequency);
Status_t HAL_I2C_Write(uint8_t device_addr, uint8_t* data, uint16_t length);
Status_t HAL_I2C_Read(uint8_t device_addr, uint8_t* data, uint16_t length);

/* HAL Timer Interface */
typedef void (*TimerCallback_t)(void);
Status_t HAL_Timer_Init(uint8_t timer_id, uint32_t period_ms, TimerCallback_t callback);
uint32_t HAL_Timer_GetTick(void);

#endif /* HAL_INTERFACE_H */
