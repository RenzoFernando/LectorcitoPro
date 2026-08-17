@echo off
setlocal EnableExtensions
chcp 65001 >nul
for %%I in ("%~dp0\..\..") do set "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%"
set "VENV_PYTHON=.venv-build\Scripts\python.exe"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "INSTALLER_SCRIPT=build\windows\installer\LectorcitoPro.iss"
set "STAGE_DIR=build\windows\installer\payload"
set "ISCC_CMD="

echo.
echo =======================================================
echo  Compilador de Instalador Windows
echo =======================================================

echo.

if not exist "%VENV_PYTHON%" (
    echo ERROR: No existe el entorno .venv-build. Ejecuta primero el setup.
    exit /b 1
)
set "PYTHON_CMD=%VENV_PYTHON%"
"%PYTHON_CMD%" --version

echo.

if not exist "build" mkdir "build"
if not exist "build\windows" mkdir "build\windows"
if not exist "build\windows\installer" mkdir "build\windows\installer"
if exist "%INSTALLER_SCRIPT%" del /q "%INSTALLER_SCRIPT%" > nul 2>&1
if exist "%STAGE_DIR%" rmdir /s /q "%STAGE_DIR%"
mkdir "%STAGE_DIR%"

call :read_meta APP_NAME app_meta.APP_NAME_INTERNAL
if errorlevel 1 goto :meta_error
call :read_meta APP_EXE_NAME app_meta.APP_EXECUTABLE_NAME
if errorlevel 1 goto :meta_error
call :read_meta ICON_FILE app_meta.APP_ICON_ICO_RELATIVE_PATH
if errorlevel 1 goto :meta_error
call :read_meta OUTPUT_FOLDER app_meta.APP_OUTPUT_DIR_NAME
if errorlevel 1 goto :meta_error
call :read_meta PRODUCT_NAME app_meta.APP_PRODUCT_NAME
if errorlevel 1 goto :meta_error
call :read_meta PRODUCT_VERSION app_meta.APP_PRODUCT_VERSION
if errorlevel 1 goto :meta_error
call :read_meta FILE_VERSION app_meta.APP_FILE_VERSION
if errorlevel 1 goto :meta_error
call :read_meta COMPANY_NAME app_meta.APP_COMPANY_NAME
if errorlevel 1 goto :meta_error
call :read_meta COPYRIGHT_TEXT app_meta.APP_LEGAL_COPYRIGHT
if errorlevel 1 goto :meta_error
call :read_meta FILE_DESCRIPTION app_meta.APP_FILE_DESCRIPTION
if errorlevel 1 goto :meta_error
call :read_meta INSTALLER_NAME app_meta.APP_INSTALLER_NAME
if errorlevel 1 goto :meta_error
call :read_meta INSTALLER_BASENAME app_meta.APP_INSTALLER_BASENAME
if errorlevel 1 goto :meta_error
call :read_meta PORTABLE_ARTIFACT_NAME app_meta.APP_PORTABLE_ARTIFACT_NAME
if errorlevel 1 goto :meta_error
call :read_meta LICENSE_FILE app_meta.APP_LICENSE_RELATIVE_PATH
if errorlevel 1 goto :meta_error
call :read_meta PUBLISHER_URL app_meta.APP_PUBLISHER_URL
if errorlevel 1 goto :meta_error
call :read_meta SUPPORT_URL app_meta.APP_SUPPORT_URL
if errorlevel 1 goto :meta_error
call :read_meta UPDATES_URL app_meta.APP_UPDATES_URL
if errorlevel 1 goto :meta_error
call :read_meta INSTALL_MARKER_FILE app_meta.APP_INSTALL_MARKER_FILE
if errorlevel 1 goto :meta_error

if not defined APP_NAME goto :meta_error
if not defined APP_EXE_NAME goto :meta_error
if not defined ICON_FILE goto :meta_error
if not defined OUTPUT_FOLDER goto :meta_error
if not defined PRODUCT_NAME goto :meta_error
if not defined PRODUCT_VERSION goto :meta_error
if not defined FILE_VERSION goto :meta_error
if not defined COMPANY_NAME goto :meta_error
if not defined COPYRIGHT_TEXT goto :meta_error
if not defined FILE_DESCRIPTION goto :meta_error
if not defined INSTALLER_NAME goto :meta_error
if not defined INSTALLER_BASENAME goto :meta_error
if not defined PORTABLE_ARTIFACT_NAME goto :meta_error
if not defined LICENSE_FILE goto :meta_error
if not defined PUBLISHER_URL goto :meta_error
if not defined SUPPORT_URL goto :meta_error
if not defined UPDATES_URL goto :meta_error
if not defined INSTALL_MARKER_FILE goto :meta_error

