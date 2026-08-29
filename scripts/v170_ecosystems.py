#!/usr/bin/env python3
"""Render how much each ecosystem builds on itself: DAS against seismology.

Figure scripts are prefixed `v` and write an output named after the script, so
a figure on a slide always says which script produced it.
"""

from __future__ import annotations

import sys
from pathlib import Path

from oss_das.figures import plates
from oss_das.figures.cli import figure_parser, resolve_out
from oss_das.figures.data import ecosystems
from oss_das.figures.render import write_figure

#: The output is named after this script, so a figure always says what made it.
NAME = Path(__file__).stem


def main() -> int:
    args = figure_parser(__doc__).parse_args()
    written = write_figure(
        NAME,
        plates.ecosystems_plate(*ecosystems()),
        resolve_out(args),
        pdf=args.pdf,
        png=args.png,
        keep_text=args.keep_text,
    )
    for path in written:
        print(f"wrote {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
