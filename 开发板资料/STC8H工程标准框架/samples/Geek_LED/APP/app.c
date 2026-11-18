
#include	"Geek_Task.h"

//将用到的任务应用对应的头文件加到这里
#include "Led1.h"
#include	"Encoder.h"

TASK_COMPONENTS Task_Comps[]=
{
//状态  计数  周期  函数
	{0, 200, 200, Led1},				/* task 1 Period： 250ms */
//	{0, 200, 200, SendEncoder},		/* task 2 Period： 200ms */
//	{0, 20, 20, Sample_INTtoUART},		/* task 3 Period： 20ms */

//	{0, 1, 1, Sample_PCA_Capture},		/* task 10 Period： 1ms */
//	{0, 1, 1, Sample_PWM15bit},				/* task 11 Period： 1ms */

	/* Add new task here */
};

u8 Tasks_Max = sizeof(Task_Comps)/sizeof(Task_Comps[0]);
