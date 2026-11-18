# STM32 自动开发流程设计

用户目标：选择有代表性且有电脑仿真模型的单片机，建立自动编译、接线、仿真、测试的流程。选择 STM32F103C8T6 / Blue Pill，直接编译 Cortex-M3 原生固件，不经过 AVR 替代。使用 PlatformIO + STM32Cube HAL，Wokwi 承担虚拟电路运行。

2026-09-27用户调整：暂停登录排查，优先交付仿真工作流。主验收后端改为本地 Renode，不依赖 Wokwi 账户。保留同一份 STM32 固件和 Wokwi 接线图；Renode 使用数字外设模型及自动脚本检查 LED GPIO/按键/串口。Renode 本身不提供 Wokwi 式面包板画面，不声称验证330Ω电阻的模拟电流或完整RCC晶振行为；发现缺失外设时明确记录模型补充与验收边界。

第一版范围：72MHz 时钟、SysTick、PC13 板载 LED、PA0 外接 LED（330Ω串联）、PB12 低有效按键（内部上拉、20ms去抖）、USART1 PA9/PA10 115200串口。按钮切换两档闪烁周期，串口输出启动和事件协议。自动场景按下/释放按钮，检查串口及外接 LED 引脚。

文件全部位于 stm32_bluepill/。src/源码、scripts/工具脚本、tests/测试、docs/说明、logs/运行证据、build/固件、tools/本地依赖；不修改开发板资料/或 wokwi_sim/，不全局安装软件、不保存凭据、不自动刷写实板。

验收分层：BUILD_READY 仅表示原生 ELF/BIN 编译及电路静态检查成功；SIMULATION_PASS 需要实际 Wokwi 执行并通过自动场景。缺少 CLI token 应报告 BLOCKED 并退出非零，不能把单元测试或预期串口文本当作芯片执行证据。VS Code 图形启动使用扩展许可证，与 CLI token 分开。

Wokwi 模型支持核心/GPIO/USART/定时器/EXTI等；ADC仅部分支持，DMA/RTC/IWDG等不支持，因此第一版不验收这些外设。后续可加入 I2C、SPI、ADC1。真实电源/模拟电路安全仍需要实板验证。

来源：https://docs.wokwi.com/parts/board-stm32-bluepill 、https://docs.platformio.org/en/latest/boards/ststm32/bluepill_f103c8.html 、https://docs.platformio.org/en/latest/frameworks/stm32cube.html 。核查日期2026-09-27。
