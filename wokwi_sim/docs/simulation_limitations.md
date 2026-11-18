# Simulation Limitations

| Feature | Status | Verified evidence / limit |
|---|---|---|
| 本地AVR CPU启动/UART/轮询Timer | BEHAVIORALLY_SIMULATED | AVR8js实际执行编译HEX；不是STC寄存器行为 |
| 8LED GPIO状态、K3按键、ADC | BEHAVIORALLY_SIMULATED | CPU端口变化/输入事件/ADC采样记录；LED电流和ADC模拟精度不建模 |
| OLED ACK/命令 | MOCKED | 本地只记录合成I2C器件ACK与[00,AE,A5,AF]，未模拟像素 |
| Wokwi Mega完整执行 | NOT_SIMULATED（待实跑） | 图纸lint通过；运行缺CLI token，提升权限运行另被审批拒绝 |
| 原生STC8051固件执行 | NOT_SIMULATED | Keil最小编译/HEX校验完成，不代表启动通过 |
| STC USB HID/ISP/debug | NOT_SIMULATED | MCU不受Wokwi支持，下载/USB端点协议未建模 |
| DS1302/RTC/晶振/备用电池 | NOT_SIMULATED | 未换成不兼容DS1307 |
| PWM/SPI/高级定时/DMA/中断/WDT | NOT_SIMULATED | 当前SPI没有确认从机，输出SKIP，不输出假PASS |
| TFT/LCD/数码管/RGB/蜂鸣器 | NOT_SIMULATED | 初轮范围外，实际器件/并行控制器需确认 |
| 单总线/红外/超声波/WiFi/蓝牙 | NOT_SIMULATED | 没有假定接口上存在传感器或模块 |
| 供电保护、电压瞬态、电源纹波/热/EMI/寄生 | NOT_SIMULATED | 无SPICE/电磁/热仿真 |

当前没有任何整板特性标为FULLY_SIMULATED。行为等效验证可发现移植应用、拓扑和自动流程错误，不能据此证明STC SFR、IRQ时序、USB、IAP或实物电气安全。

本地后端从diagram拓扑判断OLED电源/总线、ADC连接、按钮和LED端点，再由AVR指令执行产生结果。OLED为明确MOCK而非完整SSD1306。I2C时间与总线电压/上拉波形未仿真；按键无抖动。发现故障后可修复接线并重跑，但当前故障注入套件验证检测能力，没有声称通用Agent已自动修复所有故障。

真实阶段必须重新进行 Voltage / Current / Pin Tolerance / Common Ground / Power Source / Short Circuit 检查。原理图标注值不代替实测值，尤其J1模式和P1/P7复用。
