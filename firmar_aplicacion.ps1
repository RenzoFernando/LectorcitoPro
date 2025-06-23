# =======================================================================================
# ==               FIRMADOR AUTOMÁTICO PARA APLICACIONES (VERSIÓN POWERSHELL)            ==
# =======================================================================================
#
# OBJETIVO:
# Este script automatiza el proceso completo de autofirmado para un ejecutable.
# Realiza los siguientes pasos de forma secuencial:
#   1. Limpia cualquier certificado de firma antiguo relacionado con este proyecto.
#   2. Crea una nueva Autoridad de Certificación (CA) Raíz y la instala en tu PC.
#   3. Crea un nuevo certificado de firma de código validado por tu propia CA.
#   4. Exporta los archivos .pfx y .cer a una carpeta de certificados.
#   5. Firma el .exe especificado con el nuevo certificado y una marca de tiempo.
#   6. Verifica que la firma se haya aplicado correctamente.
#
# ---------------------------------------------------------------------------------------
# == INSTRUCCIONES DE USO ==
# ---------------------------------------------------------------------------------------
# 1. Abre PowerShell con privilegios de Administrador (Clic derecho -> Ejecutar como administrador).
#
# 2. Navega a la carpeta raíz de tu proyecto usando el comando 'cd':
#    Ejemplo: cd "C:\Users\renzi\PycharmProjects\LectorcitoPro"
#
# 3. La primera vez que ejecutes un script en tu sistema, necesitas permitirlo.
#    Ejecuta este comando UNA SOLA VEZ:
#    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#
# 4. Finalmente, ejecuta este script:
#    .\firmar_aplicacion.ps1
#
# =======================================================================================

Write-Host "`n"
Write-Host "   ================================" -ForegroundColor Green
Write-Host "     INICIANDO FIRMA DE APLICACION" -ForegroundColor Green
Write-Host "   ================================" -ForegroundColor Green
Write-Host "`n"

# --- 1. CONFIGURACION DE RUTAS Y VARIABLES ---
Write-Host "[PASO 1/4] Configurando rutas y variables..." -ForegroundColor Yellow

try {
    # --- [!] ZONA DE CONFIGURACIÓN PRINCIPAL [!] ---
    # Aquí puedes ajustar las variables para futuros proyectos.

    # Ruta raíz del proyecto (normalmente no necesita cambios, detecta la carpeta del script).
    $ProjectRoot = $PSScriptRoot

    # (Editable) Nombre del ejecutable que quieres firmar.
    $ExeName = "LectorcitoPro.exe"

    # (Editable) Nombre de la carpeta donde está tu .exe.
    $DownloadsDirName = "descargas"

    # (Editable) Nombre de la carpeta donde se guardarán los certificados.
    $CertsDirName = "recursos_certificado"

    # (Editable) Contraseña para el certificado. ¡Guárdala bien!
    $CertPass = "LectorcitoPro2025"

    # (Editable) Ruta a signtool.exe. Asegúrate de que la versión (ej. 10.0.26100.0)
    # coincida con la que tienes instalada del Windows SDK.
    $SigToolPath = Join-Path -Path ${env:ProgramFiles(x86)} -ChildPath "Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"

    # --- Fin de la zona de configuración ---

    # Construcción de rutas completas (normalmente no necesita cambios)
    $DownloadsDir = Join-Path -Path $ProjectRoot -ChildPath $DownloadsDirName
    $CertsDir = Join-Path -Path $ProjectRoot -ChildPath $CertsDirName
    $ExePath = Join-Path -Path $DownloadsDir -ChildPath $ExeName
    $PfxFile = Join-Path -Path $CertsDir -ChildPath "LectorcitoCodeSigning.pfx"
    $RootCertFile = Join-Path -Path $CertsDir -ChildPath "RootLectorcito.cer"

    # Crea el directorio de certificados si no existe
    if (-not (Test-Path -Path $CertsDir)) {
        Write-Host "   - Creando carpeta '$CertsDir'..."
        New-Item -ItemType Directory -Path $CertsDir | Out-Null
    }

    # Verificación de archivos necesarios
    if (-not (Test-Path -Path $SigToolPath)) {
        throw "No se encontró signtool.exe en la ruta: $SigToolPath. Por favor, instala el Windows SDK y/o corrige la ruta en este script."
    }
    if (-not (Test-Path -Path $ExePath)) {
        throw "No se encontró el archivo ejecutable: $ExePath. Por favor, compila tu aplicación primero."
    }

    Write-Host "   - Rutas configuradas correctamente."
    Write-Host "`n"
}
catch {
    Write-Host "`n[ERROR] $_" -ForegroundColor Red
    Read-Host -Prompt "Presiona Enter para salir"
    exit
}

