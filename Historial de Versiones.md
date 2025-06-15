# Historial de Versiones

## Versión 0
1. Lectura recursiva de archivos de texto (`.txt`, `.py`, etc.).
2. Concatenación de contenido en un único archivo de salida.
3. Nombre básico del reporte sin interfaz gráfica.

## Versión 1
1. Ventana simple con botón "Elegir carpeta".
2. Generación de reporte en carpeta `Lecturas` dentro de la misma ruta.
3. Nombres de archivo con formato `carpeta_vN.txt`.
4. Inclusión de icono `lector.ico`.
5. Barra de progreso indeterminada.

## Versión 2
1. Botón "Seleccionar Ruta de Lecturas": permite elegir dónde crear la carpeta `Lecturas`.  
2. Modo claro/oscuro.  
3. Enlace clickable al repositorio en la ventana.  
4. Icono de ventana (`lector.png`) cargado correctamente.  
5. Botón "Eliminar todas las Lecturas".  
6. Mejoras en el footer de créditos.  
7. Ajustes visuales (colores, fuentes).  
8. Barra de progreso siempre visible con porcentaje (0–100%).  
9. Mensajes emergentes (pop-ups) para:
   - Éxito: “¡Listo! El contenido fue guardado correctamente.”
   - Atención: “Primero debe generar un archivo para poder abrirlo.”
   - Error: “Ocurrió un error durante el análisis. Intente con otra carpeta.”
10. Pie de página con versión dinámica y enlace URL:
    ```
    Lectorcito Pro v*.*  
    Desarrollado por: Renzo Fernando Mosquera Daza y ChatGPT Plus  
    https://github.com/RenzoFernando/LectorcitoPro.git  
    © 2025 github.com/RenzoFernando – All Rights Reserved.
    ```

## Versión 3  
1. Mensaje de bienvenida dinámico según hora del día: “¡Buenos días/tardes/noches!”.  
2. Soporte multilenguaje (Español / Inglés).  
3. Alineación y espaciado del pie de página optimizados.
4. Que guarde las preferencias antes utilizadas en rutas.
5. Solucionar error de Seleccionar carpeta a leer cuando se acabade de eliminar la carpeta de lecturas
6. Libertad de elejir que EXTENSIONES_TEXTO (boton de que leer) puede reconocer y cuales no (boton de que no leer), asi mismo tambien con CARPETAS_EXCLUIDAS
7. Botón de que leer, que no leer, guardar preferencias, modo oscuro-claro, traduccion, gitHub e info. todos alineados a la derecha. Y al pasar sobre ellos descripcion de lo que hacen
8. Barra a la izquierda del ancho de los botones de la derecha y largo segun el primier y ultimo boton de la derecha
9. cambiar pie de pagina por: 
      "Copyright © - 2025 - Renzo Fernando - All Rights Reserved."
10. Bara de progreso centrada que no pase de 100%, y el porcentaje debajo de la barra
11. Encabezado centrado con:
      "LECTORCITO PRO"
      "Buen@s #####,  por favor seleccione una opción a realizar"
   dependiendo de la hora segun punto 2.
12. Cambiar y actualizar README

## Versión 4 [Proximamente, en desarrollo]
1. Cambiar el repositorio a MVC (Modelo Vista Controlador) para una mejor organización del código.
2. Arreglar alineacion y justificación (centrados) de la app
3. Ajustar el color de los botones y barra laterales
4. Mas ajutes de traducción
5. Ver y No Ver para carpetas y extensiones de archivos
6. Mejorar la UI de Ver y No Ver
7. Buen guardado de los ajustes de JSON
8. Preguntar si definir un lugar por defecto de guardado de las Lecturas o elejir uno propio con posibilidad de siempre cambiarlo
9.  Arreglo del icono de la aplicacion en todas sus ventanas
10.  Mejorar la barra de carga
11.  Añadir generador arbol de estructura de raiz a partir de una dirección de carpeta (lectura de carpetas y ya)
12.  Si hay cualquier imagen (png, jpg, svg, etc) solo poner el nombre la la imagen y su extesion pero nunca leerlas
13.  Manual de uso de la aplicasion (una imagen infografia con las instrucciones)
14.  Añadir mas saludos dependiendo de la hora
