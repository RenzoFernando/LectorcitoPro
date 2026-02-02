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

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   FIRMA DIGITAL NATIVA (PowerShell)    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# 1. CONFIGURACION DE RUTAS
# -----------------------------------------------------------------------------
$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$CarpetaSalida = Join-Path -Path $PSScriptRoot "descargas"
$NombreExe = "LectorcitoPro.exe"
$RutaExe = Join-Path -Path $CarpetaSalida $NombreExe

# Configuración del Certificado
$CarpetaCert = Join-Path -Path $PSScriptRoot "recursos_certificado"
$NombreCert = "LectorcitoPro_Key.pfx"
$RutaCert = Join-Path -Path $CarpetaCert $NombreCert
$PasswordCert = "Lectorcito123" # Contraseña interna para el archivo PFX
$SujetoCert = "CN=LectorcitoPro_Autor"

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
    # Cargar certificado existente
    try {
        $CertificadoObj = Get-PfxCertificate -FilePath $RutaCert
    } catch {
        Write-Host "[ERROR] El certificado existe pero no se pudo cargar. Puede estar dañado." -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] Creando nuevo certificado autofirmado..." -ForegroundColor Green
    
    # Crear certificado en el almacén personal del usuario
    $CertTemp = New-SelfSignedCertificate -Type CodeSigningCert `
                                          -Subject $SujetoCert `
                                          -CertStoreLocation "Cert:\CurrentUser\My" `
                                          -NotAfter (Get-Date).AddYears(5) `
                                          -FriendlyName "LectorcitoPro Developer ID"

    # Exportar a archivo PFX para guardarlo en la carpeta del proyecto
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