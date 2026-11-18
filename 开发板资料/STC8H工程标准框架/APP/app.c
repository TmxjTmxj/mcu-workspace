
#include	"Geek_Task.h"

//���õ�������Ӧ�ö�Ӧ��ͷ�ļ��ӵ�����

// ������ʱһ��Ӧ��ÿһ������ֱ��Ӧһ��*.c�ļ���һ��*.hͷ�ļ�
// c�ļ�����Ҫ����һ��������ص��豸�ĳ�ʼ������������Ĵ�����������������������
// ��ʼ������һ����System_init.c�еĳ�ʼ�����ֵ��ã�����������������һ����ʱ��������������������У��Ա��������ص���������
// �������ͷ�ļ�һ��Ӧ�ڱ��ļ���System_init.c�ļ������Ӱ���include


#include "Led1.h"
#include "WaterLight.h"
#include	"Encoder.h"

TASK_COMPONENTS Task_Comps[]=
{
// ״̬  ����  ����  ������
	{0, 200, 200, WaterLight},								/* task 1 Period: 200ms */
	{0, 200, 200, Led1},								/* task 2 Period: 200ms */
//	{0, 200, 200, SendEncoder},				/* task 2 Period�� 200ms */
//	{0, 20, 20, Sample_INTtoUART},		/* task 3 Period�� 20ms */

//	{0, 1, 1, Sample_PCA_Capture},		/* task 10 Period�� 1ms */
//	{0, 1, 1, Sample_PWM15bit},				/* task 11 Period�� 1ms */

	/* Add new task here */
};

u8 Tasks_Max = sizeof(Task_Comps)/sizeof(Task_Comps[0]);
