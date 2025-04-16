# Lectorcito Pro

**Lectorcito Pro** es una aplicación de escritorio desarrollada en Python que utiliza la librería [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) para ofrecer una interfaz gráfica moderna y limpia. La aplicación permite seleccionar una carpeta, recorrer y leer el contenido de archivos de código/texto (con extensiones configurables) y guardar la información en un archivo de reporte que se almacena en una carpeta de salida especificada. 

Perfecta y pensada para enviarle en formato .txt o texto normal a cualquier intérprete de IA para leer código sin tener que hacer el proceso de copiar y pegar de los múltiples archivos manualmente

## Funcionalidades

- **Selector de carpeta**: El usuario puede elegir una carpeta a analizar mediante un explorador de archivos.
- **Recorrido recursivo**: Lee todos los archivos con extensiones configuradas, omitiendo carpetas excluidas (como `__pycache__`, `venv`, `.git`, etc.).
- **Reporte completo**: El contenido de cada archivo se guarda en un archivo de reporte, mostrando la ruta relativa de cada archivo respecto a la carpeta seleccionada.
- **Barra de progreso**: Se muestra una barra de progreso durante la generación del reporte.
- **Abrir archivo generado**: Botón para abrir el reporte generado.
- **Abrir carpeta de salida**: Botón para abrir la carpeta donde se almacenan los reportes.
- **Icono personalizado**: La aplicación utiliza un icono personalizado para el ejecutable (`lector.ico`).  
  > **Advertencia:** Aunque el ejecutable tenga el icono correcto en el Explorador de Windows, al ejecutarlo la ventana puede mostrar otro icono (esto se debe a la forma en que Tkinter gestiona los iconos y puede requerir borrar la caché de iconos o reiniciar Windows para que se vea actualizado).

## Estructura del proyecto

La estructura básica del proyecto es la siguiente:

```
LectorcitoPro/
├── build/                   # Carpeta generada por PyInstaller
├── dist/                    # Carpeta generada por PyInstaller con el ejecutable
├── Lecturas/                # Carpeta de salida para los reportes (se crea si no existe)
├── Lectorcito_GUI_Pro_CT.py # Código fuente principal de Lectorcito Pro
├── Lectorcito_GUI_Pro_CT.spec  # Archivo spec generado por PyInstaller
├── lector.ico               # Icono usado para el ejecutable y la ventana
├── lector.png               # (Opcional) Imagen PNG para el icono de la ventana
├── README.md                # Este archivo
└── .gitignore               # Archivo para ignorar archivos/ carpetas innecesarias en Git
```

> **Nota:** La carpeta `Lecturas/` se crea al iniciar la aplicación si no existe y se usa para guardar los archivos de reporte. Se configura para que, si ya existe, se continúe utilizándola sin volver a crearla.

## Instalación y dependencias

Asegúrate de tener instalada la siguiente versión de **Python 3.x** (se recomienda Python 3.13, pero versiones anteriores funcionan también) y de contar con los siguientes módulos:

- **CustomTkinter**: Para la interfaz gráfica.
- **Pillow**: Para manejar imágenes y iconos.
- **PyInstaller**: Para compilar el proyecto a un ejecutable (.exe).

Para instalar las dependencias, ejecuta:

```bash
python -m pip install customtkinter pillow pyinstaller
```

> Si usas la versión de Python de Microsoft Store, recuerda que podrían presentarse inconvenientes; se recomienda instalar Python desde [python.org](https://www.python.org/downloads/windows/) y agregarlo al PATH.

## Uso

1. **Ejecutar la aplicación en modo script**:
   ```bash
   python Lectorcito_GUI_Pro_CT.py
   ```
2. **Compilar a ejecutable** con PyInstaller. Desde PowerShell o CMD, en la raíz del proyecto ejecuta:
   
   ```powershell
   python -m PyInstaller --onefile --noconsole --icon=lector.ico Lectorcito_GUI_Pro_CT.py
   ```
   Esto generará el ejecutable en la carpeta `dist/`.

3. **Ejecutar el ejecutable**:
   - Al abrir, la aplicación se mostrará en **modo claro**, proximamente cambio a modo oscuro.
   - Selecciona una carpeta a analizar.
   - Se generará un reporte completo (con todas las líneas de cada archivo) en la carpeta `Lecturas/`.
   - Usa los botones para abrir el reporte o la carpeta de salida.

## Advertencias y recomendaciones

- **Iconos en la ventana**: Es normal que, en algunos entornos, la ventana de la aplicación muestre un icono diferente al asignado. Esto se debe a la caché de iconos de Windows. Si el icono no se actualiza, prueba a borrar la caché de iconos o reiniciar el sistema.
- **Caché de compilación**: Si realizas cambios y recompilas, elimina las carpetas `build/` y `dist/` para evitar posibles conflictos.
- **Gestión de permisos**: Asegúrate de cerrar cualquier instancia previa del ejecutable antes de recompilar, ya que de lo contrario podrías obtener errores de "Access Denied" al intentar sobrescribir el archivo.
- **Ruta de salida**: La carpeta de reportes (`Lecturas/`) se crea automáticamente al iniciar la aplicación si no existe. Si la carpeta ya existe, se utilizará sin intentar recrearla.

## Contribuciones

Si deseas mejorar este proyecto, puedes hacer fork del mismo y enviar tus pull requests. ¡Toda mejora es bienvenida!

---

¡Disfruta de Lectorcito Pro y muchas gracias por usarlo!
