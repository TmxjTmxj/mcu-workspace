/*---------------------------------------------------------------------*/
/* --- STC MCU Limited ------------------------------------------------*/
/* --- STC 1T Series MCU Demo Programme -------------------------------*/
/* --- Mobile: (86)13922805190 ----------------------------------------*/
/* --- Fax: 86-0513-55012956,55012947,55012969 ------------------------*/
/* --- Tel: 86-0513-55012928,55012929,55012966 ------------------------*/
/* --- Web: www.STCMCU.com --------------------------------------------*/
/* --- Web: www.STCMCUDATA.com  ---------------------------------------*/
/* --- QQ:  800003751 -------------------------------------------------*/
/* ���Ҫ�ڳ�����ʹ�ô˴���,���ڳ�����ע��ʹ����STC�����ϼ�����            */
/*---------------------------------------------------------------------*/


#include	"config.h"
#include	"System_init.h"

#include	"gpio.h"
#include	"exti.h"
#include	"timer.h"
#include	"uart.h"
#include	"pwm.h"

//��App������Ҫʹ�ó�ʼ������������������������app�����ͷ�ļ�
#include "Led1.h"
#include "WaterLight.h"




/*************	���س�������	**************/


/*************	���ر�������	**************/

PWMx_Duty PWMA_Duty;

/*************	���غ�������	**************/



/*************  �ⲿ�����ͱ������� *****************/


//========================================================================
//                                IO������
//========================================================================
void	GPIO_config(void)
{
	GPIO_InitTypeDef	GPIO_InitStructure;		//�ṹ����
	
	GPIO_InitStructure.Pin  = GPIO_Pin_All;		//ָ��Ҫ��ʼ����IO,
	GPIO_InitStructure.Mode = GPIO_PullUp;		//ָ��IO������������ʽ,GPIO_PullUp,GPIO_HighZ,GPIO_OUT_OD,GPIO_OUT_PP
	GPIO_Inilize(GPIO_P6,&GPIO_InitStructure);	//��ʼ��

	GPIO_InitStructure.Pin  = GPIO_Pin_2;		//ָ��Ҫ��ʼ����IO,
	GPIO_InitStructure.Mode = GPIO_PullUp;		//ָ��IO������������ʽ,GPIO_PullUp,GPIO_HighZ,GPIO_OUT_OD,GPIO_OUT_PP
	GPIO_Inilize(GPIO_P3,&GPIO_InitStructure);	//��ʼ��	

}

//========================================================================
//                               ��ʱ������
//========================================================================
void	Timer_config(void)
{
	TIM_InitTypeDef		TIM_InitStructure;						//�ṹ����
	TIM_InitStructure.TIM_Mode      = TIM_16BitAutoReload;	//ָ������ģʽ,   TIM_16BitAutoReload,TIM_16Bit,TIM_8BitAutoReload,TIM_16BitAutoReloadNoMask
	TIM_InitStructure.TIM_Priority    = Priority_0;			//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
	TIM_InitStructure.TIM_Interrupt = ENABLE;					//�ж��Ƿ�����,   ENABLE��DISABLE
	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_1T;		//ָ��ʱ��Դ,     TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
	TIM_InitStructure.TIM_ClkOut    = DISABLE;				//�Ƿ������������, ENABLE��DISABLE
	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / 1000UL);		//��ֵ,
	TIM_InitStructure.TIM_Run       = ENABLE;					//�Ƿ��ʼ����������ʱ��, ENABLE��DISABLE
	Timer_Inilize(Timer0,&TIM_InitStructure);					//��ʼ��Timer0	  Timer0,Timer1,Timer2,Timer3,Timer4
	
//	TIM_InitStructure.TIM_Mode      = TIM_16BitAutoReload;	//ָ������ģʽ,   TIM_16BitAutoReload,TIM_16Bit,TIM_8BitAutoReload,TIM_16BitAutoReloadNoMask
//	TIM_InitStructure.TIM_Priority    = Priority_0;			//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
//	TIM_InitStructure.TIM_Interrupt = ENABLE;					//�ж��Ƿ�����,   ENABLE��DISABLE
//	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_1T;		//ָ��ʱ��Դ, TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
//	TIM_InitStructure.TIM_ClkOut    = DISABLE;				//�Ƿ������������, ENABLE��DISABLE
//	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / 10000);			//��ֵ,
//	TIM_InitStructure.TIM_Run       = ENABLE;					//�Ƿ��ʼ����������ʱ��, ENABLE��DISABLE
//	Timer_Inilize(Timer1,&TIM_InitStructure);					//��ʼ��Timer1	  Timer0,Timer1,Timer2,Timer3,Timer4

