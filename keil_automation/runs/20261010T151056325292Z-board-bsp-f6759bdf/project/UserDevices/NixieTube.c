/*************************************************************************************************************************************************************

Copyright (c) 2021 Chensj

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

免责说明：
    本软件库以开源协议免费向大众提供。作者只保证原始版本是由作者在维护，其他通过网络传播的版本也许被二次修改过，由此出现的BUG与作者无关。而当您使用原始
版本出现BUG时，请联系作者解决。
                            **********************************
                            *    联系方式：进QQ群195874899   *
                            ********************************** 
*************************************************************************************************************************************************************/

#include "main.h"

//段码
//0,1,2,3,4,5,6,7,8,9,A,B,C,D,E,F,-,NONE,H
code unsigned char _smg_seg[19]={0xC0,0xF9,0xA4,0xB0,0x99,0x92,0x82,0xF8,0x80,0x90,0x88,0x83,0xC6,0xA1,0x86,0x8E,0xBF,0xFF,0x89};
//共阳显示缓存
code unsigned char _smg_seg1[19]={0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x7,0x7F,0x6F,0x77,0x7C,0x39,0x5E,0x79,0x71,0x40,0x00,0x76};

	//共阴显示缓存, 默认各笔画不显示
xdata unsigned char NiXieTube_Buff[4]={0,0,0,0};
//小数点显示缓存



void NixieTube_init(void)
{
	
	P2M1 &= ~0xFF;	//对应位设为0
	P2M0 |= 0xFF; 	//对应位设为1, 将对应为设置为推挽输出模式，其他位模式不变	

	P7M1 &= ~0xFF;	//对应位设为0
	P7M0 |= 0xFF; 	//对应位设为1, 将对应为设置为推挽输出模式，其他位模式不变		
	
}

//========================================================================
// 描述: 数码管显示清除.
// 参数: 无.
// 返回: none.
//========================================================================
void NixieTube_Clear()
{
	NiXieTube_Buff[3] = 0;	
	NiXieTube_Buff[2] = 0;
	NiXieTube_Buff[1] = 0;				
	NiXieTube_Buff[0] = 0;
}

//========================================================================
// 描述: 数码管显示，把显示缓存的数据显示到数码管, 1ms定时器调用
// 参数: 无
// 返回: none.
//========================================================================
void NixieTube_Disp(void)
{
	static unsigned char index;
	
	SEG = ~ NiXieTube_Buff[index];
	DIG =(DIG & 0xF0 ) | ( 0x80 >>( index + 3));   //低四位不变，高四位对应位设为1
	index++;
    if(index > 4)    
    {
        index = 0;  
    }	
}



//========================================================================
// 描述: 数码管特定位显示一个数字，不影响其他位.
// 参数: 
//		pos：要显示数字的位，0-7；
//		num：要显示的数字（0-9）；
//		point：(0或者非0),0：小数点不显示；其他：小数点显示
// 返回: none.
//========================================================================
void NixieTube_OneDig(unsigned char pos, unsigned char num,unsigned char point)
{
	if(point)
		{
			NiXieTube_Buff[pos]=_smg_seg1[num] | 0x80;
		}
	else
		{
			NiXieTube_Buff[pos]=_smg_seg1[num];
		}  
}

//========================================================================
// 描述: 数码管显示整数.
// 参数: (-65536~65535).
// 返回: none.
//========================================================================
void NixieTube_Int(int num)
{
    int temp;
    unsigned char i;
	NixieTube_Clear();
	
    if(num>=0)
    {
        for(i=0;i<5;i++)
        {
            temp=num%10;
            num=num/10;
            NiXieTube_Buff[i]=_smg_seg1[temp];
            if(num == 0)
            {
                break;
            }
        }
    }
    else//负数
    {
        num = -num;
        for(i=0;i<5;i++)
        {
            temp=num%10;
            num=num/10;
            NiXieTube_Buff[i]=_smg_seg1[temp];
            if(num == 0)
            {
                NiXieTube_Buff[i+1]=_smg_seg1[16];  //添加负号
                break;
            }
        }
    }
}

//========================================================================
// 描述: 数码管显示浮点数.
// 参数: 浮点数,精度(1,2,3,4).
// 返回: none.
//========================================================================
void NixieTube_Float(float num, unsigned char jingdu)
{
    unsigned char i, point ;
    int temp;
    int int_part,float_part;
    int_part = (int)num/1;

	NixieTube_Clear();
	switch(jingdu)
	{
		case 1:
			float_part = (int)(num*10)%10;
			break;//保留1位精度
		case 2:
			float_part = (int)(num*100)%100;
			break;//保留2位精度
		case 3:
			float_part = (int)(num*1000)%1000;
			break;//保留3位精度
		case 4:
			float_part = (int)(num*10000)%10000;
			break;//保留4位精度
		default:
			float_part = (int)(num*10)%10;
			break;//保留1位精度
	}

    if(float_part<0)
    {
        float_part = -float_part;
    }
    for(i=0;i<4;i++)
    {
        temp=float_part%10;
        float_part=float_part/10;
        NiXieTube_Buff[i]=_smg_seg1[temp];
        if(float_part == 0)
        {
            break;
        }
    }
	point = i+1;

    if(int_part>=0)
    {
        for(i=i+1;i<4;i++)
        {
            temp=int_part%10;
            int_part=int_part/10;
            NiXieTube_Buff[i]=_smg_seg1[temp];
            if(int_part == 0)
            {
                break;
            }
        }
    }
    else
    {
        int_part = -int_part;
        for(i=i+1;i<4;i++)
        {
            temp=int_part%10;
            int_part=int_part/10;
            NiXieTube_Buff[i]=temp;
            if(int_part == 0)
            {
                NiXieTube_Buff[i+1]=_smg_seg1[16];//添加负号
                break;
            }
        }
    }
    
	//添加小数点
	NiXieTube_Buff[point] = NiXieTube_Buff[point] | 0x80;
}

