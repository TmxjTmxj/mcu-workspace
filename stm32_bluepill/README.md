# STM32F103C8T6 本地开发与仿真

典型的 STM32 Blue Pill，运行 STM32Cube HAL 编译出的原生 Cortex-M3 固件。主流程为 **PlatformIO 编译 → Renode 本地执行 ELF → 注入按键 → 验证 LED、GPIO、UART → 输出报告**。不需要 Wokwi 登录。

## 在 VS Code 使用

打开 `stm32-bluepill.code-workspace`。

1. 修改 `src/main.c`，Ctrl+Shift+B 编译。
2. “终端 → 运行任务”选择 **STM32: 自动仿真验收（本地无需登录）**。重新编译、核对固件和接线、运行仿真，成功显示 `SIMULATION_PASS`。
3. 浏览器打开 `logs/report.html`，播放或拖动时间轴查看真实 GPIO 采样和串口输出。页面是执行证据回放；重新验收才会更新数据。
4. 运行 **STM32: 接线故障回归**，验证正常电路通过，断开按键、LED接错引脚均被检出，成功显示 `REGRESSION_PASS`。

从外层目录执行：

```powershell
python stm32_bluepill/scripts/workflow.py all
python stm32_bluepill/scripts/workflow.py regression
python -m unittest discover -s stm32_bluepill/tests -v
```

首次安装工具需要联网；安装完成后，已有工具和固件的本地仿真不需要账户或联网。编译器、HAL、Renode、缓存都放在 `tools/`，不修改全局 PATH。Renode首次启动会建立自己的AppData目录；本项目将配置及命令历史保存到 `tools/`。

## 接线与行为

| 功能 | 引脚与连接 | 行为 |
|---|---|---|
| 外接LED | PA0 → 330Ω → LED正极；负极 → GND | 高电平亮，默认每500ms切换 |
| 板载LED | PC13，低有效 | 与外接灯同步 |
| MODE按键 | PB12 → 按键 → GND | 20ms去抖，每次按下切换100ms/500ms间隔 |
| 串口输出 | USART1，PA9 TX → 串口RX | 115200、8N1，启动/亮灭/按键事件 |
| 串口输入 | PA10 RX ← 串口TX | 预留，当前没有命令解析 |

`diagram.json` 保留Wokwi面包板接线。检查器要求它与数字平台一致；改接线时需同步更新Renode平台和验收脚本。Renode按键向PB12注入电平，LED连接PA0模型，UART直接连接USART1后端。

## 调试

运行任务 **STM32: 启动本地 GDB 仿真**，等到GDB服务监听3333后，选“STM32 本地 Renode GDB”并F5。需要VS Code C/C++扩展；结束后在仿真任务终端Ctrl+C。Renode终端输入 `sysbus.gpioPortB OnGPIO 12 false` 按下，`true` 释放。不要同时启动Wokwi的3333调试服务。

```powershell
python stm32_bluepill/scripts/debug.py --verify
```

该命令已实测：ARM GDB连接本地仿真器、命中 `main()` 断点并读取PC。VS Code F5使用同一个GDB和端口，其编辑器界面需由用户运行。

## 文件放置

```text
stm32_bluepill/
  src/main.c                     原生STM32 HAL源码
  platformio.ini                 固定构建版本
  renode/                        数字平台、RCC模型、采样器、报告模板
  scripts/                       一键工作流、安装、仿真、调试、报告
  tests/                         验证器测试、Wokwi可选场景
  .vscode/                       编译、验收、故障回归、GDB任务
  build/bluepill/                 生成的ELF/BIN
  logs/                          本次证据与报告
  tools/                         编译器、HAL、PlatformIO、Renode及缓存
  docs/                          设计、计划与验收记录
```

原始 `开发板资料/` 和已有 `wokwi_sim/` 独立保留。主流程不依赖相邻Wokwi CLI；可选Wokwi CLI仍复用 `wokwi_sim/tools/wokwi-cli.exe`。

## 验收与范围

真实证据：`logs/all_result.json`、`logs/renode_normal/serial.log`、`gpio.json`、`monitor.log`。180个10ms采样点测得慢闪500ms、快闪100ms；PA0与PC13极性正确，PB12按下/释放及串口协议匹配。故障回归和GDB证据在 `logs/regression_result.json`、`logs/renode_debug/`。验证器20项单元测试通过；单元测试本身不代表固件已执行。

数字平台只配置本例使用的Cortex-M3、64KB Flash、20KB SRAM、NVIC/SysTick、GPIO A/B/C、USART1及位带寻址。RCC补充模型使时钟就绪/切换位立即响应，Flash ACR为读写存储。**不验证晶振启动、真实时钟门控、Flash擦写、模拟电流、电阻功耗、内部上拉电气行为或PA9串口复用接线。** 未配置的ADC/I2C/SPI/DMA/USB等不能据此宣称通过。实体硬件需另做电气和外设验证。

## Wokwi可选入口

登录可用后，扩展中运行 `Wokwi: Start Simulator` 查看面包板工程。CLI需单独凭据：`python scripts/workflow.py all --backend wokwi`；缺凭据返回 `BLOCKED`。凭据不写工程文件。主流程不依赖这个步骤。

官方参考：[Renode自动测试](https://renode.readthedocs.io/en/latest/basic/renode-testing-api.html)、[UART日志](https://renode.readthedocs.io/en/latest/host-integration/uart.html)、[GDB调试](https://renode.readthedocs.io/en/latest/debugging/gdb.html)、[PlatformIO Blue Pill](https://docs.platformio.org/en/latest/boards/ststm32/bluepill_f103c8.html)、[Wokwi Blue Pill](https://docs.wokwi.com/parts/board-stm32-bluepill)。
