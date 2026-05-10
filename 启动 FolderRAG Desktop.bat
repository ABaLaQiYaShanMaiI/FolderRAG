@echo off
title FolderRAG Desktop 🚀

echo ============================================
echo   FolderRAG Desktop — 文件夹知识导出工具
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到 Python，请先安装 Python 3.8+
    echo    下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo [✓] 检测到虚拟环境
    call venv\Scripts\activate
) else (
    echo [⋯] 正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    call venv\Scripts\activate
    
    echo [⋯] 正在安装依赖（首次运行需要等待）...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo ⚠️ 部分依赖安装可能失败，继续尝试启动...
    ) else (
        echo [✓] 依赖安装完成
    )
)

echo.
echo [✓] 正在启动 FolderRAG Desktop...
echo.

:: Launch the GUI
python gui.py

:: Keep window open if error
if %errorlevel% neq 0 (
    echo.
    echo ❌ 程序异常退出，错误代码：%errorlevel%
    pause
)

:: Deactivate venv
call venv\Scripts\deactivate.bat >nul 2>&1
