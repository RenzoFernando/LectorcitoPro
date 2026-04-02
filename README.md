<div align="center">
  <img src="https://raw.githubusercontent.com/RenzoFernando/LectorcitoPro/main/resources/branding/lector.png" alt="Logo de Lectorcito Pro" width="150">
  <h1>Lectorcito Pro</h1>
  <a href="https://github.com/RenzoFernando/LectorcitoPro/releases/latest">
    <img src="https://img.shields.io/github/v/release/RenzoFernando/LectorcitoPro?style=for-the-badge&label=Descargar%20Ultima%20Version&color=blue" alt="Descargar Última Versión">
  </a>
  <p>
    Herramienta de escritorio profesional para auditoría de código, documentación técnica y consolidación de contextos para Inteligencia Artificial.
  </p>
</div>

---

<br>

## Descripción

**Lectorcito Pro** es una aplicación de escritorio nativa para Windows, desarrollada en Python bajo una arquitectura MVC (Modelo-Vista-Controlador). Su función principal es el análisis recursivo de directorios de proyectos de software para consolidar su estructura y código fuente en un único reporte legible.

Esta utilidad es fundamental para desarrolladores que necesitan:
* Generar contextos completos de un proyecto para alimentar LLMs (Modelos de Lenguaje Grande) como GPT-4, Claude o Gemini.
* Realizar auditorías de código rápidas sin navegar por múltiples subcarpetas.
* Crear documentación técnica instantánea o snapshots del estado actual del desarrollo.

La aplicación destaca por su capacidad de filtrado granular, gestión de perfiles de trabajo y una interfaz moderna de alto rendimiento.

## Tabla de Contenidos

