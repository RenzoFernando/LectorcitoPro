# Historial de Versiones

## Versión 0: Funcionalidad Básica
1.  Implementada la lectura recursiva de directorios para archivos de texto (`.txt`, `.py`, etc.).
2.  Desarrollada la concatenación del contenido de los archivos en un único reporte de salida.
3.  Establecido un sistema de nombrado básico para el archivo generado (operación por consola).
4.  Asignada la extensión `.txt` como predeterminada para todos los reportes.
5.  Añadida notificación por consola con la ruta de guardado al finalizar el proceso.

---

## Versión 1: Interfaz Gráfica Inicial
1.  Creada una ventana principal simple con un botón para seleccionar la carpeta de análisis.
2.  Automatizada la generación de reportes en una subcarpeta estándar denominada `Lecturas`.
3.  Implementado un formato de versionado para los archivos de salida: `nombre-carpeta_vN.txt`.
4.  Integrado el ícono de la aplicación (`lector.ico`) en la ventana.
5.  Añadida una barra de progreso indeterminada para feedback visual durante el análisis.

---

## Versión 2: Mejoras de UI y Funcionalidad
1.  Añadido el botón "Seleccionar Ruta de Lecturas" para permitir al usuario definir una ubicación de guardado personalizada.
2.  Implementada la funcionalidad de tema claro/oscuro.
3.  Agregado un enlace funcional al repositorio del proyecto dentro de la interfaz.
4.  Corregida la carga del ícono personalizado (`lector.png`) para asegurar su correcta visualización.
5.  Implementado el botón "Eliminar todas las Lecturas" con su respectivo diálogo de confirmación.
6.  Mejorado el pie de página (footer) con información de créditos.
7.  Realizadas optimizaciones visuales en la paleta de colores, tipografía y distribución de elementos.
8.  Actualizada la barra de progreso a un modo determinado, mostrando el porcentaje de 0 a 100%.
9.  Desarrollado un sistema de notificaciones emergentes (pop-ups) para los siguientes estados:
    * **Éxito:** "¡Listo! El contenido fue guardado correctamente."
    * **Atención:** "Primero debe generar un archivo para poder abrirlo."
    * **Error:** "Ocurrió un error durante el análisis. Intente con otra carpeta."
10. Implementado un pie de página dinámico con información de la aplicación:
    ```
    Lectorcito Pro v*.*
    Desarrollado por: Renzo Fernando Mosquera Daza
    [https://github.com/RenzoFernando/LectorcitoPro.git](https://github.com/RenzoFernando/LectorcitoPro.git)
    © 2025 [github.com/RenzoFernando](https://github.com/RenzoFernando) – All Rights Reserved.
    ```

---

## Versión 3: Personalización y Experiencia de Usuario
1.  Integrado un mensaje de bienvenida dinámico que varía según la hora del día.
2.  Añadido soporte completo para multi-idioma (Español/Inglés).
3.  Implementada la persistencia de preferencias del usuario (rutas, tema, idioma) entre sesiones.
4.  Solucionado un error que ocurría al seleccionar una carpeta tras haber eliminado el directorio `Lecturas`.
5.  Habilitada la configuración de filtros para incluir y excluir extensiones y carpetas específicas.
6.  Añadidos tooltips descriptivos a todos los botones de la barra de configuración lateral.
7.  Ajustada la alineación de las barras laterales para una mayor consistencia visual.
8.  Simplificado el pie de página a un formato de copyright estándar:
    ```
    Copyright © 2025 - Renzo Fernando - All Rights Reserved.
    ```
9.  Mejorada la barra de progreso para un centrado correcto y visualización clara del porcentaje.
10. Creado un encabezado dinámico con saludo y nombre de usuario:
    ```
    LECTORCITO PRO
    Buen@s [momento del día] [usuario], por favor seleccione una opción a realizar.
    ```

---

## Versión 4: Refactorización Arquitectónica y Funciones Clave
1.  Realizada una reorganización completa del código fuente bajo el patrón de arquitectura MVC.
2.  Desarrollada una configuración avanzada e independiente para las reglas de inclusión y exclusión.
3.  Implementada la persistencia de ajustes mediante un archivo JSON estructurado.
4.  Corregida la visualización del ícono de la aplicación para que sea consistente en todas las sub-ventanas.
5.  Añadido un diálogo inicial para que el usuario elija entre usar una ruta de guardado por defecto o seleccionarla cada vez.
6.  Integrado el soporte para cancelar operaciones de lectura en curso de forma segura.
7.  Implementado un manejo especial para archivos multimedia, los cuales ahora se listan en el reporte.
8.  Añadida la funcionalidad para generar una vista de la estructura del proyecto en formato de árbol.
9.  Refinado el manejo de errores para proporcionar mensajes más claros y específicos.
10. Implementado el guardado silencioso de preferencias y un botón para restaurar los ajustes de fábrica.

---

