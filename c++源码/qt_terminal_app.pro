QT += core gui widgets

TARGET = QtTerminalApp
TEMPLATE = app

SOURCES += \
    qt_terminal_app.cpp

HEADERS +=

# 指定输出目录
DESTDIR = ./bin

# 配置编译选项
CONFIG += c++11

# Windows平台特定配置
win32 {
    # 设置应用程序图标（如果有）
    # RC_ICONS = app_icon.ico
    
    # 避免控制台窗口弹出（如果需要）
    # CONFIG -= console
}