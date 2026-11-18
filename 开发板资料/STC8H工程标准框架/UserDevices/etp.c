#include "etp.h" //加载头文件。
/*--------------------------------------变量定义-----------------------------------*/
etp_u1 etp_run_en = 0;                    // ETP运行使能。
etp_u8 etp_task = 0;                      //任务计数。
etp_u8 etp_task_status[ETP_TASK_MAX];     //任务状态变量。
etp_u16 etp_task_count[ETP_TASK_MAX];     //任务计时变量。
etp_u16 etp_task_rerun[ETP_TASK_MAX];     //任务重新运行周期变量。
void (*etp_task_fun[ETP_TASK_MAX])(void); //任务函数。
etp_u8 etp_main_i;                        //用在etp_main函数的i。
etp_u8 etp_time_i;                        //用在etp_time_tick函数的i。
/*--------------------------------------函数定义-----------------------------------*/
/*-------------------------------------------------------
时间片任务的安装函数。
-------------------------------------------------------*/
etp_u8 etp_install(etp_u16 tim, void (*fun)(void))
{
    if (etp_task >= ETP_TASK_MAX)
    {               //假如任务槽已满，
        return 255; //返回255。
    }
    etp_task_status[etp_task] = 0;  //状态全清零。
    etp_task_count[etp_task] = 0;   //清零时间片计数。
    etp_task_rerun[etp_task] = tim; //装上任务重载值。
    etp_task_fun[etp_task] = fun;   //安装函数。
    etp_task++;                     //任务计数加1。
    return (etp_task - 1);          //返回值必须在最后一句，所以在etp_task++之后要减一才是任务的编号。
}
/*-------------------------------------------------------
时间片轮询的主函数。
-------------------------------------------------------*/
void etp_main(void)
{
    if (etp_run_en)
    {                   //仅当有任务运行的时候才运行，这样可以避免长时间占用任务变量。
        etp_run_en = 0; //清除使能标志位。
        for (etp_main_i = 0; etp_main_i < etp_task; etp_main_i++)
        { //从0到任务总数，每一个任务都轮询一遍。
            if (etp_task_status[etp_main_i] & ETP_TASK_EN)
            { //先判断任务是不是已经使能。
                if (etp_task_status[etp_main_i] & ETP_TASK_RUN)
                {                                                    //再判断任务是不是可以执行。
                    etp_task_status[etp_main_i] &= (~ETP_TASK_RUN);  //开始执行任务了，清除运行标志位。
                    etp_task_status[etp_main_i] |= (ETP_TASK_WORK);  //打上任务正在工作的标志位。
                    etp_task_fun[etp_main_i]();                      //运行任务。
                    etp_task_status[etp_main_i] &= (~ETP_TASK_WORK); //任务运行完毕，清除工作标志位。
                }
            }
        }
    }
}
/*-------------------------------------------------------
任务时间函数。
-------------------------------------------------------*/
void etp_time_tick(void)
{
    for (etp_time_i = 0; etp_time_i < etp_task; etp_time_i++)
    { //从0开始轮询到最后一个任务。
        if (etp_task_status[etp_time_i] & ETP_TASK_EN)
        {                                 //如果任务都没有使能，就直接跳过吧。
            etp_task_count[etp_time_i]++; //时间片+1。
            if (etp_task_count[etp_time_i] >= etp_task_rerun[etp_time_i])
            {                                   //假如任务到了重新运行的时机了，
                etp_task_count[etp_time_i] = 0; //先清零计数变量。
                if (etp_task_status[etp_time_i] & ETP_TASK_WORK)
                {                                                  //如果当前任务还在工作，
                    etp_task_status[etp_time_i] |= ETP_TASK_DELAY; //就置位延时标志位，表示该任务延迟。
                }
                if (etp_task_status[etp_time_i] & ETP_TASK_RUN)
                {                                                 //如果当前任务的运行标志位还在，
                    etp_task_status[etp_time_i] |= ETP_TASK_MISS; //就置位错过标志位，表示该任务错过执行机会了。
                }
                etp_task_status[etp_time_i] |= ETP_TASK_RUN; //最终还是要让任务运行起来。
                etp_run_en = 1;                              //标记有任务要运行。
            }
        }
    }
}
/*-------------------------------------------------------
任务停止函数。
-------------------------------------------------------*/
void etp_stop(etp_u8 id)
{
    if (id < etp_task)
    {                            // id必须在范围内，
        etp_task_status[id] = 0; //停止任务，清零所有标志位。
    }
}
/*-------------------------------------------------------
任务开启函数。
-------------------------------------------------------*/
void etp_start(etp_u8 id)
{
    if (id < etp_task)
    {                                      // id必须在范围内，
        etp_task_status[id] = ETP_TASK_EN; //开启任务，设置标志位，并在下一次轮询中运行。
    }
}
/*-------------------------------------------------------
任务状态获取函数。
-------------------------------------------------------*/
etp_u8 etp_get_status(etp_u8 id)
{
    if (id < etp_task)
    {                               // id必须在范围内，
        return etp_task_status[id]; //返回该id对应任务的状态。
    }
    return 0; //不在范围里就返回0。
}
