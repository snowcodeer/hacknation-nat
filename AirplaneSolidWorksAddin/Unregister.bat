@echo off
echo ========================================
echo   SolidWorks Add-in Unregistration
echo ========================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Get the script directory
set SCRIPT_DIR=%~dp0

REM Find the DLL
set DLL_PATH=%SCRIPT_DIR%bin\Debug\net48\AirplaneSolidWorksAddin.dll

if not exist "%DLL_PATH%" (
    set DLL_PATH=%SCRIPT_DIR%bin\Release\net48\AirplaneSolidWorksAddin.dll
)

if not exist "%DLL_PATH%" (
    echo ERROR: Could not find AirplaneSolidWorksAddin.dll
    pause
    exit /b 1
)

echo Found DLL at: %DLL_PATH%
echo.

REM Unregister the assembly
echo Unregistering add-in...
"%SystemRoot%\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe" /u "%DLL_PATH%"

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   Unregistration Successful!
    echo ========================================
    echo.
    echo The add-in has been removed from SolidWorks.
    echo.
) else (
    echo.
    echo ERROR: Unregistration failed!
    echo.
)

pause
