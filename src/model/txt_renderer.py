from model.report_model import ReportFile, ReportFolder, ReportProject


class TextReportRenderer:
    def __init__(self, outfile, labels: dict[str, str]):
        self.outfile = outfile
        self.labels = labels

    def write_header(self, title: str, project: ReportProject):
        self.outfile.write("=" * 80 + "\n")
        self.outfile.write(f" {title}\n")
        self.outfile.write(f" {self.labels['project'].format(project.name)}\n")
        self.outfile.write(f" {self.labels['path'].format(project.source_path)}\n")
        self.outfile.write("=" * 80 + "\n\n")

    def write_toc(self, project: ReportProject):
        return None

    def write_folder(self, folder: ReportFolder):
        folder_display = folder.relative_path if folder.relative_path else self.labels["root"]
        highlight = self.labels["important"] if folder.important else ""
        self.outfile.write(f"{self.labels['folder'].format(folder_display)}{highlight}\n")
        self.outfile.write("└" + ("─" * 78) + "\n\n")

    def write_file(self, report_file: ReportFile):
        self.outfile.write(f"{self.labels['file'].format(report_file.filename)}\n")
        self.outfile.write(f"{self.labels['file_path'].format(report_file.relative_path)}\n")

        if report_file.is_media:
            self.outfile.write("\n")
            return

        self.outfile.write("    " + ("-" * 74) + "\n")
        self.outfile.write(f"{self.labels['content_start'].format(report_file.filename)}\n\n")

        if report_file.read_error is not None:
            self.outfile.write(f"{self.labels['read_error'].format(report_file.read_error)}\n")
        else:
            content = report_file.content or ""
            for line in content.splitlines(keepends=True):
                self.outfile.write(f"    {line}")

        self.outfile.write(f"\n\n{self.labels['content_end'].format(report_file.filename)}\n")
        self.outfile.write("    " + ("-" * 74) + "\n\n\n")

    def write_tree(self, title: str, project_name: str, source_path: str, tree_text: str):
        self.outfile.write(tree_text)
