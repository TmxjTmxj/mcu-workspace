# 资料冲突与处理

## C01 USB引脚与接口
Source A：原理图U2/J1/USB1/USB2；开发板.pdf第4页背面丝印。
Source B：串口.md第3.2、7节声称两USB均接CH340、原生USB=P3.6/P3.7。
Current conclusion：USB1为USBDP/USBDN，经J1接P3.1/P3.0；USB2为UD+/UD-接CH340N。
Confidence：CONFIRMED（设计）；实物跳帽状态UNKNOWN。
Reason：原理图明确网名；P3.6实际接温湿度/单总线座，P3.7不是USB D-。

## C02 UART是否硬连
Source A：J1六针切换座与使用说明/背面短接说明。
Source B：串口.md称UART1无跳线、永久硬连。
Current conclusion：UART模式3-5及4-6；USB模式1-3及2-4（物理3-4为MCU端）。
Confidence：CONFIRMED；禁止同时桥接两种模式。
Reason：网名USBDP/P31/TXD和USBDN/P30/RXD对应切换路径。

## C03 电源
Source A：VCC经开关直接来自USB5V，U2 Vcc/ADC_VRef+接VCC；V1输出3V3给WiFi/P1。
Source B：串口.md称MCU在3.3V，CH340工作5V。
Current conclusion：本板设计MCU=5V VCC；CH340N=VBUS；3V3为独立输出。
Confidence：CONFIRMED（设计），实测电压UNKNOWN。
Reason：完整电源树与网名可追踪，不能按芯片兼容电压猜板上电压。

## C04 自动复位
Source A：CH340N RTS# pin4标NC；D1接TXD/RXD相关网，无到P5.4线。
Source B：串口.md称RTS#经D1接RST实现自动下载。
Current conclusion：未确认自动复位线路，不能生成RTS->RST连线；RST1接P5.4/GND，P5.4需ISP启用复位。
Confidence：CONFIRMED（图中NC/无连线）。
Reason：原理图优先；reset_mcu.ps1不能证明存在硬件复位连线。

## C05 时钟
Source A：ChipDevices/config.h MAIN_Fosc=24000000L。
Source B：STC8.uvproj CPU CLOCK(35000000)。
Current conclusion：bring-up按24MHz编译，实际ISP配置UNKNOWN；工程debug元数据35MHz不可用于定时验证。
Confidence：CONFIRMED（源码常量），实际时钟UNKNOWN。
Reason：芯片IRC由ISP设定；无实板频率读回。

## C06 README LED说明
Source A：APP/WaterLight.c使用P6；APP/Led1.c实际翻转P3.7。
Source B：readme.md称P6一个LED。
Current conclusion：板载8LED为P6.0-P6.7低有效；P3.7翻转不是板载8LED证据。
Confidence：CONFIRMED。
Reason：原理图LED0-7与源码实际访问。

## C07 串口2与空闲IO
Source A：UART.h与原理图引脚；P0被TFT上半数据线占用。
Source B：串口.md把UART2替代映射写成P3.6/P3.7且称P0无板载设备。
Current conclusion：UART2另一组P4.6/P4.7；UART1可映射P3.6/P3.7；P0连接TFT D8-D15，不能默认自由使用。
Confidence：CONFIRMED。
Reason：使用型号特定资料和实际板级连接。

## C08 原理图建模校正
Source A：TFT分块与DS1302分块目视核查。
Source B：首版人工录入时TFT高8位按正序、RTC主供电写VCC1。
Current conclusion：D8=P0.7至D15=P0.0；RTC主供电=VCC2，备用B1=VCC1。
Confidence：CONFIRMED；已修正hardware_graph.json。
Reason：先保留复核记录，再修正模型；未让首版录入错误成为事实。
