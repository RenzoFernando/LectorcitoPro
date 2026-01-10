
<div align="center">
  <img src="https://raw.githubusercontent.com/RenzoFernando/LectorcitoPro/main/recursos/lector.png" alt="Logo de Lectorcito Pro" width="150">
  <h1>Lectorcito Pro</h1>
  <p>
    <strong>Versión Actual: 6.0.0</strong><br>
    Una herramienta de escritorio profesional para analizar y consolidar proyectos de código fuente en reportes unificados.
  </p>
  <a href="https://github.com/RenzoFernando/LectorcitoPro/releases/latest">
    <img src="https://img.shields.io/github/v/release/RenzoFernando/LectorcitoPro?style=for-the-badge&label=Descargar%20%C3%9Altima%20Versi%C3%B3n" alt="Descargar Última Versión">
  </a>
</div>

---

## Descripción

**Lectorcito Pro** es una aplicación de escritorio para Windows, desarrollada en Python, que permite a los usuarios analizar de forma recursiva cualquier directorio de proyecto. La herramienta escanea las carpetas y archivos, y consolida todo el contenido de texto y código fuente en un único reporte `.txt` bien formateado.

Esta utilidad es ideal para generar vistas completas de un proyecto, ya sea para auditorías de código, creación de documentación técnica o para preparar el contexto necesario para análisis con herramientas de Inteligencia Artificial.

## Tabla de Contenidos

