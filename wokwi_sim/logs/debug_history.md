# Debug History

## Issue 001 — Hardware evidence conflicts
Symptom：串口说明将USB引脚、电源、J1和自动复位描述为另一种接线。
Evidence：原理图逐模块/26张图片核对，USB1/2网名与U2管脚清晰。
Category：PIN_ERROR / WIRING_ERROR / CONFIG_ERROR in secondary documentation.
Fix：以原理图建立模型，逐项记录conflicts.md；保留原资料。
Result：真实硬件图校验PASS；实际装配状态仍UNKNOWN。

## Issue 002 — Full BSP cannot link
Symptom：Keil uVision重编译退出3、L250，Target not created。
Evidence：logs/native_original_build.log，RESTRICTED VERSION 0800H，USED 20B5H；Program Size code=3581。
Category：BUILD_ERROR / LICENSE_LIMITATION。
Decision：保留完整SDK副本及失败证据，使用官方寄存器头文件完成小型polling bring-up；不绕过许可证、不刷写。
Result：477字节最小HEX编译/链接/转换成功，许可证注册表警告保留；原完整工程仍失败。

## Issue 003 — npm writes outside workspace
Symptom：默认npm缓存在AppData，mkdir EPERM。
Category：CONFIG_ERROR / ENVIRONMENT_LIMITATION。
Fix：npm --cache指向tools/npm-cache，固定avr8js@0.21.0。
Result：安装成功；未改全局缓存设置或系统PATH。

## Issue 004 — Keil warning status and output access
Symptom：C51返回1但报告1WARNING/0ERROR，直接BL51输出访问受限。
Evidence：native_build.log；R206/R207，评估版。初始BL51错误选项LIBPATH另报L204。
Fix：BL51显式链接C51S.LIB；仅当工具明确报告0ERROR才将返回1按警告接受；获准本地权限执行后编译。
Result：PASS_WITH_LICENSE_WARNING；HEX校验，复位向量0209CE（LJMP09CE）。原生运行未验证。

## Issue 005 — AVR local boot stalls after first log
Symptom：8.8M周期仅有BOOT日志，LED/ADC/I2C没有后续活动。
Evidence：runtime_red/green与AVR8js CPU内存实现；Mega RAMEND=0x21ff，库默认额外寄存器窗为0x100。
Category：SIMULATOR_CONFIG_ERROR。
Hypothesis：SP超出data缓冲，调用返回地址丢失。
Fix：SRAM分配加额外0x100寄存器窗，不修改固件来掩盖栈问题。
Result：BOOT/TIMER/ADC/I2C/8LED/K3全部观测通过，5故障场景被检测。

## Issue 006 — Windows stdout decoding
Symptom：一键lint阶段UnicodeDecodeError，Wokwi输出✓由默认GBK解码。
Evidence：workflow local首次PARTIAL；CLI手动lint退出0。
Category：CONFIG_ERROR。
Fix：子进程输出显式UTF-8/errors=replace；先写Unicode输出测试并看到缺函数失败。
Result：22项套件PASS；一键local 6/6通过。

## Issue 007 — Wokwi execution blocked
Symptom：普通CLI尝试报Missing WOKWI_CLI_TOKEN。
Evidence：wokwi_attempt.log；工具安装本身无凭据。
Additional block：提升权限默认Wokwi工作流被自动审批拒绝，理由为可能向外部服务上传项目固件/图纸，授权未被审批认可。
Decision：拒绝后未绕过；继续本地AVR8js回归，只报告本地等效READY。
Result：Wokwi lint PASS；Wokwi runtime BLOCKED；外部授权/凭据待用户完成。

## Issue 008 — Recheck graph transcription
Evidence：TFT数据D8=P07至D15=P00；RTC主供电VCC2，电池VCC1。
Fix：修正首版人工录入的顺序/供电；补足LED经J2/电阻到VCC的via连接和核心电源。
Result：122连接和64pin表，模型不再留首版错误。

## Issue 009 — Review validation gaps
Evidence：新的低可信MCU、重复package pin和来源变更测试先失败。
Fix：验证确认等级/证据与唯一性，关键资料SHA256变化后要求重新分析。
Result：完整22/22测试通过；不会把图形/芯片手册变化静默接受为旧板。
