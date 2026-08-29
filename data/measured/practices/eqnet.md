---
id: eqnet
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: main
tip: af94a08a85de4b2c917a1b9429b044e7f38e4c28
files: 101
practices:
  readme: true
  license_file: true
  packaging: true
  tests: true
  ci: true
  coverage: false
  docs: true
  examples: true
  changelog: false
  contributing: false
  lint: false
  typed: false
evidence:
  ci: .github/workflows/docs.yml
  docs: mkdocs.yml
  examples: scripts/utils/plot_example.py
  license_file: LICENSE
  packaging: setup.py
  readme: docs/README.md
  tests: tests/fastapi/test_fastapi.py
error: ''
missing: {}
---
