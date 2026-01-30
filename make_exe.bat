@echo off
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
if not "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR%\"
set "OUTPUT_DIR=%SCRIPT_DIR%out"

echo 步骤1:开始编译...
python -m nuitka ^
--mingw64 --standalone --onefile ^
--output-dir=%OUTPUT_DIR% ^
--plugin-enable=pyqt5 ^
--plugin-enable=pylint-warnings ^
--windows-icon-from-ico=%SCRIPT_DIR%cat.ico ^
--output-filename=LotteryAssist ^
--jobs=8 --lto=yes --prefer-source-code ^
--windows-console-mode=disable --remove-output %SCRIPT_DIR%app.py

if %errorlevel% neq 0 (
    echo 编译失败，退出码: %errorlevel%
    pause >nul
    exit /b %errorlevel%
)

echo 步骤2:复制资源文件...
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
xcopy /Y /Q "%SCRIPT_DIR%cat.ico" "%OUTPUT_DIR%\" >nul
xcopy /Y /Q "%SCRIPT_DIR%style.qss" "%OUTPUT_DIR%\" >nul
echo 复制完成！

if exist "%OUTPUT_DIR%\LotteryAssist.exe" (
    echo 打包成功！文件位置: %OUTPUT_DIR%\LotteryAssist.exe
) else (
    echo 警告: 未找到生成的 exe 文件
)

echo 按任意键退出...
pause >nul
