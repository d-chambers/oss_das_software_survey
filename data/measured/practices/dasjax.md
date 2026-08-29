---
id: dasjax
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: main
tip: 4df967b8db3c5dde9da168046b9c703b5635af67
files: 43
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
  typed: false
evidence:
  ci: .github/workflows/tests.yml
  license_file: LICENSE
  lint: .pre-commit-config.yaml
  packaging: pyproject.toml
  readme: README.md
  tests: tests/conftest.py
error: ''
missing: {}
---