# --- 2. CREACIÓN DE CERTIFICADOS ---
Write-Host "[PASO 2/4] Creando y exportando nuevos certificados..." -ForegroundColor Yellow

$rootName = "CN=RootLectorcito"
$codeSignName = "CN=LectorcitoCodeSigning"

# Limpia certificados viejos para evitar duplicados
Write-Host "   - Limpiando certificados antiguos..."
Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq $codeSignName } | Remove-Item -ErrorAction SilentlyContinue
Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq $rootName } | Remove-Item -ErrorAction SilentlyContinue
Get-ChildItem Cert:\CurrentUser\Root | Where-Object { $_.Subject -eq $rootName } | Remove-Item -ErrorAction SilentlyContinue

# Crea la nueva CA Raíz
Write-Host "   - Creando nueva Autoridad de Certificación (CA) Raíz..."
$rootCert = New-SelfSignedCertificate -Type Custom -Subject $rootName -KeyUsage CertSign,CRLSign -KeyLength 2048 -HashAlgorithm SHA256 -KeyExportPolicy Exportable -CertStoreLocation "Cert:\CurrentUser\My"

# Instala la CA Raíz en el almacén de confianza del usuario actual
Write-Host "   - Instalando CA Raíz en el almacén de confianza..."
$store = Get-Item -Path "Cert:\CurrentUser\Root"
$store.Open("ReadWrite")
$store.Add($rootCert)
$store.Close()

# Crea el certificado de firma de código, firmado por nuestra CA Raíz
Write-Host "   - Creando certificado de firma de código..."
$codeCert = New-SelfSignedCertificate -Type CodeSigning -Subject $codeSignName -Signer $rootCert -KeyLength 2048 -HashAlgorithm SHA256 -KeyExportPolicy Exportable -CertStoreLocation "Cert:\CurrentUser\My"

# Exporta los archivos .cer y .pfx
Write-Host "   - Exportando archivos a la carpeta $CertsDirName..."
Export-Certificate -Cert $rootCert -FilePath $RootCertFile | Out-Null
$pfxPassword = ConvertTo-SecureString -String $CertPass -Force -AsPlainText
Export-PfxCertificate -Cert $codeCert -FilePath $PfxFile -Password $pfxPassword | Out-Null

Write-Host "   - Certificados generados y exportados."
Write-Host "`n"


# --- 3. FIRMA DEL EJECUTABLE ---
Write-Host "[PASO 3/4] Firmando el archivo $ExeName..." -ForegroundColor Yellow
# /f : Especifica el archivo PFX que contiene el certificado y la clave privada.
# /p : Proporciona la contraseña para el archivo PFX.
# /sha1 : Especifica el "Thumbprint" (huella digital) del certificado a usar. Esto evita la ambigüedad si hay duplicados.
# /fd : Define el algoritmo de hash para la firma (SHA256 es el estándar moderno).
# /tr : Añade una marca de tiempo (Timestamp) desde un servidor seguro. ¡Esencial!
# /td : Algoritmo de hash para la marca de tiempo.
& $SigToolPath sign /f $PfxFile /p $CertPass /sha1 $codeCert.Thumbprint /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $ExePath

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Ocurrió un error durante la firma. Verifica la consola para más detalles." -ForegroundColor Red
    Read-Host -Prompt "Presiona Enter para salir"
    exit
}

Write-Host "   - Aplicación firmada correctamente."
Write-Host "`n"


# --- 4. VERIFICACIÓN DE LA FIRMA ---
Write-Host "[PASO 4/4] Verificando la firma digital..." -ForegroundColor Yellow
# /pa : Usa la Política de Verificación por Defecto.
# /v  : Muestra una salida detallada (verbose).
& $SigToolPath verify /pa /v $ExePath

Write-Host "`n"
Write-Host "   ================================" -ForegroundColor Green
Write-Host "         PROCESO COMPLETADO" -ForegroundColor Green
Write-Host "   ================================" -ForegroundColor Green
Write-Host "`n"
Write-Host "El archivo $ExeName ha sido firmado correctamente." -ForegroundColor Green
Write-Host "`n"

Read-Host -Prompt "Presiona Enter para salir"

