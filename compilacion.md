### GUÍA MAESTRA DE USO Y SOLUCIÓN DE PROBLEMAS

---

#### 1. Requisitos Previos (Solo una vez)

* **Python:** Debes tener **Python 3.11** instalado (NO uses 3.13 ni 3.14). Asegúrate de marcar "Add Python to PATH" al instalar.
* **Internet:** Necesario la primera vez para bajar librerías y herramientas de compilación.

---

#### 2. Pasos de Ejecución (Flujo Normal)

1. **Instalar/Resetear Entorno:**
* Ejecuta `setup_amp.bat`. En la carpeta raiz del proyecto.
* Si todo sale bien, dirá `[5/5] Entorno listo`.


2. **Compilar:**
* Ejecuta `build.bat`. En la carpeta raiz del proyecto.
* Si pregunta `Proceed and download? [Yes]/No`, escribe **Yes** y Enter.
* Al finalizar, dirá `Compilacion exitosa!`.


3. **Firmar:**
* Abre PowerShell como administrador en la ruta de la carpeta raiz del proyecto.
* Ejecuta este comando para permisos: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force`
* Ejecuta: `.\firmar_aplicacion.ps1`


4. **Distribuir:**
* Copia el archivo `LectorcitoPro.exe` que está en la carpeta `downloads/`.
* **Importante:** Borra la carpeta `recursos_certificado`.

---

#### 3. Solución de Problemas (Manual de Emergencia)

**Caso A: Nuitka falla descargando GCC / MinGW64 (Error: Timeout / ReadTimeoutError)**

* **Síntoma:** Barra de descarga en 0% o error rojo al ejecutar `build.bat`.
* **Solución:**
1. Descarga este archivo ZIP: [Link GCC MinGW64](https://github.com/brechtsanders/winlibs_mingw/releases/download/14.2.0posix-19.1.1-12.0.0-msvcrt-r2/winlibs-x86_64-posix-seh-gcc-14.2.0-llvm-19.1.1-mingw-w64msvcrt-12.0.0-r2.zip)
2. Presiona `Win + R` y pega: `%LOCALAPPDATA%\Nuitka\Nuitka\Cache\downloads\gcc\x86_64\14.2.0posix-19.1.1-12.0.0-msvcrt-r2\`
3. Pega el ZIP descargado dentro de esa carpeta.
4. Ejecuta `build.bat` de nuevo.



**Caso B: Nuitka falla descargando Dependency Walker (Error: Depends.exe)**

* **Síntoma:** Error casi al final de `build.bat` pidiendo `depends.exe`.
* **Solución:**
1. Descarga este ZIP: [Link Dependency Walker](https://www.google.com/url?sa=E&source=gmail&q=http://dependencywalker.com/depends22_x64.zip)
2. Presiona `Win + R` y pega: `%LOCALAPPDATA%\Nuitka\Nuitka\Cache\downloads\depends\x86_64\`
3. **Descomprime** el ZIP ahí. Debe quedar el archivo `depends.exe` visible.
4. Ejecuta `build.bat` de nuevo.



**Caso C: "UnauthorizedAccess" al firmar**

* **Solución:** No olvides ejecutar el comando mágico antes de firmar:  
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force`

---

#### 4. Como correr los archivos

* **setup_amp.bat:** Configura o resetea el entorno de compilación.

```
    .\setup_amp.bat
```

* **build.bat:** Compila el proyecto.

```
    .\build.bat
```

* **firmar_aplicacion.ps1:** Firma digitalmente el ejecutable.

```
    .\firmar_aplicacion.ps1
```

