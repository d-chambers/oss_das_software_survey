#!/usr/bin/env python3
"""Render the licence mix: what share of DAS software is actually open source.

Figure scripts are prefixed `v` and sit outside the `a` pipeline: they read
whatever the repository currently holds and write SVG plus PDF into figures/,
so they can be re-run after any change without re-collecting anything.
"""

from __future__ import annotations

import sys

from oss_das.figures import plates
from oss_das.figures.cli import figure_parser, resolve_out
from oss_das.figures.data import licence_mix
from oss_das.figures.render import write_figure

NAME = "das_licence"


def main() -> int:
    args = figure_parser(__doc__).parse_args()
    mix = licence_mix()
    written = write_figure(
        NAME,
        plates.licence_plate(mix),
        resolve_out(args),
        pdf=not args.no_pdf,
        keep_text=args.keep_text,
    )
    for path in written:
        print(f"wrote {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
