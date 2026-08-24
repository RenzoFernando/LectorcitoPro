# Compilación y release

## Objetivo

El release de Lectorcito Pro se genera desde Windows con un único punto de entrada:

```powershell
.\release.bat
```

El flujo valida y autocorrige el código antes de iniciar cualquier compilación. Los tres artefactos finales parten del mismo código fuente validado y ninguno reutiliza otro artefacto previamente construido.

## Requisitos

- Windows 10 u 11.
- Python 3.11 o 3.12 compatible con el entorno de build de Windows.
- Inno Setup 6.
- WSL con una distribución Linux compatible y Python 3.11, 3.12 o 3.13 para el artefacto Linux.
- Conexión a Internet cuando sea necesario preparar dependencias o herramientas que todavía no estén en caché.

`release.bat` prepara el entorno `.venv-build`; no es necesario ejecutar manualmente los scripts internos para un release normal.

## Calidad integral antes del build

La calidad se ejecuta antes de compilar cualquier artefacto y tiene dos fases.

### Fase de autocorrección

1. Sincronización de metadata web desde `src/app_meta.py`.
2. Ruff con correcciones automáticas seguras.
3. Ruff Format.
4. Prettier con escritura sobre formatos compatibles.
5. ESLint con `--fix` sobre `resources/js/**/*.js`.

Los cambios efectuados por los formatters permanecen en el working tree.

### Fase de validación estricta

1. Ruff lint final.
2. Ruff format check.
3. ESLint final sin modificaciones.
4. Prettier check.
5. Validación de `pyproject.toml` con `tomllib`.
6. Compilación sintáctica de Python.
7. Validación sintáctica de los scripts PowerShell.

Si cualquiera de estas comprobaciones falla, el release se detiene antes de compilar.

## Herramientas de calidad

Ruff se instala dentro de `.venv-build` desde `requirements/quality.txt`.

Prettier y ESLint se instalan como dependencias de desarrollo definidas en `package.json`. `scripts/windows/setup_node.ps1` utiliza Node.js 24.19.0: reutiliza una instalación compatible si está disponible o prepara una copia portable verificada por SHA-256 dentro de `.tools/`. Ni `.tools/` ni `node_modules/` forman parte del runtime ni de los artefactos finales.

## Arquitectura de Windows

Portable e Instalable son compilaciones distintas:

```text
src/main.py
    |
    +--> Nuitka --mode=onefile
    |       |
    |       +--> downloads/LectorcitoPro-Portable.exe
    |
    +--> Nuitka --mode=standalone
            |
            +--> build/windows/installed-app/LectorcitoPro.dist/
                    |
                    +--> Inno Setup
                            |
                            +--> downloads/LectorcitoPro-Setup.exe
```

`Portable != Installed executable`.

El instalador no contiene una copia renombrada de `LectorcitoPro-Portable.exe`. Inno Setup empaqueta recursivamente la distribución standalone generada específicamente para la aplicación instalada.

## Windows Portable

`scripts/windows/build_portable.bat` compila `src/main.py` con Nuitka Onefile. Utiliza:

- metadata centralizada de `src/app_meta.py`;
- el icono oficial;
- el plugin de Tk;
- `customtkinter`;
- la carpeta `resources/`.

El directorio temporal de este build es `build/windows/portable/`. El resultado final es:

```text
downloads/LectorcitoPro-Portable.exe
```

## Windows Installed App

`scripts/windows/build_installed_app.bat` vuelve a compilar `src/main.py`, esta vez con Nuitka Standalone. Su salida esperada es:

```text
build/windows/installed-app/LectorcitoPro.dist/
    LectorcitoPro.exe
    ...dependencias del runtime...
    resources/
```

Esta distribución es independiente del Portable y se conserva hasta que Inno Setup termina de empaquetarla.

## Windows Installer

`scripts/windows/build_installer.bat` requiere la distribución standalone anterior y genera un script temporal de Inno Setup dentro de `build/windows/installer/`.

La instalación es por usuario:

```ini
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\Lectorcito Pro
```

El instalador crea los accesos directos del usuario actual y copia recursivamente la distribución standalone, además de `LICENSE` y el marker de instalación utilizado por la lógica existente de la aplicación.

El resultado final es:

```text
downloads/LectorcitoPro-Setup.exe
```

> Las releases actualmente se distribuyen sin firma de código hasta disponer de una identidad de firma pública legítima. El proyecto no genera ni instala certificados autofirmados como sustituto.

## Linux

El empaquetado Linux conserva su arquitectura actual. El release general sigue invocando:

```text
scripts/linux/setup.sh
scripts/linux/build.sh
scripts/linux/release.sh
```

El artefacto continúa siendo Nuitka Onefile:

```text
downloads/LectorcitoPro-Linux-x86_64
```

Este refactor no convierte Linux a Standalone ni agrega formatos adicionales.

## Orden del release

`release.bat` delega en `scripts/release.ps1`, que ejecuta:

1. Setup Windows.
2. Calidad integral y autofix.
3. Validación estricta.
4. Build Windows Portable Onefile.
5. Build Windows Installed App Standalone.
6. Build Windows Installer.
7. Preparación del sistema Linux en WSL.
8. Build Linux Portable Onefile.
9. Verificación de artefactos.
10. SHA-256 y resumen final.

Un fallo en cualquier etapa impide continuar a las etapas posteriores.

## Directorios de trabajo

```text
build/
    release_logs/
    windows/
        portable/
        installed-app/
        installer/
    linux/
```

`downloads/` contiene exclusivamente los artefactos finales:

```text
downloads/
    LectorcitoPro-Portable.exe
    LectorcitoPro-Setup.exe
    LectorcitoPro-Linux-x86_64
```

Los logs se guardan por ejecución en `build/release_logs/YYYYMMDD-HHMMSS/`. Una ejecución exitosa elimina los temporales de compilación de Windows y Linux, pero conserva los logs y los cambios aplicados por Ruff, Prettier y ESLint.

## Resumen y hashes

El resumen final registra como mínimo:

- versión de la aplicación;
- Python utilizado en Windows;
- Nuitka utilizado en Windows;
- Python utilizado en Linux;
- ruta y SHA-256 del Portable Windows;
- ruta y SHA-256 del Installer Windows;
- ruta y SHA-256 del Portable Linux;
- ruta de los logs.

También se verifica que el ejecutable standalone instalado y el Portable no sean el mismo archivo byte por byte.

## Validación manual de release candidata

Además de las verificaciones automáticas del pipeline, una release candidata debe probarse en Windows 10 y Windows 11, preferentemente también en Windows Sandbox o una VM limpia. Deben comprobarse el Portable, la instalación por usuario, los accesos directos, la ejecución de la aplicación instalada, la desinstalación y las funciones principales de generación de reportes.
