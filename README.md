# 单片机工作区

Keil 自动化已配置在 [keil_automation](keil_automation/README.md)。在 PowerShell 中执行：

```powershell
Set-Location 'D:\codex\单片机'
.\keil.ps1 doctor
.\keil.ps1 all
```

## 文件规划

| 路径 | 用途 |
|---|---|
| `开发板资料/` | 原始原理图、芯片手册、照片与厂商 BSP，作为资料源 |
| `keil.ps1` | 统一命令入口，可从任意目录用完整路径调用 |
| `AGENTS.md` | 后续 Codex 会话的工作区入口与资料使用规则 |
| `keil_automation/config.json` | 当前选用的 Keil/C51 路径、资料引用、超时 |
| `keil_automation/firmware/` | 自动化测试固件；新的自有工程可建独立子目录 |
| `keil_automation/scenarios/` | 断点、GPIO 输入、数值断言和串口预期 |
| `keil_automation/scripts/` | 工程准备、命令行流程、调试脚本生成、进程控制 |
| `keil_automation/runs/` | 每次运行的副本、HEX、符号文件、日志与 JSON 结果 |
| `keil_automation/docs/` | 设计、官方依据、验收与已知问题 |
| `keil_automation/skills/` | Codex 的本地 Keil 操作技能，由 AGENTS.md 引导读取 |
| `wokwi_sim/` | 既有板卡解析与 AVR/Wokwi 等效仿真，不能替代 STC 原生执行证明 |
| `stm32_bluepill/`、`stm32_control/` | 既有 STM32/控制系统实验 |
| `.vscode/tasks.json` | 编辑器任务，包含 Keil 操作和原有实验入口 |

本轮验收见 [Keil 验收记录](keil_automation/docs/acceptance.md)。
