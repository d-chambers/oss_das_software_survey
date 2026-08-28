"""Small shared utilities with no project-specific policy."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def parse_date(value: str) -> date:
    return date.fromisoformat(value[:10])


def days_between(earlier: str | None, later: str) -> int | None:
    if not earlier:
        return None
    return (parse_date(later) - parse_date(earlier)).days


def normalize_name(value: str) -> str:
    """Normalize Python package names according to PEP 503."""
    return re.sub(r"[-_.]+", "-", value).lower()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def flatten_dict(value: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, item in value.items():
        name = f"{prefix}_{key}" if prefix else key
        if isinstance(item, dict):
            output.update(flatten_dict(item, name))
        elif isinstance(item, list):
            output[name] = ";".join(str(part) for part in item)
        else:
            output[name] = item
    return output
