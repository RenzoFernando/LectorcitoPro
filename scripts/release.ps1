[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Utf8Encoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $Utf8Encoding
$OutputEncoding = $Utf8Encoding
[Environment]::ExitCode = 1
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogRoot = Join-Path $ProjectRoot "build\release_logs\$Timestamp"
New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null

function Write-LogLine {
    param([string]$Path, [string]$Text)
    [System.IO.File]::AppendAllText($Path, $Text + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}

function Invoke-LoggedStep {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$LogName
    )

    $LogPath = Join-Path $LogRoot $LogName
    $CommandText = $Executable + " " + ($Arguments -join " ")
    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host " $Name" -ForegroundColor Cyan
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-LogLine -Path $LogPath -Text "Stage: $Name"
    Write-LogLine -Path $LogPath -Text "Command: $CommandText"

    $PreviousErrorActionPreference = $ErrorActionPreference
    $ExitCode = 1
    try {
        $ErrorActionPreference = "Continue"
        & $Executable @Arguments 2>&1 | ForEach-Object {
            $Line = $_.ToString()
            Write-Host $Line
            Write-LogLine -Path $LogPath -Text $Line
        }
        $ExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    Write-LogLine -Path $LogPath -Text "Exit code: $ExitCode"
    if ($ExitCode -ne 0) {
        throw "$Name fallo con codigo $ExitCode. Comando: $CommandText. Log: $LogPath"
    }
}

function Get-AppMetadata {
    $Python = Join-Path $ProjectRoot ".venv-build\Scripts\python.exe"
    if (-not (Test-Path $Python -PathType Leaf)) {
        throw "No existe $Python."
    }

    $Command = "import json,os,sys; sys.path.insert(0, os.path.abspath('src')); import app_meta; print(json.dumps({'OutputFolder': app_meta.APP_OUTPUT_DIR_NAME, 'PortableName': app_meta.APP_PORTABLE_ARTIFACT_NAME, 'InstallerName': app_meta.APP_INSTALLER_NAME, 'LinuxName': app_meta.APP_LINUX_ARTIFACT_NAME, 'AppName': app_meta.APP_NAME_INTERNAL, 'AppExeName': app_meta.APP_EXECUTABLE_NAME, 'AppVersion': app_meta.APP_VERSION, 'WindowsVersion': app_meta.APP_FILE_VERSION}))"
    $PreviousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $Output = @(& $Python -c $Command 2>&1)
        $ExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    if ($ExitCode -ne 0) {
        $Details = ($Output | ForEach-Object { $_.ToString() }) -join " "
        throw "No se pudo leer metadata desde src\app_meta.py. $Details"
    }

    $JsonText = ($Output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
    if (-not $JsonText.Trim()) {
        throw "No se pudo leer metadata desde src\app_meta.py: salida vacia."
    }

    try {
        $Metadata = $JsonText | ConvertFrom-Json
    } catch {
        throw "No se pudo interpretar metadata desde src\app_meta.py: $($_.Exception.Message)"
    }

    foreach ($PropertyName in @(
        "OutputFolder",
        "PortableName",
        "InstallerName",
        "LinuxName",
        "AppName",
        "AppExeName",
        "AppVersion",
        "WindowsVersion"
    )) {
        $Property = $Metadata.PSObject.Properties[$PropertyName]
        if ($null -eq $Property -or $null -eq $Property.Value -or -not $Property.Value.ToString().Trim()) {
            throw "Metadata incompleta: $PropertyName"
        }
    }

    return $Metadata
}

function Assert-File {
    param([string]$Path, [string]$Label)

    if (-not (Test-Path $Path -PathType Leaf)) {
        throw "No se genero ${Label}: $Path"
    }
    if ((Get-Item $Path).Length -le 0) {
        throw "$Label existe pero esta vacio: $Path"
    }
}

function Assert-VersionInfo {
    param([string]$Path, [string]$ExpectedVersion, [string]$Label)

    $Info = (Get-Item $Path).VersionInfo
    $FileVersionText = [string]$Info.FileVersion
    $ProductVersionText = [string]$Info.ProductVersion
    $NormalizedFileVersion = (($FileVersionText -replace '[^0-9.]', '').Trim('.'))
    $NormalizedProductVersion = (($ProductVersionText -replace '[^0-9.]', '').Trim('.'))
    if ($NormalizedFileVersion -ne $ExpectedVersion -and $NormalizedProductVersion -ne $ExpectedVersion) {
        throw "Metadata de version incorrecta en ${Label}. Esperado: $ExpectedVersion. FileVersion: $($Info.FileVersion). ProductVersion: $($Info.ProductVersion)"
    }
}

try {
    Write-Host "Lectorcito Pro - Release integral" -ForegroundColor Cyan
    Write-Host "Proyecto: $ProjectRoot"
    Write-Host "Logs: $LogRoot"

    $RequiredFiles = @(
        "scripts\quality.bat",
        "scripts\windows\setup.bat",
        "scripts\windows\setup_node.ps1",
        "scripts\windows\build_portable.bat",
        "scripts\windows\build_installed_app.bat",
        "scripts\windows\build_installer.bat",
        "scripts\linux\setup.sh",
        "scripts\linux\build.sh",
        "scripts\linux\release.sh",
        "src\app_meta.py",
        "requirements.txt",
        "requirements\runtime.txt",
        "requirements\windows.txt",
        "requirements\linux.txt",
        "requirements\build.txt",
        "requirements\quality.txt",
        "package.json",
        "eslint.config.mjs",
        ".prettierrc.json",
        ".prettierignore",
        ".editorconfig",
        ".gitattributes",
        "pyproject.toml",
        "README.md",
        "index.html",
        "404.html",
        "robots.txt",
        "sitemap.xml",
        "llms.txt",
        "manifest.webmanifest",
        "scripts\seo_check.py",
        "LICENSE"
    )

    foreach ($RelativePath in $RequiredFiles) {
        $FullPath = Join-Path $ProjectRoot $RelativePath
        if (-not (Test-Path $FullPath -PathType Leaf)) {
            throw "Falta un archivo requerido: $RelativePath"
        }
    }

    if (Test-Path (Join-Path $ProjectRoot "scripts\windows\sign_application.ps1")) {
        throw "La infraestructura de autofirmado local sigue presente: scripts\windows\sign_application.ps1"
    }

    if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
        throw "WSL no esta instalado. El release integral necesita WSL para generar el binario Linux desde Windows."
    }

    $WslDistros = @(& wsl.exe -l -q 2>$null | ForEach-Object { ($_.ToString() -replace "\x00", "").Trim() } | Where-Object { $_ })
    if ($LASTEXITCODE -ne 0 -or $WslDistros.Count -eq 0) {
        throw "WSL esta disponible, pero no hay una distribucion Linux instalada."
    }

    $WslCandidates = @(
        $WslDistros | Where-Object { $_ -eq "Ubuntu-24.04" }
        $WslDistros | Where-Object { $_ -like "Ubuntu-24.04*" -and $_ -ne "Ubuntu-24.04" }
        $WslDistros | Where-Object { $_ -like "Ubuntu*" -and $_ -notlike "Ubuntu-24.04*" }
        $WslDistros | Where-Object { $_ -notlike "Ubuntu*" -and $_ -notlike "docker-desktop*" }
    )

    $WslDistro = $null
    foreach ($CandidateDistro in $WslCandidates) {
        $PreviousErrorActionPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = "Continue"
            & wsl.exe -d $CandidateDistro --exec python3 -c "import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 14) else 1)" 2>$null
            $CandidateExitCode = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $PreviousErrorActionPreference
        }
        if ($CandidateExitCode -eq 0) {
            $WslDistro = $CandidateDistro
            break
        }
    }

    if (-not $WslDistro) {
        throw "No se encontro una distribucion WSL con Python 3.11, 3.12 o 3.13."
    }

    $PreviousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $WslPathOutput = @(& wsl.exe -d $WslDistro --exec wslpath -u -a "$ProjectRoot" 2>&1)
        $WslPathExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    $WslProjectRoot = $WslPathOutput | Select-Object -First 1
    if ($WslPathExitCode -ne 0 -or -not $WslProjectRoot) {
        $WslPathError = ($WslPathOutput | ForEach-Object { $_.ToString() }) -join " "
        throw "No se pudo traducir la ruta del proyecto para WSL usando $WslDistro. $WslPathError"
    }

    $WslProjectRoot = ($WslProjectRoot.ToString() -replace "\x00", "").Trim()
    $WslProjectRootEscaped = $WslProjectRoot.Replace("'", "'\''")

    Invoke-LoggedStep -Name "01 Setup Windows" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\windows\setup.bat`"") -LogName "01-setup-windows.log"
    Invoke-LoggedStep -Name "02 Code quality autofix" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\quality.bat`" fix") -LogName "02-code-quality.log"
    Invoke-LoggedStep -Name "03 Quality validation" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\quality.bat`" check") -LogName "03-quality-validation.log"

    $Metadata = Get-AppMetadata
    $OutputFolder = $Metadata.OutputFolder.ToString().Trim()
    $PortableName = $Metadata.PortableName.ToString().Trim()
    $InstallerName = $Metadata.InstallerName.ToString().Trim()
    $LinuxName = $Metadata.LinuxName.ToString().Trim()
    $AppName = $Metadata.AppName.ToString().Trim()
    $AppExeName = $Metadata.AppExeName.ToString().Trim()
    $AppVersion = $Metadata.AppVersion.ToString().Trim()
    $WindowsVersion = $Metadata.WindowsVersion.ToString().Trim()
    $OutputPath = Join-Path $ProjectRoot $OutputFolder
    $PortablePath = Join-Path $OutputPath $PortableName
    $InstallerPath = Join-Path $OutputPath $InstallerName
    $LinuxPath = Join-Path $OutputPath $LinuxName
    $InstalledExePath = Join-Path $ProjectRoot "build\windows\installed-app\$AppName.dist\$AppExeName"

    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    foreach ($ArtifactPath in @($PortablePath, $InstallerPath, $LinuxPath)) {
        if (Test-Path $ArtifactPath -PathType Leaf) {
            Remove-Item -Path $ArtifactPath -Force
        }
    }

    Invoke-LoggedStep -Name "04 Build Windows Portable Onefile" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\windows\build_portable.bat`"") -LogName "04-build-portable.log"
    Assert-File -Path $PortablePath -Label "portable Windows"
    Assert-VersionInfo -Path $PortablePath -ExpectedVersion $WindowsVersion -Label "portable Windows"

    Invoke-LoggedStep -Name "05 Build Windows Installed App Standalone" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\windows\build_installed_app.bat`"") -LogName "05-build-installed-app.log"
    Assert-File -Path $InstalledExePath -Label "ejecutable Windows instalado"
    Assert-VersionInfo -Path $InstalledExePath -ExpectedVersion $WindowsVersion -Label "ejecutable Windows instalado"

    $PortableHash = (Get-FileHash -Algorithm SHA256 -Path $PortablePath).Hash
    $InstalledHash = (Get-FileHash -Algorithm SHA256 -Path $InstalledExePath).Hash
    if ($PortableHash -eq $InstalledHash) {
        throw "El ejecutable instalado y el Portable tienen el mismo SHA-256; los builds no son independientes."
    }

    Invoke-LoggedStep -Name "06 Build Windows Installer" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\windows\build_installer.bat`"") -LogName "06-build-installer.log"
    Assert-File -Path $InstallerPath -Label "instalador Windows"
    Assert-VersionInfo -Path $InstallerPath -ExpectedVersion $WindowsVersion -Label "instalador Windows"

    $LinuxSystemSetupCommand = "cd '$WslProjectRootEscaped' && LECTORCITO_SYSTEM_ONLY=1 bash scripts/linux/setup.sh"
    Invoke-LoggedStep -Name "07 Linux system setup" -Executable "wsl.exe" -Arguments @("-d", $WslDistro, "--user", "root", "--exec", "bash", "-lc", $LinuxSystemSetupCommand) -LogName "07-linux-system-setup.log"

    $LinuxCommand = "cd '$WslProjectRootEscaped' && LECTORCITO_SKIP_SYSTEM_PACKAGES=1 bash scripts/linux/release.sh"
    Invoke-LoggedStep -Name "08 Build Linux Portable Onefile" -Executable "wsl.exe" -Arguments @("-d", $WslDistro, "--exec", "bash", "-lc", $LinuxCommand) -LogName "08-linux-release.log"
    Assert-File -Path $LinuxPath -Label "portable Linux"

    $WindowsPython = (& (Join-Path $ProjectRoot ".venv-build\Scripts\python.exe") --version 2>&1 | Select-Object -First 1).ToString().Trim()
    $NuitkaVersion = (& (Join-Path $ProjectRoot ".venv-build\Scripts\python.exe") -m nuitka --version 2>&1 | Select-Object -First 1).ToString().Trim()
    $LinuxPython = (& wsl.exe -d $WslDistro --exec python3 --version 2>&1 | Select-Object -First 1).ToString().Trim()
    $InstallerHash = (Get-FileHash -Algorithm SHA256 -Path $InstallerPath).Hash
    $LinuxHash = (Get-FileHash -Algorithm SHA256 -Path $LinuxPath).Hash
    $SummaryPath = Join-Path $LogRoot "09-summary.log"
    $Summary = @(
        "Release completed",
        "Application version: $AppVersion",
        "Python Windows version: $WindowsPython",
        "Nuitka version: $NuitkaVersion",
        "Python Linux version: $LinuxPython",
        "Windows Portable path: $PortablePath",
        "Windows Portable SHA-256: $PortableHash",
        "Windows Installed App path: $InstalledExePath",
        "Windows Installed App SHA-256: $InstalledHash",
        "Windows Installer path: $InstallerPath",
        "Windows Installer SHA-256: $InstallerHash",
        "Linux Portable path: $LinuxPath",
        "Linux Portable SHA-256: $LinuxHash",
        "Logs directory: $LogRoot"
    )
    [System.IO.File]::WriteAllLines($SummaryPath, $Summary, [System.Text.UTF8Encoding]::new($false))
    $Summary | ForEach-Object { Write-Host $_ }

    foreach ($CompilePath in @(
        (Join-Path $ProjectRoot "build\windows"),
        (Join-Path $ProjectRoot "build\linux")
    )) {
        if (Test-Path $CompilePath -PathType Container) {
            Remove-Item -Path $CompilePath -Recurse -Force
        }
    }

    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host " RELEASE COMPLETADO" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host "Artefactos finales: $OutputPath"
    Write-Host "Logs conservados: $LogRoot"
    [Environment]::ExitCode = 0
    exit 0
} catch {
    $FailurePath = Join-Path $LogRoot "09-summary.log"
    $FailureLines = @(
        "RELEASE FALLIDO",
        "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "Error: $($_.Exception.Message)",
        "Logs directory: $LogRoot"
    )
    [System.IO.File]::WriteAllLines($FailurePath, $FailureLines, [System.Text.UTF8Encoding]::new($false))
    Write-Host ""
    Write-Host "RELEASE FALLIDO" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "Logs: $LogRoot" -ForegroundColor Yellow
    [Environment]::ExitCode = 1
    exit 1
}
