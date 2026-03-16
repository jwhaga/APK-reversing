@echo off
chcp 65001 >nul
echo ========================================
echo APK 反编译工具 v2.0 - 环境检查
echo 纯 Python 实现 - 无需外部工具
echo ========================================
echo.

:: 检查 Python
echo [1/4] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] Python 未安装或未添加到 PATH
    echo     请安装 Python 3.8+ 并添加到 PATH
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [✓] Python 已安装：%PYTHON_VERSION%
)
echo.

:: 检查 pip
echo [2/4] 检查 pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [✗] pip 未安装或未添加到 PATH
) else (
    echo [✓] pip 已安装
)
echo.

:: 检查 Python 依赖
echo [3/4] 检查 Python 依赖...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [✗] PyQt5 未安装 - 运行 install.bat 安装
) else (
    echo [✓] PyQt5 已安装
)

python -c "import Crypto" >nul 2>&1
if errorlevel 1 (
    echo [✗] pycryptodome 未安装 - 运行 install.bat 安装
) else (
    echo [✓] pycryptodome 已安装
)
echo.

:: 总结
echo [4/4] 检查总结...
echo.

:: 检查是否需要安装
python -c "import PyQt5; import Crypto" >nul 2>&1
if errorlevel 1 (
    echo [!] 部分依赖未安装，请先运行 install.bat
) else (
    echo [✓] 所有依赖已就绪，可以运行 run.bat 启动程序
)
echo.

echo ========================================
echo 版本信息
echo ========================================
echo v2.0 特点:
echo   ✓ 纯 Python 实现
echo   ✓ 无需 Java 环境
echo   ✓ 无需 apktool/jadx
echo   ✓ 所有功能内置
echo.

pause
