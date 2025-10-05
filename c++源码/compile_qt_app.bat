@echo off

REM 编译Qt终端应用程序
set PRO_FILE=qt_terminal_app.pro

REM 创建输出目录
if not exist bin mkdir bin

REM 检查qmake是否可用
where qmake >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到qmake命令。
    echo 请确保已安装Qt，并将Qt的bin目录添加到系统PATH环境变量中。
    echo 例如：C:\Qt\Qt5.15.2\5.15.2\mingw81_64\bin
    echo 
    echo 如果尚未安装Qt，可以从以下网址下载：
    echo https://www.qt.io/download
    echo 安装时请选择MinGW编译器选项。
    pause
    exit /b 1
)

REM 运行qmake生成Makefile
qmake %PRO_FILE%

if %errorlevel% neq 0 (
    echo qmake执行失败！
    pause
    exit /b 1
)

REM 检查mingw32-make是否可用
where mingw32-make >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到mingw32-make命令。
    echo 请确保已安装MinGW，并将MinGW的bin目录添加到系统PATH环境变量中。
    echo 例如：C:\Qt\Qt5.15.2\Tools\mingw810_64\bin
    echo 
    echo 也可以尝试使用make命令（如果已安装）：
    echo make
    pause
    exit /b 1
)

REM 运行mingw32-make进行编译
mingw32-make

if %errorlevel% neq 0 (
    echo mingw32-make执行失败！
    pause
    exit /b 1
)

REM 编译成功
if exist bin\QtTerminalApp.exe (
    echo 编译成功！可执行文件位于：bin\QtTerminalApp.exe
) else (
    echo 编译过程完成，但未找到可执行文件。请检查输出日志。
)

pause