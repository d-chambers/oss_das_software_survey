"""Shared argument handling for the `v` figure scripts."""

from __future__ import annotations

import argparse
from pathlib import Path

from oss_das.cli import resolve_snapshot_date
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
        "--no-pdf", action="store_true", help="Write SVG only, skipping the PDF."
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
    return resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
