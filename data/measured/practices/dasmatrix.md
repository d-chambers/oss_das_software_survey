---
id: dasmatrix
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: main
tip: ab4e5f04228a5722440a64243420f1ee72809acd
files: 239
practices:
  readme: true
  license_file: false
  packaging: true
  tests: true
  ci: true
  coverage: false
  docs: true
  examples: true
  changelog: false
  contributing: true
  lint: true
  typed: true
evidence:
  ci: .github/workflows/ci.yml
  contributing: docs/contributing.md
  docs: mkdocs.yml
  examples: DASMatrix/examples.py
  lint: .pre-commit-config.yaml
  packaging: pyproject.toml
  readme: README.md
  tests: tests/unit/test_atoms.py
  typed: pyproject.toml
error: ''
missing: {}
---