//	TIM_InitStructure.TIM_Interrupt = ENABLE;					//�ж��Ƿ�����,   ENABLE��DISABLE. (ע��: Timer2�̶�Ϊ16λ�Զ���װ, �жϹ̶�Ϊ�����ȼ�)
//	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_1T;		//ָ��ʱ��Դ,     TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
//	TIM_InitStructure.TIM_ClkOut    = DISABLE;				//�Ƿ������������, ENABLE��DISABLE
//	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / 1000);				//��ֵ
//	TIM_InitStructure.TIM_Run       = ENABLE;					//�Ƿ��ʼ����������ʱ��, ENABLE��DISABLE
//	Timer_Inilize(Timer2,&TIM_InitStructure);					//��ʼ��Timer2	  Timer0,Timer1,Timer2,Timer3,Timer4

//	TIM_InitStructure.TIM_Interrupt = DISABLE;					//�ж��Ƿ�����,   ENABLE��DISABLE. (ע��: Timer2�̶�Ϊ16λ�Զ���װ, �жϹ̶�Ϊ�����ȼ�)
//	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_12T;	//ָ��ʱ��Դ,     TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
//	TIM_InitStructure.TIM_ClkOut    = ENABLE;					//�Ƿ������������, ENABLE��DISABLE
//	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / (100*12));		//��ֵ
//	TIM_InitStructure.TIM_Run       = ENABLE;					//�Ƿ��ʼ����������ʱ��, ENABLE��DISABLE
//	Timer_Inilize(Timer3,&TIM_InitStructure);					//��ʼ��Timer3	  Timer0,Timer1,Timer2,Timer3,Timer4

//	TIM_InitStructure.TIM_Interrupt = ENABLE;					//�ж��Ƿ�����,   ENABLE��DISABLE. (ע��: Timer2�̶�Ϊ16λ�Զ���װ, �жϹ̶�Ϊ�����ȼ�)
//	TIM_InitStructure.TIM_ClkSource = TIM_CLOCK_12T;	//ָ��ʱ��Դ,     TIM_CLOCK_1T,TIM_CLOCK_12T,TIM_CLOCK_Ext
//	TIM_InitStructure.TIM_ClkOut    = ENABLE;					//�Ƿ������������, ENABLE��DISABLE
//	TIM_InitStructure.TIM_Value     = 65536UL - (MAIN_Fosc / (50*12));		//��ֵ
//	TIM_InitStructure.TIM_Run       = ENABLE;					//�Ƿ��ʼ����������ʱ��, ENABLE��DISABLE
//	Timer_Inilize(Timer4,&TIM_InitStructure);					//��ʼ��Timer4	  Timer0,Timer1,Timer2,Timer3,Timer4
}


//========================================================================
//                              ���ڳ�ʼ��
//========================================================================
void	UART_config(void)
{
	COMx_InitDefine		COMx_InitStructure;					//�ṹ����
	COMx_InitStructure.UART_Mode      = UART_8bit_BRTx;		//ģʽ,       UART_ShiftRight,UART_8bit_BRTx,UART_9bit,UART_9bit_BRTx
	COMx_InitStructure.UART_BRT_Use   = BRT_Timer1;			//ѡ�����ʷ�����,   BRT_Timer1, BRT_Timer2 (ע��: ����2�̶�ʹ��BRT_Timer2)
	COMx_InitStructure.UART_BaudRate  = 115200ul;			//������, һ�� 110 ~ 115200
	COMx_InitStructure.UART_RxEnable  = ENABLE;				//��������,   ENABLE��DISABLE
	COMx_InitStructure.BaudRateDouble = DISABLE;			//�����ʼӱ�, ENABLE��DISABLE
	COMx_InitStructure.UART_Interrupt = ENABLE;				//�ж�����,   ENABLE��DISABLE
	COMx_InitStructure.UART_Priority    = Priority_0;			//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
	COMx_InitStructure.UART_P_SW      = UART1_SW_P30_P31;	//�л��˿�,   UART1_SW_P30_P31,UART1_SW_P36_P37,UART1_SW_P16_P17,UART1_SW_P43_P44
	UART_Configuration(UART1, &COMx_InitStructure);		//��ʼ������1 UART1,UART2,UART3,UART4

//	COMx_InitStructure.UART_Mode      = UART_8bit_BRTx;		//ģʽ,       UART_ShiftRight,UART_8bit_BRTx,UART_9bit,UART_9bit_BRTx
////	COMx_InitStructure.UART_BRT_Use   = BRT_Timer2;			//ѡ�����ʷ�����, BRT_Timer2 (ע��: ����2�̶�ʹ��BRT_Timer2, ���Բ���ѡ��)
//	COMx_InitStructure.UART_BaudRate  = 57600ul;			//������,     110 ~ 115200
//	COMx_InitStructure.UART_RxEnable  = ENABLE;				//��������,   ENABLE��DISABLE
//	COMx_InitStructure.UART_Interrupt = ENABLE;				//�ж�����,   ENABLE��DISABLE
//	COMx_InitStructure.UART_Priority    = Priority_0;			//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
//	COMx_InitStructure.UART_P_SW      = UART2_SW_P46_P47;	//�л��˿�,   UART2_SW_P10_P11,UART2_SW_P46_P47
//	UART_Configuration(UART2, &COMx_InitStructure);		//��ʼ������2 UART1,UART2,UART3,UART4

//	PrintString1("STC8 UART1 Test Programme!\r\n");	//UART1����һ���ַ���
//	PrintString2("STC8 UART2 Test Programme!\r\n");	//UART2����һ���ַ���
}

