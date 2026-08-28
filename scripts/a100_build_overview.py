#!/usr/bin/env python3
"""Build the overview page and copy public snapshot files into the site."""

from __future__ import annotations

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.site import load_plot_data, overview_content, prepare_docs, render_page


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    prepare_docs(snapshot_date)
    data = load_plot_data(snapshot_date)
    body, figures = overview_content(data)
    render_page(
        "index.html",
        title="Overview",
        heading="A map of open-source software for DAS",
        lede=(
            "A reproducible, dated view of reusable software for distributed "
            "acoustic sensing—what it does, how it is shared, and the different "
            "signals of community and scholarly use."
        ),
        snapshot_date=snapshot_date,
        figures=figures,
        body=body,
    )


if __name__ == "__main__":
    main()
