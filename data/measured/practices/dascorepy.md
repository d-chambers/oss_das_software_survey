---
id: dascorepy
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: main
tip: bb3619abe0ab2c00712b88b1e4a3cf7b329b682c
files: 12
practices:
  readme: true
  license_file: true
  packaging: true
  tests: true
  ci: true
  coverage: false
  docs: false
  examples: false
  changelog: false
  contributing: false
  lint: true
  typed: true
evidence:
  ci: .github/workflows/tests.yml
  license_file: LICENSE
  lint: pyproject.toml
  packaging: pyproject.toml
  readme: README.md
  tests: tests/test_patch_namespace.py
  typed: pyproject.toml
error: ''
missing: {}
---
