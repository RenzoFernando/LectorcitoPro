@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "ENTRY_POINT=src/main.py"
set "VENV_PYTHON=.venv\Scripts\python.exe"
set "META_EXPORT_SCRIPT=.build_meta_export.py"
set "META_EXPORT_CMD=.build_meta_export.cmd"
set "INSTALLER_SCRIPT=.build_installer.iss"
set "STAGE_DIR=build\installer_payload"
set "ISCC_CMD="

echo.
echo =======================================================
echo  Compilador de Instalador Windows
echo =======================================================
echo.

if exist "%VENV_PYTHON%" (
    echo [INFO] Entorno virtual detectado. Usando Python 3.11 desde .venv
    set "PYTHON_CMD=%VENV_PYTHON%"
) else (
    echo [WARN] No se detecto .venv. Usando Python del sistema - riesgo de error.
    set "PYTHON_CMD=python"
)

echo Version detectada:
"%PYTHON_CMD%" --version
echo.

if exist "%META_EXPORT_SCRIPT%" del /q "%META_EXPORT_SCRIPT%" > nul 2>&1
if exist "%META_EXPORT_CMD%" del /q "%META_EXPORT_CMD%" > nul 2>&1
if exist "%INSTALLER_SCRIPT%" del /q "%INSTALLER_SCRIPT%" > nul 2>&1

type nul > "%META_EXPORT_CMD%"

call :append_meta_line APP_NAME app_meta.APP_NAME_INTERNAL
if errorlevel 1 goto :meta_error
call :append_meta_line APP_EXE_NAME app_meta.APP_EXECUTABLE_NAME
if errorlevel 1 goto :meta_error
call :append_meta_line ICON_FILE app_meta.APP_ICON_ICO_RELATIVE_PATH
if errorlevel 1 goto :meta_error
call :append_meta_line RESOURCES_FOLDER app_meta.APP_RESOURCES_DIR_NAME
if errorlevel 1 goto :meta_error
call :append_meta_line OUTPUT_FOLDER app_meta.APP_OUTPUT_DIR_NAME
if errorlevel 1 goto :meta_error
call :append_meta_line PRODUCT_NAME app_meta.APP_PRODUCT_NAME
if errorlevel 1 goto :meta_error
call :append_meta_line FILE_DESCRIPTION app_meta.APP_FILE_DESCRIPTION
if errorlevel 1 goto :meta_error
call :append_meta_line PRODUCT_VERSION app_meta.APP_PRODUCT_VERSION
if errorlevel 1 goto :meta_error
call :append_meta_line FILE_VERSION app_meta.APP_FILE_VERSION
if errorlevel 1 goto :meta_error
call :append_meta_line COMPANY_NAME app_meta.APP_COMPANY_NAME
if errorlevel 1 goto :meta_error
call :append_meta_line COPYRIGHT_TEXT app_meta.APP_LEGAL_COPYRIGHT
if errorlevel 1 goto :meta_error
call :append_meta_line TRADEMARK_TEXT app_meta.APP_TRADEMARK
if errorlevel 1 goto :meta_error
call :append_meta_line INSTALLER_NAME app_meta.APP_INSTALLER_NAME
if errorlevel 1 goto :meta_error
call :append_meta_line INSTALLER_BASENAME app_meta.APP_INSTALLER_BASENAME
if errorlevel 1 goto :meta_error
call :append_meta_line LICENSE_FILE app_meta.APP_LICENSE_RELATIVE_PATH
if errorlevel 1 goto :meta_error
call :append_meta_line PUBLISHER_URL app_meta.APP_PUBLISHER_URL
if errorlevel 1 goto :meta_error
call :append_meta_line SUPPORT_URL app_meta.APP_SUPPORT_URL
if errorlevel 1 goto :meta_error
call :append_meta_line UPDATES_URL app_meta.APP_UPDATES_URL
if errorlevel 1 goto :meta_error
call :append_meta_line INSTALL_MARKER_FILE app_meta.APP_INSTALL_MARKER_FILE
if errorlevel 1 goto :meta_error

call "%META_EXPORT_CMD%"
if errorlevel 1 goto :meta_error

