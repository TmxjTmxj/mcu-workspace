#include "stm32f1xx_hal.h"
#include "control.h"
#include "protocol.h"
#include <stdio.h>
#include <string.h>
static UART_HandleTypeDef uart;
static ADC_HandleTypeDef adc;
static TIM_HandleTypeDef pwm;
static Control controller;
static volatile unsigned rx_head=0,rx_tail=0,rx_overflow=0;
static uint8_t rx_byte,rx_buffer[128];
static void fail(void) {
    __HAL_RCC_GPIOB_CLK_ENABLE(); __HAL_RCC_TIM2_CLK_ENABLE();
    GPIO_InitTypeDef g={0};g.Pin=GPIO_PIN_14|GPIO_PIN_0;g.Mode=GPIO_MODE_OUTPUT_PP;g.Speed=GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB,&g);HAL_GPIO_WritePin(GPIOB,GPIO_PIN_14,GPIO_PIN_RESET);
    TIM2->CCR1=0;HAL_GPIO_WritePin(GPIOB,GPIO_PIN_0,GPIO_PIN_SET);
    __disable_irq(); for(;;){}
}
void SysTick_Handler(void) { HAL_IncTick(); }
void USART1_IRQHandler(void) { HAL_UART_IRQHandler(&uart); }
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *handle) {
    if(handle!=&uart)return;
    unsigned next=(rx_head+1)%sizeof(rx_buffer);
    if(next!=rx_tail) { rx_buffer[rx_head]=rx_byte;rx_head=next; }
    else rx_overflow=1;
    HAL_UART_Receive_IT(&uart,&rx_byte,1);
}
void HAL_UART_ErrorCallback(UART_HandleTypeDef *handle) {
    if(handle!=&uart)return;
    rx_overflow=1;__HAL_UART_CLEAR_OREFLAG(handle);
    HAL_UART_Receive_IT(handle,&rx_byte,1);
}
static void clock_init(void) {
    RCC_OscInitTypeDef osc={0}; RCC_ClkInitTypeDef clk={0};
    osc.OscillatorType=RCC_OSCILLATORTYPE_HSE; osc.HSEState=RCC_HSE_ON;
    osc.HSEPredivValue=RCC_HSE_PREDIV_DIV1; osc.PLL.PLLState=RCC_PLL_ON;
    osc.PLL.PLLSource=RCC_PLLSOURCE_HSE; osc.PLL.PLLMUL=RCC_PLL_MUL9;
    if(HAL_RCC_OscConfig(&osc)!=HAL_OK) fail();
    clk.ClockType=RCC_CLOCKTYPE_SYSCLK|RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
    clk.SYSCLKSource=RCC_SYSCLKSOURCE_PLLCLK; clk.AHBCLKDivider=RCC_SYSCLK_DIV1;
    clk.APB1CLKDivider=RCC_HCLK_DIV2; clk.APB2CLKDivider=RCC_HCLK_DIV1;
    if(HAL_RCC_ClockConfig(&clk,FLASH_LATENCY_2)!=HAL_OK) fail();
    __HAL_RCC_ADC_CONFIG(RCC_ADCPCLK2_DIV6);
}
static void io_init(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE(); __HAL_RCC_GPIOB_CLK_ENABLE(); __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_USART1_CLK_ENABLE(); __HAL_RCC_ADC1_CLK_ENABLE(); __HAL_RCC_TIM2_CLK_ENABLE();
    GPIO_InitTypeDef g={0};
    g.Pin=GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_0; g.Mode=GPIO_MODE_OUTPUT_PP; g.Speed=GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB,&g); HAL_GPIO_WritePin(GPIOB,GPIO_PIN_13,GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOB,GPIO_PIN_14|GPIO_PIN_0,GPIO_PIN_RESET);
    g.Pin=GPIO_PIN_12; g.Mode=GPIO_MODE_INPUT; g.Pull=GPIO_PULLUP; HAL_GPIO_Init(GPIOB,&g);
    g.Pin=GPIO_PIN_1|GPIO_PIN_2; g.Mode=GPIO_MODE_ANALOG; g.Pull=GPIO_NOPULL; HAL_GPIO_Init(GPIOA,&g);
    g.Pin=GPIO_PIN_0|GPIO_PIN_9; g.Mode=GPIO_MODE_AF_PP; g.Speed=GPIO_SPEED_FREQ_HIGH; HAL_GPIO_Init(GPIOA,&g);
    g.Pin=GPIO_PIN_10; g.Mode=GPIO_MODE_INPUT; HAL_GPIO_Init(GPIOA,&g);
    uart.Instance=USART1; uart.Init.BaudRate=115200; uart.Init.WordLength=UART_WORDLENGTH_8B;
    uart.Init.StopBits=UART_STOPBITS_1; uart.Init.Parity=UART_PARITY_NONE;
    uart.Init.Mode=UART_MODE_TX_RX; uart.Init.HwFlowCtl=UART_HWCONTROL_NONE;
    uart.Init.OverSampling=UART_OVERSAMPLING_16;
    if(HAL_UART_Init(&uart)!=HAL_OK) fail();
    HAL_NVIC_SetPriority(USART1_IRQn,1,0);HAL_NVIC_EnableIRQ(USART1_IRQn);
    if(HAL_UART_Receive_IT(&uart,&rx_byte,1)!=HAL_OK) fail();
    adc.Instance=ADC1; adc.Init.ScanConvMode=ADC_SCAN_DISABLE;
    adc.Init.ContinuousConvMode=DISABLE; adc.Init.DiscontinuousConvMode=DISABLE;
    adc.Init.ExternalTrigConv=ADC_SOFTWARE_START; adc.Init.DataAlign=ADC_DATAALIGN_RIGHT;
    adc.Init.NbrOfConversion=1;
    if(HAL_ADC_Init(&adc)!=HAL_OK || HAL_ADCEx_Calibration_Start(&adc)!=HAL_OK) fail();
    pwm.Instance=TIM2; pwm.Init.Prescaler=71; pwm.Init.CounterMode=TIM_COUNTERMODE_UP;
    pwm.Init.Period=999; pwm.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;
    pwm.Init.AutoReloadPreload=TIM_AUTORELOAD_PRELOAD_DISABLE;
    if(HAL_TIM_PWM_Init(&pwm)!=HAL_OK) fail();
    TIM_OC_InitTypeDef oc={0}; oc.OCMode=TIM_OCMODE_PWM1; oc.Pulse=0;
    oc.OCPolarity=TIM_OCPOLARITY_HIGH; oc.OCFastMode=TIM_OCFAST_DISABLE;
    if(HAL_TIM_PWM_ConfigChannel(&pwm,&oc,TIM_CHANNEL_1)!=HAL_OK || HAL_TIM_PWM_Start(&pwm,TIM_CHANNEL_1)!=HAL_OK) fail();
}
static void emit(const char *text) {
    if(HAL_UART_Transmit(&uart,(uint8_t*)text,(uint16_t)strlen(text),30)!=HAL_OK) fail();
}
static int read_adc(uint32_t channel) {
    ADC_ChannelConfTypeDef config={0}; config.Channel=channel;
    config.Rank=ADC_REGULAR_RANK_1; config.SamplingTime=ADC_SAMPLETIME_55CYCLES_5;
    if(HAL_ADC_ConfigChannel(&adc,&config)!=HAL_OK || HAL_ADC_Start(&adc)!=HAL_OK || HAL_ADC_PollForConversion(&adc,2)!=HAL_OK) return -1;
    int value=(int)HAL_ADC_GetValue(&adc); HAL_ADC_Stop(&adc); return value;
}
static void receive(void) {
    static LineParser parser={0};
    if(rx_overflow) { parser.discard=1;rx_overflow=0; }
    while(rx_tail!=rx_head) {
        unsigned char b=rx_buffer[rx_tail];rx_tail=(rx_tail+1)%sizeof(rx_buffer);
        int complete=protocol_byte(&parser,b);
        if(complete)emit(complete==1 && control_command(&controller,parser.line)?"ACK\r\n":"NACK\r\n");
    }
}
int main(void) {
    HAL_Init(); clock_init(); io_init(); control_init(&controller);
    emit("BOOT SMART_FAN STM32F103C8\r\nREADY ADC PWM UART\r\n");
    uint32_t previous=HAL_GetTick();
    for(;;) {
        receive(); uint32_t now=HAL_GetTick();
        if(now-previous>=100) {
            previous=now;
            int raw=read_adc(ADC_CHANNEL_1), current=read_adc(ADC_CHANNEL_2);
            int temperature=raw<=4 || raw>=4090?-9999:((raw*3300/4095)-500)*10;
            control_step(&controller,temperature,current<0?3001:current*3300/4095,
                HAL_GPIO_ReadPin(GPIOB,GPIO_PIN_12)==GPIO_PIN_RESET);
            __HAL_TIM_SET_COMPARE(&pwm,TIM_CHANNEL_1,controller.duty*10);
            HAL_GPIO_WritePin(GPIOB,GPIO_PIN_14,controller.duty?GPIO_PIN_SET:GPIO_PIN_RESET);
            HAL_GPIO_WritePin(GPIOB,GPIO_PIN_0,controller.fault?GPIO_PIN_SET:GPIO_PIN_RESET);
            char text[100];
            snprintf(text,sizeof(text),"STATE,%lu,%d,%d,%d,%d,%d,%d\r\n",(unsigned long)now,
                controller.temperature,controller.target,controller.duty,controller.mode,controller.fault,controller.current);
            emit(text);
        }
        __WFI(); /* SysTick wakes at 1ms, avoiding a busy polling loop. */
    }
}
