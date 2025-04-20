# Lectorcito Pro

**Versión:** 3  
**Autor:** Renzo Fernando Mosquera Daza & ChatGPT Plus  
**Repositorio:** [https://github.com/RenzoFernando/LectorcitoPro](https://github.com/RenzoFernando/LectorcitoPro)  
© 2025

---

## Descripción

**Lectorcito Pro** es una aplicación de escritorio en Python que facilita la generación de reportes de carpetas completas de código y documentos de texto. Ofrece:

- Interfaz gráfica moderna basada en [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
- Soporte multilenguaje (Español / Inglés).
- Tema claro/oscuro con persistencia de preferencias.
- Configuración de extensiones y carpetas excluidas mediante diálogos personalizados.
- Barra de progreso con porcentaje durante la generación del reporte.
- Sidebars izquierdo y derecho para información de versión y accesos rápidos.
- Icono personalizado para ventana y ejecutable.
- Persistencia de configuración en `~/.lectorcito_cfg.json`.

El objetivo es que puedas alimentar intérpretes de IA o revisar proyectos sin necesidad de copiar/pegar manualmente el contenido de múltiples archivos.

---

## Tabla de Contenidos

1. [Características](#caracter%C3%ADsticas)
2. [Instalación de Dependencias](#instalaci%C3%B3n-de-dependencias)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Configuración](#configuraci%C3%B3n)
5. [Ejecución](#ejecuci%C3%B3n)
6. [Uso de la Aplicación](#uso-de-la-aplicaci%C3%B3n)
7. [Compilación a Ejecutable](#compilaci%C3%B3n-a-ejecutable)
8. [Firma de Ejecutables (Code Signing)](#firma-de-ejecutables-code-signing)
9. [Advertencias y Consejos](#advertencias-y-consejos)
10. [Contribuciones](#contribuciones)
11. [Licencia](#licencia)

---

## Características

- **Selector de Ruta de Lecturas:** Define dónde guardar los reportes.
- **Selector de Carpeta a Leer:** Elige el proyecto o carpeta a analizar.
- **Extensiones Configurables:** Diálogo para indicar qué extensiones de archivo leer (por defecto `.txt, .py, .html, .java, .md, .css`).
- **Carpetas Excluidas Configurables:** Diálogo para indicar qué carpetas omitir (por defecto `__pycache__, venv, .git`, etc.).
- **Reporte Detallado:** Archivo `.txt` con la ruta relativa y contenido completo de cada archivo.
- **Barra de Progreso con %:** Indicador visual del avance durante el análisis.
- **Botones de Acceso Rápido:** Abrir último archivo generado o carpeta de reportes.
- **Sidebar Izquierdo:** Texto vertical con versión de la aplicación.
- **Sidebar Derecho:** Botones rápidos para preferencias, tema, idioma, GitHub e información.
- **Tema Claro/Oscuro:** Toggle que persiste en configuración.
- **Multilenguaje (ES/EN):** Toggle que persiste en configuración.
- **Metadatos Dinámicos:** Versión y año dinámicos definidos en variables.
- **Iconos y Ventana:** Usa `lector.ico` y `lector.png` para personalizar la ventana y el ejecutable.
- **Persistencia de Configuración:** Archivo JSON en el home del usuario.

---

## Instalación de Dependencias

Requisitos mínimos:

- **Python 3.7+** (probado con 3.13)  
- **Windows 10+** (recomendado)  

Instala las librerías necesarias:

```bash
python -m pip install customtkinter pillow pyinstaller
```

---

## Estructura del Proyecto

```
LectorcitoPro/
├── build/                   # Carpeta temporal de PyInstaller
├── dist/                    # Ejecutable generado
├── recursos/               # Iconos (.ico, .png) y recursos estáticos
├── Lecturas/                # Carpeta de reportes (se crea al ejecutar)
├── Lectorcito_GUI_Pro_CT.py # Código fuente principal
├── README.md                # Documentación del proyecto
├── .gitignore               # Archivos/carpetas ignorados por Git
└── Lectorcito_GUI_Pro_CT.spec # Especificación generada por PyInstaller
```

---

## Configuración

Al primer arranque, se genera `~/.lectorcito_cfg.json` con valores por defecto. Puedes editarlo manualmente o usar los diálogos:

```json
{
  "lecturas_path": "",         
  "EXTENSIONES_TEXTO": [".txt",".py",".html",".java",".md",".css"],
  "CARPETAS_EXCLUIDAS": ["__pycache__","venv",".git"],
  "theme": "Light",
  "lang": "es"
}
```

- **lecturas_path:** Ruta donde se crean las carpetas y archivos de reporte.
- **theme:** `Light` o `Dark`.
- **lang:** `es` o `en`.

---

## Ejecución

### Como Script

```bash
python Lectorcito_GUI_Pro_CT.py
```

### Como Ejecutable

```bash
dist\Lectorcito_GUI_Pro_CT.exe
```

La ventana se abrirá en modo claro y en el idioma configurado.

---

## Uso de la Aplicación

1. **Seleccionar Ruta de Lecturas:** Permite cambiar dónde se guardarán los reportes.
2. **Elegir Carpeta a Leer:** Selecciona el directorio a analizar; inicia el proceso si ya definiste la ruta de lecturas.
3. **Monitorear Progreso:** La barra y el porcentaje indican el avance.
4. **Abrir Archivo Generado:** Clic para abrir el último reporte.
5. **Abrir Carpeta de Reportes:** Abre directamente la carpeta `Lecturas`.
6. **Eliminar Reportes:** Borra toda la carpeta `Lecturas` (confirmación previa).
7. **Sidebar Derecho:** Accesos rápidos a configuración de extensiones, carpetas excluidas, tema, idioma, GitHub e información.

---

## Compilación a Ejecutable

Desde PowerShell o CMD en la raíz del proyecto:

```powershell
python -m PyInstaller --onefile --noconsole --icon=recursos\lector.ico --add-data "recursos;recursos" Lectorcito_GUI_Pro_CT.py
```

- **--onefile:** Empaqueta todo en un único `.exe`.
- **--noconsole:** Oculta la consola de Python.
- **--icon:** Incluye el icono `lector.ico` en el ejecutable.
- **--add-data:** Copia el directorio `recursos` para que la app cargue iconos en runtime.

El ejecutable resultante queda en `dist/Lectorcito_GUI_Pro_CT.exe`.

---

## Firma de Ejecutables (Code Signing)

Para distribuir sin alertas de seguridad, firma tu `.exe` con un certificado de firma de código:

1. **Genera un certificado raíz y uno de firma** (o adquiere uno de una CA confiable).
2. **Exporta tu PFX** con contraseña.  
3. **Usa `signtool.exe`:**
   ```powershell
   & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign \
     /sha1 <TU_THUMBPRINT> \
     /fd SHA256 \
     /tr http://timestamp.digicert.com \
     /td SHA256 \
     dist\Lectorcito_GUI_Pro_CT.exe
   ```
4. **Verifica:**
   ```powershell
   signtool verify /pa /v dist\Lectorcito_GUI_Pro_CT.exe
   ```

> **Consejo:** Para que Windows confíe en tu certificado raíz, impórtalo en `Cert:\LocalMachine\Root`.

---

## Advertencias y Consejos

- Si la ventana muestra un icono distinto, borra la caché de iconos de Windows o reinicia.
- Elimina `build/` y `dist/` antes de volver a compilar para evitar conflictos.
- Cierra todas las instancias antes de recompilar para evitar bloqueos de archivo.
- Se recomienda usar Python oficial de [python.org] para evitar problemas de App Store.

---

## Contribuciones

1. Haz fork del repositorio.
2. Crea una rama descriptiva (`feature/tu-función`).
3. Realiza cambios y commits claros.
4. Abre un Pull Request.

¡Todas las mejoras son bienvenidas!

---

## Licencia

Este proyecto está licenciado bajo la [MIT License](https://opensource.org/licenses/MIT).  

