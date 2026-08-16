@echo off
setlocal EnableExtensions
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\release.ps1"
set "RELEASE_EXIT=%ERRORLEVEL%"

echo.
if not "%RELEASE_EXIT%"=="0" (
    echo =======================================================
    echo  RELEASE FALLIDO
    echo =======================================================
    echo Revisa la carpeta build\release_logs para identificar la etapa.
    pause
    exit /b %RELEASE_EXIT%
)

echo =======================================================
echo  RELEASE COMPLETADO CORRECTAMENTE
echo =======================================================
echo Los artefactos finales estan en downloads.
pause
exit /b 0
