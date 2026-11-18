/*---------------------------------------------------------------------*/
/* --- STC MCU Limited ------------------------------------------------*/
/* --- STC 1T Series MCU Demo Programme -------------------------------*/
/* --- Mobile: (86)13922805190 ----------------------------------------*/
/* --- Fax: 86-0513-55012956,55012947,55012969 ------------------------*/
/* --- Tel: 86-0513-55012928,55012929,55012966 ------------------------*/
/* --- Web: www.STCMCU.com --------------------------------------------*/
/* --- Web: www.STCMCUDATA.com  ---------------------------------------*/
/* --- QQ:  800003751 -------------------------------------------------*/
/* 如果要在程序中使用此代码,请在程序中注明使用了STC的资料及程序            */
/*---------------------------------------------------------------------*/


#include	"config.h"
#include	"System_init.h"

#include	"gpio.h"
#include	"exti.h"
#include	"timer.h"
#include	"uart.h"
#include	"pwm.h"

//若App任务需要使用初始化函数，则在这里包含进相关app任务的头文件
#include "Led1.h"




/*************	本地常量声明	**************/


/*************	本地变量声明	**************/

PWMx_Duty PWMA_Duty;

/*************	本地函数声明	**************/



/*************  外部函数和变量声明 *****************/


//========================================================================
//                                IO口配置
//========================================================================
void	GPIO_config(void)
{
	GPIO_InitTypeDef	GPIO_InitStructure;		//结构定义
	
	GPIO_InitStructure.Pin  = GPIO_Pin_All;		//指定要初始化的IO,
	GPIO_InitStructure.Mode = GPIO_PullUp;		//指定IO的输入或输出方式,GPIO_PullUp,GPIO_HighZ,GPIO_OUT_OD,GPIO_OUT_PP
	GPIO_Inilize(GPIO_P6,&GPIO_InitStructure);	//初始化

	GPIO_InitStructure.Pin  = GPIO_Pin_2;		//指定要初始化的IO,
	GPIO_InitStructure.Mode = GPIO_PullUp;		//指定IO的输入或输出方式,GPIO_PullUp,GPIO_HighZ,GPIO_OUT_OD,GPIO_OUT_PP
	GPIO_Inilize(GPIO_P3,&GPIO_InitStructure);	//初始化	

}

//========================================================================
//                               定时器配置
//========================================================================
void	Timer_config(void)
{
	TIM_InitTypeDef		TIM_InitStructure;						//结构定义
	TIM_InitStructure.TIM_Mode      = TIM_16BitAutoReload;	//指定工作模式,   TIM_16BitAutoReload,TIM_16Bit,TIM_8BitAutoReload,TIM_16BitAutoReloadNoMask
	TIM_InitStructure.TIM_Priority    = Priority_0;			//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
	TIM_InitStructure.TIM_Interrupt = ENABLE;					//中断是否允许,   ENABLE或DISABLE
	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_1T;		//指定时钟源,     TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
	TIM_InitStructure.TIM_ClkOut    = DISABLE;				//是否输出高速脉冲, ENABLE或DISABLE
	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / 1000UL);		//初值,
	TIM_InitStructure.TIM_Run       = ENABLE;					//是否初始化后启动定时器, ENABLE或DISABLE
	Timer_Inilize(Timer0,&TIM_InitStructure);					//初始化Timer0	  Timer0,Timer1,Timer2,Timer3,Timer4
	
//	TIM_InitStructure.TIM_Mode      = TIM_16BitAutoReload;	//指定工作模式,   TIM_16BitAutoReload,TIM_16Bit,TIM_8BitAutoReload,TIM_16BitAutoReloadNoMask
//	TIM_InitStructure.TIM_Priority    = Priority_0;			//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
//	TIM_InitStructure.TIM_Interrupt = ENABLE;					//中断是否允许,   ENABLE或DISABLE
//	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_1T;		//指定时钟源, TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
//	TIM_InitStructure.TIM_ClkOut    = DISABLE;				//是否输出高速脉冲, ENABLE或DISABLE
//	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / 10000);			//初值,
//	TIM_InitStructure.TIM_Run       = ENABLE;					//是否初始化后启动定时器, ENABLE或DISABLE
//	Timer_Inilize(Timer1,&TIM_InitStructure);					//初始化Timer1	  Timer0,Timer1,Timer2,Timer3,Timer4

