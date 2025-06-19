import os
import threading


def count_files(folder: str, text_extensions: list[str], media_extensions: list[str], excludes: list[str]) -> int:
    """Cuenta el número total de archivos a procesar (texto y media)."""
    file_count = 0
    all_extensions = text_extensions + media_extensions
    try:
        for root, dirs, files in os.walk(folder, topdown=True):
            dirs[:] = [d for d in dirs if d not in excludes]
            for filename in files:
                if any(filename.lower().endswith(ext) for ext in all_extensions):
                    file_count += 1
    except OSError:
        return 0
    return file_count


def generate_report(
        source_folder: str,
        output_path: str,
        extensions: list[str],
        media_extensions: list[str],
        excludes: list[str],
        cancel_event: threading.Event,  # Parámetro para la cancelación
        progress_callback: callable = None
) -> tuple[str, str | None]:
    """
    Genera el reporte. Devuelve una tupla (status, path).
    Status puede ser: 'success', 'cancelled', 'no_files', 'error'.
    """
    total_files = count_files(source_folder, extensions, media_extensions, excludes)
    if total_files == 0:
        return "no_files", None

    folder_name = os.path.basename(os.path.normpath(source_folder))
    version = 1
    while True:
        report_filename = f"{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path):
            break
        version += 1

    processed_files = 0
    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            outfile.write(f"REPORTE DE ARCHIVOS EN: {source_folder}\n\n")

            for root, dirs, files in os.walk(source_folder, topdown=True):
                if cancel_event.is_set(): break

                dirs[:] = [d for d in dirs if d not in excludes]
                files.sort()

                # Para escribir el nombre de la carpeta solo si tiene contenido relevante
                rel_root = os.path.relpath(root, source_folder)
                files_in_folder = [f for f in files if
                                   any(f.lower().endswith(ext) for ext in extensions + media_extensions)]
                if not files_in_folder: continue

                outfile.write(f"Carpeta: {rel_root}\n")

                for filename in files:
                    if cancel_event.is_set(): break

                    file_path = os.path.join(root, filename)
                    is_text = any(filename.lower().endswith(ext) for ext in extensions)
                    is_media = any(filename.lower().endswith(ext) for ext in media_extensions)

                    if not (is_text or is_media): continue

                    processed_files += 1
                    relative_file_path = os.path.relpath(file_path, source_folder)

                    outfile.write(f"    Archivo: {relative_file_path}\n")

                    if is_text:
                        outfile.write(f"    {'-------- CONTENIDO --------'}\n")
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                outfile.write(infile.read())
                            outfile.write("\n")  # Asegura un salto de línea
                        except Exception as e:
                            outfile.write(f"    [Error leyendo el archivo: {e}]\n")
                        outfile.write(f"    {'-------- FIN --------'}\n\n")

                    if progress_callback:
                        progress_callback((processed_files / total_files) * 100)
                else:  # Este else pertenece al for de `files`
                    continue  # Continúa el loop principal si el for interno no fue interrumpido
                break  # Interrumpe el loop principal si el for interno lo fue

    except Exception as e:
        print(f"Error al generar el reporte: {e}")
        # Si el error ocurre después de abrir el archivo, intentamos borrar el archivo parcial
        if 'outfile' in locals() and not outfile.closed:
            outfile.close()
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        return "error", None

    # --- Lógica de limpieza post-proceso ---
    if cancel_event.is_set():
        # No necesitamos cerrar el 'outfile' aquí, el `with` ya lo hizo, incluso si hubo un break.
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        return "cancelled", None

    return "success", final_report_path
