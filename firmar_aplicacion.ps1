<#
.SYNOPSIS
    Script de autofirmado nativo para LectorcitoPro.
    No requiere Windows SDK ni signtool.exe.

.DESCRIPTION
    1. Genera un certificado Autofirmado temporal.
    2. Firma el EXE generado por build.bat.
    3. Elimina la necesidad de instalar herramientas externas.

.INSTRUCCIONES SI FALLA POR PERMISOS:
    Si ves un error rojo de "UnauthorizedAccess" o "signing script",
    copia y pega este comando en la terminal antes de ejecutar el script:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
#>

function Get-PythonCommand {
    $venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        return $venvPython
    }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }
    return "python"
}

function Get-AppMetaValue([string]$Expression, [string]$DefaultValue) {
    try {
        $python = Get-PythonCommand
        $command = "import os,sys; sys.path.insert(0, os.path.abspath('src')); import app_meta; print($Expression)"
        $value = (& $python -c $command 2>$null | Select-Object -First 1)
        if ($null -ne $value) {
            $trimmed = $value.ToString().Trim()
            if ($trimmed) {
                return $trimmed
            }
        }
    } catch {
    }
    return $DefaultValue
}

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   FIRMA DIGITAL NATIVA (PowerShell)    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# 1. CONFIGURACION DE RUTAS
# -----------------------------------------------------------------------------
$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $PSScriptRoot

$CarpetaSalidaName = Get-AppMetaValue "app_meta.APP_OUTPUT_DIR_NAME" "downloads"
$NombreExe = Get-AppMetaValue "app_meta.APP_EXECUTABLE_NAME" "LectorcitoPro.exe"
$CarpetaCertName = Get-AppMetaValue "app_meta.APP_CERT_DIR_NAME" "certificate_resources"
$AppNameInternal = Get-AppMetaValue "app_meta.APP_NAME_INTERNAL" "LectorcitoPro"
$PublisherName = Get-AppMetaValue "app_meta.APP_PUBLISHER_NAME" "Renzo Fernando Mosquera Daza"
$FriendlySignerName = Get-AppMetaValue "app_meta.APP_SIGNATURE_FRIENDLY_NAME" "Lectorcito Pro Code Signing"

$CarpetaSalida = Join-Path -Path $PSScriptRoot $CarpetaSalidaName
$RutaExe = Join-Path -Path $CarpetaSalida $NombreExe

# Configuración del Certificado
$CarpetaCert = Join-Path -Path $PSScriptRoot $CarpetaCertName
$NombreCert = "${AppNameInternal}_Key.pfx"
$RutaCert = Join-Path -Path $CarpetaCert $NombreCert
$PasswordCert = "Lectorcito123"
$SujetoCert = "CN=$PublisherName"

# -----------------------------------------------------------------------------
# 2. VERIFICACIONES
# -----------------------------------------------------------------------------

# Verificar que existe el EXE
if (-not (Test-Path -Path $RutaExe)) {
    Write-Host "[ERROR] No se encuentra el archivo: $RutaExe" -ForegroundColor Red
    Write-Host "Primero ejecuta 'build.bat' para compilar."
    Read-Host "Presiona Enter para salir"
    exit
}

# Crear carpeta de recursos si no existe
if (-not (Test-Path -Path $CarpetaCert)) {
    New-Item -ItemType Directory -Force -Path $CarpetaCert | Out-Null
}

# -----------------------------------------------------------------------------
# 3. GESTION DEL CERTIFICADO (CREAR O CARGAR)
# -----------------------------------------------------------------------------
$CertificadoObj = $null

if (Test-Path -Path $RutaCert) {
    Write-Host "[INFO] Certificado existente encontrado." -ForegroundColor Yellow
    try {
        $CertificadoObj = Get-PfxCertificate -FilePath $RutaCert
    } catch {
        Write-Host "[ERROR] El certificado existe pero no se pudo cargar. Puede estar dañado." -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] Creando nuevo certificado autofirmado..." -ForegroundColor Green

    $CertTemp = New-SelfSignedCertificate -Type CodeSigningCert `
                                          -Subject $SujetoCert `
                                          -CertStoreLocation "Cert:\CurrentUser\My" `
                                          -NotAfter (Get-Date).AddYears(5) `
                                          -FriendlyName $FriendlySignerName

    $PasswordSecure = ConvertTo-SecureString -String $PasswordCert -Force -AsPlainText
    Export-PfxCertificate -Cert $CertTemp -FilePath $RutaCert -Password $PasswordSecure
    
    $CertificadoObj = $CertTemp
    Write-Host "   -> Certificado creado en: $RutaCert" -ForegroundColor Gray
}

if (-not $CertificadoObj) {
    Write-Host "[FATAL] No se pudo obtener un objeto de certificado válido." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit
}

# -----------------------------------------------------------------------------
# 4. FIRMADO DIGITAL
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "[PROCESO] Firmando '$NombreExe'..." -ForegroundColor Cyan

# Intentamos firmar con Timestamp (para que la firma no caduque cuando el cert expire)
# Usamos un servidor de timestamp público (DigiCert)
$TimestampUrl = "http://timestamp.digicert.com"

try {
    Set-AuthenticodeSignature -FilePath $RutaExe `
                              -Certificate $CertificadoObj `
                              -TimestampServer $TimestampUrl `
                              -HashAlgorithm SHA256
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   EXITO: APLICACION FIRMADA CORRECTAMENTE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Archivo: $RutaExe"
    Write-Host "Estado:  Firmado Digitalmente (Self-Signed)"
    Write-Host "Nota:    Al ser autofirmado, Windows SmartScreen aun podria"
    Write-Host "         mostrar una advertencia la primera vez, pero la"
    Write-Host "         integridad del archivo esta garantizada."
    Write-Host "========================================" -ForegroundColor Green

} catch {
    Write-Host "[ERROR] Falló el firmado: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Presiona Enter para finalizar"