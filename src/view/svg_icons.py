from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw

# =============================================================================
# RENDERIZADO LIGERO DE ICONOS SVG
# =============================================================================

_TOKEN_RE = re.compile(r"[A-Za-z]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
_COMMAND_LENGTHS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6}


def _parse_viewbox(root: ET.Element) -> tuple[float, float, float, float]:
    raw = root.attrib.get("viewBox", "0 0 16 16")
    values = [float(value) for value in raw.replace(",", " ").split()]
    if len(values) != 4:
        return 0.0, 0.0, 16.0, 16.0
    return values[0], values[1], max(1.0, values[2]), max(1.0, values[3])


def _sample_cubic(p0, p1, p2, p3, steps: int = 14):
    points = []
    for index in range(1, steps + 1):
        t = index / steps
        inv = 1.0 - t
        x = (
            inv * inv * inv * p0[0]
            + 3.0 * inv * inv * t * p1[0]
            + 3.0 * inv * t * t * p2[0]
            + t * t * t * p3[0]
        )
        y = (
            inv * inv * inv * p0[1]
            + 3.0 * inv * inv * t * p1[1]
            + 3.0 * inv * t * t * p2[1]
            + t * t * t * p3[1]
        )
        points.append((x, y))
    return points


def _parse_path_data(path_data: str):
    tokens = _TOKEN_RE.findall(path_data or "")
    index = 0
    command = None
    current = (0.0, 0.0)
    start = None
    subpath = []
    paths = []

    def finish_current(closed=False):
        nonlocal subpath
        if len(subpath) >= 2:
            paths.append((subpath, closed))
        subpath = []

    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token.upper()
            index += 1
            if command == "Z":
                if start is not None and subpath and subpath[-1] != start:
                    subpath.append(start)
                finish_current(closed=True)
                current = start or current
                start = None
                command = None
                continue

        if command not in _COMMAND_LENGTHS:
            index += 1
            continue

        need = _COMMAND_LENGTHS[command]
        if index + need > len(tokens):
            break
        try:
            values = [float(value) for value in tokens[index : index + need]]
        except ValueError:
            index += 1
            continue
        index += need

        if command == "M":
            if subpath:
                finish_current(closed=False)
            current = (values[0], values[1])
            start = current
            subpath = [current]
            command = "L"
        elif command == "L":
            current = (values[0], values[1])
            if not subpath:
                start = current
                subpath = [current]
            else:
                subpath.append(current)
        elif command == "H":
            current = (values[0], current[1])
            if not subpath:
                start = current
                subpath = [current]
            else:
                subpath.append(current)
        elif command == "V":
            current = (current[0], values[0])
            if not subpath:
                start = current
                subpath = [current]
            else:
                subpath.append(current)
        elif command == "C":
            if not subpath:
                start = current
                subpath = [current]
            p0 = current
            p1 = (values[0], values[1])
            p2 = (values[2], values[3])
            p3 = (values[4], values[5])
            subpath.extend(_sample_cubic(p0, p1, p2, p3))
            current = p3

    if subpath:
        finish_current(closed=False)
    return paths


def _transform_point(point, viewbox, pixel_size):
    min_x, min_y, box_w, box_h = viewbox
    pixel_w, pixel_h = pixel_size
    scale = min(pixel_w / box_w, pixel_h / box_h)
    offset_x = (pixel_w - box_w * scale) / 2.0
    offset_y = (pixel_h - box_h * scale) / 2.0
    return (
        offset_x + (point[0] - min_x) * scale,
        offset_y + (point[1] - min_y) * scale,
    )


@lru_cache(maxsize=128)
def render_svg_icon(
    svg_path: str,
    color: str,
    width: int,
    height: int,
    supersample: int = 4,
) -> Image.Image:
    """Rasteriza los SVG simples del proyecto sin agregar dependencias externas."""
    path = Path(svg_path)
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    viewbox = _parse_viewbox(root)
    pixel_size = (
        max(1, int(width)) * max(1, int(supersample)),
        max(1, int(height)) * max(1, int(supersample)),
    )
    image = Image.new("RGBA", pixel_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    box_scale = min(pixel_size[0] / viewbox[2], pixel_size[1] / viewbox[3])

    for element in root.iter():
        if element.tag.split("}")[-1] != "path":
            continue
        path_data = element.attrib.get("d", "")
        if not path_data:
            continue

        try:
            stroke_width = max(
                1, int(round(float(element.attrib.get("stroke-width", "1")) * box_scale))
            )
        except Exception:
            stroke_width = max(1, int(round(box_scale)))

        round_caps = element.attrib.get("stroke-linecap", "").lower() == "round"
        radius = stroke_width / 2.0

        for raw_points, closed in _parse_path_data(path_data):
            points = [_transform_point(point, viewbox, pixel_size) for point in raw_points]
            if len(points) < 2:
                continue
            draw.line(points, fill=color, width=stroke_width, joint="curve")

            if round_caps and not closed:
                for endpoint in (points[0], points[-1]):
                    x, y = endpoint
                    draw.ellipse(
                        (x - radius, y - radius, x + radius, y + radius),
                        fill=color,
                    )

    return image


def load_ctk_svg_image(
    svg_path: str,
    *,
    size: tuple[int, int],
    light_color: str,
    dark_color: str,
) -> ctk.CTkImage:
    width, height = int(size[0]), int(size[1])
    light_image = render_svg_icon(svg_path, light_color, width, height)
    dark_image = render_svg_icon(svg_path, dark_color, width, height)
    return ctk.CTkImage(
        light_image=light_image,
        dark_image=dark_image,
        size=(width, height),
    )
