import os
import sys
from time import sleep

# ==============================================================================
# LECTORCITO.PY (VERSIÓN DE CONSOLA MEJORADA)
# ==============================================================================
# Este script lee de forma recursiva una carpeta y genera un reporte de texto
# consolidado, utilizando la misma lógica de formato y filtrado que la
# aplicación LectorcitoPro.
#
# Para personalizar qué se lee y qué se ignora, edite el diccionario
# de CONFIGURACIÓN que se encuentra a continuación.
# ==============================================================================


# --- CONFIGURACIÓN DE LECTURA ---
# Edite estas listas para controlar el comportamiento del script.
CONFIG = {
    # Carpetas a resaltar en el reporte.
    "etiquetas_carpetas_importantes": [
        {"nombre": "src", "estado": "activo"}
    ],
    # Extensiones de archivo a leer.
    "etiquetas_extensiones_incluidas": [
        {"nombre": ".txt", "estado": "activo"},
        {"nombre": ".py", "estado": "activo"},
        {"nombre": ".html", "estado": "activo"},
        {"nombre": ".java", "estado": "activo"},
        {"nombre": ".md", "estado": "activo"},
        {"nombre": ".css", "estado": "activo"},
        {"nombre": ".js", "estado": "activo"},
        {"nombre": ".json", "estado": "activo"}
    ],
    # Carpetas a ignorar por completo durante la lectura.
    "etiquetas_carpetas_excluidas": [
        {"nombre": "__pycache__", "estado": "activo"},
        {"nombre": "env", "estado": "activo"},
        {"nombre": "venv", "estado": "activo"},
        {"nombre": ".venv", "estado": "activo"},
        {"nombre": ".git", "estado": "activo"},
        {"nombre": "build", "estado": "activo"},
        {"nombre": "dist", "estado": "activo"},
        {"nombre": ".idea", "estado": "activo"}
    ],
    # Archivos específicos a ignorar por su nombre completo.
    "etiquetas_archivos_excluidos": [
        {"nombre": "Pipfile.lock", "estado": "activo"},
        {"nombre": "package.json", "estado": "activo"},
        {"nombre": "package-lock.json", "estado": "activo"}
    ],
    # Extensiones de archivos multimedia y otros binarios que no se leen pero se listan.
    "media_extensions": [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp',
        '.mp4', '.mkv', '.avi', '.mov', '.webm', '.mp3', '.wav', '.flac', '.ogg',
        '.zip', '.rar', '.7z', '.tar', '.gz', '.pdf', '.doc', '.docx', '.xls',
        '.xlsx', '.ppt', '.pptx', '.exe', '.dll', '.bin', '.iso', '.so', '.dylib'
    ]
}


def _get_active_tags(key: str) -> set:
    """Extrae los nombres de las etiquetas activas desde la configuración."""
    tag_list = CONFIG.get(key, [])
    return {tag['nombre'] for tag in tag_list if tag.get('estado') == 'activo'}


def _count_files_to_process(folder: str) -> int:
    """Cuenta los archivos a procesar aplicando las reglas de exclusión."""
    file_count = 0
    extensions_to_include = _get_active_tags("etiquetas_extensiones_incluidas")
    extensions_to_check = extensions_to_include.union(set(CONFIG.get("media_extensions", [])))
    folders_to_exclude = _get_active_tags("etiquetas_carpetas_excluidas")
    files_to_exclude = _get_active_tags("etiquetas_archivos_excluidos")

    try:
        for root, dirs, files in os.walk(folder, topdown=True):
            dirs[:] = [d for d in dirs if d not in folders_to_exclude]
            for filename in files:
                if filename in files_to_exclude:
                    continue
                if any(filename.lower().endswith(ext) for ext in extensions_to_check):
                    file_count += 1
    except OSError as e:
        print(f"Error al contar archivos en {folder}: {e}")
        return 0
    return file_count


