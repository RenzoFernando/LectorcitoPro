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

[CmdletBinding()]
param()

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

function Get-ExistingSelfSignedCodeSigningCertificate([string]$FriendlyName, [string]$SubjectName) {
    $certificates = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert -ErrorAction SilentlyContinue |
        Where-Object {
            $_.HasPrivateKey -and
            $_.NotAfter -gt (Get-Date) -and
            $_.Subject -eq $SubjectName -and
            $_.Issuer -eq $SubjectName -and
            $_.FriendlyName -eq $FriendlyName
        } |
        Sort-Object NotAfter -Descending

    return ($certificates | Select-Object -First 1)
}

function New-LocalCodeSigningCertificate([string]$FriendlyName, [string]$SubjectName) {
    if (-not (Get-Command New-SelfSignedCertificate -ErrorAction SilentlyContinue)) {
        throw "No se encontro el cmdlet New-SelfSignedCertificate en este Windows."
    }

    $params = @{
        Type              = "CodeSigningCert"
        Subject           = $SubjectName
        FriendlyName      = $FriendlyName
        CertStoreLocation = "Cert:\CurrentUser\My"
        KeyAlgorithm      = "RSA"
        KeyLength         = 4096
        HashAlgorithm     = "SHA256"
        NotAfter          = (Get-Date).AddYears(3)
    }

    $cert = New-SelfSignedCertificate @params
    if (-not $cert) {
        throw "No se pudo crear el certificado autofirmado."
    }

    return $cert
}

function Add-CertificateToStore([System.Security.Cryptography.X509Certificates.X509Certificate2]$Certificate, [string]$StoreName) {
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store($StoreName, "CurrentUser")
    try {
        $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
        $exists = $store.Certificates | Where-Object { $_.Thumbprint -eq $Certificate.Thumbprint } | Select-Object -First 1
        if (-not $exists) {
            $publicCertificate = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2 -ArgumentList @(,$Certificate.RawData)
            $store.Add($publicCertificate)
        }
    } finally {
        $store.Close()
    }
}

function Trust-LocalCodeSigningCertificate([System.Security.Cryptography.X509Certificates.X509Certificate2]$Certificate) {
    Add-CertificateToStore -Certificate $Certificate -StoreName "Root"
    Add-CertificateToStore -Certificate $Certificate -StoreName "TrustedPublisher"
}

function Get-ManagedCodeSigningCertificate([string]$FriendlyName, [string]$SubjectName) {
    $existing = Get-ExistingSelfSignedCodeSigningCertificate -FriendlyName $FriendlyName -SubjectName $SubjectName
    if ($existing) {
        return [PSCustomObject]@{
            Certificate = $existing
            Created     = $false
        }
    }

    $created = New-LocalCodeSigningCertificate -FriendlyName $FriendlyName -SubjectName $SubjectName
    return [PSCustomObject]@{
        Certificate = $created
        Created     = $true
    }
}

