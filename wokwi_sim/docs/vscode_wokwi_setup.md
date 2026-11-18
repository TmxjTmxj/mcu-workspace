# VS Code 内使用 Wokwi：官方现成方案

核查日期：2026-09-27。此页记录接入方案，不代表 GUI 仿真已启动或验收通过。

## 方案选择

使用官方扩展 `wokwi.wokwi-vscode`。本机已安装 3.7.0；现有工程通过项目内 AVR GCC 生成 Mega 等效固件，不需要额外安装 PlatformIO 或 Arduino CLI。

官方 Marketplace 明确说明仿真在 VS Code 内运行，代码不离开本机。此前 CLI 缺少 `WOKWI_CLI_TOKEN` 的结果及上传相关审批记录，不应当作为 VS Code 扩展必须上传固件、或必须提供 CLI token 的证据。扩展需完成自身许可证激活。普通模式需要互联网；官方离线模式需要 Pro 计划。

## 文件放置

在 VS Code 中打开 `D:/codex/单片机/wokwi_sim` 文件夹，使 `wokwi.toml` 和 `diagram.json` 位于打开的工程根目录。保持原始 `开发板资料/` 独立。

```text
wokwi_sim/
  wokwi.toml                 扩展配置
  diagram.json               电路图
  firmware/equivalent/       AVR 等效源码
  build/equivalent.hex       扩展加载的固件
  build/equivalent.elf       ELF
  scripts/                   编译等脚本
  docs/                      方案和硬件说明
  logs/                      执行证据
  tools/                     项目内工具
```

当前配置已经符合官方 AVR 固件格式和相对路径要求：

```toml
[wokwi]
version = 1
firmware = "build/equivalent.hex"
elf = "build/equivalent.elf"
```

## 操作步骤

1. 打开上述工程文件夹。
2. 按 F1，执行 `Wokwi: Request a new License`；允许打开官方网页。
3. 在网页点击 `GET YOUR LICENSE`，按需由用户完成登录；允许网页返回 VS Code，确认出现许可证激活信息。不要把许可证或账户凭据写入项目或聊天。
4. 在该文件夹终端编译：`python scripts/build_firmware.py --target equivalent`。如果从外层工作区运行，使用 `python wokwi_sim/scripts/build_firmware.py --target equivalent`。
5. 按 F1，执行 `Wokwi: Start Simulator`。
6. 检查 LED 循环、K3 按键事件和实际串口输出；观察成功前仍保持 Wokwi 实跑未验证的状态。

外层 `D:/codex/单片机/.vscode/tasks.json` 适用于打开外层工作区，路径含 `wokwi_sim/`。直接打开内层仿真文件夹时，使用本页命令，不要照搬外层任务路径。

## 适用范围

官方支持清单列出 AVR、ARM、RISC-V、Xtensa，未列出 STC/8051。这里运行 ATmega2560 外设行为等效工程，不能直接执行原始 STC HEX，也不能据此证明 STC 硬件或原生程序正确。

## 官方来源

- [扩展 Marketplace](https://marketplace.visualstudio.com/items?itemName=wokwi.wokwi-vscode)
- [安装、激活和官方示例](https://docs.wokwi.com/vscode/getting-started)
- [项目配置](https://docs.wokwi.com/vscode/project-config)
- [许可证页面](https://wokwi.com/license)：当前注明个人 30 天许可证，开源项目免费，商业用途需购买许可；以实际账户权益为准。
- [离线模式](https://docs.wokwi.com/vscode/offline-mode)
- [支持硬件](https://docs.wokwi.com/getting-started/supported-hardware)
- [官方 Arduino Simon Game / PlatformIO 示例](https://github.com/wokwi/arduino-simon-game)：可作为独立接入参照，当前工程不需要替换成该例子。
- [CLI 安装说明](https://docs.wokwi.com/wokwi-ci/cli-installation)：官方推荐扩展用于本地开发，CLI 用于 CI；二者共享工程文件。
