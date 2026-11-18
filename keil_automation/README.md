# Keil 自动编译与软件仿真

这里提供已经实际运行的 µVision 命令行流程。默认使用 `D:/keil/UV4/UV4.exe`（5.14.1）和安装中注册的 C51（9.60.7.0）。无第三方 Python 依赖，不需要联网、API 密钥或全局 PATH 配置。

## 常用命令

在 `D:/codex/单片机` 的 PowerShell 中：

```powershell
.\keil.ps1 doctor                         # 检查安装、版本和项目资料
.\keil.ps1 inventory                      # 已配置目录内查找 Keil 实际程序
.\keil.ps1 projects                       # 列出资料中的目标/源码
.\keil.ps1 build --profile smoke8051       # 新副本中编译通用 8051 夹具
.\keil.ps1 simulate                       # 真正启动 µVision 模拟器并验收
.\keil.ps1 simulate --scenario '.\keil_automation\scenarios\stc8h_gpio.json' # 按板卡原理图验证 P6/P3.3
.\keil.ps1 regress                        # 正向通过 + 错 LED 引脚必须被检出
.\keil.ps1 build --profile stc-native      # STC8H 最小原生固件编译
.\keil.ps1 build --profile board-bsp       # 完整资料工程，当前受 2KB 限制
.\keil.ps1 all                            # 环境、回归、原生与 BSP 全流程
.\keil.ps1 report                         # 读取最近一次 all 的结果
.\keil.ps1 open                           # 在 Keil 中打开最近仿真工程副本
```

也可以从其他目录调用：

```powershell
& 'D:\codex\单片机\keil.ps1' simulate
```

若 PowerShell 的执行策略不允许脚本，直接调用相同的 Python 入口，不必修改系统策略：

```powershell
python 'D:\codex\单片机\keil_automation\scripts\keil_cli.py' simulate
```

Codex 的 Windows 沙箱可能使 µVision 无法派生 C51，日志为 `failed to execute ... C51.EXE`。本轮获准的本地执行已跑通；后续由 Codex 使用正常权限申请机制执行这类命令即可，不应把沙箱失败改记为成功。在普通 Windows PowerShell 中直接运行命令也可。

## 本轮实测与范围

| 项目 | 结果 |
|---|---|
| 标准 8051 CPU/Timer0 中断/标准 UART/GPIO 软件仿真 | 5 个断言通过，串口有 `KEIL_UART_OK` |
| STC8H 工程、P6 LED 与 P3.3 K3 程序逻辑 | 不访问实物，松开/按下/再次松开，7 个断言通过；不验证 GPIO 电气和 1T 时序 |
| LED 引脚错误负向用例 | LED 断言失败，其他断言通过；回归正确检出故障 |
| STC8H 最小原生源码 | 编译、链接及 HEX 校验通过，保留许可证读取警告；未在实物运行 |
| STC8H 完整 BSP | `L250`：评估版链接容量限制，记录为阻塞 |
| `Backup.001` 中 µVision 5.40 | 本机测试启动退出 `0xC0000135`，未生成日志；不作默认工具 |

板卡依据在 `../wokwi_sim/docs/board_analysis.md`。默认通用测试选用 8052 器件和 11.0592MHz/12T 设置，包含标准 8051 的测试功能。它不是板上 STC8H 24MHz/1T 精确时序模型。独立 `stc8h_gpio.json` 保留原资料的 STC8H8K64U 器件配置和 STC 头文件，验证 P3.3 输入与 P6 寄存器驱动逻辑。此结果不证明 GPIO 电气、实际 LED、USB、PWM、ADC、I2C/OLED 或精确时间已验证。STC32G 替代装配及实物芯片型号仍需确认。

## 扩展自己的工程与测试

先检查目标，再在副本中编译：

```powershell
.\keil.ps1 inspect '.\开发板资料\STC8H工程标准框架\STC8.uvproj'
.\keil.ps1 build --project '.\开发板资料\STC8H工程标准框架\STC8.uvproj' --target STC8 --dry-run
.\keil.ps1 build --project '.\开发板资料\STC8H工程标准框架\STC8.uvproj' --target STC8
```

源文件和 include 必须在工程自身目录树中；内部绝对路径会重定位到副本，外部依赖先放入自有工程。工程须放在独立子目录，不能让源目录包含自动化输出目录。目标名要精确匹配。当前构建验收面向 C51 产生 HEX 的可执行工程，不接受 ARM、只生成库或依赖外部自定义构建工具的工程；自动化会禁用工程里的 User Programs，固定副本输出目录。原始 MiscControls/控制文件可能覆盖输出路径，除 BSP 使用的 REMOVEUNUSED 外会拒绝，需迁移为标准项目选项再运行。

