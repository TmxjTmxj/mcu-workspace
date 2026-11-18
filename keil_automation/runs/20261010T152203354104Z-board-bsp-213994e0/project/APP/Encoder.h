
#include "STC8xxxx.h"

#define ENCODER_A		P32    //  编码器  A  ——外部中断INT0（P3.2)引脚，下降沿产生中断，根据此时的B的电平高与低，判断是正转还是反转，并计数
#define ENCODER_B		P33

void SendEncoder(void);