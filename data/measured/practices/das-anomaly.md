---
id: das-anomaly
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: main
tip: b82c9b79c7f744bf270fa12e561cd6c8df867122
files: 52
practices:
  readme: true
  license_file: true
  packaging: true
  tests: true
  ci: true
  coverage: true
  docs: false
  examples: true
  changelog: false
  contributing: false
  lint: true
  typed: false
evidence:
  ci: .github/workflows/run_test.yml
  coverage: README badge
  examples: examples/plot_psd.ipynb
  license_file: LICENSE
  lint: .pre-commit-config.yaml
  packaging: pyproject.toml
  readme: README.md
  tests: tests/conftest.py
error: ''
missing: {}
---