if not defined APP_NAME goto :meta_error
if not defined APP_EXE_NAME goto :meta_error
if not defined ICON_FILE goto :meta_error
if not defined RESOURCES_FOLDER goto :meta_error
if not defined OUTPUT_FOLDER goto :meta_error
if not defined PRODUCT_NAME goto :meta_error
if not defined FILE_DESCRIPTION goto :meta_error
if not defined PRODUCT_VERSION goto :meta_error
if not defined FILE_VERSION goto :meta_error
if not defined COMPANY_NAME goto :meta_error
if not defined COPYRIGHT_TEXT goto :meta_error
if not defined TRADEMARK_TEXT goto :meta_error
if not defined INSTALLER_NAME goto :meta_error
if not defined INSTALLER_BASENAME goto :meta_error
if not defined LICENSE_FILE goto :meta_error
if not defined PUBLISHER_URL goto :meta_error
if not defined SUPPORT_URL goto :meta_error
if not defined UPDATES_URL goto :meta_error
if not defined INSTALL_MARKER_FILE goto :meta_error

if not exist "%LICENSE_FILE%" (
    echo.
    echo ******************************************************
    echo * ERROR: No se encontro el archivo de licencia.      *
    echo * Falta: %LICENSE_FILE%                              *
    echo ******************************************************
    goto :fail
)

echo Metadatos detectados:
echo [APP] %APP_NAME%
echo [EXE] %APP_EXE_NAME%
echo [ICON] %ICON_FILE%
echo [RESOURCES] %RESOURCES_FOLDER%
echo [OUTPUT] %OUTPUT_FOLDER%
echo [PRODUCT] %PRODUCT_NAME%
echo [DESCRIPTION] %FILE_DESCRIPTION%
echo [PRODUCT VERSION] %PRODUCT_VERSION%
echo [FILE VERSION] %FILE_VERSION%
echo [COMPANY] %COMPANY_NAME%
echo [COPYRIGHT] %COPYRIGHT_TEXT%
echo [TRADEMARK] %TRADEMARK_TEXT%
echo [INSTALLER] %INSTALLER_NAME%
echo [LICENSE] %LICENSE_FILE%
echo [PUBLISHER URL] %PUBLISHER_URL%
echo [SUPPORT URL] %SUPPORT_URL%
echo [UPDATES URL] %UPDATES_URL%
echo.

echo Instalando/Verificando Nuitka y dependencias...
"%PYTHON_CMD%" -m pip install -r requirements.txt --default-timeout=100 > nul
echo.

echo Limpiando artefactos anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "%APP_NAME%.dist" rmdir /s /q "%APP_NAME%.dist"
if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"
if exist "%OUTPUT_FOLDER%\%INSTALLER_NAME%" del /q "%OUTPUT_FOLDER%\%INSTALLER_NAME%" > nul 2>&1
echo Limpieza completada.
echo.

echo =======================================================
echo  Generando ejecutable base para instalador...
echo =======================================================
echo.

"%PYTHON_CMD%" -m nuitka --onefile --standalone --output-filename="%APP_EXE_NAME%" --windows-icon-from-ico="%ICON_FILE%" --windows-console-mode=disable --windows-company-name="%COMPANY_NAME%" --product-name="%PRODUCT_NAME%" --file-description="%FILE_DESCRIPTION%" --file-version="%FILE_VERSION%" --product-version="%PRODUCT_VERSION%" --copyright="%COPYRIGHT_TEXT%" --trademark="%TRADEMARK_TEXT%" --enable-plugin=tk-inter --include-package=customtkinter --include-data-dir="%RESOURCES_FOLDER%=%RESOURCES_FOLDER%" --output-dir=dist --remove-output "%ENTRY_POINT%"

if %errorlevel% neq 0 (
    echo.
    echo ******************************************************
    echo * ERROR: La compilacion base del instalador fallo.   *
    echo ******************************************************
    goto :fail
)

if not exist "%STAGE_DIR%" mkdir "%STAGE_DIR%"
move "dist\%APP_EXE_NAME%" "%STAGE_DIR%\%APP_EXE_NAME%" > nul
> "%STAGE_DIR%\%INSTALL_MARKER_FILE%" echo installed

if %errorlevel% neq 0 (
    echo.
    echo ******************************************************
    echo * ERROR: No se pudo preparar el payload del          *
    echo * instalador.                                        *
    echo ******************************************************
    goto :fail
)

