from __future__ import annotations

import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_URL = "https://renzofernando.github.io/LectorcitoPro/"


def normalize_text(value: str) -> str:
    return " ".join(value.split())


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.h1_parts: list[list[str]] = []
        self.meta: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.json_ld: list[str] = []
        self.faq_items: list[dict[str, str]] = []
        self._in_title = False
        self._current_h1: list[str] | None = None
        self._json_ld_parts: list[str] | None = None
        self._faq_depth = 0
        self._faq_question_parts: list[str] | None = None
        self._faq_answer_parts: list[str] | None = None
        self._capture_faq_question = False
        self._capture_faq_answer = False

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {key: value or "" for key, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = self._attrs(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._current_h1 = []
        elif tag == "meta":
            self.meta.append(data)
        elif tag == "link":
            self.links.append(data)
        elif tag == "img":
            self.images.append(data)
        elif tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self._json_ld_parts = []

        if self._faq_depth == 0 and "data-faq-item" in data:
            self._faq_depth = 1
            self._faq_question_parts = []
            self._faq_answer_parts = []
        elif self._faq_depth > 0:
            self._faq_depth += 1

        if self._faq_depth > 0 and tag == "h3":
            self._capture_faq_question = True
        elif self._faq_depth > 0 and tag == "p":
            self._capture_faq_answer = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "h1" and self._current_h1 is not None:
            self.h1_parts.append(self._current_h1)
            self._current_h1 = None
        elif tag == "script" and self._json_ld_parts is not None:
            self.json_ld.append("".join(self._json_ld_parts))
            self._json_ld_parts = None

        if self._faq_depth > 0:
            if tag == "h3":
                self._capture_faq_question = False
            elif tag == "p":
                self._capture_faq_answer = False
            self._faq_depth -= 1
            if self._faq_depth == 0:
                self.faq_items.append(
                    {
                        "question": normalize_text("".join(self._faq_question_parts or [])),
                        "answer": normalize_text("".join(self._faq_answer_parts or [])),
                    }
                )
                self._faq_question_parts = None
                self._faq_answer_parts = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._current_h1 is not None:
            self._current_h1.append(data)
        if self._json_ld_parts is not None:
            self._json_ld_parts.append(data)
        if self._capture_faq_question and self._faq_question_parts is not None:
            self._faq_question_parts.append(data)
        if self._capture_faq_answer and self._faq_answer_parts is not None:
            self._faq_answer_parts.append(data)

    @property
    def title(self) -> str:
        return normalize_text("".join(self.title_parts))

    @property
    def h1s(self) -> list[str]:
        return [normalize_text("".join(parts)) for parts in self.h1_parts]


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def meta_content(parser: PageParser, *, name: str | None = None, prop: str | None = None) -> str:
    for meta in parser.meta:
        if name is not None and meta.get("name", "").lower() == name.lower():
            return meta.get("content", "")
        if prop is not None and meta.get("property", "").lower() == prop.lower():
            return meta.get("content", "")
    return ""


def link_href(parser: PageParser, rel: str) -> str:
    for link in parser.links:
        rel_tokens = link.get("rel", "").lower().split()
        if rel.lower() in rel_tokens:
            return link.get("href", "")
    return ""


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_json_ld(parser: PageParser, errors: list[str], label: str) -> list[dict]:
    result: list[dict] = []
    for raw in parser.json_ld:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as error:
            fail(errors, f"{label}: JSON-LD inválido: {error}")
            continue
        if isinstance(parsed, dict):
            result.append(parsed)
    return result


def iter_schema_nodes(documents: list[dict]):
    for document in documents:
        yield document
        graph = document.get("@graph")
        if isinstance(graph, list):
            for node in graph:
                if isinstance(node, dict):
                    yield node


def validate_index(errors: list[str]) -> None:
    path = ROOT / "index.html"
    parser = parse_page(path)

    if not parser.title:
        fail(errors, "index.html: falta <title>.")
    if len(parser.h1s) != 1:
        fail(errors, f"index.html: debe existir exactamente un H1; encontrados {len(parser.h1s)}.")
    elif parser.title == parser.h1s[0]:
        fail(errors, "index.html: el H1 no debe ser una copia exacta del meta-título.")

    description = meta_content(parser, name="description")
    if len(description) < 80:
        fail(errors, "index.html: la meta description es inexistente o demasiado corta.")
    if meta_content(parser, name="robots").lower().find("index") < 0:
        fail(errors, "index.html: falta una directiva robots indexable.")
    if link_href(parser, "canonical") != CANONICAL_URL:
        fail(errors, "index.html: canonical incorrecta.")

    for property_name in ("og:title", "og:description", "og:url", "og:image"):
        if not meta_content(parser, prop=property_name):
            fail(errors, f"index.html: falta {property_name}.")
    for name in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
        if not meta_content(parser, name=name):
            fail(errors, f"index.html: falta {name}.")

    if not link_href(parser, "manifest"):
        fail(errors, "index.html: falta el manifest.")

    for image in parser.images:
        if "alt" not in image:
            fail(errors, f"index.html: imagen sin alt: {image.get('src', '<sin src>')}")

    documents = load_json_ld(parser, errors, "index.html")
    types = {node.get("@type") for node in iter_schema_nodes(documents)}
    for expected_type in ("WebSite", "SoftwareApplication", "FAQPage"):
        if expected_type not in types:
            fail(errors, f"index.html: falta structured data {expected_type}.")

    faq_schema = next(
        (node for node in iter_schema_nodes(documents) if node.get("@type") == "FAQPage"), None
    )
    if faq_schema is None:
        return

    schema_items = []
    for item in faq_schema.get("mainEntity", []):
        if not isinstance(item, dict):
            continue
        answer = item.get("acceptedAnswer", {})
        schema_items.append(
            {
                "question": normalize_text(str(item.get("name", ""))),
                "answer": normalize_text(str(answer.get("text", ""))) if isinstance(answer, dict) else "",
            }
        )
    if schema_items != parser.faq_items:
        fail(errors, "index.html: la FAQ visible no coincide exactamente con FAQPage JSON-LD.")

    source = path.read_text(encoding="utf-8")
    if "mobile-sticky-cta" not in source:
        fail(errors, "index.html: falta CTA móvil fijo.")
    if "data-share" not in source:
        fail(errors, "index.html: falta el control de compartir.")
    if re.search(r'resources/icons/[^"\']+\.png', source, flags=re.IGNORECASE):
        fail(errors, "index.html: todavía referencia PNG dentro de resources/icons.")

    for link in re.findall(r'href=["\']([^"\']+)["\']', source, flags=re.IGNORECASE):
        if link.lower().endswith(".html"):
            fail(errors, f"index.html: enlace interno con extensión .html: {link}")


def validate_404(errors: list[str]) -> None:
    source = (ROOT / "404.html").read_text(encoding="utf-8")
    parser = parse_page(ROOT / "404.html")
    if '<base href="/LectorcitoPro/"' not in source:
        fail(errors, "404.html: falta la base del sitio para resolver recursos desde rutas anidadas.")
    if not parser.title or parser.title == "Lectorcito Pro | Auditoría de código y contexto para IA":
        fail(errors, "404.html: necesita un meta-título propio.")
    if len(parser.h1s) != 1:
        fail(errors, f"404.html: debe existir exactamente un H1; encontrados {len(parser.h1s)}.")
    if not meta_content(parser, name="description"):
        fail(errors, "404.html: falta meta description.")
    robots = meta_content(parser, name="robots").lower()
    if "noindex" not in robots:
        fail(errors, "404.html: debe ser noindex.")
    for image in parser.images:
        if "alt" not in image:
            fail(errors, f"404.html: imagen sin alt: {image.get('src', '<sin src>')}")


def validate_support_files(errors: list[str]) -> None:
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "/LectorcitoPro/page/" not in robots:
        fail(errors, "robots.txt: falta bloquear /page/.")
    if f"Sitemap: {CANONICAL_URL}sitemap.xml" not in robots:
        fail(errors, "robots.txt: falta referencia al sitemap canónico.")

    sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text or "" for node in sitemap_root.findall("sm:url/sm:loc", namespace)]
    if locations != [CANONICAL_URL]:
        fail(errors, f"sitemap.xml: URLs inesperadas: {locations!r}")
    if any(".html" in location or "/page/" in location for location in locations):
        fail(errors, "sitemap.xml: contiene una URL no canónica o no indexable.")

    manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))
    for key in ("name", "short_name", "start_url", "scope", "theme_color"):
        if not manifest.get(key):
            fail(errors, f"manifest.webmanifest: falta {key}.")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    if "# Lectorcito Pro" not in llms or CANONICAL_URL not in llms:
        fail(errors, "llms.txt: falta identificación o URL oficial.")