1.  [Uso de la Aplicación](#uso)
2.  [Características Principales](#caracteristicas)
3.  [Estructura del Proyecto](#estructura)
4.  [Versiones Disponibles](#versiones)
5.  [Sistema de Configuración](#configuracion)
6.  [Guía para Desarrolladores](#desarrolladores)
7.  [Licencia](#licencia)

---

## <a name="uso"></a>Uso de la Aplicación

El uso de **Lectorcito Pro** está diseñado para ser directo y no requiere instalación.

1.  **Acceder al Ejecutable:**
    Navegue a la carpeta `descargas/` que se encuentra en el repositorio.

2.  **Ejecutar la Aplicación:**
    Haga doble clic en el archivo `LectorcitoPro.exe`. La aplicación se iniciará, mostrando la interfaz principal.

3.  **Generar un Reporte:**
    * **Generar Lectura Completa:** Es el botón principal. Al presionarlo, podrá seleccionar una o múltiples carpetas para analizar. La aplicación procesará los archivos y generará el reporte `.txt`.
    * **Crear Estructura de Árbol:** Genera un archivo de texto que muestra únicamente la estructura de carpetas y archivos del proyecto seleccionado.

4.  **Configurar la Aplicación:**
    Utilice los iconos de la barra lateral derecha para personalizar el comportamiento de la aplicación. Puede configurar:
    * **Filtros de "Ver" y "No Ver":** Para incluir o excluir carpetas y tipos de archivo.
    * **Tema:** Alternar entre los modos, claro y oscuro.
    * **Idioma:** Cambiar entre Español e Inglés.
    * **Restaurar:** Volver a la configuración de fábrica.

Una vez generado un reporte, este se guardará en una carpeta llamada `Lecturas`, creada automáticamente por la aplicación.

---

## <a name="caracteristicas"></a>Características Principales

* **Análisis Recursivo de Proyectos:** Navega por la estructura completa de un directorio para identificar y procesar archivos relevantes.
* **Generación de Reportes Consolidados:** Une el contenido de múltiples archivos en un único `.txt` formateado, preservando la estructura y el nombre de cada archivo y carpeta.
* **Interfaz Gráfica Intuitiva:** Desarrollada con CustomTkinter, ofrece una experiencia de usuario moderna y personalizable con temas claro y oscuro.
* **Alta Personalización de Filtros:** Permite al usuario definir con precisión:
    * **Carpetas a incluir:** Para destacar directorios importantes (ej. `src`).
    * **Extensiones a leer:** Para especificar qué tipo de archivos procesar (ej. `.py`, `.html`, `.css`).
    * **Carpetas a excluir:** Para ignorar directorios como `node_modules`, `.venv` o `__pycache__`.
    * **Archivos a excluir:** Para omitir archivos específicos por su nombre (ej. `.env`, `package-lock.json`).
* **Soporte Multi-idioma:** Interfaz disponible en Español e Inglés.
* **Procesamiento Asíncrono:** Las tareas de análisis se ejecutan en hilos separados para mantener la interfaz receptiva, con opción de cancelación.
* **Feedback Visual Avanzado:** Barra de progreso animada, GIF de estado y notificaciones emergentes para informar sobre el estado de las operaciones.
* **Generación de Árbol de Directorios:** Funcionalidad para crear un reporte de texto que visualiza la estructura de carpetas del proyecto.
* **Persistencia de Configuración:** Guarda automáticamente las preferencias del usuario para una experiencia consistente entre sesiones.

---

## <a name="estructura"></a>Estructura del Proyecto
```
LectorcitoPro/
├── GuíaCertificados.md
├── Historial de Versiones.md
├── README.md
├── descargas
│   ├── Lectorcito.py
│   └── LectorcitoPro.exe
├── recursos
├── recursos_externos
├── requirements.txt
└── src
    ├── config.py
    ├── controller
    │   ├── controller.py
    │   └── handlers.py
    ├── main.py
    ├── model
    │   └── processor.py
    ├── utils.py
    └── view
        ├── dialogs.py
        ├── tags_dialog.py
        ├── tooltip.py
        ├── translations.py
        └── ui.py
```

---

## <a name="versiones"></a>Versiones Disponibles

La carpeta `descargas/` contiene dos versiones de la aplicación para distintos casos de uso:

* **Versión Pro (`LectorcitoPro.exe`):**
    * **Uso Recomendado:** Para la mayoría de los usuarios.
    * **Descripción:** Es un ejecutable que no requiere instalación. Provee una interfaz gráfica completa desde donde se pueden configurar todas las opciones de manera visual, como los filtros de inclusión/exclusión, el idioma y el tema.

* **Versión Básica (`Lectorcito.py`):**
    * **Uso:** Para desarrolladores o para ejecuciones rápidas desde la terminal.
    * **Descripción:** Es un script de Python que se ejecuta en la consola. Requiere que los filtros (extensiones y carpetas excluidas) se modifiquen directamente en el código fuente del archivo.

---

## <a name="configuracion"></a>Sistema de Configuración

La aplicación guarda todas las preferencias del usuario en un archivo `config.json`. Este archivo se ubica automáticamente en el directorio estándar de configuración de aplicaciones del sistema operativo (gestionado por `appdirs`), garantizando que no se creen archivos innecesarios en la carpeta del programa.

Para restaurar la configuración original, se puede usar el botón "Restaurar Ajustes" en la barra lateral o eliminar manualmente dicho archivo de configuración.

---

## <a name="desarrolladores"></a>Guía para Desarrolladores

Instrucciones para compilar desde el código fuente

  ### Arquitectura del Software
  El proyecto sigue el patrón de diseño **Modelo-Vista-Controlador (MVC)** para garantizar una separación clara de responsabilidades, facilitar la mantenibilidad y promover la escalabilidad.

  * **Modelo (`src/model`):** Contiene la lógica de negocio, incluyendo el análisis de archivos y el procesamiento de directorios.
  * **Vista (`src/view`):** Compuesta por los elementos de la interfaz de usuario.
  * **Controlador (`src/controller`):** Actúa como intermediario entre el Modelo y la Vista.

  ### Puesta en Marcha del Entorno
  1.  **Requisitos:** Python 3.7+ y `git`.
  2.  **Clonar el Repositorio:**
      ```bash
      git clone [https://github.com/RenzoFernando/LectorcitoPro.git](https://github.com/RenzoFernando/LectorcitoPro.git)
      cd LectorcitoPro
      ```
  3.  **Configurar el Entorno Virtual y Dependencias:** Ejecute el script por lotes que automatiza el proceso:
      ```batch
      setup_amp.bat
      ```
  4.  **Ejecutar la Aplicación:**
      ```bash
      python src/main.py
      ```

  ### Compilación
  Para generar el archivo `.exe`, ejecute el script de compilación:
  ```batch
  build.bat
  ```
  Este se encargará de todo el proceso con PyInstaller y dejará el ejecutable final en la carpeta `descargas/`.



---

## <a name="licencia"></a>Licencia

Este proyecto se distribuye bajo los términos de la **Licencia MIT**.  
Copyright © 2025 - Renzo Fernando Mosquera Daza.
