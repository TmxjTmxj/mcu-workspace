# 官方文档依据

核对日期：2026-10-10。下列说明为实际采用的接口摘要，不复制整本手册。老链接的 `.htm` 有时重定向失败，`.asp` 或 `uv4cl` 版本在本轮可访问。

| 官方来源 | 本项目采用的行为 |
|---|---|
| [Keil µVision Command Line](https://www.keil.com/support/man/docs/uv4/uv4_commandline.asp) | `-r` 重编译，`-t` 选目标，`-j0` 隐藏窗口，`-o` 编译日志，`-d` 配合初始化脚本自动测试；退出码 0 无警告，1 警告，2/3 错误。本文未把 `-f` 烧录加入默认流程。 |
| [Keil Debug settings](https://www.keil.com/support/man/docs/uv4cl/uv4cl_dg_debug.htm) | 启动时加载符号文件并执行 Initialization File；测试工程使用 Simulator，禁用恢复旧断点/函数和 Run to main 自动干扰。 |
| [Keil Go](https://www.keil.com/support/man/docs/uv4cl/uv4cl_cm_go.htm) | `G, function` 在指定符号处设置临时断点并运行至该处，便于输入注入和结果检查。 |
| [Keil LOG](https://www.keil.com/support/man/docs/uv4cl/uv4cl_cm_log.htm) | `LOG > file` 收集命令窗口输出，结束用 `LOG OFF`。 |
| [Keil SLOG](https://www.keil.com/support/man/docs/uv4/uv4_cm_slog.asp) | `SLOG > file` 收集串口窗口输入/输出，结束用 `SLOG OFF`。 |
| [Keil Predefined Functions](https://www.keil.com/support/man/docs/uv4/uv4_df_predeffunct.asp) | 用调试语言 `printf` 输出变量和断言；不是固件伪造模拟结果。 |
| [Keil EXIT](https://www.keil.com/support/man/docs/uv4cl/uv4cl_cm_exit.htm) | 脚本末尾独立写 `EXIT`；官方明确不允许作为 `exec` 的参数。 |
| [Keil batch process waiting](https://www.keil.com/support/docs/3998.htm) | 直接从交互命令行启动可能立即返回。本工具持有创建的进程句柄并等待退出，有超时。 |
| [Keil Remote Control](https://www.keil.com/support/docs/2636.htm) | 官方自动测试路径支持命令行和 debugger INI；交互 DDE/UVSOCK 留作后续需要时扩展。 |
| [Keil Evaluation Limitations](https://www.keil.com/demo/limits.asp?bhcp=1) | C51 评估版限制 2KB 对象代码，代码起点 0x0800；限制不通过更换脚本或截断产物解决。 |
| [Microsoft C++ application dependency troubleshooting](https://github.com/MicrosoftDocs/cpp-docs/blob/main/docs/build/troubleshooting-c-cpp-isolated-applications-and-side-by-side-assemblies.md) | 5.40 副本启动返回 0xC0000135，与依赖装载问题一致；本轮没有确认缺失的具体 DLL。 |
| [OpenAI repo-local skills and AGENTS.md](https://developers.openai.com/blog/skills-agents-sdk) | 用工作区指令和可复用技能保存操作知识；当前受权限限制，技能存放普通项目目录并由 AGENTS.md 指向。 |

本机附带官方帮助：`D:/keil/UV4/uv4.chm`、`D:/keil/C51/HLP/uv4cl.chm`、`c51.chm`、`bl51.chm`。

[Keil Core Simulation](https://www.keil.com/products/uvision/db_sim.asp) 明确软件模拟器使用 PC 和器件模拟驱动运行程序，不要求连接实物。实际能力取决于所用模拟驱动；本轮 STC8H GPIO 实测只声明寄存器与程序逻辑。

开发板证据来自本地原理图、STC 手册与已有分析报告，不能由 Keil 官方文档推断实物芯片已确认或 STC 专有外设已完整建模。