if not exist "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%" (
    echo ERROR: No existe "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%".
    echo El instalador utiliza el mismo binario portable ya firmado.
    goto :fail
)
if not exist "%LICENSE_FILE%" (
    echo ERROR: No existe "%LICENSE_FILE%".
    goto :fail
)

copy /y "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%" "%STAGE_DIR%\%APP_EXE_NAME%" > nul
if errorlevel 1 goto :fail
> "%STAGE_DIR%\%INSTALL_MARKER_FILE%" echo installed
copy /y "%LICENSE_FILE%" "%STAGE_DIR%\%LICENSE_FILE%" > nul
if errorlevel 1 goto :fail

call :resolve_iscc
if not defined ISCC_CMD (
    echo ERROR: No se encontro ISCC.exe de Inno Setup 6.
    echo Define ISCC_PATH o instala Inno Setup 6.
    goto :fail
)
if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"
if exist "%OUTPUT_FOLDER%\%INSTALLER_NAME%" del /q "%OUTPUT_FOLDER%\%INSTALLER_NAME%" > nul 2>&1

> "%INSTALLER_SCRIPT%" echo [Setup]
>> "%INSTALLER_SCRIPT%" echo SourceDir=%PROJECT_ROOT%
>> "%INSTALLER_SCRIPT%" echo AppId={{B9D7D8A0-8E70-4E8C-AB34-0A2C7965E5C1}
>> "%INSTALLER_SCRIPT%" echo AppName=%PRODUCT_NAME%
>> "%INSTALLER_SCRIPT%" echo AppVersion=%PRODUCT_VERSION%
>> "%INSTALLER_SCRIPT%" echo AppPublisher=%COMPANY_NAME%
>> "%INSTALLER_SCRIPT%" echo AppPublisherURL=%PUBLISHER_URL%
>> "%INSTALLER_SCRIPT%" echo AppSupportURL=%SUPPORT_URL%
>> "%INSTALLER_SCRIPT%" echo AppUpdatesURL=%UPDATES_URL%
>> "%INSTALLER_SCRIPT%" echo AppCopyright=%COPYRIGHT_TEXT%
>> "%INSTALLER_SCRIPT%" echo DefaultDirName={autopf}\%PRODUCT_NAME%
>> "%INSTALLER_SCRIPT%" echo DefaultGroupName=%PRODUCT_NAME%
>> "%INSTALLER_SCRIPT%" echo OutputDir=%OUTPUT_FOLDER%
>> "%INSTALLER_SCRIPT%" echo OutputBaseFilename=%INSTALLER_BASENAME%
>> "%INSTALLER_SCRIPT%" echo SetupIconFile=%ICON_FILE%
>> "%INSTALLER_SCRIPT%" echo UninstallDisplayIcon={app}\%APP_EXE_NAME%
>> "%INSTALLER_SCRIPT%" echo LicenseFile=%LICENSE_FILE%
>> "%INSTALLER_SCRIPT%" echo Compression=lzma
>> "%INSTALLER_SCRIPT%" echo SolidCompression=yes
>> "%INSTALLER_SCRIPT%" echo WizardStyle=modern
>> "%INSTALLER_SCRIPT%" echo PrivilegesRequired=admin
>> "%INSTALLER_SCRIPT%" echo ArchitecturesAllowed=x64compatible
>> "%INSTALLER_SCRIPT%" echo ArchitecturesInstallIn64BitMode=x64compatible
>> "%INSTALLER_SCRIPT%" echo VersionInfoCompany=%COMPANY_NAME%
>> "%INSTALLER_SCRIPT%" echo VersionInfoDescription=%FILE_DESCRIPTION%
>> "%INSTALLER_SCRIPT%" echo VersionInfoVersion=%PRODUCT_VERSION%
>> "%INSTALLER_SCRIPT%" echo VersionInfoProductName=%PRODUCT_NAME%
>> "%INSTALLER_SCRIPT%" echo VersionInfoProductVersion=%PRODUCT_VERSION%
>> "%INSTALLER_SCRIPT%" echo UsePreviousAppDir=yes
>> "%INSTALLER_SCRIPT%" echo UsePreviousTasks=yes
>> "%INSTALLER_SCRIPT%" echo DisableProgramGroupPage=yes
>> "%INSTALLER_SCRIPT%" echo.
>> "%INSTALLER_SCRIPT%" echo [Tasks]
>> "%INSTALLER_SCRIPT%" echo Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; GroupDescription: "Accesos directos:"
>> "%INSTALLER_SCRIPT%" echo.
>> "%INSTALLER_SCRIPT%" echo [Files]
>> "%INSTALLER_SCRIPT%" echo Source: "%STAGE_DIR%\%APP_EXE_NAME%"; DestDir: "{app}"; Flags: ignoreversion
>> "%INSTALLER_SCRIPT%" echo Source: "%STAGE_DIR%\%INSTALL_MARKER_FILE%"; DestDir: "{app}"; Flags: ignoreversion
>> "%INSTALLER_SCRIPT%" echo Source: "%STAGE_DIR%\%LICENSE_FILE%"; DestDir: "{app}"; Flags: ignoreversion
>> "%INSTALLER_SCRIPT%" echo.
>> "%INSTALLER_SCRIPT%" echo [InstallDelete]
>> "%INSTALLER_SCRIPT%" echo Type: files; Name: "{group}\Desinstalar %PRODUCT_NAME%"
>> "%INSTALLER_SCRIPT%" echo.
>> "%INSTALLER_SCRIPT%" echo [Icons]
>> "%INSTALLER_SCRIPT%" echo Name: "{autodesktop}\%PRODUCT_NAME%"; Filename: "{app}\%APP_EXE_NAME%"; WorkingDir: "{app}"; IconFilename: "{app}\%APP_EXE_NAME%"; Tasks: desktopicon
>> "%INSTALLER_SCRIPT%" echo Name: "{autoprograms}\%PRODUCT_NAME%"; Filename: "{app}\%APP_EXE_NAME%"; WorkingDir: "{app}"; IconFilename: "{app}\%APP_EXE_NAME%"
>> "%INSTALLER_SCRIPT%" echo.
>> "%INSTALLER_SCRIPT%" echo [Run]
>> "%INSTALLER_SCRIPT%" echo Filename: "{app}\%APP_EXE_NAME%"; Description: "Abrir %PRODUCT_NAME% ahora"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent unchecked runasoriginaluser

"%ISCC_CMD%" "%INSTALLER_SCRIPT%"
if errorlevel 1 goto :fail
if not exist "%OUTPUT_FOLDER%\%INSTALLER_NAME%" goto :fail

echo.
echo =======================================================
echo  Instalador generado correctamente!
echo =======================================================

echo.
echo %OUTPUT_FOLDER%\%INSTALLER_NAME%
call :cleanup
endlocal
exit /b 0

:read_meta
set "%~1="
set "META_VALUE_FILE=%TEMP%\LectorcitoPro_meta_%RANDOM%_%RANDOM%.tmp"
"%PYTHON_CMD%" -c "import os,sys; sys.path.insert(0, os.path.abspath('src')); import app_meta; print(%~2)" > "%META_VALUE_FILE%"
if errorlevel 1 (
    if exist "%META_VALUE_FILE%" del /q "%META_VALUE_FILE%" > nul 2>&1
    exit /b 1
)
set /p "%~1="<"%META_VALUE_FILE%"
del /q "%META_VALUE_FILE%" > nul 2>&1
if not defined %~1 exit /b 1
exit /b 0

:resolve_iscc
if defined ISCC_PATH if exist "%ISCC_PATH%" set "ISCC_CMD=%ISCC_PATH%"
if defined ISCC_CMD goto :eof
if defined INNO_SETUP_HOME if exist "%INNO_SETUP_HOME%\ISCC.exe" set "ISCC_CMD=%INNO_SETUP_HOME%\ISCC.exe"
if defined ISCC_CMD goto :eof
where ISCC.exe > nul 2>&1
if not errorlevel 1 set "ISCC_CMD=ISCC.exe"
if defined ISCC_CMD goto :eof
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if defined ISCC_CMD goto :eof
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if defined ISCC_CMD goto :eof
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if defined ISCC_CMD goto :eof
if exist "%PROJECT_ROOT%\tools\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%PROJECT_ROOT%\tools\Inno Setup 6\ISCC.exe"
goto :eof

:meta_error
echo ERROR: No se pudieron cargar los metadatos desde src\app_meta.py.
goto :fail

:cleanup
if exist "%INSTALLER_SCRIPT%" del /q "%INSTALLER_SCRIPT%" > nul 2>&1
if exist "%STAGE_DIR%" rmdir /s /q "%STAGE_DIR%"
goto :eof

:fail
call :cleanup
endlocal
exit /b 1

:: $env:ISCC_PATH="C:\Users\renzi\AppData\Local\Programs\Inno Setup 6\ISCC.exe"

:: Seleccionar CRLF - Windows (\r\n).
