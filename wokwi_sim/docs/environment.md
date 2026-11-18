# Environment

| Tool | Installed / version | Status |
|---|---|---|
| VS Code | D:/VScode/VSCode/bin/code.cmd | Installed；扩展清单CLI访问用户数据目录受沙箱限制，改用只读扩展目录检查 |
| Wokwi VS Code extension | wokwi.wokwi-vscode 3.7.0 | Installed；许可证有效性UNKNOWN，未读取或导出凭据 |
| Wokwi CLI | 项目tools/wokwi-cli.exe 0.27.1 | Installed locally；lint PASS；CLI token absent |
| PlatformIO | PATH未发现 | Not Installed/Not Found；AVR GCC可替代本轮等效编译 |
| Arduino CLI | PATH未发现 | Not Installed/Not Found；无需全局安装 |
| ESP-IDF / STM32 toolchain | 未确认安装；arm-none-eabi-gcc未在PATH | Not Needed for STC/AVR current targets |
| Keil uVision/C51 | D:/keil；C51 9.60.7.0、BL51 6.22、OH51 2.7 | 2KB评估版，许可证注册表警告；原BSP L250 |
| AVR GCC | 项目tools/avr/bin；7.3.0 Arduino7 | 本地下载，Arduino官方包清单SHA256校验成功 |
| Python | D:/python/python.exe | Installed；pymupdf/Pillow已可用，无全局pip安装 |
| Node/npm | C:/Program Files/nodejs | Installed；npm缓存改到工作区，未修改系统环境 |
| AVR8js | 0.21.0，项目tools/local-emulator | npm锁文件固定，实际CPU回归PASS |
| Git | C:/Program Files/Git/cmd/git.exe | Installed；当前工作区不是仓库，未git init或提交 |

下载来源：Arduino downloads.arduino.cc官方包清单/AVR工具；Wokwi官方GitHub releases；avr8js npm包及官方仓库。工具只写工作区，不改系统PATH、不刷写硬件。Keil最小固件编译在获准的本地提升权限执行中完成，用于读许可证与生成工作区产物。

Wokwi上传相关提升权限执行被自动审批拒绝。拒绝后没有换入口、浏览器或间接脚本绕过。此前普通CLI启动已记录缺token错误；当前报告保留该证据。
