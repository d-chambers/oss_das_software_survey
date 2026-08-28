#!/usr/bin/env python3
"""Build separate adoption and scholarly-impact views."""

from __future__ import annotations

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.site import adoption_figures, load_plot_data, render_page


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    data = load_plot_data(snapshot_date)
    render_page(
        "adoption.html",
        title="Adoption",
        heading="Adoption has several incompatible units",
        lede=(
            "Repository attention, installation traffic, and scholarly citations "
            "answer different questions. These charts stay separate and retain "
            "their original collection windows."
        ),
        snapshot_date=snapshot_date,
        figures=adoption_figures(data),
        body=(
            '<p class="note">Package downloads include CI and other automated '
            "traffic. Conda counts are cumulative per artifact, while PyPI is a "
            "recent mirror-filtered window. Canonical citations are not summed with "
            "related publications.</p>"
        ),
    )


if __name__ == "__main__":
    main()
