# 本地 STM32 仿真验收 · 2026-09-27

用户暂停Wokwi登录排查，交付主路径改为PlatformIO + Renode 1.17.0。

- 构建：STM32Cube HAL原生Cortex-M3 ELF/BIN，Flash4212B，RAM116B；来源和制品SHA256记录在构建清单。
- all：SIMULATION_PASS。Renode执行实际ELF，180个10ms采样点，PA0和低有效PC13同步，慢闪500ms、快闪100ms。PB12按下/释放，UART按序报告BOOT/READY/PRESSED/FAST/RELEASED。
- regression：REGRESSION_PASS。按键断开导致缺按下事件；LED改接PA1导致实际LED状态与PA0不符，两组故障均为预期FAIL。
- GDB：GDB_PASS。ARM GDB通过3333连接Renode并停在main，PC=0x08000f1c。VS Code界面F5尚未由用户运行。
- 验证器：20项测试通过，包括错误目标/复位向量、缺事件、旧日志、错误极性、错误时序和接线图偏离模型。
- 页面：本地浏览器已查看接线状态、时间轴和UART回放。页面只显示真实执行证据，不进行实时CPU仿真。

原始STC资料保持独立；所有新增文件放在stm32_bluepill内。Renode首次启动创建AppData自身目录，配置和命令历史已定向项目tools。工具版本固定，正式运行不用Wokwi账号。

模型边界详见README：RCC/Flash ACR是本例的功能补充，UART后端连接USART1，按键直接注入PB12，不验证模拟电气、晶振时序、内部上拉、PA9复用等。

## 建议长期记录

典型MCU选择STM32F103C8T6；账户网络阻塞时以本地Renode作为自动验收主路径，Wokwi保留作可选接线前端。验收必须结合实际串口和GPIO/LED模型，单凭日志文本或编译成功不能报告仿真通过。工具、源码、构建制品和日志在工程中分目录存放。

Obsidian知识库位于当前授权写入范围之外，本次不写入知识库。
