@echo off
REM Bluejay3D Configurator Easy Launcher for Windows
title Bluejay3D Configurator
cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python launch_bluejay3d_configurator.py
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        py -3 launch_bluejay3d_configurator.py
    ) else (
        echo [ERROR] Python not found on PATH. Please install Python 3.
        pause
    )
)
