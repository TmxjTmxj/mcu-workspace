# STM32 Blue Pill Implementation Plan

> 执行：当前会话直接实施；不新增聊天。使用 executing-plans、TDD 和 verification-before-completion。当前目录不是 Git 仓库，因此不创建 worktree 或提交。

**Goal:** 原生 STM32 自动构建和虚拟接线测试。
**Architecture:** PlatformIO STM32Cube HAL + 本地Renode；Wokwi为可选前端。Python入口管理项目内工具和日志，明确区分编译成功与仿真实跑。
**Spec:** design.md

## Constraints
- 独立 stm32_bluepill/；原输入与 Mega 工程保留。
- 不保存许可证/token，不刷写实板。
- 缺凭据返回 BLOCKED；旧日志不能产生 PASS。

## Review focus
- 缺令牌、失败串口、缺少事件、编译失败及路径含中文的目录必须得到正确状态。

## Task 1: 原生工程与编译
- [x] 配置PlatformIO、STM32Cube HAL、项目内依赖安装。
- [x] 编译生成ELF/BIN，记录构建结果与工具版本。

## Task 2: 电路和测试入口
- [x] 协议验证器测试正常、缺事件、FAIL和旧日志。
- [x] 实现build/check/simulate/all/regression；保留Wokwi电路与场景。
- [x] Renode实跑通过：180个GPIO采样点，慢闪500ms、快闪100ms、串口和按键事件正确。
- [x] 按键断开和LED接错引脚均被检出。

## Task 3: VS Code 和交付
- [x] 提供独立workspace、tasks、GDB配置和中文README。
- [x] GDB实际连接并命中main断点，生成运行证据回放。
- [x] 只读审查后补充接线一致性校验，明确数字模型范围。
