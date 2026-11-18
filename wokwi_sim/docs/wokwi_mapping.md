# Wokwi Mapping

核对日期：2026-09-27。官方支持列表：https://docs.wokwi.com/getting-started/supported-hardware 。
Mega引脚：https://docs.wokwi.com/parts/wokwi-arduino-mega 。
SSD1306模型：https://docs.wokwi.com/parts/board-ssd1306 。

| Real component | Wokwi equivalent | Support / strategy |
|---|---|---|
| STC8H8K64U | ATmega2560 | 非兼容CPU，只移植外设行为；原固件不能执行 |
| LED0-LED7 | wokwi-led + 1kohm resistor | 8路低有效，P6.0-7 ->Mega22-29 |
| K3 | wokwi-pushbutton | P3.3 ->Mega2，按下接地 |
| K0/K1/K2/RST | 未放入当前图 | 避免USB/UART/IR复用争用；RST不是Mega相同寄存器 |
| ADJ1 | wokwi-potentiometer | P1.0 ->A0；ADC精度由12位降为10位 |
| OLED插座 | board-ssd1306 0x3C | 合成测试外设；真实控制器/地址UNKNOWN |
| CH340N UART1 | serialMonitor | 串口日志替代；不模拟CH340芯片与下载协议 |
| DS1302 | None | 无原生模型；DS1307为I2C，不能直接替换三线协议 |
| 4位共阳LED | wokwi-7segment可评估 | 未启用；需保留位选PNP行为，不能假装TM1637 |
| RGB | wokwi-rgb-led可用 | 当前未启用，需独立P7复用配置 |
| 蜂鸣器 | wokwi-buzzer可等效 | 当前未启用；电磁/电流模型不等价 |
| DHT/DS18B20插座 | 原生器件模型可用 | 实际插入件UNKNOWN，当前不假定 |
| 超声波 | HC-SR04模型可用 | 实际型号UNKNOWN，当前不假定 |
| IR | Wokwi IR receiver可用 | 当前未启用，K2共享需处理 |
| TFT480x320并行 | 无已确认等效 | 不能用SPI ILI9341声称原协议通过 |
| LCD1602/12864接口 | LCD1602模型可评估 | 实际接入控制器UNKNOWN，当前未启用 |
| ESP8266/蓝牙 | None | 仅插座，未实现AT协议模型 |
| 电源/USB/DMA/高级PWM | None | 当前不仿真 |

硬件图30个器件/接口节点中，10个已确认外设行为进入当前测试（8LED、K3、ADJ1），另有OLED和UART桥两项测试替代。计数映射覆盖33.3%仅说明已建行为模型节点比例，不是整板或MCU真实性评分；原生8051执行覆盖为0。

diagram.json只由真实hardware_graph.json + simulator_adapter.json导出。适配器必须与编译HAL固定映射一致；不能编辑图后静默改变固件引脚。合成OLED地址写在适配层，不写成真实OLED事实。

Custom Chip评估：DS1302三线行为模型可作为下一模块；当前不是首轮Boot/LED/UART关键依赖。Wokwi Custom Chip的外设模型不能自动成为STC CPU指令/寄存器模型；首轮未实现8051自定义CPU。