## Versión 5: Roadmap 
1.  Finalizar el centrado y justificación de todos los elementos de la interfaz para una alineación perfecta.
2.  Realizar un rediseño visual de botones y barras laterales, mejorando colores, bordes y efectos `hover`.
3.  Optimizar la claridad y el posicionamiento de los tooltips.
4.  Crear un nuevo selector visual para el idioma y el tema en la pantalla de inicio.
5.  Ampliar la variedad y personalización de los saludos dinámicos.
6.  Mejorar visual y funcionalmente la barra de progreso, añadiendo un GIF para el estado inactivo.
7.  Implementar transiciones suaves y animaciones ligeras para mejorar la experiencia de usuario.
8.  Optimizar la interfaz para un diseño responsivo que se adapte a diferentes resoluciones de pantalla.
9.  Rediseñar los diálogos de configuración ("Ver" / "No Ver") para un estilo más moderno y compacto.
10. Integrar un manual de usuario visual (infografía) accesible desde la aplicación.

---

---

## Versión 6: Rediseño Visual y Optimización de Interfaz
1.  Mejorada integralmente la interfaz de la barra de carga, con un diseño visual integrado y feedback preciso.
2.  Ajustado el tamaño, disposición y orden lógico de los botones principales para mejorar la ergonomía.
3.  Perfeccionada la paleta de colores general, optimizando contrastes y coherencia en temas Claro y Oscuro.
4.  Realizada una mejora visual completa en todos los menús, barras laterales y contenedores de la aplicación.
5.  Acomodados los mensajes emergentes (pop-ups) y estandarizadas sus opciones de cerrado con animaciones fade-out.
6.  Optimizado el comportamiento de las subventanas y ventanas modales para un mejor manejo del foco y la superposición.
7.  Eliminadas opciones antiguas o inutilizables, limpiando la interfaz de elementos redundantes.
8.  Implementadas transiciones visuales suaves en la aparición y desaparición de elementos de la UI.
9.  Actualizados los iconos y recursos gráficos para mantener consistencia con el nuevo estilo moderno.
10. Ajustados los layouts internos para asegurar una alineación y distribución perfecta de todos los componentes.

---

## Versión 7: Funcionalidades Avanzadas y Ecosistema
1.  Implementado un nuevo botón de "Recursos Multimedia" que permite listar archivos binarios sin procesar su contenido.
2.  Mejorada la lógica interna de creación de documentos y optimizado el orden secuencial de lectura de archivos.
3.  Añadido el módulo de "Gestión de Perfiles" con capacidades de guardado y carga de configuraciones personalizadas.
4.  Incorporada la funcionalidad de "Autodetección" inteligente de extensiones para facilitar la configuración de filtros.
5.  Habilitada la opción para generar los reportes finales en formato Markdown (`.md`) además de texto plano.
6.  Sustituida la infografía interna por un enlace directo a la nueva página web de documentación oficial.
7.  Integrados botones en la sección de Ajustes para crear accesos directos (Escritorio, Inicio, Barra de Tareas).
8.  Implementado un sistema de validación para evitar conflictos lógicos entre etiquetas de inclusión y exclusión.
9.  Optimizado el sistema de Tooltips para ofrecer descripciones contextuales en los nuevos elementos de la interfaz.
10. Refactorizado el sistema de persistencia para soportar la estructura compleja de los nuevos perfiles y ajustes.

---

## Versión 8: Calidad, Estabilidad y Distribución Profesional
1.  Reestructurada la infraestructura de ventanas, aperturas y transiciones para lograr una experiencia más limpia, sólida y coherente desde el arranque hasta el cierre de diálogos.
2.  Refinado el flujo visual de inicialización de la aplicación para que la carga se perciba más profesional, reduciendo glitches, saltos y apariciones bruscas.
3.  Optimizadas operaciones clave y vistas pesadas para mejorar la rapidez general de uso en escenarios reales de lectura, navegación y configuración.
4.  Corregidas inconsistencias visuales integrales entre paneles, modales, estados y elementos compartidos de la interfaz.
5.  Fortalecida la presentación profesional del producto mediante metadata más completa para ejecutable, instalador, publicación y distribución.
6.  Implementado empaquetado dual de release con artefacto **portable** y artefacto **instalable**, dejando una distribución más flexible para distintos tipos de usuario.
7.  Mejorada la integración con Windows mediante un flujo más confiable de instalación, accesos directos y comportamiento esperado del sistema operativo.
8.  Actualizada la documentación pública y la landing page para reflejar correctamente la nueva distribución, la release final 8.0.9 y el instalable como opción recomendada.
9.  Integrada la función de exclusión asistida con `.gitignore` dentro del apartado de **Qué No Ver**, reforzando limpieza, precisión y rendimiento al analizar proyectos.
10. Consolidado el cierre estable de la versión 8 con una release final enfocada en calidad, estabilidad, optimización y preparación profesional para producción.