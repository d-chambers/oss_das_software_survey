#!/usr/bin/env python3
"""Quarto pre-render step for the talk. Run by `quarto render`, not by hand.

Reads:  figures/figures.json, figures/*.png, figures/*.svg, deck/slides.qmd
Writes: deck/_numbers.yml, deck/_svg/*.pdf

Three jobs quarto has no native way to do:

* resolve the measurements the slides cite into metadata quarto can substitute,
* prove each figure is the one those measurements describe, and
* convert hand-drawn SVGs to PDF, which beamer cannot place directly.

The first two exist because a deck that hard-codes its numbers goes stale
silently: the deck this replaced showed 78 projects on one slide and 77 on the
next. A citation this step cannot resolve stops the render.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

#: How a slide cites a measurement: {{< meta n.ecosystem_totals.projects >}}
REFERENCE = re.compile(r"\{\{<\s*meta\s+n\.([A-Za-z0-9_.]+)\s*>\}\}")

#: How a slide cites a figure. Every one must exist, or the slide renders a gap.
FIGURE = re.compile(r"!\[[^\]]*\]\((\.\./figures/[^)]+)\)")

#: How a slide cites a hand-drawn figure. Beamer cannot place an SVG, so the
#: build converts each to PDF -- vector in, vector out, sharp at any projection
#: size -- and the slide references the converted file.
VECTOR = re.compile(r"\(_svg/([A-Za-z0-9_.-]+)\.pdf\)")

#: Figures that scripts/v000_build_all.py regenerates, and so must be current.
GENERATED = re.compile(r"/v\d{3}_")

#: How far apart one build's outputs may be written, in seconds.
ONE_BUILD = 900.0


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    """Every scalar leaf of the sidecar, keyed by its dotted path."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            out.update(flatten(item, f"{prefix}.{key}" if prefix else str(key)))
        return out
    if isinstance(value, list):
        # By index, so n.network.providers.0.2 reaches the hub's count. Dropping
        # lists put the most quotable numbers out of reach and pushed them back
        # onto the slides as literals, which is what this build exists to stop.
        out = {}
        for index, item in enumerate(value):
            out.update(flatten(item, f"{prefix}.{index}" if prefix else str(index)))
        return out
    return {prefix: value}


def render_number(value: Any) -> str:
    """Numbers as a reader says them, with thousands separated."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return str(value)
    return f"{value:,}" if abs(value) >= 1_000 else f"{value:g}"


def as_yaml(tree: dict, indent: int = 0) -> str:
    """The nested mapping quarto substitutes from, quoted so it cannot re-type.

    Hand-rolled rather than PyYAML: quarto runs a pre-render script with the
    system interpreter, which has no access to this project's environment.
    """
    lines = []
    for key, value in tree.items():
        pad = "  " * indent
        if isinstance(value, dict):
            lines.append(f"{pad}{key}:")
            lines.append(as_yaml(value, indent + 1).rstrip("\n"))
        else:
            lines.append(f"{pad}{key}: '{str(value).replace(chr(39), chr(39) * 2)}'")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Tree holding deck/ and figures/. Defaults to the repository.",
    )
    args = parser.parse_args()

    deck = args.root / "deck"
    slides = deck / "slides.qmd"
    sidecar = args.root / "figures" / "figures.json"
    for path in (slides, sidecar):
        if not path.exists():
            print(f"missing {path}", file=sys.stderr)
            return 2

    numbers = flatten(json.loads(sidecar.read_text()))
    text = slides.read_text()

    wanted = set(REFERENCE.findall(text))
    missing = sorted(key for key in wanted if key not in numbers)
    if missing:
        # An authoring mistake, not an unreachable state, so it reports rather
        # than raising: a traceback tells the author less than the sentence does.
        print(
            "the deck cites measurements the sidecar does not define: "
            + ", ".join(missing)
            + " -- re-run scripts/v000_build_all.py, or fix the reference",
            file=sys.stderr,
        )
        return 2

    # Convert every cited SVG before anything looks for the file it becomes.
    vectors = sorted(set(VECTOR.findall(text)))
    if vectors:
        if shutil.which("inkscape") is None:
            print(
                "inkscape is not installed, so the vector figures cannot be "
                f"converted: {vectors}",
                file=sys.stderr,
            )
            return 2
        built = deck / "_svg"
        built.mkdir(exist_ok=True)
        for stem in vectors:
            source = args.root / "figures" / f"{stem}.svg"
            if not source.exists():
                print(f"no such vector figure: {source}", file=sys.stderr)
                return 2
            target = built / f"{stem}.pdf"
            if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
                continue
            code = subprocess.run(
                [
                    "inkscape",
                    "--export-type=pdf",
                    "--export-area-drawing",
                    f"--export-filename={target}",
                    str(source),
                ],
                capture_output=True,
            ).returncode
            if code != 0 or not target.exists():
                print(f"could not convert {source}", file=sys.stderr)
                return 2
        print(f"converted {len(vectors)} vector figures", file=sys.stderr)

    figures = sorted(set(FIGURE.findall(text)))
    absent = [f for f in figures if not (deck / f).resolve().exists()]
    if absent:
        print(f"the deck cites figures that do not exist: {absent}", file=sys.stderr)
        return 2

    # Anything naming figures/ that the reference form did not catch would slip
    # past both checks above and render as a gap.
    unaccounted = sorted(
        set(re.findall(r"[^\s()\[\]\"']*figures/[^\s()\[\]\"']+", text))
        - set(figures)
        - {f"figures/{stem}.svg" for stem in vectors}
    )
    if unaccounted:
        print(
            f"figures referenced in a form this build cannot check: {unaccounted}",
            file=sys.stderr,
        )
        return 2

    # Content, not modification time. Git rewrites every mtime to the checkout
    # time, so a spread of seconds proved nothing: a stale figure beside a fresh
    # sidecar looked current, which is the exact failure this guards against.
    recorded = json.loads(sidecar.read_text()).get("figures") or {}
    if not recorded:
        print(
            "figures.json records no figure checksums; re-run "
            "scripts/v000_build_all.py",
            file=sys.stderr,
        )
        return 2
    drifted = []
    for reference in figures:
        path = (deck / reference).resolve()
        if not GENERATED.search(reference):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if recorded.get(path.name) != digest:
            drifted.append(path.name)
    if drifted:
        print(
            f"these figures are not the ones figures.json describes: "
            f"{', '.join(sorted(drifted))} -- run scripts/v000_build_all.py so "
            "the slides and their numbers come from one build",
            file=sys.stderr,
        )
        return 2

    # Nested, not flat: quarto resolves {{< meta n.a.b >}} by walking the
    # metadata tree, so a key literally named "a.b" is never found and the
    # shortcode prints itself into the slide.
    tree: dict[str, Any] = {}
    for key in sorted(wanted):
        cursor = tree
        *parents, leaf = key.split(".")
        for part in parents:
            cursor = cursor.setdefault(part, {})
        cursor[leaf] = render_number(numbers[key])

    out = deck / "_numbers.yml"
    out.write_text(
        "# Written by deck/prepare.py. Do not edit.\n" + as_yaml({"n": tree})
    )
    print(f"resolved {len(wanted)} numbers and {len(figures)} figures", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
