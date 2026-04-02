<div align="center">
  <img src="https://raw.githubusercontent.com/RenzoFernando/LectorcitoPro/main/resources/branding/lector.png" alt="Logo de Lectorcito Pro" width="150">
  <h1>Lectorcito Pro</h1>
  <a href="https://github.com/RenzoFernando/LectorcitoPro/releases/latest">
    <img src="https://img.shields.io/github/v/release/RenzoFernando/LectorcitoPro?style=for-the-badge&label=Release%20Actual&color=blue" alt="Release Actual">
  </a>
  <p>
    Herramienta de escritorio profesional para auditoría de código, documentación técnica y consolidación de contextos para Inteligencia Artificial.
  </p>
</div>

---

## Descripción

**Lectorcito Pro** es una aplicación de escritorio nativa para Windows, desarrollada en Python bajo una arquitectura MVC (Modelo-Vista-Controlador). Su función principal es analizar directorios de proyectos de software, consolidar su estructura y extraer el contenido relevante en un único reporte legible.

Está orientada a desarrolladores que necesitan:

* Generar contexto limpio y útil para LLMs como GPT, Claude o Gemini.
* Revisar proyectos completos sin navegar carpeta por carpeta.
* Crear documentación técnica rápida del estado actual de un repositorio.
* Preparar entregables de auditoría con filtros, exclusiones y perfiles reutilizables.

La línea **8.0.9** cierra la versión 8 con un enfoque claro en **calidad, estabilidad, rapidez y distribución profesional**.

## Tabla de Contenidos

1. [Acceso y Descarga](#acceso)
2. [Qué aporta la versión 8](#version8)
3. [Características Técnicas](#caracteristicas)
4. [Manual de Uso](#uso)
5. [Distribución Windows](#distribucion)
6. [Estructura del Proyecto](#estructura)
7. [Guía para Desarrolladores](#desarrolladores)
8. [Licencia](#licencia)

---

## <a name="acceso"></a>Acceso y Descarga

Lectorcito Pro ahora se distribuye en **dos artefactos oficiales**:

* **Instalable recomendado:** `LectorcitoPro-Setup.exe`
  * Opción principal para usuarios finales.
  * Integra mejor el flujo nativo de Windows.
  * Permite una instalación más limpia y consistente.

* **Portable opcional:** `LectorcitoPro-Portable.exe`
  * Pensado para ejecución directa sin instalación.
  * Útil para pruebas, soporte técnico o uso puntual.

Canales oficiales:

* **Sitio Web Oficial:** https://renzofernando.github.io/LectorcitoPro/
* **GitHub Releases:** https://github.com/RenzoFernando/LectorcitoPro/releases/latest

---

## <a name="version8"></a>Qué aporta la versión 8

La versión 8 consolida el trabajo hecho en rendimiento, consistencia visual y distribución:

* Infraestructura de ventanas, apertura y transiciones refinada.
* Setup más limpio y presentación más profesional del producto.
* Mejoras de rapidez en operaciones frecuentes y vistas pesadas.
* Ajustes visuales integrales para reducir inconsistencias entre pantallas.
* Metadatos profesionales para ejecutable, instalador y publicación.
* Empaquetado dual con artefacto **instalable** y **portable**.
* Mejor integración con Windows para accesos directos y comportamiento esperado.
* Mejor organización del flujo de descarga y documentación pública.
* Integración de exclusiones asistidas con `.gitignore` desde la aplicación.
* Cierre estable de la rama 8 con release final **8.0.9**.

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

## <a name="distribucion"></a>Distribución Windows

La publicación final de la versión 8 se apoya en dos flujos complementarios:

* **Portable:** orientado a ejecución directa.
* **Instalable:** orientado a distribución recomendada para usuarios finales.

Además, la release mantiene:

* Nombres de artefactos estables para publicación en GitHub Releases.
* Integración con accesos directos de Windows.
* Metadatos de producto, versión, copyright y descripción profesional.
* Página oficial de documentación enlazada a la release pública.

---

## <a name="estructura"></a>Estructura del Proyecto

```text
LectorcitoPro/
├── historialDeVersiones.md
├── LICENSE
├── README.md
├── buildinstaller.bat
├── buildportable.bat
├── compilacion.md
├── firmarAplicacion.ps1
├── index.html
├── pyproject.toml
├── requirements.txt
├── setupAmp.bat
├── resources/...
└── src/
    ├── __init__.py
    ├── app_meta.py
    ├── config.py
    ├── file_rules.py
    ├── main.py
    ├── utils.py
    ├── controller/
    │   ├── __init__.py
    │   ├── controller.py
    │   └── handlers.py
    ├── model/
    │   ├── __init__.py
    │   └── processor.py
    └── view/
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
```

---

## <a name="desarrolladores"></a>Guía para Desarrolladores

### Requisitos del Entorno

* **Python:** 3.11 recomendado.
* **Sistema Operativo:** Windows 10/11.
* **Compilación:** Nuitka.
* **Instalador:** Inno Setup 6.

### Configuración y compilación

1. **Clonar el repositorio**

```bash
git clone https://github.com/RenzoFernando/LectorcitoPro.git
cd LectorcitoPro
```

2. **Preparar entorno**

```batch
.\setupAmp.bat
```

3. **Ejecutar en desarrollo**

```bash
.venv\Scripts\python.exe src/main.py
```

4. **Compilar versión portable**

```batch
.buildportable.bat
```

5. **Compilar instalador**

```batch
.buildinstaller.bat
```

Los artefactos resultantes se generan en la carpeta `downloads/`.

---

## <a name="licencia"></a>Licencia

Este proyecto se distribuye bajo los términos de la **Licencia MIT**.
Copyright © 2026 - Renzo Fernando Mosquera Daza - All Rights Reserved.
