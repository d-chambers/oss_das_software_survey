#!/usr/bin/env python3
"""Build observable maintenance-signal views."""

from __future__ import annotations

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.site import health_figures, load_plot_data, render_page


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    data = load_plot_data(snapshot_date)
    render_page(
        "health.html",
        title="Health signals",
        heading="Maintenance signals need context",
        lede=(
            "Recency and repository structure are observable facts, not a verdict "
            "on scientific quality or long-term sustainability. Mature, stable "
            "software may change infrequently."
        ),
        snapshot_date=snapshot_date,
        figures=health_figures(data),
        body=(
            '<p class="note">Documentation, tests, and continuous integration are detected '
            "from paths in the default-branch tree. Presence does not measure "
            "coverage, accuracy, or maintenance quality. Lines of code are a rough "
            "size estimate from language byte counts, not a measure of quality or effort.</p>"
        ),
    )


if __name__ == "__main__":
    main()