//========================================================================
//                             �ⲿ�жϳ�ʼ��
//========================================================================
void	Exti_config(void)
{
	EXTI_InitTypeDef	Exti_InitStructure;							//�ṹ����

	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//�ж�ʹ��,   ENABLE��DISABLE
	Exti_InitStructure.EXTI_Mode      = EXT_MODE_Fall;//�ж�ģʽ,   EXT_MODE_RiseFall,EXT_MODE_Fall
	Exti_InitStructure.EXTI_Priority  = Priority_0;		//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
	Ext_Inilize(EXT_INT0,&Exti_InitStructure);				//��ʼ��

//	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//�ж�ʹ��,   ENABLE��DISABLE
//	Exti_InitStructure.EXTI_Mode      = EXT_MODE_Fall;//�ж�ģʽ,   EXT_MODE_RiseFall,EXT_MODE_Fall
//	Exti_InitStructure.EXTI_Priority  = Priority_0;		//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
//	Ext_Inilize(EXT_INT1,&Exti_InitStructure);				//��ʼ��

//	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//�ж�ʹ��,   ENABLE��DISABLE
//	Ext_Inilize(EXT_INT2,&Exti_InitStructure);				//��ʼ��

//	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//�ж�ʹ��,   ENABLE��DISABLE
//	Ext_Inilize(EXT_INT3,&Exti_InitStructure);				//��ʼ��

//	Exti_InitStructure.EXTI_Interrupt = ENABLE;				//�ж�ʹ��,   ENABLE��DISABLE
//	Ext_Inilize(EXT_INT4,&Exti_InitStructure);				//��ʼ��
}

