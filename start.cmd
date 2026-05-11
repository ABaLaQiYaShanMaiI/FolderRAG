@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =============================================
echo  FolderKnowledgeSiteGeneratorForAI - 文档知识门户生成器
echo  Loading...
echo =============================================
echo.
python gui.py
if errorlevel 1 (
    echo.
    echo [Error] Failed to start GUI.
    echo Make sure Python is installed.
    echo Run: pip install -r requirements.txt
    echo.
    pause
)