<div align="center">
  <h1>Lectorcito Pro</h1>

  <img src="https://raw.githubusercontent.com/RenzoFernando/LectorcitoPro/main/resources/branding/lector.png" alt="Logo de Lectorcito Pro" width="175">
  <br>
  <p>
    <a href="https://github.com/RenzoFernando/LectorcitoPro/releases/latest">
      <img src="https://img.shields.io/github/v/release/RenzoFernando/LectorcitoPro?style=for-the-badge&label=VERSION%20Actual&color=blue" alt="Release Actual">
    </a>
    <a href="https://github.com/RenzoFernando/LectorcitoPro/releases/latest">
      <img src="https://img.shields.io/badge/VER%20RELEASES-2E9D46?style=for-the-badge" alt="Ver releases">
    </a>
    <a href="https://renzofernando.github.io/LectorcitoPro/">
      <img src="https://img.shields.io/badge/VER%20PÁGINA%20Y%20DESCARGAR-2F6FE4?style=for-the-badge" alt="Abrir página oficial y descargar">
    </a>
    <br>
    <br>
    <strong>
      Herramienta de escritorio para auditoría de código, documentación técnica y consolidación de contextos para Inteligencia Artificial.
    </strong>
  </p>
</div>

---

## Descripción

**Lectorcito Pro** es una aplicación de escritorio para Windows y Linux desarrollada en Python. Analiza proyectos de software de forma recursiva, organiza su estructura y consolida el contenido relevante en reportes TXT o Markdown listos para revisión, documentación o uso como contexto para modelos de Inteligencia Artificial.

Está orientada a desarrolladores que necesitan:

* Consolidar proyectos completos en un único reporte legible.
* Preparar contexto limpio para LLMs como GPT, Claude o Gemini.
* Aplicar reglas de inclusión, exclusión y manejo de archivos multimedia.
* Generar documentación técnica o vistas de estructura sin recorrer manualmente cada carpeta.
* Reutilizar configuraciones mediante perfiles.

---

## Distribución

Lectorcito Pro se publica en tres formatos oficiales:

* **Windows — Instalable:** `LectorcitoPro-Setup.exe`  
  Opción recomendada para uso habitual en Windows. Integra la aplicación mediante un instalador y facilita el acceso desde el sistema.

* **Windows — Portable:** `LectorcitoPro-Portable.exe`  
  Ejecutable independiente que puede utilizarse directamente sin instalación.

* **Linux — Portable:** `LectorcitoPro-Linux-x86_64`  
  Binario único para Linux x86_64. No requiere instalador adicional y puede necesitar permiso de ejecución después de la descarga.

La descarga para usuarios finales se realiza desde la **página oficial**. GitHub Releases se mantiene como canal de publicación del proyecto.

---

## Características Técnicas

* **Arquitectura MVC** con separación entre interfaz, control, procesamiento, renderizado, internacionalización y servicios de plataforma.
* **Análisis recursivo de proyectos** con lectura y consolidación del contenido relevante.
* **Salida TXT y Markdown** para distintos flujos de documentación y análisis.
* **Filtros configurables** para Qué Ver, Qué No Ver y archivos Multimedia.
* **Compatibilidad con `.gitignore`** como apoyo para excluir contenido innecesario.
* **Generación de estructura de árbol** sin necesidad de leer el contenido de los archivos.
* **Gestión de perfiles** para guardar y reutilizar configuraciones.
* **Interfaz con tema claro y oscuro**, soporte de Español e Inglés y adaptación DPI.
* **Procesamiento asíncrono y cancelación segura** durante operaciones de lectura.
* **Soporte para Windows y Linux** con artefactos de distribución independientes.

---

## Desarrollo

### Requisitos básicos

* Python 3.11, 3.12 o 3.13.
* Git.
* Para el release integral desde Windows: Inno Setup 6 y WSL con una distribución Linux compatible.

### Preparar el entorno

```bash
git clone https://github.com/RenzoFernando/LectorcitoPro.git
cd LectorcitoPro
python -m pip install -r requirements.txt
```

### Generar el release completo

Desde Windows:

```powershell
.\release.bat
```

La documentación técnica detallada se mantiene en:

* [`docs/compilation.md`](docs/compilation.md) — compilación, dependencias, firma, builds y proceso de release.
* [`docs/versionHistory.md`](docs/versionHistory.md) — historial de versiones y evolución del proyecto.

---

## Autor y Licencia

**Autor:** Renzo Fernando Mosquera Daza

Este proyecto se distribuye bajo los términos de la **Licencia MIT**. Consulta el archivo [`LICENSE`](LICENSE) para conocer los términos completos.

Copyright © 2026 - Renzo Fernando Mosquera Daza - All Rights Reserved.
