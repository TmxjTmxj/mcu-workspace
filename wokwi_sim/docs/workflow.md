# Board-to-Simulation Workflow

入口：`python wokwi_sim/run_workflow.py --backend local`，无需当前目录切换；所有内部路径相对于脚本解析，支持中文路径。

1. `scan_board_docs.py`递归盘点全部输入，哈希/分类/读取文本/PDF/XML/图片/ZIP/HEX，机械与专有二进制显式记录。
2. `hardware.py`验证确认等级、证据、引脚、端点、电压及适配器；关键来源SHA256变化时拒绝继续，需人工重新分析。
3. `hardware.py`根据真实图与独立适配层生成Wokwi图；不按通用AI推测生成未确认板级GPIO。
4. `build_firmware.py`删除本目标旧产物后重新编译，返回错误即失败；Keil明确0ERROR且退出1只作为警告接受，保留许可证信息。
5. Wokwi CLI lint验证diagram；`run_simulation.py`执行所选后端，串口日志必须是本轮新产物。
6. `verify_serial.py`检查完整协议及错误标志；回归运行实际编译HEX与故障拓扑，不能用expected_serial.txt代替实测日志。

本轮不是全自动理解任意PDF的系统。扫描器能提取/索引，真实图由证据分析后建立；原理图图形网表尚未自动恢复。后续增加解析器/Renode/实物后端时，应继续消费hardware_graph.json并保留source_fingerprints和unknowns。

默认Wokwi命令返回PARTIAL/非零，直到凭据/上传授权及实际运行验证完成。显式local后端只报告`EQUIVALENT_LOCAL_WORKFLOW_READY`，绝不报告整板`REPRODUCIBLE WORKFLOW READY`。

`--native`可把原生最小编译纳入本轮；完整Keil BSP仍另受2KB限制。原生失败不得吞掉或复用先前HEX。单独构建结果见native_verified_build.json.log，常规local工作流仅构建AVR等效目标。

串口PASS仅证明相应固件代码与模型路径。额外观测：8路PORTA低有效轮转、0.2-0.3秒注入的K3接地事件、ADC=512、112个I2C地址探测、合成OLED命令序列。失败场景由runner返回1，测试套件断言其被检测后返回0。
