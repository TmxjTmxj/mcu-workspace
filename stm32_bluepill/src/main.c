#include "stm32f1xx_hal.h"
#include <string.h>

static UART_HandleTypeDef uart;

static void fail(void) {
    /* UART may not exist yet; debugger can break here. */
    __disable_irq();
    for (;;) {}
}

static void clock_init(void) {
    RCC_OscInitTypeDef osc = {0};
    RCC_ClkInitTypeDef clk = {0};
    osc.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    osc.HSEState = RCC_HSE_ON;
    osc.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
    osc.PLL.PLLState = RCC_PLL_ON;
    osc.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    osc.PLL.PLLMUL = RCC_PLL_MUL9; /* Blue Pill: 8MHz HSE -> 72MHz */
    if (HAL_RCC_OscConfig(&osc) != HAL_OK) fail();
    clk.ClockType = RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK |
                    RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    clk.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    clk.AHBCLKDivider = RCC_SYSCLK_DIV1;
    clk.APB1CLKDivider = RCC_HCLK_DIV2;
    clk.APB2CLKDivider = RCC_HCLK_DIV1;
    if (HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_2) != HAL_OK) fail();
}

void SysTick_Handler(void) { HAL_IncTick(); }

static void io_init(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_USART1_CLK_ENABLE();
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_0;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &gpio);
    gpio.Pin = GPIO_PIN_13;
    HAL_GPIO_Init(GPIOC, &gpio);
    /* Apply idle levels after mode setup, including on digital GPIO models. */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
    gpio.Pin = GPIO_PIN_12;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOB, &gpio);
    gpio.Pin = GPIO_PIN_9;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &gpio);
    gpio.Pin = GPIO_PIN_10;
    gpio.Mode = GPIO_MODE_INPUT;
    HAL_GPIO_Init(GPIOA, &gpio);
    uart.Instance = USART1;
    uart.Init.BaudRate = 115200;
    uart.Init.WordLength = UART_WORDLENGTH_8B;
    uart.Init.StopBits = UART_STOPBITS_1;
    uart.Init.Parity = UART_PARITY_NONE;
    uart.Init.Mode = UART_MODE_TX_RX;
    uart.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    uart.Init.OverSampling = UART_OVERSAMPLING_16;
    if (HAL_UART_Init(&uart) != HAL_OK) fail();
}

static void emit(const char *text) {
    if (HAL_UART_Transmit(&uart, (uint8_t *)text, (uint16_t)strlen(text), 100) != HAL_OK) fail();
}

int main(void) {
    HAL_Init();
    clock_init();
    io_init();
    emit("BOOT STM32F103C8\r\nCLOCK 72000000\r\nREADY\r\n");
    uint32_t last_led = HAL_GetTick(), changed_at = HAL_GetTick();
    GPIO_PinState candidate = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_12);
    GPIO_PinState stable = GPIO_PIN_SET;
    unsigned fast = 0, lit = 0;
    for (;;) {
        uint32_t now = HAL_GetTick();
        GPIO_PinState input = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_12);
        if (input != candidate) { candidate = input; changed_at = now; }
        if (candidate != stable && (uint32_t)(now - changed_at) >= 20) {
            stable = candidate;
            if (stable == GPIO_PIN_RESET) {
                emit("BUTTON PRESSED\r\n");
                fast ^= 1;
                emit(fast ? "MODE FAST\r\n" : "MODE SLOW\r\n");
            } else emit("BUTTON RELEASED\r\n");
        }
        if ((uint32_t)(now - last_led) >= (fast ? 100u : 500u)) {
            last_led = now;
            lit ^= 1;
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, lit ? GPIO_PIN_SET : GPIO_PIN_RESET);
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, lit ? GPIO_PIN_RESET : GPIO_PIN_SET);
            emit(lit ? "LED ON\r\n" : "LED OFF\r\n");
        }
    }
}