1.  [Acceso y Descarga](#acceso)
2.  [Características Técnicas](#caracteristicas)
3.  [Manual de Uso](#uso)
4.  [Estructura del Proyecto](#estructura)
5.  [Guía para Desarrolladores](#desarrolladores)
6.  [Licencia](#licencia)

---

## <a name="acceso"></a>Acceso y Descarga

Lectorcito Pro se distribuye como una aplicación portable (`.exe`) compilada nativamente, por lo que no requiere instalación ni dependencias externas en el equipo del usuario final.

Puede descargar la última versión estable desde los siguientes canales oficiales:

* **Sitio Web Oficial:** [https://renzofernando.github.io/LectorcitoPro/](https://renzofernando.github.io/LectorcitoPro/)
* **GitHub Releases:** [https://github.com/RenzoFernando/LectorcitoPro/releases/latest](https://github.com/RenzoFernando/LectorcitoPro/releases/latest)

---

## <a name="caracteristicas"></a>Características Técnicas

* **Arquitectura MVC:** Separación estricta entre la lógica de negocio, la interfaz de usuario y el control de flujo, garantizando estabilidad y escalabilidad.
* **Motor de Análisis Recursivo:** Escaneo profundo de directorios con capacidad de omisión inteligente basada en filtros preconfigurados.
* **Gestión de Perfiles:** Permite guardar y alternar entre diferentes configuraciones de entorno (ej. Perfil "Python Back-end", Perfil "React Front-end").
* **Filtrado Granular:**
    * **Inclusión (Qué Ver):** Definición explícita de extensiones y carpetas críticas.
    * **Exclusión (Qué No Ver):** Bloqueo de directorios pesados (node_modules, venv) y archivos sensibles.
    * **Modo Multimedia:** Listado de archivos binarios o de medios sin procesar su contenido (reducción de ruido en el reporte).
* **Generación de Árboles:** Creación de diagramas de jerarquía de carpetas independientes al contenido.
* **Interfaz Moderna (CustomTkinter):** Soporte nativo para modo oscuro/claro, escalado de DPI y diseño responsivo.
* **Multilenguaje:** Cambio en tiempo real entre Español e Inglés.
* **Procesamiento Asíncrono:** Ejecución en hilos separados para evitar el congelamiento de la interfaz durante análisis pesados, con opción de cancelación segura.

---

## <a name="uso"></a>Manual de Uso

La interfaz se divide en tres secciones principales: Panel Central (Acciones), Barra Lateral Izquierda (Info) y Barra Lateral Derecha (Herramientas).

### 1. Acciones Principales

* **Generar Lectura Completa:** Abre un selector de directorios. La aplicación analizará la carpeta seleccionada aplicando los filtros activos y generará un archivo consolidado (ej. `Reporte_NombreProyecto_v1.txt`).
* **Crear Estructura de Árbol:** Genera un archivo de texto que visualiza únicamente la jerarquía de carpetas y archivos, útil para entender la arquitectura sin leer el código.
* **Seleccionar Destino:** Por defecto, los reportes se guardan en una carpeta interna. Esta opción permite definir una ruta personalizada externa para la salida de archivos.

### 2. Configuración y Filtros (Barra Lateral)

* **Qué Ver (Inclusión):** Configure aquí las extensiones de archivo que desea leer (ej: `.py`, `.js`, `.md`) y las carpetas que desea resaltar. Incluye una función de "Autodetectar" que escanea un directorio y sugiere extensiones.
* **Qué No Ver (Exclusión):** Defina carpetas a ignorar recursivamente (ej: `.git`, `__pycache__`) y archivos específicos a omitir.
* **Etiqueta (Multimedia):** Extensiones que aparecerán listadas en el reporte para constancia de su existencia, pero cuyo contenido binario no será impreso.
* **Gestor de Perfiles:** Guarde su configuración actual de filtros bajo un nombre específico para reutilizarla posteriormente en proyectos de distinta naturaleza tecnológica.

### 3. Ajustes Generales

Desde el menú de ajustes se puede configurar:
* **Formato de Salida:** Elegir entre `.txt` (texto plano) o `.md` (Markdown).
* **Integración con el Sistema:** Crear accesos directos en el Escritorio, Menú de Inicio o Barra de Tareas.

---

## <a name="estructura"></a>Estructura del Proyecto

```text
LectorcitoPro/
├── Historial de Versiones.md
├── README.md
├── build.bat
├── compilacion.md
├── firmar_aplicacion.ps1
├── index.html
├── pyproject.toml
├── requirements.txt
├── setup_amp.bat
├── resources/...
└── src
    ├── __init__.py
    ├── app_meta.py
    ├── config.py
    ├── file_rules.py
    ├── main.py
    ├── utils.py
    ├── controller
    │   ├── __init__.py
    │   ├── controller.py
    │   └── handlers.py
    ├── model
    │   ├── __init__.py
    │   └── processor.py
    └── view
        ├── __init__.py
        ├── dialogs.py
        ├── gradient_progress.py
        ├── profiles_dialog.py
        ├── settings_dialog.py
        ├── sidebars.py
        ├── status_panel.py
        ├── tags_dialog.py
        ├── tooltip.py
        ├── translations.py
        ├── ui.py
        ├── ui_assets.py
        └── ui_constants.py
````

---

## <a name="desarrolladores"></a>Guía para Desarrolladores

Si desea compilar el proyecto desde el código fuente o contribuir al desarrollo, siga estos pasos.

### Requisitos del Entorno

* **Lenguaje:** Python 3.11 (Recomendado para compatibilidad con Nuitka).
* **Gestión de Versiones:** Git.
* **Sistema Operativo:** Windows 10/11 (SDKs nativos).

### Configuración y Compilación

El proyecto incluye scripts automatizados en la raíz para facilitar el despliegue del entorno de desarrollo.

1. **Clonar el Repositorio:**

```bash
git clone https://github.com/RenzoFernando/LectorcitoPro.git
cd LectorcitoPro
```

2. **Preparar Entorno Virtual:**
   Ejecute el script `setup_amp.bat`. Este script creará el entorno virtual (`.venv`), actualizará `pip` e instalará todas las dependencias listadas en `requirements.txt`.

```batch
.\setup_amp.bat
```

3. **Ejecución en Desarrollo:**
   Para correr la aplicación sin compilar:

```bash
.venv\Scripts\python.exe src/main.py
```

4. **Compilación a Ejecutable (.exe):**
   El proyecto utiliza **Nuitka** para compilar el código Python a C++ y posteriormente a código máquina, garantizando alto rendimiento y ofuscación. Ejecute el script de construcción:

```batch
.\build.bat
```

El ejecutable resultante (`LectorcitoPro.exe`) se ubicará en la carpeta `downloads/`.

---

## <a name="licencia"></a>Licencia

Este proyecto se distribuye bajo los términos de la **Licencia MIT**.
Copyright © 2026 - Renzo Fernando Mosquera Daza - All Rights Reserved.
