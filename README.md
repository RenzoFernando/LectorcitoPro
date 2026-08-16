<div align="center">
  <h1>Lectorcito Pro</h1>
  
  <img src="https://raw.githubusercontent.com/RenzoFernando/LectorcitoPro/main/resources/branding/lector.png" alt="Logo de Lectorcito Pro" width="175">
  <br>
  <p>
    <a href="https://github.com/RenzoFernando/LectorcitoPro/releases/latest">
      <img src="https://img.shields.io/github/v/release/RenzoFernando/LectorcitoPro?style=for-the-badge&label=VERSION%20Actual&color=blue" alt="Release Actual">
    </a>
    <a href="https://github.com/RenzoFernando/LectorcitoPro/releases/latest">
      <img src="https://img.shields.io/badge/VER%20RELEASES-2E9D46?style=for-the-badge" alt="Ver descargas y releases">
    </a>
    <a href="https://renzofernando.github.io/LectorcitoPro/">
      <img src="https://img.shields.io/badge/VER%20PÁGINA%20Y%20DESCARGAR-2F6FE4?style=for-the-badge" alt="Abrir página oficial">
    </a>
    <br>
    <br>
    <strong>
      Herramienta de escritorio profesional para auditoría de código, documentación técnica y consolidación de contextos para Inteligencia Artificial.
    </strong>
  </p>

</div>

---

## Descripción

**Lectorcito Pro** es una aplicación de escritorio para Windows y Linux, desarrollada en Python con separación entre control, interfaz, procesamiento, renderizado, internacionalización y servicios de plataforma. Su función principal es analizar directorios de proyectos de software, consolidar su estructura y extraer el contenido relevante en un único reporte legible.

Está orientada a desarrolladores que necesitan:

* Generar contexto limpio y útil para LLMs como GPT, Claude o Gemini.
* Revisar proyectos completos sin navegar carpeta por carpeta.
* Crear documentación técnica rápida del estado actual de un repositorio.
* Preparar entregables de auditoría con filtros, exclusiones y perfiles reutilizables.

## Tabla de Contenidos

