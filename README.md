
# Lectorcito Pro

**Lectorcito Pro** es una aplicación de escritorio desarrollada en Python que utiliza la librería [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) para ofrecer una interfaz gráfica moderna, limpia y funcional. La aplicación permite seleccionar una carpeta, recorrer y leer el contenido de archivos de código o texto (de acuerdo a las extensiones configurables) y generar un reporte completo en un archivo de texto. Además, incluye opciones para abrir el reporte generado y la carpeta de salida.

> **Objetivo:**  
> Facilitar la tarea de leer código o documentos cuando se requiere alimentar intérpretes de IA sin necesidad de copiar y pegar el contenido de múltiples archivos de forma manual.

---

## Tabla de Contenidos

- [Características](#características)
- [Requisitos y Dependencias](#requisitos-y-dependencias)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Uso](#uso)
- [Compilación a Ejecutable](#compilación-a-ejecutable)
- [Advertencias y Recomendaciones](#advertencias-y-recomendaciones)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

---

## Características

- **Selector de Carpeta:**  
  Permite al usuario elegir una carpeta mediante un explorador de archivos.

- **Recorrido Recursivo:**  
  Lee de forma recursiva todos los archivos con extensiones configuradas (por ejemplo, `.txt`, `.py`, `.html`, `.java`, `.md`, `.css`) y omite aquellas carpetas que no se desean analizar (como `__pycache__`, `venv`, `.git`, etc.).

- **Reporte Completo:**  
  Genera un archivo de reporte que incluye el contenido completo de cada archivo leído, mostrando además la ruta relativa del archivo respecto a la carpeta seleccionada.

- **Barra de Progreso:**  
  Se muestra una barra de progreso durante la generación del reporte para informar al usuario del avance del proceso.

- **Botones de Acceso Rápido:**  
  - **Abrir Archivo Generado:** Permite visualizar el reporte directamente.
  - **Abrir Carpeta de Salida:** Abre la carpeta donde se almacenan los reportes.

- **Icono Personalizado:**  
  El ejecutable se compila con un icono personalizado (`lector.ico`) y, opcionalmente, la ventana usa `lector.png` para mejorar la apariencia.  
  > **Nota:** Debido a la forma en que Tkinter maneja los iconos, es posible que la ventana en ejecución muestre otro icono (esto puede solucionarse borrando la caché de iconos o reiniciando Windows).

- **Portabilidad:**  
  El proyecto está preparado para funcionar en cualquier equipo, ya que la carpeta de salida se crea de forma relativa a la ubicación del script o ejecutable.

---

## Requisitos y Dependencias

**Requisitos de Sistema:**

- **Sistema Operativo:** Windows (se recomienda Windows 10 o superior)
- **Python:** Se recomienda usar Python 3.13 (o versiones 3.x compatibles).  
  > **Importante:** Se recomienda descargar Python desde [python.org](https://www.python.org/downloads/windows/) y asegurarse de que la instalación se agregue al `PATH`.

**Dependencias:**

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)  
- [Pillow](https://pypi.org/project/Pillow/)  
- [PyInstaller](https://www.pyinstaller.org/)

Para instalar todas las dependencias, usa:

```bash
python -m pip install customtkinter pillow pyinstaller
```

---

## Estructura del Proyecto

La estructura recomendada del proyecto es la siguiente:

```
LectorcitoPro/
├── build/                   # Carpeta generada por PyInstaller (archivo temporario)
├── dist/                    # Carpeta que contendrá el ejecutable generado
├── Lecturas/                # Carpeta de salida para los reportes (se crea automáticamente)
├── Lectorcito_GUI_Pro_CT.py # Código fuente principal
├── Lectorcito_GUI_Pro_CT.spec  # Archivo de especificaciones generado por PyInstaller
├── lector.ico               # Icono usado para el ejecutable y la ventana
├── lector.png               # (Opcional) Imagen PNG para el icono de la ventana
├── README.md                # Este archivo
└── .gitignore               # Archivo para ignorar archivos/carpetas innecesarias en Git
```

> **Importante:** La carpeta `Lecturas/` se crea automáticamente en la misma ubicación que el script (o ejecutable) y se utiliza para guardar los reportes generados.

---

## Instalación

1. **Clona el repositorio** (o descarga el ZIP):

   ```bash
   git clone https://github.com/RenzoFernando/LectorcitoPro.git
   ```

2. **Accede a la carpeta del proyecto:**

   ```bash
   cd LectorcitoPro
   ```

3. **Instala las dependencias:**

   ```bash
   python -m pip install customtkinter pillow pyinstaller
   ```

---

## Uso

### Ejecución en Modo Script

Para ejecutar la aplicación desde el código fuente, en la raíz del proyecto:

```bash
python Lectorcito_GUI_Pro_CT.py
```

La aplicación se abrirá en **modo claro** y podrás seleccionar una carpeta para analizar. El reporte se generará en la carpeta `Lecturas/`.

### Funciones Principales

- **Elegir Carpeta:**  
  Selecciona la carpeta a analizar a través de un explorador de archivos.

- **Reporte:**  
  La aplicación recorre todos los archivos (de las extensiones configuradas) en la carpeta seleccionada y crea un archivo de reporte que incluye la ruta relativa y el contenido completo de cada archivo.

- **Abrir Reporte:**  
  Botón que permite abrir el archivo de reporte generado.

- **Abrir Carpeta de Reportes:**  
  Botón que abre la carpeta `Lecturas/` donde se almacenan los reportes.

---

## Compilación a Ejecutable

Para compilar la aplicación a un ejecutable (.exe) utilizando PyInstaller:

1. **Verifica que estás usando la instalación de Python correcta:**

   ```bash
   where python
   python --version
   ```

2. **Desde la raíz del proyecto, ejecuta el siguiente comando en CMD o PowerShell:**

   ```powershell
   python -m PyInstaller --onefile --noconsole --icon=lector.ico Lectorcito_GUI_Pro_CT.py
   ```

   Esto generará una carpeta `dist/` en la que se encontrará el ejecutable `Lectorcito_GUI_Pro_CT.exe`.

---

## Advertencias y Recomendaciones

- **Iconos en la Ventana:**  
  Es posible que la ventana de la aplicación muestre un icono distinto al establecido en el ejecutable. Este comportamiento se debe a cómo Tkinter maneja los iconos y la caché de Windows. Si no se actualiza, prueba borrar la caché de iconos o reiniciar el sistema.

- **Caché de Compilación:**  
  Si realizas cambios en el código y recompilas, elimina las carpetas `build/` y `dist/` para evitar conflictos.

- **Permisos:**  
  Asegúrate de cerrar cualquier instancia del ejecutable antes de recompilar; de lo contrario, podrías recibir errores por acceso denegado.

- **Ruta de Salida (Lecturas/):**  
  La carpeta de reportes se crea de forma relativa a la ubicación del script o ejecutable, haciendo el proyecto portable para cualquier usuario que lo descargue desde GitHub.

- **Compatibilidad:**  
  Este proyecto ha sido probado con Python 3.13 y CustomTkinter. Se recomienda utilizar Python descargado desde python.org para evitar problemas con la versión de Microsoft Store.

---

## Contribuciones

Si deseas contribuir a este proyecto, sigue estos pasos:

1. Haz un **fork** del repositorio.
2. Crea una nueva rama para tu función o arreglo:
   ```bash
   git checkout -b feature/nueva-función
   ```
3. Realiza tus cambios y haz commits descriptivos.
4. Envía un **pull request** para revisión.

¡Todas las mejoras y correcciones son bienvenidas!

---
¡Disfruta de Lectorcito Pro y muchas gracias por usarlo!