/***************  PWM��ʼ������ *****************/
void	PWM_config(void)
{
	PWMx_InitDefine		PWMx_InitStructure;
	
	PWMx_InitStructure.PWM1_Mode    =	CCMRn_PWM_MODE1;	//ģʽ,		CCMRn_FREEZE,CCMRn_MATCH_VALID,CCMRn_MATCH_INVALID,CCMRn_ROLLOVER,CCMRn_FORCE_INVALID,CCMRn_FORCE_VALID,CCMRn_PWM_MODE1,CCMRn_PWM_MODE2
	PWMx_InitStructure.PWM2_Mode    =	CCMRn_PWM_MODE1;	//ģʽ,		CCMRn_FREEZE,CCMRn_MATCH_VALID,CCMRn_MATCH_INVALID,CCMRn_ROLLOVER,CCMRn_FORCE_INVALID,CCMRn_FORCE_VALID,CCMRn_PWM_MODE1,CCMRn_PWM_MODE2
	PWMx_InitStructure.PWM3_Mode    =	CCMRn_PWM_MODE1;	//ģʽ,		CCMRn_FREEZE,CCMRn_MATCH_VALID,CCMRn_MATCH_INVALID,CCMRn_ROLLOVER,CCMRn_FORCE_INVALID,CCMRn_FORCE_VALID,CCMRn_PWM_MODE1,CCMRn_PWM_MODE2
	PWMx_InitStructure.PWM4_Mode    =	CCMRn_PWM_MODE1;	//ģʽ,		CCMRn_FREEZE,CCMRn_MATCH_VALID,CCMRn_MATCH_INVALID,CCMRn_ROLLOVER,CCMRn_FORCE_INVALID,CCMRn_FORCE_VALID,CCMRn_PWM_MODE1,CCMRn_PWM_MODE2

	PWMx_InitStructure.PWM1_SetPriority  = Priority_0;			//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
	PWMx_InitStructure.PWM2_SetPriority  = Priority_0;			//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
	PWMx_InitStructure.PWM3_SetPriority  = Priority_0;			//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
	PWMx_InitStructure.PWM4_SetPriority  = Priority_0;			//ָ���ж����ȼ�(�͵���) Priority_0,Priority_1,Priority_2,Priority_3
	
	PWMx_InitStructure.PWM_Period   = MAIN_Fosc /1000;     //2047;							//����ʱ��,   0~65535
	PWMx_InitStructure.PWM1_Duty    = PWMA_Duty.PWM1_Duty;	//PWM1ռ�ձ�ʱ��, 0~Period
	PWMx_InitStructure.PWM2_Duty    = PWMA_Duty.PWM2_Duty;	//PWM2ռ�ձ�ʱ��, 0~Period
	PWMx_InitStructure.PWM3_Duty    = PWMA_Duty.PWM3_Duty;	//PWM3ռ�ձ�ʱ��, 0~Period
	PWMx_InitStructure.PWM4_Duty    = PWMA_Duty.PWM4_Duty;	//PWM4ռ�ձ�ʱ��, 0~Period
	PWMx_InitStructure.PWM_DeadTime = 0;								//��������������, 0~255
	
	PWMx_InitStructure.PWM_EnoSelect   = ENO1P | ENO1N | ENO2P | ENO2N | ENO3P | ENO3N | ENO4P | ENO4N;	//���ͨ��ѡ��,	ENO1P,ENO1N,ENO2P,ENO2N,ENO3P,ENO3N,ENO4P,ENO4N / ENO5P,ENO6P,ENO7P,ENO8P
	PWMx_InitStructure.PWM_PS_SW       = PWM1_SW_P60_P61| PWM2_SW_P62_P63 | PWM3_SW_P64_P65 | PWM4_SW_P66_P67;	
												//�л��˿�,		PWM1_SW_P10_P11,PWM1_SW_P20_P21,PWM1_SW_P60_P61
												//						PWM2_SW_P12_P13,PWM2_SW_P22_P23,PWM2_SW_P62_P63
												//						PWM3_SW_P14_P15,PWM3_SW_P24_P25,PWM3_SW_P64_P65
												//						PWM4_SW_P16_P17,PWM4_SW_P26_P27,PWM4_SW_P66_P67,PWM4_SW_P34_P33

	PWMx_InitStructure.PWM_CC1Enable   = ENABLE;				//����PWM1P���벶��/�Ƚ����,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC1NEnable  = ENABLE;				//����PWM1N���벶��/�Ƚ����,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC2Enable   = ENABLE;				//����PWM2P���벶��/�Ƚ����,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC2NEnable  = ENABLE;				//����PWM2N���벶��/�Ƚ����,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC3Enable   = ENABLE;				//����PWM3P���벶��/�Ƚ����,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC3NEnable  = ENABLE;				//����PWM3N���벶��/�Ƚ����,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC4Enable   = ENABLE;				//����PWM4P���벶��/�Ƚ����,  ENABLE,DISABLE
	PWMx_InitStructure.PWM_CC4NEnable  = ENABLE;				//����PWM4N���벶��/�Ƚ����,  ENABLE,DISABLE
	
	PWMx_InitStructure.PWM_MainOutEnable= ENABLE;				//�����ʹ��, ENABLE,DISABLE
	PWMx_InitStructure.PWM_CEN_Enable   = ENABLE;				//ʹ�ܼ�����, ENABLE,DISABLE
	PWM_Configuration(PWMA, &PWMx_InitStructure);				//��ʼ��PWM,  PWMA,PWMB
}


//========================================================================
//                                ϵͳ��ʼ��
//========================================================================
void	SYS_Init(void)
{
	// Ƭ���豸�ĳ�ʼ��
	
	Timer_config();    // �������������ʱ��T0����һ��1ms�Ļ�׼��ʱ������������������������1ms�Ķ�ʱ���δ���

	EA = 1;	
	
	// �û��豸�ĳ�ʼ��
	Led1Init();
	WaterLightInit();


}

