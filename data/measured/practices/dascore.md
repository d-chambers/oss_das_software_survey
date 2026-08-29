---
id: dascore
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: master
tip: e377e6635fab0d15881ee5175edfa1865d5c3836
files: 368
practices:
  readme: true
  license_file: true
  packaging: true
  tests: true
  ci: true
  coverage: true
  docs: true
  examples: true
  changelog: true
  contributing: true
  lint: true
  typed: false
evidence:
  changelog: docs/changelog.qmd
  ci: .github/workflows/lint.yml
  contributing: docs/contributing/contributing.qmd
  coverage: README badge
  docs: scripts/_templates/_quarto.yml
  examples: dascore/examples.py
  license_file: docs/LICENSE
  lint: .pre-commit-config.yaml
  packaging: pyproject.toml
  readme: readme.md
  tests: tests/conftest.py
error: ''
missing: {}
---
