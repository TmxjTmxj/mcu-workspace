# 板卡识别与资料解析

Board：原理图标题 `STC8H_32G_LQFP64`，外观图标识 Geek/STC8H/STC32。
Designer：S.J. Chen（原理图署名）；Manufacturer：UNKNOWN，山东大学丝印不能证明制造商。
Revision：UNKNOWN；原理图创建 2022-11-20、更新 2023-06-01。
MCU：原理图 U2=`STC8H8K64U-LQFP64`，明确允许 STC32G12K128-LQFP64 替代装配；实物芯片丝印/硅版本 UNKNOWN。

## 完整盘点

496 个文件，313 个不同 SHA256 内容。完整路径、大小、类型、A-E 类别、解析状态和编码在 inventory.json；重复的 SDK/样例不是独立硬件证据。

3 个 PDF 共 2109 页，全部可用文本已提取：stc8h.pdf 2103 页、开发板.pdf 5 页、开发板原理图.pdf 1 页。开发板.pdf 前四页为图片，已目视检查；芯片手册按 STC8H8K64U 型号相关章节深入核对，未声称逐页人工审阅 2103 页。

全部 26 PNG 已读取验证并目视比对，其中 19 张是原理图分块；另有正反面、模块、使用和 README 配图。机械 STL/STEP（3 文件）仅确认类型/保留，未进行机械 CAD 重建。Keil 对象/调试二进制和用户状态文件（96 文件）记为 UNPARSED，未删除或跳过清单。其余 356 个文本、7 个 XML 工程、4 个 HEX 与 ZIP 已解析，精确状态以 inventory_summary.json 为准。乱码扩展名与 GB18030 编码已保留。

可信度：原理图与型号专属手册 > BSP/工程 > README/串口.md > 外观推测。外观图片和串口.md 无法推翻明确网名；冲突见 conflicts.md。

## MCU 资源

手册印刷页 172-176（PDF 页 204-208）确认：8051 1T，Flash 64KiB，DATA+IDATA 256B，XDATA 8192B，USB RAM 1280B；最大 60 GPIO，无 P1.2；5 个 16 位定时器；4 UART；SPI 主/从；I2C 主/从；8 路/2组高级 PWM；12位 ADC 15个外部通道，通道15读内部参考；PWM 可用于滤波后的 DAC 功能，不等价于独立模拟 DAC。

全速 USB、RTC、WDT、MDU16；经典 22 中断源与4级优先级。DMA、LCM 与全 GPIO 中断有硅版本限制，实际版本 UNKNOWN。没有板载 CAN、Ethernet、SDIO 控制器或外部 Flash/PSRAM 的证据。

运行电压范围为 1.9-5.5V；本板设计 VCC=5V。IRC 可配置45MHz及以下，实际 ISP 时钟 UNKNOWN；代码 MAIN_Fosc=24MHz，Keil XML CLOCK=35MHz 属冲突，不能由代码常量证明实际频率。外接 X1=32.768kHz 服务 DS1302，不能当作 MCU 主晶振。

## 兼容性

| 环境 | 结论 |
|---|---|
| Keil C51 | 原工程原生支持；当前安装为2KB评估版 |
| Arduino | 未提供原生 STC Arduino core；AVR 等效工程是移植版 |
| PlatformIO | 未提供本板原生配置；不视为已支持 |
| STM32Cube / ESP-IDF | MCU架构不符，不能用于原生构建 |
| Wokwi | 官方支持ARM/AVR/RISC-V/Xtensa，未列8051/STC；本板仅外设等效 |
| Debug | STC ISP/片上仿真资料；没有已确认的SWD/JTAG接口 |

Wokwi能力来源（2026-09-27核对）：https://docs.wokwi.com/getting-started/supported-hardware 。芯片数据依据本地手册，不从同系列其他型号猜测。