复制 `scenarios/smoke8051.json`，修改 `commands` 和 `checks`。可增加 `project`（相对场景文件的 `.uvproj/.uvprojx` 路径）和 `target` 来仿真自己的工程。未填 `project` 时使用 smoke 固件。

```powershell
.\keil.ps1 simulate --scenario '.\keil_automation\scenarios\smoke8051.json'
```

场景字段：

| 字段 | 含义 |
|---|---|
| `project`、`target`（可选） | 工作区内自有工程及精确目标名；工程须支持 Keil 软件模拟器 |
| `profile`（可选） | `smoke8051`（默认）或 `stc8h-gpio`；自有 project 与非默认 profile 不混用 |
| `commands` | 顺序执行 `RESET`、`G/GO`、`TSTEP/PSTEP` 或数值输入赋值，例如 `PORT3 = 0xfb` |
| `checks` | `name` 唯一断言名、`symbol` 数值变量/寄存器、`equals` 0..65535 的预期值 |
| `uart_marker`（可选） | 串口日志必须包含的标记；省略/null 表示不验收串口 |

用 `G, 函数名` 在读取输入前设置断点，再改变 `PORTn` 外部引脚输入；用 `G, test_done` 到达结果检查点。示例设置的是标准模拟器的 P3.2 测试输入。固件保留调试信息，供脚本读取符号。流程自动生成日志、随机运行 ID、完整断言集与 `EXIT`；场景不自行控制日志或装载其他镜像。更复杂的调试语言扩展从 `scripts/simulation.py` 做起，并根据实际器件模型重新定义验收范围。

## 产物和结果契约

每次操作生成 `runs/<UTC时间>-<操作>-<随机值>/`，不会使用上一轮的 HEX：

```text
运行目录/
  project/                 本轮源副本和 firmware.uvproj
    Objects/               符号可执行文件、HEX、对象文件
    Listings/              汇编列表、链接映射
    debug.ini              自动生成的模拟器测试脚本
    debug.log              程序实际执行后的数值断言
    serial.log             模拟 UART 输出
  build.log                uVision 编译输出
  process.log              编译进程输出
  build-result.json        退出码、许可证警告、产物校验和
  scenario.json            本轮场景
  debug-process.log        调试进程输出
  result.json              本轮仿真结果
```

`runs/latest-build.json`、`latest-simulation.json`、`latest-regression.json`、`latest-all.json` 指向各类最近结果；`report` 读取 `latest-all.json`，它是该次运行快照。单独 `simulate` 不会更新 `latest-all.json`。每个结果带实际 `run_dir` 与进程记录，查看日期后再引用。

命令 stdout 为 JSON，Python 启动器的环境警告可能出现在 stderr。CLI 成功返回 0，失败返回 1。状态包括 `PASS`、`PASS_WITH_WARNINGS`、`PASS_WITH_LIMITATIONS`、`FAIL`；当前正在执行的指针为 `RUNNING`。新请求即使配置解析、启动或工程准备出错，也会用本次失败替换该类旧结果。`all` 的 `PASS_WITH_LIMITATIONS` 仅允许已明确识别的 BSP L250 阻塞，不等于 BSP 已通过；其他失败返回 1。`wrong-led` 单独仿真故意返回 1；`regress` 仅在正向通过、LED 故障被检出、其他项通过且调试进程正常退出时返回 0。

读命令返回如 `{"schema_version":1,"command":"doctor","status":"PASS",...}`。失败返回如 `{"schema_version":1,"command":"inspect","status":"FAIL","error":"..."}`。构建结果增加 `process`、`artifacts` 与 `build_log`；仿真结果增加 `assertions`、`complete` 与 `uart_ok`。

一次只运行一个编译/调试流程。编译默认超时 90 秒，仿真 45 秒；超时只结束本流程创建的进程树。当前配置见 `config.json`。`KEIL_UV4` 可临时选择其他安装，`KEIL_PYTHON` 可指定 Python。`KEIL_C51_ROOT` 必须与所选 µVision 的 `TOOLS.INI` 注册路径一致，不能单靠变量切换编译器。

## 测试与依据

```powershell
python -m unittest discover -s '.\keil_automation\tests' -v
.\keil.ps1 all
```

详见 [官方文档依据](docs/official-sources.md)、[验收记录](docs/acceptance.md) 和 [Codex 本地技能](skills/keil-local/SKILL.md)。
