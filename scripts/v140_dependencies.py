#!/usr/bin/env python3
"""Render what the ecosystem's Python is built on: the most-used packages.

Figure scripts are prefixed `v` and sit outside the `a` pipeline: they read
whatever the repository currently holds and write SVG plus PNG into figures/,
so they can be re-run after any change without re-collecting anything.
"""

from __future__ import annotations

import sys
from pathlib import Path

from oss_das.figures import plates
from oss_das.figures.cli import figure_parser, resolve_out
from oss_das.figures.data import dependency_mix_from_records
from oss_das.figures.render import write_figure

#: The output is named after this script, so a figure always says what made it.
NAME = Path(__file__).stem


def main() -> int:
    args = figure_parser(__doc__).parse_args()
    written = write_figure(
        NAME,
        plates.dependency_plate(dependency_mix_from_records()),
        resolve_out(args),
        pdf=args.pdf,
        keep_text=args.keep_text,
    )
    for path in written:
        print(f"wrote {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