def validate_branding_migration(errors: list[str]) -> None:
    branding_dir = ROOT / "resources" / "branding"
    expected = {
        "app_icon.ico",
        "app_icon.png",
        "logo_light_theme.png",
        "logo_dark_theme.png",
    }
    legacy = {
        "lector.ico",
        "lector.png",
        "logo_claro.png",
        "logo_oscuro.png",
    }

    missing = sorted(name for name in expected if not (branding_dir / name).is_file())
    if missing:
        fail(errors, f"Faltan recursos de branding renombrados: {', '.join(missing)}")

    remaining_legacy = sorted(name for name in legacy if (branding_dir / name).exists())
    if remaining_legacy:
        fail(errors, f"Persisten nombres antiguos en branding: {', '.join(remaining_legacy)}")


def validate_icon_migration(errors: list[str]) -> None:
    expected_icons = {
        "close",
        "delete",
        "destination",
        "github",
        "hide",
        "info",
        "language",
        "last_report",
        "media",
        "moon",
        "profiles",
        "read_complete",
        "readings_folder",
        "restore",
        "settings",
        "sun",
        "tree",
        "view",
    }
    missing_icons = [
        name for name in sorted(expected_icons) if not (ROOT / "resources/icons" / f"{name}.svg").is_file()
    ]
    if missing_icons:
        fail(errors, f"Faltan SVG migrados en resources/icons: {', '.join(missing_icons)}")

    targets = [
        ROOT / "src/view/ui_assets.py",
        ROOT / "resources/css/styles.css",
        ROOT / "resources/js/scripts.js",
        ROOT / "index.html",
    ]
    for path in targets:
        source = path.read_text(encoding="utf-8")
        if "icons/svg" in source or '"icons", "svg"' in source:
            fail(errors, f"{path.relative_to(ROOT)}: todavía usa resources/icons/svg.")
        if path.suffix in {".html", ".js", ".css"} and re.search(
            r"(?:resources/|\.\./)?icons/[^\s\"')]+\.png", source, flags=re.IGNORECASE
        ):
            fail(errors, f"{path.relative_to(ROOT)}: todavía usa PNG dentro de resources/icons.")


