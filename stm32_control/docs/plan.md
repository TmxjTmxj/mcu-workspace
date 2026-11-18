# 智能风扇 Implementation Plan

> 当前会话使用executing-plans原生实施；目录不是Git仓库，不建worktree或提交。使用TDD和verification-before-completion验收。

**Goal:** 完成交互协议、传感器、电机PWM、自动控制与无线桥的可学习工程。
**Architecture:** STM32 HAL控制核与硬件层分离；Renode原生CPU+外设模型+热对象闭环；ESP32无线桥独立固件。
**Tech Stack:** PlatformIO固定版本、STM32Cube HAL、Renode1.17.0、Arduino ESP32、Python标准库。
**Spec:** design.md

## Constraints
- 不覆盖blink工程及用户资料；复用既有tools。
- 实际执行STM32固件，不以Python控制器替代MCU决策。
- 无线固件编译与真实射频测试分开报告。
- 只有新鲜证据、完整采样和全部断言通过才能PASS。

## Review focus
过期结果/制品；非法与超长命令；故障后的重启；PWM使能和方向；Wi-Fi/BLE测试边界。

## Task 1: 控制器与通信
- [ ] 先写C测试：AUTO输出、手动限制、故障锁存、急停、非法命令。
- [ ] 实现firmware/controller/control.c/.h，主程序HAL ADC/PWM/UART采样输出。
- [ ] 编译原生ELF/BIN并测试控制核。

## Task 2: 实际闭环仿真
- [ ] 先写验证器测试：收敛、不收敛、故障未停机和空证据。
- [ ] 实现ADC功能模型、官方TIM2、热对象和PWM观测，执行固件。
- [ ] 正常及传感器故障/超温/急停/堵转/错误PWM接线均验收。

## Task 3: 无线桥
- [ ] ESP32 Wi-Fi HTTP/BLE GATT→共享UART命令，状态回读。
- [ ] 编译ESP32固件；用STM32实际仿真验证相同命令协议。
- [ ] 标明未做真实射频测试，提供接线及实体板验收步骤。

## Task 4: 学习与交付
- [ ] VS Code任务/GDB、入门练习、接线说明、结果图和课程清单。
- [ ] 全量验证、只读审查、修正发现的问题，再报告实际范围。
