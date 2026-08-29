#!/usr/bin/env bash
# Run the pipeline end to end, stopping at the first failure.
#
# A stops before the model layer and the agent (both cost money) unless
# RUN_MODELS=1; review is interactive and is never run from here. B and C run
# in full. GITHUB_TOKEN is needed for a010 and b012; without it both record
# GitHub as unavailable rather than failing.
set -euo pipefail
cd "$(dirname "$0")/.."

run() { echo "== $*"; uv run python "$@"; }

run scripts/a010_discover_forges.py
run scripts/a011_discover_registries.py
if [[ "${RUN_MODELS:-0}" == "1" ]]; then
  run scripts/a020_triage.py --model "${TRIAGE_MODEL:-haiku}"
  run scripts/a021_enrich.py
else
  run scripts/a020_triage.py
  echo "skipping the model layer and enrichment (set RUN_MODELS=1); review with: uv run marimo edit notebooks/review.py"
fi

run scripts/b010_mirror.py "$@"
run scripts/b011_git.py
run scripts/b012_forge.py
run scripts/b013_registry.py
run scripts/b014_publications.py
run scripts/b015_practices.py

run scripts/c010_build_tables.py
echo "done: uv run marimo run notebooks/ecosystem.py"