def validate_generated_metadata(errors: list[str]) -> None:
    module_path = ROOT / "src/app_meta.py"
    spec = importlib.util.spec_from_file_location("lectorcito_app_meta", module_path)
    if spec is None or spec.loader is None:
        fail(errors, "No se pudo cargar src/app_meta.py para validar metadata web.")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected = module.build_web_meta_js()
    actual = (ROOT / "resources/js/app_meta.js").read_text(encoding="utf-8")
    if actual != expected:
        fail(errors, "resources/js/app_meta.js está desincronizado de src/app_meta.py.")


def main() -> int:
    errors: list[str] = []
    required = [
        "index.html",
        "404.html",
        "robots.txt",
        "sitemap.xml",
        "llms.txt",
        "manifest.webmanifest",
        "resources/css/styles.css",
        "resources/js/scripts.js",
        "resources/js/app_meta.js",
    ]
    for relative_path in required:
        if not (ROOT / relative_path).is_file():
            fail(errors, f"Falta archivo SEO requerido: {relative_path}")

    if not errors:
        validate_index(errors)
        validate_404(errors)
        validate_support_files(errors)
        validate_branding_migration(errors)
        validate_icon_migration(errors)
        validate_generated_metadata(errors)

    if errors:
        print("Validación SEO fallida:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validación SEO correcta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
