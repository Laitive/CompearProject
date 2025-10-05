@echo off

REM 编译配置读取器
set SOURCE_FILE=config_reader_cpp.cpp
set OUTPUT_FILE=bin\config_reader_cpp.exe

REM 创建输出目录
if not exist bin mkdir bin

REM 使用g++编译（需要已安装MinGW）
g++ -std=c++17 %SOURCE_FILE% -o %OUTPUT_FILE%

REM 检查编译结果
if %errorlevel% equ 0 (
    echo 编译成功！可执行文件位于：%OUTPUT_FILE%
) else (
    echo 编译失败！请检查是否已安装MinGW，并确保g++命令可用。
    echo 如果未安装MinGW，可以从以下网址下载：https://sourceforge.net/projects/mingw-w64/
    pause
)