#!/usr/bin/env python3
"""Build the ecosystem landscape and capability page."""

from __future__ import annotations

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.site import landscape_figures, load_plot_data, render_page


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    data = load_plot_data(snapshot_date)
    render_page(
        "landscape.html",
        title="Landscape",
        heading="Different tools occupy different niches",
        lede=(
            "Categories and capabilities are manually reviewed. The adoption "
            "scatter includes only projects with both repository and recent PyPI data; "
            "registry absence is not plotted as zero."
        ),
        snapshot_date=snapshot_date,
        figures=landscape_figures(data),
        body=(
            '<p class="note">Use the legend to isolate categories and hover for '
            'exact values. Visit the <a href="catalog.html">catalog</a> for projects '
            "that are not distributed through PyPI.</p>"
        ),
    )


if __name__ == "__main__":
    main()