1. [Acceso y Descarga](#acceso)
2. [Características Técnicas](#caracteristicas)
3. [Manual de Uso](#uso)
4. [Distribución](#distribucion)
5. [Estructura del Proyecto](#estructura)
6. [Guía para Desarrolladores](#desarrolladores)
7. [Licencia](#licencia)

---

## <a name="acceso"></a>Acceso y Descarga

Lectorcito Pro se distribuye en **tres artefactos oficiales**:

* **Windows instalable recomendado:** `LectorcitoPro-Setup.exe`
  * Opción principal para usuarios finales de Windows.
  * Integra el ejecutable, la licencia y los accesos del instalador.

* **Windows portable:** `LectorcitoPro-Portable.exe`
  * Ejecutable único para uso directo sin instalación.

* **Linux portable x86_64:** `LectorcitoPro-Linux-x86_64`
  * Binario único generado con Nuitka Onefile.
  * No requiere un instalador adicional.
  * En Linux puede requerir `chmod +x LectorcitoPro-Linux-x86_64` después de descargarlo.

Canales oficiales:

* **Sitio Web Oficial:** https://renzofernando.github.io/LectorcitoPro/
* **GitHub Releases:** https://github.com/RenzoFernando/LectorcitoPro/releases/latest

---

## <a name="caracteristicas"></a>Características Técnicas

* **Arquitectura MVC:** separación clara entre lógica, interfaz y control de flujo.
* **Motor de análisis recursivo:** lectura profunda del proyecto con filtros configurables.
* **Gestión de perfiles:** almacenamiento y recuperación de configuraciones por tipo de trabajo.
* **Filtrado granular:**
  * **Qué Ver:** extensiones y carpetas importantes.
  * **Qué No Ver:** carpetas, archivos específicos y exclusiones apoyadas en `.gitignore`.
  * **Multimedia:** listado de archivos binarios sin procesar su contenido.
* **Generación de árbol:** exportación de la estructura del proyecto sin leer el código.
* **Interfaz moderna:** desarrollada con CustomTkinter, soporte de tema claro/oscuro y buen manejo de DPI.
* **Multilenguaje:** interfaz en Español e Inglés.
* **Procesamiento asíncrono:** evita congelamientos durante lecturas grandes y permite cancelación segura.
* **Distribución profesional:** ejecutable portable, instalador nativo, metadata de producto y publicación coherente.

---

## <a name="uso"></a>Manual de Uso

La interfaz principal se divide en tres bloques: acciones principales, barra lateral de configuración y panel de ajustes.

### 1. Acciones principales

* **Seleccionar Destino:** define dónde se guardarán los reportes generados.
* **Generar Lectura Completa:** analiza una carpeta completa y produce un reporte consolidado.
* **Crear Estructura de Árbol:** exporta la jerarquía del proyecto sin leer el contenido de los archivos.
* **Abrir Carpeta de Lecturas:** abre la ruta activa de salida.
* **Abrir Último Reporte:** acceso directo al archivo más reciente.
* **Eliminar Lecturas:** limpieza de la carpeta de salida actual.

### 2. Configuración lateral

* **Qué Ver:** extensiones y carpetas relevantes que sí deben incluirse.
* **Qué No Ver:** exclusiones manuales y apoyo en `.gitignore` para evitar ruido y acelerar la lectura.
* **Multimedia:** marca extensiones que deben registrarse, pero no expandirse en el reporte.
* **Gestor de Perfiles:** guarda configuraciones reutilizables por stack o tipo de proyecto.

### 3. Ajustes generales

Desde el panel de ajustes se puede:

* Elegir el formato de salida (`.txt` o `.md`).
* Crear accesos directos de Windows.
* Restaurar la configuración de fábrica.
* Consultar información de versión y documentación pública.

---

## <a name="distribucion"></a>Distribución

### Windows

* **Portable:** `LectorcitoPro-Portable.exe`.
* **Instalable:** `LectorcitoPro-Setup.exe`.
* Ambos artefactos pasan por el flujo de firma configurado para el proyecto.

### Linux

* **Portable Onefile x86_64:** `LectorcitoPro-Linux-x86_64`.
* Se genera como un único binario distribuible.
* No existe un segundo instalador Linux dentro del flujo oficial de la Versión 10.

Todos los artefactos finales se generan en `downloads/`.

---

## <a name="estructura"></a>Estructura del Proyecto

```text
LectorcitoPro/
├── release.bat
├── README.md
├── LICENSE
├── index.html
├── pyproject.toml
├── requirements.txt
├── requirements/
│   ├── runtime.txt
│   ├── windows.txt
│   ├── linux.txt
│   ├── build.txt
│   └── dev.txt
├── versionHistory.md
├── docs/
│   └── compilation.md
├── scripts/
│   ├── release.ps1
│   ├── windows/
│   │   ├── setup.bat
│   │   ├── build_portable.bat
│   │   ├── build_installer.bat
│   │   └── sign_application.ps1
│   └── linux/
│       ├── setup.sh
│       ├── build.sh
│       └── release.sh
├── resources/...
└── src/
    ├── controller/
    ├── i18n/
    ├── model/
    ├── platform_services/
    └── view/
```

---

## <a name="desarrolladores"></a>Guía para Desarrolladores

### Requisitos del Entorno

* **Python:** 3.11, 3.12 o 3.13 para ejecución; el build Windows utiliza 3.11 o 3.12.
* **Windows:** Windows 10/11.
* **Linux:** una distribución WSL instalada para el release integral desde Windows; Ubuntu LTS es la referencia recomendada para construir el binario Linux.
* **Runtime común:** `requirements/runtime.txt`.
* **Runtime Windows:** `requirements/windows.txt`.
* **Runtime Linux:** `requirements/linux.txt`.
* **Build:** `requirements/build.txt`.
* **Desarrollo opcional:** `requirements/dev.txt`.
* **Compilación:** Nuitka.
* **Instalador Windows:** Inno Setup 6.

### Configuración y compilación

1. **Clonar el repositorio**

```bash
git clone https://github.com/RenzoFernando/LectorcitoPro.git
cd LectorcitoPro
```

2. **Instalar únicamente el runtime común para desarrollo**

```powershell
python -m pip install -r requirements.txt
```

3. **Sincronizar metadata web cuando se modifique `src/app_meta.py`**

```powershell
python src/app_meta.py
```

4. **Generar el release completo desde Windows**

```powershell
.\release.bat
```

El orquestador ejecuta setup, portable Windows, firma del portable, instalador Windows, firma del instalador y build portable Linux mediante WSL.

Los artefactos resultantes se generan en `downloads/` y los registros de cada ejecución se guardan en `build/release_logs/`.

Para ejecutar etapas individuales consulta `docs/compilation.md`.

---

## <a name="licencia"></a>Licencia

Este proyecto se distribuye bajo los términos de la **Licencia MIT**.
Copyright © 2026 - Renzo Fernando Mosquera Daza - All Rights Reserved.
