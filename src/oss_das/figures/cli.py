"""Shared argument handling for the `v` figure scripts."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from oss_das.core import PATHS


def figure_parser(description: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--snapshot-date",
        default=None,
        help="Snapshot to read; defaults to the newest one present.",
    )
    parser.add_argument("--out", type=Path, default=None, help="Output directory.")
    parser.add_argument(
        "--pdf", action="store_true", help="Also write a PDF beside the SVG."
    )
    parser.add_argument(
        "--no-png",
        dest="png",
        action="store_false",
        help="Skip the PNG. It is written by default, because the PNG is what "
        "goes on a slide.",
    )
    parser.add_argument(
        "--keep-text",
        action="store_true",
        help="Keep PDF text selectable instead of converting it to outlines.",
    )
    return parser


def resolve_out(args: argparse.Namespace) -> Path:
    return args.out or PATHS.root / "figures"


def snapshot(args: argparse.Namespace) -> str:
    """The snapshot to read: the one asked for, else the newest on disk."""
    if args.snapshot_date:
        date.fromisoformat(args.snapshot_date)
        return args.snapshot_date
    dated = sorted(
        p.name
        for p in (PATHS.root / "data" / "snapshots").glob("????-??-??")
        if p.is_dir()
    )
    return dated[-1] if dated else date.today().isoformat()
