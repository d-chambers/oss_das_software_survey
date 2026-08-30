#!/usr/bin/env python3
"""Render commits per year again, with each year's new arrivals called out.

The same plate as v120: the bars, the cohorts and the colour ramp are
identical. What changes is that the topmost band -- the projects committing in
their first year -- is drawn in red, and the figure above each bar is that
band's share of the year's commits. It answers the question v120 leaves open:
the field grows because projects keep arriving, not because the existing ones
deepen.

Figure scripts are prefixed `v` and write an output named after the script, so
a figure on a slide always says which script produced it.
"""

from __future__ import annotations

import sys
from pathlib import Path

from oss_das.figures import plates
from oss_das.figures.cli import figure_parser, resolve_out
from oss_das.figures.data import growth_by_cohort
from oss_das.figures.render import write_figure

#: The output is named after this script, so a figure always says what made it.
NAME = Path(__file__).stem


def main() -> int:
    args = figure_parser(__doc__).parse_args()
    written = write_figure(
        NAME,
        plates.stacked_years_plate(
            growth_by_cohort(),
            "Commits by year",
            "",
            sequential=True,
            highlight_new=True,
        ),
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