function Sign-Artifact(
    [string]$FilePath,
    [System.Security.Cryptography.X509Certificates.X509Certificate2]$Certificate,
    [string]$TimestampUrl
) {
    if (-not (Test-Path $FilePath)) {
        throw "No existe el archivo: $FilePath"
    }

    $signature = $null
    $usedTimestamp = $false

    if ($TimestampUrl) {
        try {
            $signature = Set-AuthenticodeSignature `
                -FilePath $FilePath `
                -Certificate $Certificate `
                -HashAlgorithm SHA256 `
                -IncludeChain All `
                -TimestampServer $TimestampUrl `
                -ErrorAction Stop
            $usedTimestamp = $true
        } catch {
            Write-Host "[WARN] No se pudo agregar timestamp a: $FilePath" -ForegroundColor Yellow
            Write-Host "[WARN] Se aplicara la firma sin timestamp." -ForegroundColor Yellow
        }
    }

    if (-not $signature) {
        $signature = Set-AuthenticodeSignature `
            -FilePath $FilePath `
            -Certificate $Certificate `
            -HashAlgorithm SHA256 `
            -IncludeChain All `
            -ErrorAction Stop
    }

    $verification = Get-AuthenticodeSignature -FilePath $FilePath
    if ($verification.Status -ne "Valid") {
        throw "La verificacion fallo para '$FilePath'. Estado: $($verification.Status) - $($verification.StatusMessage)"
    }

    return [PSCustomObject]@{
        Signature      = $verification
        UsedTimestamp  = $usedTimestamp
    }
}

Clear-Host
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "     FIRMA DIGITAL LOCAL AUTOMATICA     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $PSScriptRoot

$CarpetaSalidaName = Get-AppMetaValue "app_meta.APP_OUTPUT_DIR_NAME" "downloads"
$PortableArtifactName = Get-AppMetaValue "app_meta.APP_PORTABLE_ARTIFACT_NAME" "LectorcitoPro-Portable.exe"
$InstallerName = Get-AppMetaValue "app_meta.APP_INSTALLER_NAME" "LectorcitoPro-Setup.exe"
$TimestampUrl = Get-AppMetaValue "app_meta.APP_SIGNING_TIMESTAMP_URL" "http://timestamp.digicert.com"
$PublisherName = Get-AppMetaValue "app_meta.APP_PUBLISHER_NAME" "Lectorcito Pro"
$SignatureFriendlyName = Get-AppMetaValue "app_meta.APP_SIGNATURE_FRIENDLY_NAME" "Lectorcito Pro Code Signing"

$SubjectName = "CN=$PublisherName"
$CarpetaSalida = Join-Path -Path $PSScriptRoot $CarpetaSalidaName
$RutaPortable = Join-Path -Path $CarpetaSalida $PortableArtifactName
$RutaInstaller = Join-Path -Path $CarpetaSalida $InstallerName

$Artifacts = @(
    [PSCustomObject]@{ Nombre = "Portable"; Ruta = $RutaPortable },
    [PSCustomObject]@{ Nombre = "Installer"; Ruta = $RutaInstaller }
)

$ExistingArtifacts = @($Artifacts | Where-Object { Test-Path $_.Ruta })

if ($ExistingArtifacts.Count -eq 0) {
    Write-Host "[ERROR] No se encontraron artefactos para firmar en: $CarpetaSalida" -ForegroundColor Red
    Write-Host "Primero ejecuta buildportable.bat y buildinstaller.bat."
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "[INFO] Carpeta de salida: $CarpetaSalida" -ForegroundColor Yellow
Write-Host ""

foreach ($artifact in $Artifacts) {
    if (Test-Path $artifact.Ruta) {
        Write-Host "[OK] Detectado $($artifact.Nombre): $($artifact.Ruta)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] No encontrado $($artifact.Nombre): $($artifact.Ruta)" -ForegroundColor Yellow
    }
}

Write-Host ""

try {
    $managedCertificate = Get-ManagedCodeSigningCertificate -FriendlyName $SignatureFriendlyName -SubjectName $SubjectName
    $certificate = $managedCertificate.Certificate

    Trust-LocalCodeSigningCertificate -Certificate $certificate

    if ($managedCertificate.Created) {
        Write-Host "[OK] Certificado autofirmado creado." -ForegroundColor Green
    } else {
        Write-Host "[OK] Certificado autofirmado reutilizado." -ForegroundColor Green
    }

    Write-Host "[INFO] Subject: $($certificate.Subject)" -ForegroundColor Green
    Write-Host "[INFO] Thumbprint: $($certificate.Thumbprint)" -ForegroundColor Green
    Write-Host "[INFO] Valido hasta: $($certificate.NotAfter)" -ForegroundColor Green
    Write-Host ""

    foreach ($artifact in $ExistingArtifacts) {
        Write-Host "[PROCESO] Firmando $($artifact.Nombre)..." -ForegroundColor Cyan
        $result = Sign-Artifact -FilePath $artifact.Ruta -Certificate $certificate -TimestampUrl $TimestampUrl
        if ($result.UsedTimestamp) {
            Write-Host "[OK] $($artifact.Nombre) firmado y verificado con timestamp." -ForegroundColor Green
        } else {
            Write-Host "[OK] $($artifact.Nombre) firmado y verificado sin timestamp." -ForegroundColor Green
        }
        Write-Host ""
    }

    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   EXITO: ARCHIVOS FIRMADOS EN SITIO    " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    foreach ($artifact in $ExistingArtifacts) {
        Write-Host $artifact.Ruta
    }
    Write-Host "========================================" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Fallo el firmado: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Presiona Enter para finalizar"
    exit 1
}

Write-Host ""
Read-Host "Presiona Enter para finalizar"

#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
#.\firmarAplicacion.ps1