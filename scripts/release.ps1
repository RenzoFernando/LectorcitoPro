[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
[Environment]::ExitCode = 1
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

$RootTemporaryFiles = @(
    (Join-Path $ProjectRoot ".build_meta_export.py"),
    (Join-Path $ProjectRoot ".build_meta_export.cmd")
)

foreach ($TemporaryFile in $RootTemporaryFiles) {
    if (Test-Path $TemporaryFile -PathType Leaf) {
        Remove-Item -Path $TemporaryFile -Force
    }
}

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogRoot = Join-Path $ProjectRoot "build\release_logs\$Timestamp"
New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null

function Invoke-LoggedStep {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$LogName
    )

    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host " $Name" -ForegroundColor Cyan
    Write-Host "=======================================================" -ForegroundColor Cyan

    $LogPath = Join-Path $LogRoot $LogName
    $PreviousErrorActionPreference = $ErrorActionPreference
    $ExitCode = 1
    $Writer = [System.IO.StreamWriter]::new($LogPath, $false, [System.Text.UTF8Encoding]::new($false))

    try {
        $ErrorActionPreference = "Continue"
        & $Executable @Arguments 2>&1 | ForEach-Object {
            $Line = $_.ToString()
            Write-Host $Line
            $Writer.WriteLine($Line)
            $Writer.Flush()
        }
        $ExitCode = $LASTEXITCODE
    } finally {
        $Writer.Dispose()
        $ErrorActionPreference = $PreviousErrorActionPreference
    }

    if ($ExitCode -ne 0) {
        throw "$Name fallo con codigo $ExitCode. Log: $LogPath"
    }
}

function Get-AppMetaValue {
    param([string]$Expression)

    $Python = Join-Path $ProjectRoot ".venv-build\Scripts\python.exe"
    if (-not (Test-Path $Python)) {
        throw "No existe $Python."
    }

    $Command = "import os,sys; sys.path.insert(0, os.path.abspath('src')); import app_meta; print($Expression)"
    $Value = (& $Python -c $Command 2>$null | Select-Object -First 1)
    if (-not $Value) {
        throw "No se pudo leer metadata: $Expression"
    }

    return $Value.ToString().Trim()
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

Write-Host "Lectorcito Pro - Release integral" -ForegroundColor Cyan
Write-Host "Proyecto: $ProjectRoot"
Write-Host "Logs: $LogRoot"

$RequiredFiles = @(
    "scripts\windows\setup.bat",
    "scripts\windows\build_portable.bat",
    "scripts\windows\build_installer.bat",
    "scripts\windows\sign_application.ps1",
    "scripts\linux\setup.sh",
    "scripts\linux\build.sh",
    "scripts\linux\release.sh",
    "src\app_meta.py",
    "requirements.txt",
    "requirements\runtime.txt",
    "requirements\windows.txt",
    "requirements\linux.txt",
    "requirements\build.txt",
    "LICENSE"
)

foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $ProjectRoot $RelativePath
    if (-not (Test-Path $FullPath)) {
        throw "Falta un archivo requerido: $RelativePath"
    }
}

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw "WSL no esta instalado. El release integral necesita WSL para generar el unico binario Linux desde Windows."
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
    throw "No se encontro una distribucion WSL con Python 3.11, 3.12 o 3.13. Instala Ubuntu 24.04 LTS con: wsl.exe --install -d Ubuntu-24.04"
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

