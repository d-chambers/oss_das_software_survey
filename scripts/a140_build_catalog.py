#!/usr/bin/env python3
"""Build the searchable catalog and review-decision page."""

from __future__ import annotations

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.site import catalog_html, load_site_data, render_page


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    data = load_site_data(snapshot_date)
    render_page(
        "catalog.html",
        title="Catalog",
        heading="A reviewable catalog, including the edges",
        lede=(
            "Search included tools, the licensing and reusability watchlist, and "
            "explicit exclusions. Every decision remains visible and revisable."
        ),
        snapshot_date=snapshot_date,
        body=catalog_html(data),
    )


if __name__ == "__main__":
    main()
