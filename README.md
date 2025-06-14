
# Lectorcito Pro

**Versión:** 4.0  
**Autor:** Renzo Fernando Mosquera Daza & ChatGPT Plus  
**Repositorio:** https://github.com/RenzoFernando/LectorcitoPro  
© 2025

---

## 📖 Descripción

**Lectorcito Pro** es una herramienta en Python que genera un único reporte `.txt` a partir de todo el contenido de una carpeta de código y texto. Se ofrece en dos versiones:

- **Básica (`.py`)**: script solo por consola (`descargas/Lectorcito.py`), requiere editar manualmente las extensiones y carpetas excluidas.  
- **Pro (`.exe`)**: ejecutable con GUI (CustomTkinter) para configurar extensiones, exclusiones, tema y idioma desde la interfaz.

---

## 📑 Tabla de Contenidos

1. [Características](#características)  
2. [Instalación](#instalación)  
3. [Estructura de Proyecto](#estructura-de-proyecto)  
4. [Descargas](#descargas)   
5. [Ejecución](#ejecución)  
6. [Compilación a Ejecutable](#compilación-a-ejecutable)  
7. [Firma de Ejecutables (Code Signing)](#firma-de-ejecutables-code-signing)  
8. [Advertencias y Consejos](#advertencias-y-consejos)  
9. [Contribuciones](#contribuciones)  
10. [Licencia](#licencia)

---

## 🚀 Características

- **Arquitectura MVC** bien separada (`src/config.py`, `src/controller/`, `src/model/`, `src/view/`).  
- **Extensiones y exclusiones** personalizables en tiempo de ejecución.  
- **Multilenguaje (ES/EN)** y **tema claro/oscuro** con persistencia.  
- **Barra de progreso** con porcentaje real.  
- **Sidebars**: izquierda (versión vertical), derecha (atajos a configuración, GitHub, info).  
- **Carpeta `descargas/`** con los binarios `.py` y `.exe`.  
- **Interfaz GUI** Pro para usuarios finales; **script básico** para desarrolladores.  
- **Persistencia** de preferencias en JSON (`appdirs`).

---

## 🔧 Instalación

**Requisitos mínimos**:

- Python 3.7+  
- Windows 10+ (recomendado para GUI)

Instala dependencias:

```bash
pip install -r requirements.txt
````

---

## 📂 Estructura de Proyecto

```
LectorcitoPro/
├── descargas/               # Lectorcito.py (básico) y LectorcitoPro.exe (Pro)
├── recursos/                
├── recursos_externos/      
├── src/
│   ├── config.py           
│   ├── utils.py            
│   ├── main.py              
│   ├── controller/
│   ├── model/
│   └── view/
├── requirements.txt
├── setup_amp.bat            
├── .gitignore
└── README.md
```

---

## 📥 Descargas

* **Versión básica** (`descargas/Lectorcito.py`):

  * Ejecuta en consola y edita en código las listas `EXTENSIONES_TEXTO` y `CARPETAS_EXCLUIDAS`.
* **Versión Pro** (`descargas/LectorcitoPro.exe`):

  * Todo configurable desde la GUI: extensiones, exclusiones, ruta de reportes, tema e idioma.

---

## ▶️ Ejecución

* **Básica**:

  ```bash
  python descargas/Lectorcito.py
  ```

* **Pro**:

  ```bash
  descargas\LectorcitoPro.exe
  ```

---

## 🛠️ Compilación a Ejecutable

```powershell
python -m PyInstaller --onefile --noconsole `
  --icon=recursos\lector.ico `
  --add-data "recursos;recursos" `
  src/main.py
```

---

## 🔐 Firma de Ejecutables (Code Signing)

Para distribuir sin alertas de seguridad, firma tu `.exe` con un certificado de firma de código:

1. **Genera un certificado raíz y uno de firma** (o adquiere uno de una CA confiable).

2. **Exporta tu PFX** con contraseña fuerte.

3. **Usa `signtool.exe`:**

   ```powershell
   & "C:\Program Files (x86)\Windows Kits\10\bin\<versión>\x64\signtool.exe" sign `
     /sha1 <TU_THUMBPRINT> `
     /f recursos_externos\MiCertificado.pfx `
     /p TuContraseña `
     /fd SHA256 `
     /tr http://timestamp.digicert.com `
     /td SHA256 `
     descargas\LectorcitoPro.exe
   ```

4. **Verifica:**

   ```powershell
   signtool verify /pa /v descargas\LectorcitoPro.exe
   ```

> **Consejo:** Importa tu CA raíz en `Cert:\LocalMachine\Root` para confianza global.

---

## ⚠️ Advertencias y Consejos

* Limpia `build/` y `dist/` antes de recompilar.
* Cierra instancias antes de sobrescribir el `.exe`.
* Protege tu `.pfx` en un lugar seguro (HSM, USB cifrado).
* En la versión `.py`, revisa rutas y extensiones tras cada cambio.

---

## 🤝 Contribuciones

1. Haz **fork** del repositorio.
2. Crea una rama descriptiva (`feature/tu-función`).
3. Realiza cambios y commits claros.
4. Abre un **Pull Request**.

---

## 📄 Licencia

Este proyecto está licenciado bajo la **MIT License**.
