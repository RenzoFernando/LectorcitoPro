### GUÍA MAESTRA DE USO Y PUBLICACIÓN

---

#### 1. Requisitos Previos (Solo una vez)

* **Python:** Debes tener **Python 3.11** instalado (NO uses 3.13 ni 3.14). Asegúrate de marcar "Add Python to PATH" al instalar.
* **Internet:** Necesario la primera vez para bajar librerías y herramientas de compilación.
* **Inno Setup 6:** Necesario para generar el instalador.
* **Firmado actual:** El script `firmarAplicacion.ps1` funciona con **autofirmado local** y no requiere `signtool.exe` ni Windows SDK para su flujo actual.

---

#### 2. Flujo Correcto de Release

1. **Instalar/Resetear Entorno:**
* Ejecuta `setupAmp.bat` en la carpeta raíz del proyecto.
* Si todo sale bien, dirá `[5/5] Entorno listo`.

2. **Compilar Portable:**
* Ejecuta `buildportable.bat`.
* Al finalizar, dejará el archivo portable en `downloads/`.

3. **Compilar Instalador:**
* Ejecuta `buildinstaller.bat`.
* Al finalizar, dejará el instalador en `downloads/`.
* El instalador mostrará la licencia durante el wizard y además instalará el archivo `LICENSE` dentro de la aplicación.

4. **Firmado Local Actual:**
* Ejecuta `firmarAplicacion.ps1`.
* El script genera o reutiliza un certificado autofirmado local y firma los artefactos encontrados en `downloads/`.
* Este flujo sirve para validación local y pruebas del empaquetado en Windows.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\firmarAplicacion.ps1
```

5. **Distribuir:**
* Publica únicamente los artefactos que realmente hayas validado.
* El script actual de `firmarAplicacion.ps1` **no reemplaza** un certificado público real para confianza de distribución externa.

---

#### 3. Alcance del Firmado Actual

**Script actual**
* Usa certificado autofirmado local.
* Firma el portable y el instalador si existen en `downloads/`.
* Puede servir para pruebas, validación interna y comprobación del flujo de release.
* No equivale a un firmado público de confianza para SmartScreen o distribución abierta.

---

#### 4. Archivos Finales Esperados

En `downloads/` deben quedar como base:

* `LectorcitoPro-Portable.exe`
* `LectorcitoPro-Setup.exe`

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

**Caso D: firmarAplicacion.ps1 falla por permisos**

* **Síntoma:** PowerShell bloquea la ejecución del script.
* **Solución:**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\firmarAplicacion.ps1
```

**Caso E: No se encuentran artefactos para firmar**

* **Síntoma:** el script indica que no encontró archivos en `downloads/`.
* **Solución:**
1. Ejecuta primero `buildportable.bat` y `buildinstaller.bat`.
2. Luego vuelve a correr `firmarAplicacion.ps1`.

**Caso F: El sistema no encuentra el cmdlet New-SelfSignedCertificate**

* **Síntoma:** el script de firmado falla al intentar crear el certificado.
* **Solución:**
1. Ejecuta el proceso en una instalación de Windows que tenga disponible `New-SelfSignedCertificate`.
2. Si estás en un entorno muy recortado, valida el firmado en otro equipo Windows compatible.

---

#### 6. Cómo correr los archivos

* **setupAmp.bat:** Configura o resetea el entorno de compilación.

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

* **firmarAplicacion.ps1:** Firma localmente los artefactos generados.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\firmarAplicacion.ps1
```
