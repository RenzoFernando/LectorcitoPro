from model.markdown_renderer import MarkdownReportRenderer
from model.txt_renderer import TextReportRenderer


_RENDERERS = {
    ".md": MarkdownReportRenderer,
    ".txt": TextReportRenderer,
}


def get_report_renderer(report_extension: str, outfile, labels: dict[str, str]):
    renderer_class = _RENDERERS.get(report_extension, MarkdownReportRenderer)
    return renderer_class(outfile, labels)
