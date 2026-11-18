#include "WaterLight.h"
#include "GPIO.h"

static u8 water_index = 0;

void WaterLightInit(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.Pin = GPIO_Pin_All;
    GPIO_InitStructure.Mode = GPIO_PullUp;
    GPIO_Inilize(GPIO_P6, &GPIO_InitStructure);
    P6 = 0xFF;
}

void WaterLight(void)
{
    P6 = ~(1 << water_index);
    water_index++;
    if (water_index >= 8) water_index = 0;
}
