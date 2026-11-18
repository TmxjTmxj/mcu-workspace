# STC8H_32G_LQFP64 Board2Sim

已建立可重复执行的**外设行为等效工作流**。原理图主控为 STC8H8K64U-LQFP64；Wokwi 不支持 8051，当前 Wokwi 图使用 ATmega2560 和 AVR 固件。原始 STC HEX 不可加载到该 Mega 图中。

当前验收：本地 AVR8js 等效回归 READY；Wokwi 图纸 lint PASS，Wokwi 实际执行 BLOCKED（缺少 CLI token，提升权限执行另被自动审批拒绝）；STC 最小固件编译成功并保留许可证警告，原生运行 NOT_VERIFIED。完整原始 BSP 编译受 Keil 2KB 评估版限制。

## 快速运行

在当前工作区根目录：

```powershell
python wokwi_sim/run_workflow.py --backend local
```

执行：全部资料盘点 → 硬件图/来源校验 → diagram 生成 → AVR 固件编译 → Wokwi 图纸 lint → 本地 CPU 行为仿真 → 回归/故障测试。

成功输出 `EQUIVALENT_LOCAL_WORKFLOW_READY`，它不表示真实 STC 核心或 Wokwi 已通过。日志位于 `logs/workflow_local.json`、`logs/local_none.json` 和 `logs/tests.log`。

默认后端为 Wokwi：

```powershell
python wokwi_sim/run_workflow.py
```

需要 Wokwi 服务凭据及对上传图纸/AVR 固件的授权。无令牌时应退出非零并记录 BLOCKED。当前会话的提升权限运行被自动审批拒绝，未绕过该拒绝。

## 编译

```powershell
python wokwi_sim/scripts/build_firmware.py --target equivalent
python wokwi_sim/scripts/build_firmware.py --target native
```

等效固件为 `build/equivalent.elf` 和 `build/equivalent.hex`，由工作区内 AVR GCC 7.3.0 编译，无 Arduino/PlatformIO 全局安装依赖。

原生固件为 `build/native/main.hex`，复用资料中的 STC 官方寄存器头文件。Keil 默认位置 `D:/keil/C51`，可通过 `KEIL_C51_ROOT` 指定。Keil 警告码 R207/R206 与注册表许可证访问有关；评估版代码位于 0x0800 以上，当前 HEX 复位向量是 `LJMP 0x09CE`。它已通过 Intel HEX 校验，未刷写、未验证真实启动。24MHz IRC 必须在 STC-ISP 中配置，RST/P5.4 复位功能也需相应配置。

完整原工程的只读来源在 `开发板资料/`，工作区副本在 `firmware/native/project/`。其重编译 L250 证据见 `logs/native_original_build.log`，没有把历史 HEX 冒充新编译结果。

## VS Code / Wokwi

1. 在 VS Code 中打开 `wokwi_sim/` 文件夹（配置位于该文件夹根部）。
2. 先运行等效固件编译命令。
3. 使用已安装的 Wokwi 扩展，完成其许可证流程后执行 `Wokwi: Start Simulator`。
4. 图中 8 个 LED 应循环亮；按 K3 应输出 `[EVENT] BUTTON K3 PRESSED`；可选合成 OLED 接受全亮命令。

工作区根的 `.vscode/tasks.json` 提供本地工作流、两种固件编译和测试任务。Wokwi 扩展许可证与 CLI token 是不同凭据；安装扩展不代表许可证有效。

## 测试

```powershell
python -m unittest discover -s wokwi_sim/tests -v
```

22 项测试覆盖未知/无证据硬件、重复引脚、映射冲突、源码变更、旧日志、错误日志，以及实际编译的 AVR HEX 执行。5 个故障场景：错误 I2C 地址、OLED 断电、SDA/SCL 交换、错误 LED GPIO、按键断线。故障测试通过表示故障被正确检测，不表示错误场景自身正常工作。

`tests/expected_serial.txt` 仅为协议校验夹具，绝不作为执行证据。实际串口证据由 CPU 执行生成。OLED 在本地后端仅验证 ACK 与命令序列，未模拟像素。

## 硬件与限制

- [板卡分析](docs/board_analysis.md)、[架构与电源树](docs/hardware_architecture.md)、[引脚表](docs/pin_mapping.md)
- [资料冲突](docs/conflicts.md)、[Wokwi 映射](docs/wokwi_mapping.md)、[仿真限制](docs/simulation_limitations.md)
- [环境](docs/environment.md)、[工作流](docs/workflow.md)、[验收](docs/acceptance.md)
- [完整清单](docs/inventory.json)、[目录树](docs/inventory_tree.txt)、[调试历史](logs/debug_history.md)

真实电源树是 `USB +5V → F1 → VBUS → ON/OFF1 → VCC(5V) → V1 → 3V3`。原生 USB 为 P3.0 D-/P3.1 D+，通过 J1 切换。软件模型不验证电源纹波、瞬态、过流、EMI、PCB 寄生或真实硬件安全。实体接线前重新检查电压、电流、引脚容限、共地、电源来源与短路。

## 结构

```text
wokwi_sim/
  hardware_graph.json         真实板卡及证据；不依赖 Wokwi
  simulator_adapter.json      明示的 STC → Mega 行为重映射
  diagram.json / wokwi.toml    Wokwi 等效工程
  run_workflow.py              一键入口；失败/阻塞退出非零
  firmware/native/            原生 STC 最小固件与原 BSP 副本
  firmware/equivalent/        AVR 外设行为固件
  scripts/                    扫描、校验、编译、执行、串口验证
  tests/                      单元、真实 CPU 回归与 Wokwi 场景
  benchmark/                  基线与故障检测指标
  docs/ / logs/ / build/       资料报告、实测证据、构建产物
  tools/                      工作区内工具、锁文件和许可证
```

迁移机器时保留 `tools/local-emulator/package*.json`，可运行 `python scripts/setup_tools.py` 在项目内重新获取已校验的 AVR 工具和锁定的 AVR8js。Wokwi CLI 按官方发布获取，不把任何凭据写入项目。

下一步优先完成授权后的 Wokwi 等效工程实跑；若目标是运行原始 STC 固件，则需要增加真正支持 STC 寄存器/外设的后端，或使用厂商实板在线仿真。
