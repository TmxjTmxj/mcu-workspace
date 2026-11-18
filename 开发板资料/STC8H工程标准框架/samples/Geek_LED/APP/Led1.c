
//这是其中一个任务的例子，任务：每隔一定时间需要执行的函数，如数据采集、数据更新、数据就算后输出控制信号等等
//任务必须是能正常返回的函数，不可是阻塞的，任务的一次执行时间一般应小于所有任务的最小间隔，否则会出现个别任务执行的延后


#include "Led1.h"
#include	"GPIO.h"

void Led1Init(void)
{
	GPIO_InitTypeDef	GPIO_InitStructure;		//结构定义
	
	GPIO_InitStructure.Pin  = GPIO_Pin_7;		//指定要初始化的IO,
	GPIO_InitStructure.Mode = GPIO_PullUp;		//指定IO的输入或输出方式,GPIO_PullUp,GPIO_HighZ,GPIO_OUT_OD,GPIO_OUT_PP
	GPIO_Inilize(GPIO_P3,&GPIO_InitStructure);	//初始化

//	GPIO_InitStructure.Pin  = GPIO_Pin_All;		//指定要初始化的IO, GPIO_Pin_0 ~ GPIO_Pin_7
//	GPIO_InitStructure.Mode = GPIO_PullUp;		//指定IO的输入或输出方式,GPIO_PullUp,GPIO_HighZ,GPIO_OUT_OD,GPIO_OUT_PP
//	GPIO_Inilize(GPIO_P6,&GPIO_InitStructure);	//初始化

}
void Led1(void)
{
	P37 = !P37;
}