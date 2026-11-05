// Source: FractalEngineer/config (fork of betaflight/config), branch SP8-AIO, commit d368ecbb1 "Config: Add FRACSP8AIO target" (GPL-3.0).
// Adapted for Betaflight 4.5 (BetaFlight 3D Edition): SERIAL_PORT_UART1 -> SERIAL_PORT_USART1 (port renamed in 2025.12).
/*
 * This file is part of Betaflight.
 *
 * Betaflight is free software. You can redistribute this software
 * and/or modify this software under the terms of the GNU General
 * Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later
 * version.
 *
 * Betaflight is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public
 * License along with this software.
 *
 * If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#define BOARD_NAME              FRACSP8AIO
#define MANUFACTURER_ID         FRAC

#define FC_TARGET_MCU           AT32F435G

#define USE_ACC
#define USE_ACC_SPI_ICM42688P

#define USE_GYRO
#define USE_GYRO_SPI_ICM42688P

#define GYRO_1_EXTI_PIN         PB7
#define GYRO_1_CS_PIN           PA4
#define GYRO_1_SPI_INSTANCE     SPI1

#define USE_FLASH
#define USE_FLASH_W25Q128FV
#define FLASH_CS_PIN            PA15
#define FLASH_SPI_INSTANCE      SPI3

#define USE_MAX7456
#define MAX7456_SPI_CS_PIN      PB12
#define MAX7456_SPI_INSTANCE    SPI2

#define LED0_PIN                PA13

#define BEEPER_PIN              PA8

#define MOTOR1_PIN              PB0
#define MOTOR2_PIN              PB1
#define MOTOR3_PIN              PA3
#define MOTOR4_PIN              PA2

#define UART1_TX_PIN            PA9
#define UART1_RX_PIN            PA10

#define UART3_TX_PIN            PB11
#define UART3_RX_PIN            PB10

#define UART4_TX_PIN            PH3
#define UART4_RX_PIN            PH2

#define UART5_TX_PIN            PB6
#define UART5_RX_PIN            PB8

#define SPI1_SCK_PIN            PA5
#define SPI1_SDI_PIN            PA6
#define SPI1_SDO_PIN            PA7

#define SPI2_SCK_PIN            PB13
#define SPI2_SDI_PIN            PB14
#define SPI2_SDO_PIN            PB15

#define SPI3_SCK_PIN            PB3
#define SPI3_SDI_PIN            PB4
#define SPI3_SDO_PIN            PB5

#define ADC_VBAT_PIN            PA0
#define ADC_CURR_PIN            PA1

#define LED_STRIP_PIN           PB9

#define PINIO1_PIN              PA14

#define TIMER_PIN_MAPPING \
    TIMER_PIN_MAP(0, PB0, 1, 9) \
    TIMER_PIN_MAP(1, PB1, 1, 10) \
    TIMER_PIN_MAP(2, PA3, 1, 11) \
    TIMER_PIN_MAP(3, PA2, 1, 12)

#define ADC1_DMA_OPT            0
#define ADC_INSTANCE            ADC1

#define DEFAULT_BLACKBOX_DEVICE BLACKBOX_DEVICE_FLASH

#define DEFAULT_CURRENT_METER_SOURCE CURRENT_METER_ADC
#define DEFAULT_CURRENT_METER_SCALE 1180

#define DEFAULT_VOLTAGE_METER_SOURCE VOLTAGE_METER_ADC
#define DEFAULT_VOLTAGE_METER_SCALE_DEFAULT 110

#define SERIALRX_PROVIDER       SERIALRX_CRSF
#define SERIALRX_UART           SERIAL_PORT_USART1   // 4.5 name (2025.12: SERIAL_PORT_UART1)
