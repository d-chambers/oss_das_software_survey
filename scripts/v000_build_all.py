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

from oss_das.core import PATHS
from oss_das.figures.cli import figure_parser
from oss_das.figures.data import (
    composition_from_records,
    funnel_from_records,
    growth_from_records,
    licence_from_records,
    maturity_from_records,
    pipeline_from_records,
    totals_from_records,
)


def main() -> int:
    args = figure_parser(__doc__).parse_args()
    out = args.out or PATHS.root / "figures"
    scripts = sorted(Path(__file__).resolve().parent.glob("v0[1-9]0_*.py"))

    failed: list[str] = []
    for script in scripts:
        command = [sys.executable, str(script), "--out", str(out)]
        if args.pdf:
            command.append("--pdf")
        if args.keep_text:
            command.append("--keep-text")
        result = subprocess.run(command, capture_output=True, text=True)
        sys.stderr.write(result.stderr)
        if result.returncode != 0:
            failed.append(script.name)

    sidecar = {
        "source": "working tree",
        "ecosystem_totals": totals_from_records().sidecar(),
        "pipeline_flow": pipeline_from_records().sidecar(),
        "funnel": funnel_from_records().sidecar(),
        "licence_mix": licence_from_records().sidecar(),
        "composition": composition_from_records().sidecar(),
        "growth": growth_from_records().sidecar(),
        "maturity": maturity_from_records().sidecar(),
    }
    (out / "figures.json").write_text(json.dumps(sidecar, indent=1) + "\n")
    print(f"wrote {out / 'figures.json'}", file=sys.stderr)

    totals = totals_from_records()
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