//	TIM_InitStructure.TIM_Interrupt = ENABLE;					//中断是否允许,   ENABLE或DISABLE. (注意: Timer2固定为16位自动重装, 中断固定为低优先级)
//	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_1T;		//指定时钟源,     TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
//	TIM_InitStructure.TIM_ClkOut    = DISABLE;				//是否输出高速脉冲, ENABLE或DISABLE
//	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / 1000);				//初值
//	TIM_InitStructure.TIM_Run       = ENABLE;					//是否初始化后启动定时器, ENABLE或DISABLE
//	Timer_Inilize(Timer2,&TIM_InitStructure);					//初始化Timer2	  Timer0,Timer1,Timer2,Timer3,Timer4

//	TIM_InitStructure.TIM_Interrupt = DISABLE;					//中断是否允许,   ENABLE或DISABLE. (注意: Timer2固定为16位自动重装, 中断固定为低优先级)
//	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_12T;	//指定时钟源,     TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
//	TIM_InitStructure.TIM_ClkOut    = ENABLE;					//是否输出高速脉冲, ENABLE或DISABLE
//	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / (100*12));		//初值
//	TIM_InitStructure.TIM_Run       = ENABLE;					//是否初始化后启动定时器, ENABLE或DISABLE
//	Timer_Inilize(Timer3,&TIM_InitStructure);					//初始化Timer3	  Timer0,Timer1,Timer2,Timer3,Timer4

//	TIM_InitStructure.TIM_Interrupt = ENABLE;					//中断是否允许,   ENABLE或DISABLE. (注意: Timer2固定为16位自动重装, 中断固定为低优先级)
//	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_12T;	//指定时钟源,     TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
//	TIM_InitStructure.TIM_ClkOut    = ENABLE;					//是否输出高速脉冲, ENABLE或DISABLE
//	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / (50*12));		//初值
//	TIM_InitStructure.TIM_Run       = ENABLE;					//是否初始化后启动定时器, ENABLE或DISABLE
//	Timer_Inilize(Timer4,&TIM_InitStructure);					//初始化Timer4	  Timer0,Timer1,Timer2,Timer3,Timer4
}


//========================================================================
//                              串口初始化
//========================================================================
void	UART_config(void)
{
	COMx_InitDefine		COMx_InitStructure;					//结构定义
	COMx_InitStructure.UART_Mode      = UART_8bit_BRTx;		//模式,       UART_ShiftRight,UART_8bit_BRTx,UART_9bit,UART_9bit_BRTx
	COMx_InitStructure.UART_BRT_Use   = BRT_Timer1;			//选择波特率发生器,   BRT_Timer1, BRT_Timer2 (注意: 串口2固定使用BRT_Timer2)
	COMx_InitStructure.UART_BaudRate  = 115200ul;			//波特率, 一般 110 ~ 115200
	COMx_InitStructure.UART_RxEnable  = ENABLE;				//接收允许,   ENABLE或DISABLE
	COMx_InitStructure.BaudRateDouble = DISABLE;			//波特率加倍, ENABLE或DISABLE
	COMx_InitStructure.UART_Interrupt = ENABLE;				//中断允许,   ENABLE或DISABLE
	COMx_InitStructure.UART_Priority    = Priority_0;			//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
	COMx_InitStructure.UART_P_SW      = UART1_SW_P30_P31;	//切换端口,   UART1_SW_P30_P31,UART1_SW_P36_P37,UART1_SW_P16_P17,UART1_SW_P43_P44
	UART_Configuration(UART1, &COMx_InitStructure);		//初始化串口1 UART1,UART2,UART3,UART4

//	COMx_InitStructure.UART_Mode      = UART_8bit_BRTx;		//模式,       UART_ShiftRight,UART_8bit_BRTx,UART_9bit,UART_9bit_BRTx
////	COMx_InitStructure.UART_BRT_Use   = BRT_Timer2;			//选择波特率发生器, BRT_Timer2 (注意: 串口2固定使用BRT_Timer2, 所以不用选择)
//	COMx_InitStructure.UART_BaudRate  = 57600ul;			//波特率,     110 ~ 115200
//	COMx_InitStructure.UART_RxEnable  = ENABLE;				//接收允许,   ENABLE或DISABLE
//	COMx_InitStructure.UART_Interrupt = ENABLE;				//中断允许,   ENABLE或DISABLE
//	COMx_InitStructure.UART_Priority    = Priority_0;			//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
//	COMx_InitStructure.UART_P_SW      = UART2_SW_P46_P47;	//切换端口,   UART2_SW_P10_P11,UART2_SW_P46_P47
//	UART_Configuration(UART2, &COMx_InitStructure);		//初始化串口2 UART1,UART2,UART3,UART4

//	PrintString1("STC8 UART1 Test Programme!\r\n");	//UART1发送一个字符串
//	PrintString2("STC8 UART2 Test Programme!\r\n");	//UART2发送一个字符串
}

