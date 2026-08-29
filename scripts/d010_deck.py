#!/usr/bin/env python3
"""Compile the talk from the repository: figures, numbers, and slides.

Reads:  figures/figures.json, figures/*.png, deck/slides.qmd
Writes: deck/_numbers.yml, deck/talk.pdf

Every number on a slide is a reference into the measurement sidecar, never a
literal. A deck that hard-codes its numbers goes stale silently -- the previous
one showed 78 projects on one slide and 77 on the next -- so a reference this
script cannot resolve fails the build instead of rendering blank.
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

import yaml

from oss_das.core import PATHS

#: How a slide cites a measurement: {{< meta n.ecosystem_totals.projects >}}
REFERENCE = re.compile(r"\{\{<\s*meta\s+n\.([A-Za-z0-9_.]+)\s*>\}\}")

#: How a slide cites a figure. Every one must exist, or the slide renders a gap.
FIGURE = re.compile(r"!\[[^\]]*\]\((\.\./figures/[^)]+)\)")

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


def render(deck: Path, slides: Path, numbers: Path, extra: list[str] | None = None):
    """Run quarto in the deck directory, surfacing only what failed."""
    result = subprocess.run(
        [
            "quarto",
            "render",
            slides.name,
            "--metadata-file",
            numbers.name,
            *(extra or []),
        ],
        cwd=deck,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr[-4000:])
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=PATHS.root,
        help="Tree holding deck/ and figures/. Defaults to the repository.",
    )
    parser.add_argument(
        "--no-render", action="store_true", help="Resolve numbers but skip quarto."
    )
    parser.add_argument(
        "--notes",
        action="store_true",
        help="Also write talk-notes.pdf, the speaker notes alone.",
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

    figures = sorted(set(FIGURE.findall(text)))
    absent = [f for f in figures if not (deck / f).resolve().exists()]
    if absent:
        print(f"the deck cites figures that do not exist: {absent}", file=sys.stderr)
        return 2

    # Anything naming figures/ that the reference form did not catch would slip
    # past both checks above and render as a gap.
    unaccounted = sorted(
        set(re.findall(r"[^\s()\[\]\"']*figures/[^\s()\[\]\"']+", text)) - set(figures)
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
        "# Written by scripts/d010_deck.py. Do not edit.\n"
        + yaml.safe_dump(
            {"n": tree}, sort_keys=True, default_flow_style=False, default_style="'"
        )
    )
    print(f"resolved {len(wanted)} numbers and {len(figures)} figures", file=sys.stderr)

    if args.no_render:
        return 0
    if shutil.which("quarto") is None:
        print("quarto is not installed, so no PDF was written", file=sys.stderr)
        return 2
    if render(deck, slides, out) != 0:
        return 1
    print(f"wrote {deck / 'talk.pdf'}", file=sys.stderr)

    if args.notes:
        # The slides carry no prose by design, so the notes are where the talk
        # actually lives. Beamer hides them from the slide PDF; this renders
        # them alone, as something to hold.
        header = deck / "_notes.tex"
        header.write_text(
            "\\setbeameroption{show only notes}\n"
            "\\setbeamerfont{note page}{size=\\small}\n"
        )
        code = render(
            deck,
            slides,
            out,
            extra=[
                "--metadata",
                "include-in-header:_notes.tex",
                "--output",
                "talk-notes.pdf",
            ],
        )
        header.unlink(missing_ok=True)
        if code != 0:
            return 1
        print(f"wrote {deck / 'talk-notes.pdf'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
