"""Write a figure to disk as SVG and PDF.

The SVG is the source of truth; the PDF is what goes into a slide deck or a
paper, where a vector that a viewer cannot re-render is what is wanted.

Conversion shells out to Inkscape rather than using a Python renderer, because
these figures are set in Georgia and the point of the PDF is that the typography
survives. A Python rasteriser silently substitutes a fallback face when the font
is missing, and a silently wrong figure is worse than a missing one -- so a
missing converter raises rather than degrading.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class RenderError(RuntimeError):
    """A figure could not be converted to PDF."""


def _converter() -> str:
    found = shutil.which("inkscape")
    if found is None:
        raise RenderError(
            "inkscape is not installed, so no PDF can be written. "
            "Install it (apt install inkscape), or drop --pdf to write SVG only."
        )
    return found


def write_figure(
    name: str, svg: str, out_dir: Path, *, pdf: bool = True, keep_text: bool = False
) -> list[Path]:
    """Write ``name``.svg, and ``name``.pdf unless ``pdf`` is false.

    Text is converted to outlines by default so the figure renders identically
    wherever the PDF is opened. Pass ``keep_text`` to keep it live and
    selectable, which a publisher may require but which then depends on the
    reader having the font."""
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / f"{name}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    written = [svg_path]
    if not pdf:
        return written
    pdf_path = out_dir / f"{name}.pdf"
    command = [_converter(), "--export-type=pdf"]
    if not keep_text:
        command.append("--export-text-to-path")
    command += [f"--export-filename={pdf_path}", str(svg_path)]
    result = subprocess.run(
        command,
        capture_output=True,
        timeout=180,
    )
    if result.returncode != 0 or not pdf_path.exists():
        detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
        raise RenderError(
            detail[-1] if detail else f"inkscape exited {result.returncode}"
        )
    written.append(pdf_path)
    return written


def load_asset(name: str, assets_dir: Path) -> str:
    """Return a hand-drawn SVG fragment for a plate to embed.

    Artwork is kept as editable SVG rather than generated, so it can be opened
    in a vector editor and changed without touching Python. Only the fragment's
    inner markup is taken; positioning is the plate's job.
    """
    path = assets_dir / f"{name}.svg"
    if not path.exists():
        raise RenderError(f"no such figure asset: {path}")
    text = path.read_text(encoding="utf-8")
    start, end = text.find("<g"), text.rfind("</g>")
    if start == -1 or end == -1:
        raise RenderError(f"{path}: expected a top-level <g> to embed")
    return text[start : end + 4]