//========================================================================
//                             外部中断初始化
//========================================================================
void	Exti_config(void)
{
	EXTI_InitTypeDef	Exti_InitStructure;							//结构定义

	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//中断使能,   ENABLE或DISABLE
	Exti_InitStructure.EXTI_Mode      = EXT_MODE_Fall;//中断模式,   EXT_MODE_RiseFall,EXT_MODE_Fall
	Exti_InitStructure.EXTI_Priority  = Priority_0;		//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
	Ext_Inilize(EXT_INT0,&Exti_InitStructure);				//初始化

//	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//中断使能,   ENABLE或DISABLE
//	Exti_InitStructure.EXTI_Mode      = EXT_MODE_Fall;//中断模式,   EXT_MODE_RiseFall,EXT_MODE_Fall
//	Exti_InitStructure.EXTI_Priority  = Priority_0;		//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
//	Ext_Inilize(EXT_INT1,&Exti_InitStructure);				//初始化

//	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//中断使能,   ENABLE或DISABLE
//	Ext_Inilize(EXT_INT2,&Exti_InitStructure);				//初始化

//	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//中断使能,   ENABLE或DISABLE
//	Ext_Inilize(EXT_INT3,&Exti_InitStructure);				//初始化

//	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//中断使能,   ENABLE或DISABLE
//	Ext_Inilize(EXT_INT4,&Exti_InitStructure);				//初始化
}

