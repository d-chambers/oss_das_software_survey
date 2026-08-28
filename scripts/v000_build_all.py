#!/usr/bin/env python3
"""Render every figure, and write the sidecar recording their numbers.

Runs each `v0NN_*.py` in order. A figure that fails does not stop the rest --
one unreachable measurement should not cost the whole deck -- but the exit
status is non-zero so a failure cannot pass unnoticed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from oss_das.cli import resolve_snapshot_date
from oss_das.core import PATHS
from oss_das.figures.cli import figure_parser
from oss_das.figures.data import (
    composition,
    ecosystem_totals,
    growth,
    licence_mix,
    maturity,
    pipeline_flow,
    selection_funnel,
)


def main() -> int:
    args = figure_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    out = args.out or PATHS.root / "figures"
    scripts = sorted(Path(__file__).resolve().parent.glob("v0[1-9]0_*.py"))

    failed: list[str] = []
    for script in scripts:
        command = [
            sys.executable,
            str(script),
            "--snapshot-date",
            snapshot_date,
            "--out",
            str(out),
        ]
        if args.no_pdf:
            command.append("--no-pdf")
        if args.keep_text:
            command.append("--keep-text")
        result = subprocess.run(command, capture_output=True, text=True)
        sys.stderr.write(result.stderr)
        if result.returncode != 0:
            failed.append(script.name)

    sidecar = {
        "snapshot": snapshot_date,
        "ecosystem_totals": ecosystem_totals().sidecar(),
        "pipeline_flow": pipeline_flow(snapshot_date).sidecar(),
        "selection_funnel": selection_funnel(snapshot_date).sidecar(),
        "licence_mix": licence_mix().sidecar(),
        "composition": composition().sidecar(),
        "growth": growth().sidecar(),
        "maturity": maturity().sidecar(),
    }
    (out / "figures.json").write_text(json.dumps(sidecar, indent=1) + "\n")
    print(f"wrote {out / 'figures.json'}", file=sys.stderr)

    totals = ecosystem_totals()
    if totals.unmirrored:
        print(
            f"note: {len(totals.unmirrored)} included project(s) have no mirror, so "
            f"contribute no commits or lines: {', '.join(totals.unmirrored)}",
            file=sys.stderr,
        )
    if failed:
        print(f"FAILED: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(
        f"{len(scripts) - len(failed)}/{len(scripts)} figures rendered", file=sys.stderr
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
