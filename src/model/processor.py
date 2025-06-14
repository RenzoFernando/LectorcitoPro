import os


def count_files(folder: str, extensions: list[str], excludes: list[str]) -> int:

    file_count = 0
    try:
        for root, dirs, files in os.walk(folder, topdown=True):
            # Modifica la lista de directorios en el lugar para que os.walk no los recorra
            dirs[:] = [d for d in dirs if d not in excludes]

            for filename in files:
                if any(filename.lower().endswith(ext) for ext in extensions):
                    file_count += 1
    except OSError:
        return 0  # Devuelve 0 si la carpeta no es accesible
    return file_count


def generate_report(
        source_folder: str,
        output_path: str,
        extensions: list[str],
        excludes: list[str],
        progress_callback: callable = None
) -> str | None:
    total_files = count_files(source_folder, extensions, excludes)
    if total_files == 0:
        return None

    # --- Generar nombre de archivo con versión ---
    folder_name = os.path.basename(os.path.normpath(source_folder))
    version = 1
    while True:
        report_filename = f"{folder_name}_v{version}.txt"
        final_report_path = os.path.join(output_path, report_filename)
        if not os.path.exists(final_report_path):
            break
        version += 1

    # --- Procesar archivos y escribir reporte ---
    processed_files = 0
    try:
        with open(final_report_path, "w", encoding="utf-8") as outfile:
            outfile.write(f"REPORTE DE ARCHIVOS EN: {source_folder}\n\n")

            for root, dirs, files in os.walk(source_folder, topdown=True):
                dirs[:] = [d for d in dirs if d not in excludes]

                # Ordena los archivos para un reporte consistente
                files.sort()

                relative_root = os.path.relpath(root, source_folder)
                # No escribir "Carpeta: ." para el directorio raíz
                if relative_root != ".":
                    outfile.write(f"Carpeta: {relative_root}\n")

                for filename in files:
                    if any(filename.lower().endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, filename)
                        relative_file_path = os.path.relpath(file_path, source_folder)

                        outfile.write(f"    Archivo: {relative_file_path}\n")
                        outfile.write(f"    {'-' * 20} CONTENIDO {'-' * 20}\n")
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                                for line in infile:
                                    outfile.write(f"    {line}")
                        except Exception as e:
                            outfile.write(f"    [Error leyendo el archivo: {e}]\n")
                        outfile.write(f"\n    {'=' * 20} FIN {'=' * 25}\n\n")

                        processed_files += 1
                        if progress_callback:
                            # Calcula el porcentaje y llama al callback
                            percentage = (processed_files / total_files) * 100
                            progress_callback(percentage)

    except Exception as e:
        # Si hay un error de escritura, elimina el archivo parcial y devuelve None
        if os.path.exists(final_report_path):
            os.remove(final_report_path)
        print(f"Error al generar el reporte: {e}")
        return None

    return final_report_path
