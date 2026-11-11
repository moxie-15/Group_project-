@echo off
REM ==============================================================================
REM File: run_all.bat
REM Project: Group 9 — Smart Grid FDI Anomaly Engine (Vivado / FPGA)
REM Description: Windows One-Click Double-Click Demo Runner.
REM              Double-click this file in Windows Explorer to run the entire
REM              Python simulation, evaluation, and plotting pipeline!
REM ==============================================================================

title Group 9 - Smart Grid FDI Anomaly Engine Demo Runner
color 0A

echo ==============================================================================
echo        GROUP 9: SMART GRID FDI ANOMALY ENGINE (FPGA / VIVADO)
echo                   AUTOMATED ONE-CLICK DEMO RUNNER
echo ==============================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

echo [*] Launching Master Pipeline...
python run_all.py

echo.
echo ==============================================================================
echo [DONE] All datasets, models, metrics, and plots have been generated!
echo Check the 'results' folder for the 6 output PNG graphs.
echo ==============================================================================
echo.
pause
