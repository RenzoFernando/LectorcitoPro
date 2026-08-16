# GUÍA MAESTRA DE COMPILACIÓN Y RELEASE

## 1. Resultado oficial de la Versión 10

El flujo de release genera exactamente tres artefactos de aplicación dentro de `downloads/`:

* `LectorcitoPro-Portable.exe` — portable para Windows.
* `LectorcitoPro-Setup.exe` — instalador para Windows.
* `LectorcitoPro-Linux-x86_64` — portable Onefile para Linux x86_64.

Linux utiliza un único binario portable. No se genera un segundo instalador Linux.

## 2. Punto único de entrada

Desde la raíz del proyecto se ejecuta únicamente:

```powershell
.\release.bat
```

`release.bat` delega la orquestación a `scripts/release.ps1`. No es necesario ejecutar manualmente los scripts internos durante un release normal.

## 3. Orden del release integral

El flujo se ejecuta en este orden:

1. Validación de estructura y disponibilidad de WSL.
2. Setup limpio del entorno Windows.
3. Build de `LectorcitoPro-Portable.exe`.
4. Firma y verificación del portable Windows.
5. Build de `LectorcitoPro-Setup.exe` reutilizando el portable ya firmado como binario instalado.
6. Firma y verificación del instalador Windows.
7. Setup y build Linux mediante WSL.
8. Verificación de los tres artefactos.
9. Cálculo de SHA-256.
10. Resumen final.

Si una etapa falla, el flujo se detiene y devuelve un código de error.

## 4. Requisitos de Windows

* Windows 10 o Windows 11.
* Python 3.11 o 3.12.
* Acceso a Internet para instalar dependencias cuando sea necesario.
* Inno Setup 6.
* PowerShell con `New-SelfSignedCertificate` disponible para el esquema de firma local actual.
* WSL con al menos una distribución Linux instalada para generar el artefacto Linux desde el mismo `release.bat`.

Para el binario Linux con mayor compatibilidad entre Ubuntu, Kali y Arch x86_64, se recomienda utilizar una distribución Ubuntu LTS como entorno de compilación WSL.

## 5. Requisitos de Linux

El script `scripts/linux/setup.sh` reconoce automáticamente sistemas basados en:

* `apt-get`, como Ubuntu y Kali.
* `pacman`, como Arch Linux.

Instala o verifica las herramientas necesarias para Python, Tk, compilación nativa, `patchelf`, `ccache`, `xdg-utils` y utilidades de escritorio.

## 6. Artefacto Linux

El artefacto Linux oficial es:

```text
LectorcitoPro-Linux-x86_64
```

Se genera con Nuitka en modo Onefile y contiene la aplicación en un único archivo distribuible.

Después de descargarlo en Linux puede ser necesario ejecutar:

```bash
chmod +x LectorcitoPro-Linux-x86_64
./LectorcitoPro-Linux-x86_64
```

No se genera `.exe`, `.tar.gz`, `.deb`, `.rpm` ni un segundo instalador Linux dentro del flujo oficial.

## 7. Firma de Windows

La firma actual continúa utilizando un certificado autofirmado local.

El flujo integral firma primero el portable. Después el instalador reutiliza ese mismo binario firmado como ejecutable interno y, finalmente, el propio instalador también se firma.

Esto permite que:

* `LectorcitoPro-Portable.exe` quede firmado.
* El `LectorcitoPro.exe` contenido dentro del instalador provenga del mismo binario firmado.
* `LectorcitoPro-Setup.exe` quede firmado después de ser empaquetado.

El autofirmado local sirve para validación y pruebas, pero no sustituye un certificado público de confianza para SmartScreen.

## 8. Logs

Cada ejecución crea una carpeta con timestamp:

```text
build/release_logs/
└── YYYYMMDD-HHMMSS/
    ├── 01-setup-windows.log
    ├── 02-build-portable.log
    ├── 03-sign-portable.log
    ├── 04-build-installer.log
    ├── 05-sign-installer.log
    ├── 06-linux-release.log
    └── 07-summary.log
```

El resumen final incluye la ruta y SHA-256 de cada artefacto.

## 9. Scripts internos

Los scripts internos quedan organizados así:

```text
scripts/
├── release.ps1
├── windows/
│   ├── setup.bat
│   ├── build_portable.bat
│   ├── build_installer.bat
│   └── sign_application.ps1
└── linux/
    ├── setup.sh
    ├── build.sh
    └── release.sh
```

Durante un release normal no deben ejecutarse manualmente.

## 10. Ejecución manual de emergencia

### Windows setup

```powershell
.\scripts\windows\setup.bat
```

### Windows portable

```powershell
.\scripts\windows\build_portable.bat
```

### Firmar portable

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows\sign_application.ps1 -Mode Portable
```

### Windows installer

El instalador requiere que el portable exista previamente y esté firmado.

```powershell
.\scripts\windows\build_installer.bat
```

### Firmar instalador

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows\sign_application.ps1 -Mode Installer
```

### Linux dentro de Linux o WSL

```bash
bash scripts/linux/release.sh
```

## 11. Solución de problemas

### WSL no está instalado

El release integral se detendrá antes de compilar. Instala WSL y una distribución Linux y vuelve a ejecutar `release.bat`.

### Inno Setup no está instalado

Instala Inno Setup 6 o define `ISCC_PATH` antes de ejecutar el release:

```powershell
$env:ISCC_PATH="C:\Users\TuUsuario\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
.\release.bat
```

### Nuitka falla descargando herramientas

Conserva las soluciones manuales de caché de Nuitka utilizadas anteriormente para MinGW64 y Dependency Walker. Después vuelve a ejecutar `release.bat`.

### La firma falla

El detalle queda registrado en `build/release_logs/<timestamp>/03-sign-portable.log` o `05-sign-installer.log`.

### El build Linux falla

Revisa `build/release_logs/<timestamp>/06-linux-release.log`. Si quieres aislar el problema, abre la distribución WSL y ejecuta:

```bash
cd /ruta/al/proyecto
bash scripts/linux/release.sh
```

## 12. Carpeta de salida

Se conserva `downloads/` como carpeta oficial de salida porque ya forma parte de la metadata y del flujo de publicación del proyecto. La infraestructura interna queda separada en `scripts/` y `build/`, mientras `downloads/` contiene únicamente los artefactos que se distribuyen.
