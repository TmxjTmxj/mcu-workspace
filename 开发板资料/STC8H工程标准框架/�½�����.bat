@echo off
title STC8工程一键生成
echo.    
echo 输入新工程名，会在当前路径下的samples文件夹下生成新的工程文件夹，文件夹名为：STC8_输入的工程名，可以拷贝该文件夹至其它目录）
echo.     
color a
set /p address=请输入工程名（请不要输入中文，keil对中文的支持不好，最好路径也是全英文的）:
cd samples
md "STC8_%address%"
cd "STC8_%address%"

md "User"
xcopy "..\..\User" "%cd%\User" /s/e

md "APP"
xcopy "..\..\APP" "%cd%\APP" /s/e

md "ChipDevices"
xcopy "..\..\ChipDevices" "%cd%\ChipDevices" /s/e

md "UserDevices"
xcopy "..\..\UserDevices" "%cd%\UserDevices" /s/e

md "ISR"
xcopy "..\..\ISR" "%cd%\ISR" /s/e

copy "..\..\STC8.uvproj"  "%cd%\STC8.uvproj"

copy "..\..\清理工程.bat" "%cd%\清理工程.bat"