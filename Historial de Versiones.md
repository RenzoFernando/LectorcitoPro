# Historial de Versiones

## Versión 0

1. Lectura recursiva de archivos de texto (`.txt`, `.py`, etc.).
2. Concatenación del contenido en un único archivo de salida.
3. Nombre básico del archivo generado (sin interfaz gráfica).
4. Inclusión de extensión `.txt` predeterminada para el reporte generado.
5. Impresión por consola del path donde se guardó el archivo final.

## Versión 1

1. Ventana simple con botón "Elegir carpeta".
2. Generación del reporte en una carpeta llamada `Lecturas` en la misma ubicación.
3. Nombre del archivo generado con formato `carpeta_vN.txt`.
4. Inclusión del ícono `lector.ico`.
5. Barra de progreso indeterminada.

## Versión 2

1. Botón "Seleccionar Ruta de Lecturas" para elegir la ubicación de la carpeta `Lecturas`.
2. Implementación del modo claro/oscuro.
3. Enlace clickeable al repositorio dentro de la interfaz.
4. Ícono personalizado (`lector.png`) cargado correctamente en la ventana.
5. Botón "Eliminar todas las Lecturas" con confirmación.
6. Mejoras en el pie de página (footer) con créditos.
7. Mejoras visuales en colores, tipografía y distribución.
8. Barra de progreso siempre visible con porcentaje (0–100%).
9. Mensajes emergentes (pop-ups):
   * Éxito: “¡Listo! El contenido fue guardado correctamente.”
   * Atención: “Primero debe generar un archivo para poder abrirlo.”
   * Error: “Ocurrió un error durante el análisis. Intente con otra carpeta.”
10. Pie de página dinámico con número de versión y enlace al repositorio:
 ```
 Lectorcito Pro v*.*  
 Desarrollado por: Renzo Fernando Mosquera Daza  
 https://github.com/RenzoFernando/LectorcitoPro.git  
 © 2025 github.com/RenzoFernando – All Rights Reserved.
 ```

## Versión 3

1. Mensaje de bienvenida dinámico según la hora del día (“¡Buenos días!”, “¡Buenas tardes!”, “¡Buenas noches!”).
2. Soporte multilenguaje (Español/Inglés).
3. Persistencia de preferencias para rutas utilizadas anteriormente.
4. Corrección del error al seleccionar una carpeta después de haber eliminado la carpeta de Lecturas.
5. Posibilidad de configurar libremente:
   * Las extensiones de archivos que se desean leer ("Ver").
   * Las carpetas y extensiones que se desean excluir ("No Ver").
6. Alineación y descripción emergente (tooltip) para los botones de configuración lateral (Ver, No Ver, Guardar preferencias, Tema claro/oscuro, Idioma, GitHub e Información).
7. Barra lateral izquierda ajustada al ancho y altura de los botones laterales derechos.
8. Pie de página simplificado a:
```
Copyright © 2025 - Renzo Fernando - All Rights Reserved.
```
9. Barra de progreso centrada que no sobrepase el 100% y con porcentaje visible debajo.
10. Encabezado centrado dinámico:
```
LECTORCITO PRO  
Buen@s [momento del día] [usuario], por favor seleccione una opción a realizar.
```

## Versión 4

1. Reorganización completa del código usando el patrón MVC (Modelo-Vista-Controlador).
2. Configuración avanzada independiente para carpetas y extensiones ("Ver" / "No Ver").
3. Mejora en la persistencia de ajustes mediante archivo JSON estructurado.
4. Corrección del icono personalizado de la aplicación en todas las ventanas y subventanas emergentes.
5. Pregunta inicial opcional: usar lugar por defecto para guardar los reportes o permitir elegirlo cada vez.
6. Soporte para cancelar una lectura en curso y eliminar archivos interrumpidos.
7. Manejo especial para imágenes (`.png`, `.jpg`, `.svg`, etc.), y demas extensiones multimedia y solo solo mostrar su nombre y extensión.
8. Soporte para estructuras tipo árbol (tree-view) del contenido leído, sin leer archivos.
9. Mejor manejo de errores y mensajes claros en caso de fallos durante el procesamiento.
10. Implementar guardado silencioso de preferencias y añadir botón para restaurar ajustes.

## Versión 5 (En desarrollo)

1. Corrección de alineación y justificación de todos los elementos de la interfaz (centrado total).
2. Rediseño visual de botones y sidebars: colores, bordes, sombras y estados de hover.
3. Mejora en los tooltips y alineación de íconos en barra lateral derecha.
4. Nuevo selector visual de idioma y tema desde el inicio.
5. Mayor variedad y personalización de saludos dinámicos según hora del día.
6. Mejora visual y funcional en la barra de progreso (color, suavidad, animación).
7. Transiciones suaves y efectos en la interfaz (fade in/out o animaciones ligeras).
8. Interfaz optimizada para pantallas pequeñas o resolución variable (responsive).
9. Diálogos “Ver” y “No Ver” con estilo más atractivo y compacto.
10. Manual visual (infografía dentro del programa o accesible desde el botón de información).