/***************  PWM初始化函数 *****************/
void	PWM_config(void)
{
	PWMx_InitDefine		PWMx_InitStructure;
	
	PWMx_InitStructure.PWM1_Mode    =	CCMRn_PWM_MODE1;	//模式,		CCMRn_FREEZE,CCMRn_MATCH_VALID,CCMRn_MATCH_INVALID,CCMRn_ROLLOVER,CCMRn_FORCE_INVALID,CCMRn_FORCE_VALID,CCMRn_PWM_MODE1,CCMRn_PWM_MODE2
	PWMx_InitStructure.PWM2_Mode    =	CCMRn_PWM_MODE1;	//模式,		CCMRn_FREEZE,CCMRn_MATCH_VALID,CCMRn_MATCH_INVALID,CCMRn_ROLLOVER,CCMRn_FORCE_INVALID,CCMRn_FORCE_VALID,CCMRn_PWM_MODE1,CCMRn_PWM_MODE2
	PWMx_InitStructure.PWM3_Mode    =	CCMRn_PWM_MODE1;	//模式,		CCMRn_FREEZE,CCMRn_MATCH_VALID,CCMRn_MATCH_INVALID,CCMRn_ROLLOVER,CCMRn_FORCE_INVALID,CCMRn_FORCE_VALID,CCMRn_PWM_MODE1,CCMRn_PWM_MODE2
	PWMx_InitStructure.PWM4_Mode    =	CCMRn_PWM_MODE1;	//模式,		CCMRn_FREEZE,CCMRn_MATCH_VALID,CCMRn_MATCH_INVALID,CCMRn_ROLLOVER,CCMRn_FORCE_INVALID,CCMRn_FORCE_VALID,CCMRn_PWM_MODE1,CCMRn_PWM_MODE2

	PWMx_InitStructure.PWM1_SetPriority  = Priority_0;			//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
	PWMx_InitStructure.PWM2_SetPriority  = Priority_0;			//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
	PWMx_InitStructure.PWM3_SetPriority  = Priority_0;			//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
	PWMx_InitStructure.PWM4_SetPriority  = Priority_0;			//指定中断优先级(低到高) Priority_0,Priority_1,Priority_2,Priority_3
	
	PWMx_InitStructure.PWM_Period   = MAIN_Fosc /1000;     //2047;							//周期时间,   0~65535
	PWMx_InitStructure.PWM1_Duty    = PWMA_Duty.PWM1_Duty;	//PWM1占空比时间, 0~Period
	PWMx_InitStructure.PWM2_Duty    = PWMA_Duty.PWM2_Duty;	//PWM2占空比时间, 0~Period
	PWMx_InitStructure.PWM3_Duty    = PWMA_Duty.PWM3_Duty;	//PWM3占空比时间, 0~Period
	PWMx_InitStructure.PWM4_Duty    = PWMA_Duty.PWM4_Duty;	//PWM4占空比时间, 0~Period
	PWMx_InitStructure.PWM_DeadTime = 0;								//死区发生器设置, 0~255
	
	PWMx_InitStructure.PWM_EnoSelect   = ENO1P | ENO1N | ENO2P | ENO2N | ENO3P | ENO3N | ENO4P | ENO4N;	//输出通道选择,	ENO1P,ENO1N,ENO2P,ENO2N,ENO3P,ENO3N,ENO4P,ENO4N / ENO5P,ENO6P,ENO7P,ENO8P
	PWMx_InitStructure.PWM_PS_SW       = PWM1_SW_P60_P61| PWM2_SW_P62_P63 | PWM3_SW_P64_P65 | PWM4_SW_P66_P67;	
												//切换端口,		PWM1_SW_P10_P11,PWM1_SW_P20_P21,PWM1_SW_P60_P61
												//						PWM2_SW_P12_P13,PWM2_SW_P22_P23,PWM2_SW_P62_P63
												//						PWM3_SW_P14_P15,PWM3_SW_P24_P25,PWM3_SW_P64_P65
												//						PWM4_SW_P16_P17,PWM4_SW_P26_P27,PWM4_SW_P66_P67,PWM4_SW_P34_P33

	PWMx_InitStructure.PWM_CC1Enable   = ENABLE;				//开启PWM1P输入捕获/比较输出,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC1NEnable  = ENABLE;				//开启PWM1N输入捕获/比较输出,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC2Enable   = ENABLE;				//开启PWM2P输入捕获/比较输出,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC2NEnable  = ENABLE;				//开启PWM2N输入捕获/比较输出,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC3Enable   = ENABLE;				//开启PWM3P输入捕获/比较输出,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC3NEnable  = ENABLE;				//开启PWM3N输入捕获/比较输出,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC4Enable   = ENABLE;				//开启PWM4P输入捕获/比较输出,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC4NEnable  = ENABLE;				//开启PWM4N输入捕获/比较输出,  ENABLE,DISABLE
	
	PWMx_InitStructure.PWM_MainOutEnable= ENABLE;				//主输出使能, ENABLE,DISABLE
	PWMx_InitStructure.PWM_CEN_Enable   = ENABLE;				//使能计数器, ENABLE,DISABLE
	PWM_Configuration(PWMA, &PWMx_InitStructure);				//初始化PWM,  PWMA,PWMB
}


//========================================================================
//                                系统初始化
//========================================================================
void	SYS_Init(void)
{
	// 片内设备的初始化
	GPIO_config();
	Timer_config();

	EA = 1;	
	
	// 用户设备的初始化


}

