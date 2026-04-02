### GUÍA MAESTRA DE USO Y PUBLICACIÓN

---

#### 1. Requisitos Previos (Solo una vez)

* **Python:** Debes tener **Python 3.11** instalado (NO uses 3.13 ni 3.14). Asegúrate de marcar "Add Python to PATH" al instalar.
* **Internet:** Necesario la primera vez para bajar librerías y herramientas de compilación.
* **Inno Setup 6:** Necesario para generar el instalador.
* **Windows SDK / signtool.exe:** Necesario para la firma de distribución real.

---

#### 2. Flujo Correcto de Release

1. **Instalar/Resetear Entorno:**
* Ejecuta `setup_amp.bat`. En la carpeta raiz del proyecto.
* Si todo sale bien, dirá `[5/5] Entorno listo`.

2. **Compilar Portable:**
* Ejecuta `buildportable.bat`.
* Al finalizar, dejará el archivo portable en `downloads/`.
* También copiará `LICENSE.txt` en `downloads/`.

3. **Compilar Instalador:**
* Ejecuta `buildinstaller.bat`.
* Al finalizar, dejará el instalador en `downloads/`.
* El instalador mostrará la licencia durante el wizard y además instalará `LICENSE.txt`.

4. **Firmado de Prueba:**
* Este modo no publica nada.
* Sirve para validar el flujo sin asumir confianza pública.
* Si no se configura un certificado, el script no firma y solo deja claro que sigues en modo test.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\firmarAplicacion.ps1 -Mode Test
```

5. **Firmado de Distribución:**
* Este modo exige certificado real de publicación.
* Firma el portable y el instalador.
* Puedes usar un `.pfx` o un certificado instalado en el almacén del usuario.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$env:SIGN_PFX_PATH="C:\Ruta\MiCertificadoPublico.pfx"
$env:SIGN_PFX_PASSWORD="TuPassword"
.\firmarAplicacion.ps1 -Mode Distribution
```

6. **Alternativa con thumbprint:**
* Si el certificado ya está instalado en `CurrentUser\My`, usa el SHA1.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$env:SIGN_CERT_SHA1="A1B2C3D4E5F60718293A4B5C6D7E8F9012345678"
.\firmarAplicacion.ps1 -Mode Distribution
```

7. **Distribuir:**
* Publica únicamente los artefactos ya firmados de `downloads/`.
* No publiques certificados, `.pfx`, contraseñas ni carpetas privadas de firma.

---

#### 3. Diferencia entre Prueba y Distribución

**Modo Test**
* No representa confianza pública.
* No resuelve SmartScreen.
* No debe usarse como publicación final.

**Modo Distribution**
* Está preparado para usar un certificado real.
* Firma ambos artefactos finales.
* Es el flujo correcto para release pública.

---

#### 4. Archivos Finales Esperados

En `downloads/` deben quedar como base:

* `Lectorcito Pro Portable.exe`
* `LectorcitoPro-Setup.exe`
* `LICENSE.txt`

---

#### 5. Solución de Problemas (Manual de Emergencia)

**Caso A: Nuitka falla descargando GCC / MinGW64 (Error: Timeout / ReadTimeoutError)**

* **Síntoma:** Barra de descarga en 0% o error rojo al ejecutar el build.
* **Solución:**
1. Descarga este archivo ZIP: `winlibs-x86_64-posix-seh-gcc-14.2.0-llvm-19.1.1-mingw-w64msvcrt-12.0.0-r2.zip`
2. Presiona `Win + R` y pega: `%LOCALAPPDATA%\Nuitka\Nuitka\Cache\downloads\gcc\x86_64\14.2.0posix-19.1.1-12.0.0-msvcrt-r2\`
3. Pega el ZIP descargado dentro de esa carpeta.
4. Ejecuta el build de nuevo.

**Caso B: Nuitka falla descargando Dependency Walker (Error: Depends.exe)**

* **Síntoma:** Error casi al final del build pidiendo `depends.exe`.
* **Solución:**
1. Descarga `depends22_x64.zip`
2. Presiona `Win + R` y pega: `%LOCALAPPDATA%\Nuitka\Nuitka\Cache\downloads\depends\x86_64\`
3. **Descomprime** el ZIP ahí. Debe quedar el archivo `depends.exe` visible.
4. Ejecuta el build de nuevo.

**Caso C: No se encuentra ISCC.exe**

* **Síntoma:** `buildinstaller.bat` falla diciendo que no encontró Inno Setup.
* **Solución:**
1. Instala Inno Setup 6.
2. O define la variable `ISCC_PATH`.

```batch
set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
.\buildinstaller.bat
```

**Caso D: No se encuentra signtool.exe**

* **Síntoma:** `firmarAplicacion.ps1` falla diciendo que no encontró `signtool.exe`.
* **Solución:**
1. Instala Windows SDK.
2. O define la variable `SIGNTOOL_PATH`.

```powershell
$env:SIGNTOOL_PATH="C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
.\firmarAplicacion.ps1 -Mode Distribution
```

**Caso E: Distribution rechaza el certificado**

* **Síntoma:** el script indica que `Distribution no admite certificado autofirmado`.
* **Solución:**
1. No uses certificados locales de prueba.
2. Conecta un certificado público real antes de publicar.

---

#### 6. Como correr los archivos

* **setup_amp.bat:** Configura o resetea el entorno de compilación.

```powershell
.\setupAmp.bat
```

* **buildportable.bat:** Compila la versión portable.

```powershell
.\buildportable.bat
```

* **buildinstaller.bat:** Compila la versión instalable.

```powershell
.\buildinstaller.bat
```

* **firmarAplicacion.ps1:** Firma los artefactos de release.

```powershell
.\firmarAplicacion.ps1 -Mode Distribution
```
