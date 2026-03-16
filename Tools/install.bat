@echo off
chcp 65001 >nul
echo ========================================
echo APK 反编译工具 v2.0 - 安装脚本
echo 纯 Python 实现 - 无需外部工具
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python 版本检查通过
python --version
echo.

:: 安装 Python 依赖
echo [信息] 安装 Python 依赖...
echo 正在安装 PyQt5 (图形界面库)...
pip install PyQt5 -q

echo 正在安装 pycryptodome (加密库)...
pip install pycryptodome -q

if errorlevel 1 (
    echo [警告] 部分依赖安装失败，请检查网络连接
) else (
    echo [成功] Python 依赖安装完成
)

echo.
echo ========================================
echo 安装完成!
echo ========================================
echo.
echo 特点:
echo   ✓ 纯 Python 实现
echo   ✓ 无需下载 apktool/jadx
echo   ✓ 无需 Java 环境
echo   ✓ 所有功能内置
echo.
echo 使用方法:
echo   双击运行：run.bat
echo   或手动运行：python gui_standalone.py
echo.
pause
