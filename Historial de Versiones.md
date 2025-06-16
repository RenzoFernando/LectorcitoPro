# Historial de Versiones

## Versión 0

1. Lectura recursiva de archivos de texto (`.txt`, `.py`, etc.).
2. Concatenación del contenido en un único archivo de salida.
3. Nombre básico del archivo generado (sin interfaz gráfica).

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
3. Optimización del alineado y espaciado en el pie de página.
4. Persistencia de preferencias para rutas utilizadas anteriormente.
5. Corrección del error al seleccionar una carpeta después de haber eliminado la carpeta de Lecturas.
6. Posibilidad de configurar libremente:

   * Las extensiones de archivos que se desean leer ("Ver").
   * Las carpetas y extensiones que se desean excluir ("No Ver").
7. Alineación y descripción emergente (tooltip) para los botones de configuración lateral (Ver, No Ver, Guardar preferencias, Tema claro/oscuro, Idioma, GitHub e Información).
8. Barra lateral izquierda ajustada al ancho y altura de los botones laterales derechos.
9. Pie de página simplificado a:
```
Copyright © 2025 - Renzo Fernando - All Rights Reserved.
```
10. Barra de progreso centrada que no sobrepase el 100% y con porcentaje visible debajo.
11. Encabezado centrado dinámico:
```
LECTORCITO PRO  
Buen@s [momento del día] [usuario], por favor seleccione una opción a realizar.
```
12. Actualización completa del archivo `README.md`.

## Versión 4 (Próximamente, en desarrollo)

1. Reorganización completa del código usando el patrón MVC (Modelo-Vista-Controlador).
2. Corrección de alineación y justificación de elementos en la interfaz (centrados).
3. Ajuste y mejora del color y estilo de los botones y barras laterales.
4. Ajustes adicionales en la traducción Español/Inglés.
5. Configuración avanzada independiente para carpetas y extensiones ("Ver"/"No Ver").
6. Mejora significativa en la interfaz de los diálogos "Ver" y "No Ver".
7. Mejora en la persistencia de ajustes mediante archivo JSON.
8. Pregunta inicial opcional: usar lugar por defecto para guardar los reportes o permitir al usuario elegirlo libremente cada vez.
9. Corrección del icono personalizado de la aplicación en todas las ventanas y subventanas emergentes.
10. Mejora visual y funcional en la barra de progreso.
11. Función adicional: Generar una estructura tipo árbol (tree-view) mostrando solo la jerarquía de carpetas y archivos según Ver y No Ver.
12. Manejo especial para imágenes (png, jpg, svg, etc.): solo mostrar su nombre y extensión, nunca incluir su contenido en el reporte.
13. Creación de un manual de usuario visual (infografía con instrucciones claras sobre cómo usar la aplicación).
14. Más variedad de saludos dinámicos según la hora del día.
15. Facilidad para cancelar una lectura en curso y limpiar lo no terminado.
