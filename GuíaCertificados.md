
# Guía de certificados de firma de código

> **Objetivo:** que cualquier ejecutable que distribuyas aparezca como “Publicador conocido” y no sea bloqueado por SmartScreen o antivirus.

---

## 1. Conceptos clave

- **Firma de código**: firma digital que asegura que el binario no ha sido alterado y proviene de ti.
- **Timestamping**: marca temporal que prolonga la validez de la firma incluso cuando tu certificado expire.
- **Autoridad de certificación (CA)**:
  - **Self‑signed**: tú mismo creas tu propia “CA raíz” y emites certificados. Útil para pruebas internas.
  - **CA pública**: compras un certificado a DigiCert, Sectigo, etc. Cualquier Windows confía automáticamente.

---

## 2. Entorno y herramientas

- **PowerShell (administrador)**
- **Windows SDK** (incluye `signtool.exe`), por ejemplo:
  ```
  C:\Program Files (x86)\Windows Kits\10\bin\<versión>\x64\signtool.exe
  ```
- Tu ejecutable empaquetado con PyInstaller o similar, en `dist\MiApp.exe`.

---

## 3. Opción A: Self‑signed (solo para pruebas internas)

### 3.1. Crear tu CA raíz

```powershell
# Paso 1: Generar certificado raíz (RootCA)
New-SelfSignedCertificate `
  -Type Custom `
  -Subject "CN=MiRootCA" `
  -KeyUsage CertSign,CRLSign `
  -KeyLength 2048 `
  -HashAlgorithm SHA256 `
  -KeyExportPolicy Exportable `
  -CertStoreLocation "Cert:\CurrentUser\My"
```

### 3.2. Extraer e instalar tu CA raíz en “Entidades de certificación raíz de confianza”

```powershell
# Exportar la raíz a un archivo .cer
Export-Certificate `
  -Cert (Get-ChildItem Cert:\CurrentUser\My | Where-Object Subject -EQ "CN=MiRootCA") `
  -FilePath .\MiRootCA.cer

# Importar la raíz en CurrentUser\Root (o en LocalMachine\Root para todos los usuarios)
Import-Certificate `
  -FilePath .\MiRootCA.cer `
  -CertStoreLocation Cert:\CurrentUser\Root
```

### 3.3. Crear un certificado de firma de código firmado por tu CA

```powershell
# Obtener el objeto de tu RootCA en memoria
$root = Get-ChildItem Cert:\CurrentUser\My | Where-Object Subject -EQ "CN=MiRootCA" | Select-Object -First 1

# Generar el certificado de código firmado por tu RootCA
New-SelfSignedCertificate `
  -Type CodeSigning `
  -Subject "CN=MiAppCodeSigning" `
  -Signer $root `
  -KeyLength 2048 `
  -HashAlgorithm SHA256 `
  -KeyExportPolicy Exportable `
  -CertStoreLocation "Cert:\CurrentUser\My"
```

### 3.4. Exportar a PFX (incluye clave privada)

```powershell
$pfxPassword = ConvertTo-SecureString -String "P@ssw0rdFuerte" -Force -AsPlainText

Export-PfxCertificate `
  -Cert (Get-ChildItem Cert:\CurrentUser\My | Where-Object Subject -EQ "CN=MiAppCodeSigning") `
  -FilePath .\MiAppCodeSigning.pfx `
  -Password $pfxPassword
```

### 3.5. Firmar tu ejecutable con `signtool.exe`

```powershell
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign `
  /f .\MiAppCodeSigning.pfx `
  /p P@ssw0rdFuerte `
  /fd SHA256 `
  /tr http://timestamp.digicert.com `
  /td SHA256 `
  .\dist\MiApp.exe
```

### 3.6. Verificar la firma

```powershell
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" verify `
  /pa /v .\dist\MiApp.exe
```

> ✅ Debe decir “Successfully verified… Number of files successfully Verified: 1”

---

## 4. Opción B: Certificado de CA pública (recomendado para distribución)

1. **Comprar** un **Code Signing Certificate** (OV o EV) a una CA reconocida (DigiCert, Sectigo, GlobalSign…).
2. La CA te enviará un archivo `.pfx` y te darán instrucciones para instalarlo en tu almacén de certificados.
3. Firmar con hash y timestamp igual que en 3.5, pero **no necesitas importar ninguna raíz**: Windows confiará automáticamente.

```powershell
# Firma con tu certificado comprado — puedes usar /a para elegir automáticamente de tu almacén:
& "signtool.exe" sign `
  /a `
  /fd SHA256 `
  /tr http://timestamp.digicert.com `
  /td SHA256 `
  .\dist\MiApp.exe
```

---

## 5. Timestamping

- **¿Para qué sirve?** que la firma siga siendo válida tras la expiración de tu certificado.
- Ya lo vimos con `/tr http://timestamp.digicert.com /td SHA256`.

---

## 6. Empaquetado en instalador

- Herramientas: **Inno Setup**, **NSIS**, **WiX Toolset**…
- Dentro del script del instalador, puedes:
  - Copiar `MiApp.exe` a `Program Files`.
  - Registrar accesos directos en Menú Inicio.
  - Registrar tu RootCA (solo para self‑signed).

---

## 7. Buenas prácticas

- **Clave privada**: protégela con contraseña fuerte y acceso restringido.
- **Respaldo**: guarda copias de tu PFX en lugar seguro (HSM, USB cifrado).
- **Revocación**: si tu PFX se filtra, revoca inmediatamente el certificado en la CA.
- **Automatización**: integra `signtool.exe` en tu pipeline de CI/CD para firmas automáticas.

---

Con estos pasos tienes **el flujo completo** desde generación hasta distribución. ¡Éxito firmando tu aplicación!