call :resolve_iscc
if not defined ISCC_CMD (
    echo.
    echo ******************************************************
    echo * ERROR: No se encontro ISCC.exe de Inno Setup 6.    *
    echo * Instala Inno Setup 6 o define ISCC_PATH antes      *
    echo * de ejecutar este script.                           *
    echo *                                                    *
    echo * Ejemplo:                                           *
    echo * set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe" *
    echo * .\buildinstaller.bat                               *
    echo ******************************************************
    goto :fail
)

echo [INFO] ISCC detectado en:
echo        %ISCC_CMD%
echo.

> "%INSTALLER_SCRIPT%" echo [Setup]
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
>> "%INSTALLER_SCRIPT%" echo Source: "%LICENSE_FILE%"; DestDir: "{app}"; Flags: ignoreversion
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
>> "%INSTALLER_SCRIPT%" echo.
>> "%INSTALLER_SCRIPT%" echo [Code]
>> "%INSTALLER_SCRIPT%" echo procedure CurPageChanged^(CurPageID: Integer^);
>> "%INSTALLER_SCRIPT%" echo begin
>> "%INSTALLER_SCRIPT%" echo   if CurPageID = wpFinished then
>> "%INSTALLER_SCRIPT%" echo   begin
>> "%INSTALLER_SCRIPT%" echo     WizardForm.FinishedLabel.Caption :=
>> "%INSTALLER_SCRIPT%" echo       WizardForm.FinishedLabel.Caption + #13#10 + #13#10 +
>> "%INSTALLER_SCRIPT%" echo       'Ruta instalada:' + #13#10 +
>> "%INSTALLER_SCRIPT%" echo       ExpandConstant^('{app}'^);
>> "%INSTALLER_SCRIPT%" echo   end;
>> "%INSTALLER_SCRIPT%" echo end;

echo.
echo =======================================================
echo  Generando instalador nativo...
echo =======================================================
echo.

"%ISCC_CMD%" "%INSTALLER_SCRIPT%"
if %errorlevel% neq 0 (
    echo.
    echo ******************************************************
    echo * ERROR: La generacion del instalador fallo.         *
    echo ******************************************************
    goto :fail
)

echo.
echo =======================================================
echo  Instalador generado correctamente!
echo =======================================================
echo.
echo El archivo %INSTALLER_NAME% esta listo en la carpeta '%OUTPUT_FOLDER%'.
echo.

goto :cleanup_success

:append_meta_line
>> "%META_EXPORT_CMD%" "%PYTHON_CMD%" -c "import os,sys; sys.path.insert(0, os.path.abspath('src')); import app_meta; value=str(%2).replace(chr(34), ''); print('set \"%1={}\"'.format(value))"
exit /b %errorlevel%

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

if exist "%cd%\tools\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%cd%\tools\Inno Setup 6\ISCC.exe"
goto :eof

:meta_error
echo.
echo ******************************************************
echo * ERROR: No se pudieron cargar los metadatos desde   *
echo * 'src\app_meta.py'.                                 *
echo ******************************************************
goto :fail

:cleanup_success
if exist "dist" rmdir /s /q dist
if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"
if exist "%STAGE_DIR%" rmdir /s /q "%STAGE_DIR%"
if exist "%INSTALLER_SCRIPT%" del /q "%INSTALLER_SCRIPT%" > nul 2>&1
if exist "%META_EXPORT_SCRIPT%" del /q "%META_EXPORT_SCRIPT%" > nul 2>&1
if exist "%META_EXPORT_CMD%" del /q "%META_EXPORT_CMD%" > nul 2>&1
pause
endlocal
goto :eof

:fail
if exist "dist" rmdir /s /q dist
if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"
if exist "%STAGE_DIR%" rmdir /s /q "%STAGE_DIR%"
if exist "%INSTALLER_SCRIPT%" del /q "%INSTALLER_SCRIPT%" > nul 2>&1
if exist "%META_EXPORT_SCRIPT%" del /q "%META_EXPORT_SCRIPT%" > nul 2>&1
if exist "%META_EXPORT_CMD%" del /q "%META_EXPORT_CMD%" > nul 2>&1
pause
exit /b 1

:: $env:ISCC_PATH="C:\Users\renzi\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
:: Seleccionar CRLF - Windows (\r\n).