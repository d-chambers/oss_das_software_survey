"""Write a figure to disk as SVG, PNG, and optionally PDF.

The SVG is the source of truth. The PNG is what goes on a slide: PowerPoint
places it without re-rendering anything, so what is seen in the deck is exactly
what was written here. The PDF is for a paper, where a vector is wanted.

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


#: Pixels across the exported PNG. Wide enough to fill a 16:9 slide at better
#: than screen resolution, so the deck never shows a softened edge.
PNG_WIDTH = 2400

#: User units of clear space left around the ink when cropping. Enough to keep
#: a descender or a bar's edge off the boundary, not enough to read as margin.
PNG_MARGIN = 20


def _export(svg_path: Path, out_path: Path, args: list[str]) -> Path:
    # Crop to the ink rather than the canvas: whatever slack a plate leaves at
    # its edges is not the slide's problem. A figure with nothing drawn in it
    # has no bounding box to crop to, so fall back to the page and let an
    # empty figure be empty rather than an error.
    crops = (["--export-area-drawing", f"--export-margin={PNG_MARGIN}"], [])
    for crop in crops:
        result = subprocess.run(
            [
                _converter(),
                *crop,
                *args,
                f"--export-filename={out_path}",
                str(svg_path),
            ],
            capture_output=True,
            timeout=180,
        )
        if result.returncode == 0 and out_path.exists():
            return out_path
        stderr = result.stderr.decode("utf-8", "replace")
        if "bounding box" not in stderr:
            break
    detail = stderr.strip().splitlines()
    raise RenderError(detail[-1] if detail else f"inkscape exited {result.returncode}")


def write_figure(
    name: str,
    svg: str,
    out_dir: Path,
    *,
    pdf: bool = False,
    png: bool = True,
    keep_text: bool = False,
) -> list[Path]:
    """Write ``name``.svg, ``name``.png, and ``name``.pdf if asked.

    Text is converted to outlines in the PDF by default so the figure renders
    identically wherever it is opened. Pass ``keep_text`` to keep it live and
    selectable, which a publisher may require but which then depends on the
    reader having the font."""
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / f"{name}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    written = [svg_path]
    if png:
        written.append(
            _export(
                svg_path,
                out_dir / f"{name}.png",
                ["--export-type=png", f"--export-width={PNG_WIDTH}"],
            )
        )
    if pdf:
        args = ["--export-type=pdf"]
        if not keep_text:
            args.append("--export-text-to-path")
        written.append(_export(svg_path, out_dir / f"{name}.pdf", args))
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
