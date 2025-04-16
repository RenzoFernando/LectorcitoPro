import os

EXTENSIONES_TEXTO = ['.txt', '.py', '.html', '.java', '.md', '.css']
CARPETAS_EXCLUIDAS = ['__pycache__', 'venv', '.venv', 'migrations', '.git']  # Puedes agregar aquí las carpetas a ignorar

def recorrer_carpeta(ruta_actual, archivo_salida, nivel=0):
    indent = " " * nivel  # Sangría para mostrar jerarquía
    carpeta_nombre = os.path.basename(ruta_actual)

    # Ignorar si la carpeta está en la lista de excluidas
    if carpeta_nombre in CARPETAS_EXCLUIDAS:
        archivo_salida.write(f"{indent}⚠️ Carpeta ignorada: {carpeta_nombre}\n")
        return

    archivo_salida.write(f"{indent} Carpeta: {carpeta_nombre}\n")

    try:
        elementos = sorted(os.listdir(ruta_actual))
    except Exception as e:
        archivo_salida.write(f"{indent}[Error al listar {ruta_actual}]: {e}\n")
        return

    for nombre in elementos:
        ruta_completa = os.path.join(ruta_actual, nombre)
        if os.path.isdir(ruta_completa):
            recorrer_carpeta(ruta_completa, archivo_salida, nivel + 1)
        elif os.path.isfile(ruta_completa):
            ext = os.path.splitext(nombre)[1].lower()
            if ext in EXTENSIONES_TEXTO:
                try:
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    archivo_salida.write(f"{indent}     Archivo: {nombre} ({ext})\n")
                    archivo_salida.write(f"{indent}    -------- CONTENIDO --------\n")
                    for linea in contenido.splitlines():
                        archivo_salida.write(f"{indent}    {linea}\n")
                    archivo_salida.write(f"{indent}    -------- FIN DEL ARCHIVO --------\n\n")
                except Exception as e:
                    archivo_salida.write(f"{indent}    [Error leyendo {nombre}]: {e}\n\n")

def guardar_contenido_completo(ruta_principal, nombre_base="total_codigo_del_proyecto_", extension=".txt"):
    version = 1
    # Construimos el nombre completo inicial
    nombre_salida = f"{nombre_base}v.{version}{extension}"
    ruta_salida = os.path.join(ruta_principal, nombre_salida)
    
    # Si ya existe, aumentamos la versión hasta encontrar un nombre que no exista
    while os.path.exists(ruta_salida):
        version += 1
        nombre_salida = f"{nombre_base} v.{version}{extension}"
        ruta_salida = os.path.join(ruta_principal, nombre_salida)
        
    with open(ruta_salida, "w", encoding="utf-8") as salida:
        salida.write(f"REPORTE DE ARCHIVOS DE TEXTO EN: {ruta_principal}\n\n")
        recorrer_carpeta(ruta_principal, salida)

    print(f"\n✅ Todo el contenido ha sido guardado en:\n{ruta_salida}")

# Ejecución
if __name__ == "__main__":
    ruta = input("🔎 Ingresa la ruta de la carpeta principal: ").strip()
    if os.path.isdir(ruta):
        guardar_contenido_completo(ruta)
    else:
        print("❌ La ruta proporcionada no es válida.")
