#ifndef _ECBM_ETP_H_//头文件防止重加载必备，先看看有没有定义过这个，定义说明已经加载过一次了。
#define _ECBM_ETP_H_//没定义说明是首次加载，那么往下执行。并且定义这个宏定义，防止下一次被加载。
/*-------------------------------------------------------------------------------------
The MIT License (MIT)

Copyright (c) 2021 奈特

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

免责说明：
    本软件库以MIT开源协议免费向大众提供。作者只保证原始版本是由作者在维护修BUG，
其他通过网络传播的版本也许被二次修改过，由此出现的BUG与作者无关。而当您使用原始
版本出现BUG时，请联系作者解决。
                            **************************
                            * 联系方式：进群778916610 *
                            **************************
------------------------------------------------------------------------------------*///这是开源协议，下面是图形界面选项。
//-----------------以下是图形设置界面，可在Configuration Wizard界面设置-----------------
//<<< Use Configuration Wizard in Context Menu >>>
//<o>最大任务数
//<1-254>
//<i>请根据实际需求设置，因为这个会占用RAM空间。最低必须有一个。
#define ETP_TASK_MAX   10
//<<< end of configuration section >>>
//-----------------以下是图形设置界面，可在Configuration Wizard界面设置-----------------
/*---------------------------------------宏定义-------------------------------------*/
#define etp_u1  bit             //1位无符号变量
#define etp_u8  unsigned char   //8位无符号变量
#define etp_u16 unsigned int    //16位无符号变量
#define etp_u32 unsigned long   //32位无符号变量

#define ETP_TASK_EN         0x80//任务使能标志位，置位代表该任务能被ETP框架执行。
#define ETP_TASK_RUN        0x40//任务运行标志位，置位代表该任务将在下一次轮询中执行。
#define ETP_TASK_WORK       0x20//任务工作标志位，任务正在运行时置位，运行结束时复位。
#define ETP_TASK_DELAY      0x08//任务延时标志位，当任务在下一次运行标志来临时还没执行完毕时置位。
#define ETP_TASK_MISS       0x04//任务错过标志位，当任务没有响应上一次运行标志时置位。
/*--------------------------------------变量定义-----------------------------------*/
extern  etp_u1  etp_run_en;                         //ETP运行使能。
extern  etp_u8  etp_task;                           //任务计数。
extern  etp_u8  etp_task_status[ETP_TASK_MAX];      //任务状态变量。
extern  etp_u16 etp_task_count [ETP_TASK_MAX];      //任务计时变量。
extern  etp_u16 etp_task_rerun [ETP_TASK_MAX];      //任务重载周期变量。
extern  void    (* etp_task_fun[ETP_TASK_MAX])(void);//任务函数。
extern  etp_u8  etp_main_i;                         //用在etp_main函数的i。
extern  etp_u8  etp_time_i;                         //用在etp_time_tick函数的i。
/*--------------------------------------函数定义-----------------------------------*/
/*-------------------------------------------------------
函数名：etp_install
描  述：时间片任务的安装函数，安装之后不会马上运行。
输  入：
    tim     该任务的执行周期，单位是“时间片个数”。
    fun     任务函数。
输  出：无
返回值：
    0~254   该任务的编号。
    255     任务槽已满，任务安装失败。
创建者：奈特
调用例程：无
创建日期：2021-08-11
修改记录：
2021-11-25：更换一种新的写法。
-------------------------------------------------------*/
extern etp_u8 etp_install(etp_u16 tim,void (* fun)(void));
/*-------------------------------------------------------
函数名：etp_main
描  述：时间片轮询的主函数，放入main函数的主循环里执行。
输  入：无
输  出：无
返回值：无
创建者：奈特
调用例程：无
创建日期：2021-08-11
修改记录：
2021-11-25：增加了使能位控制，提高了控制效率。
-------------------------------------------------------*/
extern void etp_main(void);
/*-------------------------------------------------------
函数名：etp_time_tick
描  述：任务时间函数，一般放入定时器中断中，因为该函数的执行周期就是时间片的长度。
输  入：无
输  出：无
返回值：无
创建者：奈特
调用例程：无
创建日期：2021-08-11
修改记录：
2021-11-25：改名为etp_time_tick。
-------------------------------------------------------*/
extern void etp_time_tick(void);
/*-------------------------------------------------------
函数名：etp_stop
描  述：任务停止函数，用于停止一个任务。
输  入：
    id      停止任务的编号。
输  出：无
返回值：无
创建者：奈特
调用例程：无
创建日期：2021-08-11
修改记录：
2021-11-25：放宽了判断机制。
-------------------------------------------------------*/
extern void etp_stop(etp_u8 id);
/*-------------------------------------------------------
函数名：etp_start
描  述：任务开启函数，用于开启一个任务，开启之后在下一次轮询中执行。
输  入：
    id      开启任务的编号。
输  出：无
返回值：无
创建者：奈特
调用例程：无
创建日期：2021-08-11
修改记录：
2021-11-25：放宽了判断机制。
-------------------------------------------------------*/
extern void etp_start(etp_u8 id);
/*-------------------------------------------------------
函数名：etp_get_status
描  述：任务状态获取函数，用于获取某个任务的状态，通过状态可知道任务是否正常运行。
输  入：
    id      任务的编号。
输  出：无
返回值：
    任务的状态。
创建者：奈特
调用例程：无
创建日期：2021-11-08
修改记录：
2021-11-25：放宽了判断机制。
-------------------------------------------------------*/
extern etp_u8 etp_get_status(etp_u8 id);
#endif  //和最上面的#ifndef配合成一个程序段。
        //以一个空行为结尾。