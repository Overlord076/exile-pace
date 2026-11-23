@echo off
chcp 65001 >nul
title Установка ExilePace

echo ==================================================
echo   Установка PoE Heist ^& PoE 2 Tracker для Windows
echo ==================================================
echo.

:: 1. Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/3] Python не найден. Устанавливаем через winget...
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo Ошибка автоматической установки Python.
        echo Скачайте и установите Python вручную с https://python.org
        echo Обязательно отметьте галочку "Add Python to PATH" при установке!
        pause
        exit /b 1
    )
    echo Python установлен! Перезапустите этот файл install_windows.bat для завершения настройки.
    pause
    exit /b 0
) else (
    echo [1/3] Python найден.
)

:: 2. Копирование файлов в %LOCALAPPDATA%\ExilePace
set "INSTALL_DIR=%LOCALAPPDATA%\ExilePace"
echo [2/3] Копируем файлы в "%INSTALL_DIR%"...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /Y "%~dp0heist_stats.py" "%INSTALL_DIR%\heist_stats.py" >nul
copy /Y "%~dp0icon.png" "%INSTALL_DIR%\icon.png" >nul
python -m pip install --quiet pystray pillow

:: 3. Создание ярлыков на Рабочем столе через PowerShell
echo [3/3] Создаем ярлыки на Рабочем столе...
for /f "delims=" %%p in ('where pythonw') do set "PYTHONW_PATH=%%p" & goto :found_pw
:found_pw

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$desk = [Environment]::GetFolderPath('Desktop'); " ^
  "$s1 = $ws.CreateShortcut(\"$desk\PoE 1 Heist Overlay.lnk\"); " ^
  "$s1.TargetPath = '%PYTHONW_PATH%'; " ^
  "$s1.Arguments = '\"%INSTALL_DIR%\heist_stats.py\" today --overlay'; " ^
  "$s1.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s1.IconLocation = 'shell32.dll,13'; " ^
  "$s1.Save(); " ^
  "$s2 = $ws.CreateShortcut(\"$desk\PoE 2 Tracker Overlay.lnk\"); " ^
  "$s2.TargetPath = '%PYTHONW_PATH%'; " ^
  "$s2.Arguments = '\"%INSTALL_DIR%\heist_stats.py\" --poe2 today --overlay'; " ^
  "$s2.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s2.IconLocation = 'shell32.dll,13'; " ^
  "$s2.Save();"

echo.
echo ==================================================
echo   Установка успешно завершена!
echo   На Рабочем столе созданы ярлыки запуска.
echo ==================================================
pause
