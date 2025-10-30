/**
 * @file oled_driver.h
 * @brief OLED display driver interface
 * @version 1.0
 * @date 2025-10-30
 */

#ifndef OLED_DRIVER_H
#define OLED_DRIVER_H

#include "common_types.h"

/* OLED Interface Functions */
Status_t OLED_Init(uint8_t sda_pin, uint8_t scl_pin, uint8_t address);
Status_t OLED_Clear(void);
Status_t OLED_SetCursor(uint8_t x, uint8_t y);
Status_t OLED_Print(const char* text);
Status_t OLED_Println(const char* text);
Status_t OLED_Update(void);
Status_t OLED_DrawLine(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1);
Status_t OLED_SetTextSize(uint8_t size);

#endif /* OLED_DRIVER_H */
