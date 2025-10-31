/**
 * @file hal_gpio.cpp
 * @brief Hardware Abstraction Layer - GPIO implementation for ESP32
 * @version 1.0
 * @date 2025-10-30
 */

#include <Arduino.h>
#include "hal_interface.h"

Status_t HAL_GPIO_Init(uint8_t pin, GPIO_Mode_t mode) {
    if (pin > 39) {
        return STATUS_INVALID_PARAM;
    }
    
    switch (mode) {
        case HAL_GPIO_MODE_INPUT:
            pinMode(pin, INPUT);
            break;
        case HAL_GPIO_MODE_OUTPUT:
            pinMode(pin, OUTPUT);
            break;
        case HAL_GPIO_MODE_INPUT_PULLUP:
            pinMode(pin, INPUT_PULLUP);
            break;
        case HAL_GPIO_MODE_INPUT_PULLDOWN:
            pinMode(pin, INPUT_PULLDOWN);
            break;
        default:
            return STATUS_INVALID_PARAM;
    }
    
    return STATUS_OK;
}

Status_t HAL_GPIO_Write(uint8_t pin, GPIO_Level_t level) {
    if (pin > 39) {
        return STATUS_INVALID_PARAM;
    }
    
    digitalWrite(pin, (level == GPIO_LEVEL_HIGH) ? HIGH : LOW);
    return STATUS_OK;
}

GPIO_Level_t HAL_GPIO_Read(uint8_t pin) {
    if (pin > 39) {
        return GPIO_LEVEL_LOW;
    }
    
    return (digitalRead(pin) == HIGH) ? GPIO_LEVEL_HIGH : GPIO_LEVEL_LOW;
}

Status_t HAL_GPIO_Toggle(uint8_t pin) {
    if (pin > 39) {
        return STATUS_INVALID_PARAM;
    }
    
    GPIO_Level_t current_level = HAL_GPIO_Read(pin);
    GPIO_Level_t new_level = (current_level == GPIO_LEVEL_HIGH) ? GPIO_LEVEL_LOW : GPIO_LEVEL_HIGH;
    
    return HAL_GPIO_Write(pin, new_level);
}
