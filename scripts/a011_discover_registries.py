#!/usr/bin/env python3
"""Sweep the package registries for fiber-sensing packages and record each once.

Reads:  data/rejected.yml, data/raw/candidates/**/*.md (existing keys are kept)
Writes: data/raw/candidates/{pypi,conda,julia}/<name>.md (write-once,
        long description as body), data/raw/coverage.csv (one row per registry)

A registry is searched, not looked up: every name in the PyPI simple index,
the conda-forge channel data, and the Julia General registry is filtered by
name token, and the matches' metadata is read for domain vocabulary. That is
what finds a package nobody has told the census about. No token is needed.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime

from oss_das.clients import (
    CondaForgeChannelClient,
    JuliaRegistryFilesClient,
    PyPIClient,
)
from oss_das.clients.base import SourceError
from oss_das.core import load_rejections
from oss_das.discover import (
    CandidateStore,
    append_coverage,
    conda_candidate,
    julia_candidate,
    julia_registry_names,
    pypi_candidate,
    registry_failure_row,
    sweep_registry,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--registry", nargs="*", choices=["pypi", "conda", "julia"], default=None
    )
    args = parser.parse_args()
    chosen = set(args.registry or ["pypi", "conda", "julia"])

    store = CandidateStore(rejected=frozenset(load_rejections()))
    now = datetime.now(UTC).replace(microsecond=0)
    today = now.date().isoformat()

    def report(name: str, error: Exception) -> None:
        print(f"  FAIL {name}: {str(error)[:100]}", file=sys.stderr)

    def sweep_pypi() -> list[str]:
        with PyPIClient(min_interval=0.2) as pypi:
            names = pypi.index_names()
            print(f"pypi index: {len(names)} names", file=sys.stderr)
            return sweep_registry(
                "pypi",
                names,
                lambda name: pypi_candidate(pypi.metadata(name), first_seen=today),
                store=store,
                fetched_at=now.isoformat(),
                coverage=append_coverage,
                on_error=report,
            )

    def sweep_conda() -> list[str]:
        with CondaForgeChannelClient() as conda:
            packages = conda.channeldata()
        print(f"conda-forge index: {len(packages)} names", file=sys.stderr)
        return sweep_registry(
            "conda",
            packages,
            lambda name: conda_candidate(name, packages[name], first_seen=today),
            store=store,
            fetched_at=now.isoformat(),
            coverage=append_coverage,
            on_error=report,
        )

    def sweep_julia() -> list[str]:
        with JuliaRegistryFilesClient() as julia:
            paths = julia_registry_names(julia.registry_toml())
            print(f"julia general index: {len(paths)} names", file=sys.stderr)
            return sweep_registry(
                "julia",
                paths,
                lambda name: julia_candidate(
                    name, paths[name], julia.package_toml(paths[name]), first_seen=today
                ),
                store=store,
                fetched_at=now.isoformat(),
                coverage=append_coverage,
                on_error=report,
            )

    sweeps = {"pypi": sweep_pypi, "conda": sweep_conda, "julia": sweep_julia}
    totals: dict[str, int] = {}
    for source, sweep in sweeps.items():
        if source not in chosen:
            continue
        try:
            totals[source] = len(sweep())
        except (SourceError, KeyError, TypeError, ValueError) as error:
            # An unreadable index is recorded, and the next registry still runs.
            append_coverage(
                registry_failure_row(source, error, fetched_at=now.isoformat())
            )
            print(f"{source}: index unavailable: {str(error)[:200]}", file=sys.stderr)

    for source, count in totals.items():
        print(f"{source}: {count} new candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