def generar_reporte_consola(source_folder: str):
    """
    Función principal que genera el reporte consolidado para la carpeta especificada.
    """
    print("Analizando proyecto...")
    total_files = _count_files_to_process(source_folder)
    if total_files == 0:
        print("❌ No se encontraron archivos válidos para procesar con la configuración actual.")
        return

    # Obtiene los filtros activos.
    important_folders = _get_active_tags("etiquetas_carpetas_importantes")
    text_ext = _get_active_tags("etiquetas_extensiones_incluidas")
    media_ext = set(CONFIG.get("media_extensions", []))
    excluded_folders = _get_active_tags("etiquetas_carpetas_excluidas")
    excluded_files = _get_active_tags("etiquetas_archivos_excluidos")

    folder_name = os.path.basename(os.path.normpath(source_folder))
    output_dir = os.path.join(os.getcwd(), "Lecturas")
    os.makedirs(output_dir, exist_ok=True)

    version = 1
    while True:
        report_filename = f"{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_dir, report_filename)
        if not os.path.exists(final_report_path):
            break
        version += 1

    processed_files = 0
    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            # Escribe el encabezado del reporte.
            outfile.write("=" * 80 + "\n")
            outfile.write(f" LECTORCITO PRO - REPORTE DE PROYECTO\n")
            outfile.write(f" PROYECTO: {folder_name}\n")
            outfile.write(f" RUTA: {os.path.abspath(source_folder)}\n")
            outfile.write("=" * 80 + "\n\n")

            for root, dirs, files in os.walk(source_folder, topdown=True):
                dirs[:] = [d for d in dirs if d not in excluded_folders]
                files.sort()

                files_in_dir = []
                for filename in files:
                    if filename in excluded_files:
                        continue
                    is_text = any(filename.lower().endswith(ext) for ext in text_ext)
                    is_media = any(filename.lower().endswith(ext) for ext in media_ext)
                    if is_text or is_media:
                        files_in_dir.append((filename, is_text, is_media))

                if not files_in_dir:
                    continue

                relative_path = os.path.relpath(root, source_folder)
                folder_name_display = relative_path if relative_path != '.' else 'RAÍZ DEL PROYECTO'
                highlight = " [IMPORTANTE]" if os.path.basename(root) in important_folders else ""
                outfile.write(f"■ CARPETA: {folder_name_display}{highlight}\n")
                outfile.write(f"└" + ("─" * 78) + "\n\n")

                for filename, is_text, is_media in files_in_dir:
                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    # Muestra el progreso en la consola.
                    sys.stdout.write(f"\rProcesando: [{processed_files}/{total_files}] {progress:.1f}% - {filename}...")
                    sys.stdout.flush()

                    file_path = os.path.join(root, filename)
                    outfile.write(f"  ● Archivo: {filename}\n")

                    if is_text:
                        outfile.write("    " + ("-" * 74) + "\n")
                        outfile.write("    >> INICIO DEL CONTENIDO\n\n")
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                for line in infile:
                                    outfile.write(f"    {line}")
                        except Exception as e:
                            outfile.write(f"    [Error al leer el archivo: {e}]\n")
                        outfile.write(f"\n\n    << FIN DEL CONTENIDO\n")
                        outfile.write("    " + ("-" * 74) + "\n\n\n")
                    elif is_media:
                        outfile.write("\n")

        # Mensaje final de éxito.
        sys.stdout.write("\n")  # Nueva línea después de la barra de progreso.
        print("\n✅ ¡Reporte generado con éxito!")
        print(f"   El archivo ha sido guardado en: {os.path.abspath(final_report_path)}")

    except Exception as e:
        print(f"\n❌ Error crítico al generar el reporte: {e}")
        if os.path.exists(final_report_path):
            os.remove(final_report_path)


if __name__ == "__main__":
    print("--- Lectorcito (Versión de Consola) ---")
    try:
        ruta_carpeta = input("🔎 Ingrese la ruta de la carpeta del proyecto a analizar: ").strip()
        if os.path.isdir(ruta_carpeta):
            generar_reporte_consola(ruta_carpeta)
        else:
            print("❌ La ruta proporcionada no es un directorio válido.")
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\nHa ocurrido un error inesperado: {e}")

