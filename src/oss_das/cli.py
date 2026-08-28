"""Shared command-line argument helpers for ordered scripts."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from oss_das.core import newest_snapshot


def snapshot_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--snapshot-date",
        default=None,
        help="Snapshot date in YYYY-MM-DD format; defaults to latest or today.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use existing snapshot inputs and make no network requests.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing output for this stage.",
    )
    return parser


def resolve_snapshot_date(value: str | None, *, prefer_latest: bool = False) -> str:
    if value:
        date.fromisoformat(value)
        return value
    if prefer_latest:
        try:
            return newest_snapshot()
        except FileNotFoundError:
            pass
    return date.today().isoformat()


def require_existing(path: Path, *, offline: bool) -> bool:
    """Return True when an offline run should reuse the recorded input."""
    if path.exists() and offline:
        return True
    if offline:
        raise FileNotFoundError(f"offline input does not exist: {path}")
    return False
