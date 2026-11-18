---
name: keil-local
description: 在本单片机工作区用已安装的 Keil/C51 检查工程、隔离编译、运行软件仿真和读取验收结果。适用于 Keil 自动化任务；实物 STC 烧录和串口调试需要对应的用户请求。
---

# Keil 本地工作流

统一入口为工作区根目录 `keil.ps1`，实现位于 `keil_automation/scripts/keil_cli.py`，仅需 Python 标准库。先读 [README](../../README.md)，涉及具体器件能力时读 [官方依据](../../docs/official-sources.md) 与 `wokwi_sim/docs/board_analysis.md`。

1. 运行 `doctor`。必要时 `inventory` 和 `projects` 查找安装与精确目标，使用 `inspect` 读取选定工程。
2. 用户要求编译时使用 `build --profile stc-native` 或 `build --project ... --target ...`。构建发生在新 `runs` 副本中；资料源不编辑。使用 `--dry-run` 检查计划。
3. 用户要求软件仿真时运行 `simulate`；自有工程可用 `--scenario` 提供断点、输入、数值断言及串口标记。先确认该器件的 Keil 模型支持需要的外设。
   针对这块板子的离线按键/LED 程序测试，使用 `--scenario keil_automation/scenarios/stc8h_gpio.json`。保留 STC 头文件、P6 LED 和 P3.3 K3 映射；已实测 7 个寄存器/逻辑断言通过，不能推广为完整 STC 外设和电气验证。
4. 修改测试固件或脚本后运行相应单元测试和真实仿真；默认夹具的正反向验收用 `regress`。环境完整验收用 `all`。
5. 根据本轮 `run_dir`、编译退出码、HEX 校验、断言和串口日志报告结果。`report` 是最近一次 all 的快照，单独模拟之后应读 latest-simulation。不能用历史通过替代当前失败。

```powershell
& 'D:\codex\单片机\keil.ps1' doctor
& 'D:\codex\单片机\keil.ps1' simulate --scenario 'D:\codex\单片机\keil_automation\scenarios\smoke8051.json'
& 'D:\codex\单片机\keil.ps1' all
```

当前默认 µVision 5.14.1 已实测；Backup.001 的 5.40 启动失败，不根据版本号自动切换。C51 的许可证读取警告必须保留，完整 BSP 的 L250 属实际容量限制。`PASS_WITH_LIMITATIONS` 表示流程完成且仍有明确限制。

本流程不需要 OpenAI API、网络认证或密钥。Codex Windows 沙箱中 C51 子进程可能无法运行；若日志明确 `failed to execute C51.EXE`，按工具的正常权限流程请求本地执行，保留失败证据。审批拒绝后不换入口绕过。

通用测试使用标准 8051/8052 模型。它不证明 STC8H 的 1T 时序、USB/ADC/PWM/I2C 或板上 LED/OLED 已在实物工作。不要自动执行旧资料中的 Flash、AutoFlash、reset_mcu 等脚本。后续收到实物操作请求，再依照该请求选用烧录/串口流程。