Invoke-LoggedStep -Name "1/7 Setup Windows" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\windows\setup.bat`"") -LogName "01-setup-windows.log"
Invoke-LoggedStep -Name "2/7 Build Windows Portable" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\windows\build_portable.bat`"") -LogName "02-build-portable.log"
Invoke-LoggedStep -Name "3/7 Firma Windows Portable" -Executable "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$ProjectRoot\scripts\windows\sign_application.ps1", "-Mode", "Portable") -LogName "03-sign-portable.log"
Invoke-LoggedStep -Name "4/7 Build Windows Installer" -Executable "cmd.exe" -Arguments @("/d", "/c", "`"$ProjectRoot\scripts\windows\build_installer.bat`"") -LogName "04-build-installer.log"
Invoke-LoggedStep -Name "5/7 Firma Windows Installer" -Executable "powershell.exe" -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$ProjectRoot\scripts\windows\sign_application.ps1", "-Mode", "Installer") -LogName "05-sign-installer.log"

$LinuxSystemSetupCommand = "cd '$WslProjectRootEscaped' && LECTORCITO_SYSTEM_ONLY=1 bash scripts/linux/setup.sh"
Invoke-LoggedStep -Name "6/7 Linux - Dependencias del sistema" -Executable "wsl.exe" -Arguments @("-d", $WslDistro, "--user", "root", "--exec", "bash", "-lc", $LinuxSystemSetupCommand) -LogName "06-linux-system-setup.log"

$LinuxCommand = "cd '$WslProjectRootEscaped' && LECTORCITO_SKIP_SYSTEM_PACKAGES=1 bash scripts/linux/release.sh"
Invoke-LoggedStep -Name "6/7 Build Linux Portable Onefile" -Executable "wsl.exe" -Arguments @("-d", $WslDistro, "--exec", "bash", "-lc", $LinuxCommand) -LogName "06-linux-release.log"

$OutputFolder = Get-AppMetaValue "app_meta.APP_OUTPUT_DIR_NAME"
$PortableName = Get-AppMetaValue "app_meta.APP_PORTABLE_ARTIFACT_NAME"
$InstallerName = Get-AppMetaValue "app_meta.APP_INSTALLER_NAME"
$LinuxName = Get-AppMetaValue "app_meta.APP_LINUX_ARTIFACT_NAME"
$OutputPath = Join-Path $ProjectRoot $OutputFolder
$PortablePath = Join-Path $OutputPath $PortableName
$InstallerPath = Join-Path $OutputPath $InstallerName
$LinuxPath = Join-Path $OutputPath $LinuxName

Assert-File -Path $PortablePath -Label "portable Windows"
Assert-File -Path $InstallerPath -Label "instalador Windows"
Assert-File -Path $LinuxPath -Label "portable Linux"

$PortableSignature = Get-AuthenticodeSignature -FilePath $PortablePath
$InstallerSignature = Get-AuthenticodeSignature -FilePath $InstallerPath

if ($PortableSignature.Status -ne "Valid") {
    throw "La firma del portable Windows no es valida: $($PortableSignature.Status)"
}

if ($InstallerSignature.Status -ne "Valid") {
    throw "La firma del instalador Windows no es valida: $($InstallerSignature.Status)"
}

$SummaryPath = Join-Path $LogRoot "07-summary.log"
$Summary = @(
    "Release completado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "Windows portable: $PortablePath",
    "SHA256: $((Get-FileHash -Algorithm SHA256 -Path $PortablePath).Hash)",
    "Windows installer: $InstallerPath",
    "SHA256: $((Get-FileHash -Algorithm SHA256 -Path $InstallerPath).Hash)",
    "Linux portable: $LinuxPath",
    "SHA256: $((Get-FileHash -Algorithm SHA256 -Path $LinuxPath).Hash)",
    "Logs: $LogRoot"
)

$Summary | Tee-Object -FilePath $SummaryPath

foreach ($TemporaryFile in $RootTemporaryFiles) {
    if (Test-Path $TemporaryFile -PathType Leaf) {
        Remove-Item -Path $TemporaryFile -Force
    }
}

$BuildPath = Join-Path $ProjectRoot "build"
if (Test-Path $BuildPath -PathType Container) {
    Remove-Item -Path $BuildPath -Recurse -Force
}

foreach ($TemporaryFile in $RootTemporaryFiles) {
    if (Test-Path $TemporaryFile) {
        throw "No se pudo eliminar el archivo temporal: $TemporaryFile"
    }
}

if (Test-Path $BuildPath) {
    throw "No se pudo eliminar la carpeta temporal de build: $BuildPath"
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host " 7/7 RELEASE COMPLETADO" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "Los tres artefactos estan en: $OutputPath"
Write-Host "Limpieza final completada: build y temporales eliminados."
[Environment]::ExitCode = 0
exit 0
